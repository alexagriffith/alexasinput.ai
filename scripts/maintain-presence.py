#!/usr/bin/env python3
"""Refresh public content from publisher feeds; never publish drafts or infer names."""
import argparse
import concurrent.futures
import datetime as dt
import email.utils
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_URL = "https://raw.githubusercontent.com/alexagriffith/alexagriffith.githhub.io/master/data/presence.json"

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def plain(value):
    parser = Text()
    parser.feed(value or "")
    return " ".join(" ".join(parser.parts).split())

def https(value):
    if urlparse(value).scheme != "https" or not urlparse(value).netloc:
        raise ValueError("Expected a public HTTPS URL")
    return value

def fetch(url):
    last = None
    for attempt in range(3):
        try:
            req = Request(https(url), headers={"User-Agent": "AlexaGriffith-PublicSiteMaintenance/1.0", "Accept": "*/*"})
            with urlopen(req, timeout=25) as response:
                data = response.read(6_000_001)
                if len(data) > 6_000_000:
                    raise ValueError("Source response exceeded 6 MB")
                return data.decode("utf-8")
        except (HTTPError, URLError, TimeoutError) as exc:
            last = exc
            if attempt < 2:
                time.sleep(attempt + 1)
    raise last

def feed(url, expected):
    document = ET.fromstring(fetch(url))
    channel = document.find("channel")
    if channel is None or expected.lower() not in (channel.findtext("title") or "").lower():
        raise ValueError("Feed identity did not match " + expected)
    now = dt.datetime.now(dt.timezone.utc)
    entries = []
    for item in channel.findall("item"):
        if not item.findtext("pubDate"):
            continue
        published = email.utils.parsedate_to_datetime(item.findtext("pubDate"))
        if published.tzinfo is None:
            published = published.replace(tzinfo=dt.timezone.utc)
        if published > now:
            continue
        link = https(item.findtext("link") or "")
        title = plain(item.findtext("title"))
        if not title:
            raise ValueError("Published feed item has no title")
        entries.append({
            "title": title, "url": link, "date": published.date().isoformat(),
            "description": plain(item.findtext("description"))[:320]
        })
    if not entries:
        raise ValueError("Feed has no published entries")
    return sorted(entries, key=lambda item: item["date"], reverse=True)

class ArticleLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.items = {}
    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "a" and "/articles/" in attr.get("href", ""):
            self.current = [urljoin("https://developers.redhat.com", attr["href"]), []]
    def handle_data(self, data):
        if self.current:
            self.current[1].append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.current:
            url, words = self.current
            title = " ".join(" ".join(words).split())
            match = re.search(r"/articles/(\d{4})/(\d{2})/(\d{2})/", url)
            if title and match:
                self.items[url] = {"url": https(url), "title": title, "date": "-".join(match.groups())}
            self.current = None

def articles(url):
    parser = ArticleLinks()
    parser.feed(fetch(url))
    if not parser.items:
        raise ValueError("Could not parse published Red Hat articles; preserving existing content")
    return sorted(parser.items.values(), key=lambda item: item["date"], reverse=True)[:4]

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

def replace_region(source, name, body):
    start, end = "<!-- presence:" + name + ":start -->", "<!-- presence:" + name + ":end -->"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError("Missing or duplicate generated region: " + name)
    return source.split(start)[0] + start + body + end + source.split(end)[1]

def refresh(site):
    local_registry = json.loads((ROOT / "data/presence.json").read_text())
    registry = json.loads(fetch(REGISTRY_URL)) if site == "podcast" else local_registry
    links = registry["links"]
    # Validate each source before changing its section. Unavailable sources keep
    # their last reviewed content and are explicitly reported as unverified.
    inputs = {
        "alexas_input": (feed, (links["alexas_rss"], "Alexa")),
        "attention": (feed, (links["attention_rss"], "Attention Deficit")),
        "writing": (articles, (links["writing"],))
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {key: pool.submit(fn, *args) for key, (fn, args) in inputs.items()}
        snapshots = {}
        failures = {}
        previous = ROOT / "data/published.json"
        if previous.exists():
            snapshots = json.loads(previous.read_text())
        for key, future in futures.items():
            try:
                snapshots[key] = future.result()
            except Exception as exc:
                failures[key] = str(exc)
                print("::warning::Published source unavailable; preserving " + key + ": " + str(exc))
        write_json(ROOT / "reports/source-health.json", {"unverified_sources": failures})
    esc = lambda value: html.escape(value, quote=True)
    if site == "personal":
        path = ROOT / "index.html"
        source = path.read_text()
        for key, region in (("alexas_input", "latest-alexas-input"), ("attention", "latest-attention")):
            if not snapshots.get(key):
                continue
            ep = snapshots[key][0]
            body = '<p>Latest published episode: <a href="' + esc(ep["url"]) + '">' + esc(ep["title"]) + '</a> <time datetime="' + ep["date"] + '">(' + ep["date"] + ')</time>.</p>'
            source = replace_region(source, region, body)
        # Keep the historical archive; only the bounded recent-writing region
        # refreshes. Entries already outside that region are not duplicated.
        outside = replace_region(source, "writing", "")
        recent = [a for a in snapshots.get("writing", []) if a["url"] not in outside]
        body = "\n".join('<li><a href="' + esc(a["url"]) + '">' + esc(a["title"]) + '</a> [' + a["date"] + ']</li>' for a in recent)
        if snapshots.get("writing"):
            source = replace_region(source, "writing", "\n" + body + "\n")
        if source != path.read_text():
            path.write_text(source)
    else:
        path = ROOT / "data/site.json"
        data = json.loads(path.read_text())
        data["bio"] = registry["podcasts"]["alexas_input"]["description"]
        data["host_bio"] = registry["person"]["bio"]
        data["description"] = registry["podcasts"]["alexas_input"]["short_description"]
        if snapshots.get("alexas_input"):
            data["latest_published"] = snapshots["alexas_input"][0]
        if snapshots.get("attention"):
            data["attention"]["episodes"] = snapshots["attention"][:3]
        if snapshots.get("writing"):
            data["writing"] = snapshots["writing"]
        for platform in data["platforms"]:
            keys = {"YouTube": "alexas_youtube", "Spotify": "alexas_spotify", "Apple Podcasts": "alexas_apple", "RSS": "alexas_rss", "Substack": "alexas_substack", "Instagram": "alexas_instagram", "TikTok": "alexas_tiktok", "X": "x"}
            if platform["name"] in keys:
                platform["url"] = links[keys[platform["name"]]]
        write_json(ROOT / "data/presence.json", registry)
        write_json(path, data)
    # No check timestamp in tracked output: unchanged publications make no commit.
    write_json(ROOT / "data/published.json", snapshots)

def check(site):
    registry = json.loads((ROOT / "data/presence.json").read_text())
    assert registry["person"]["name"] == "Alexa Griffith"
    assert "Forward Deployed Engineer" in registry["person"]["jobTitle"]
    for value in registry["links"].values():
        https(value)
    pages = ["index.html", "links/index.html", "kubecon/index.html"] if site == "personal" else ["index.html"]
    for filename in pages:
        source = (ROOT / filename).read_text()
        assert len(re.findall(r"<h1(?:\s|>)", source)) == 1, filename + ": expected one main heading"
        assert 'rel="canonical"' in source, filename + ": missing canonical URL"
        ids = re.findall(r'\bid="([^"]+)"', source)
        assert len(ids) == len(set(ids)), filename + ": duplicate IDs"
        for block in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', source):
            json.loads(block)
        assert "@lexal0u" not in source, filename + ": obsolete current social handle"
    print("Public identity, canonical URLs, headings and structured data passed.")

def package(site):
    target = ROOT / "_site"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()
    names = ["index.html", "robots.txt", "sitemap.xml", "CNAME", "assets", "data"]
    names += ["links", "kubecon", "personal.html", "resume.html", "favicon.png", "apple-touch-icon.png"] if site == "personal" else ["favicon.svg", "styles.css", "site.js"]
    for name in names:
        path = ROOT / name
        if path.is_dir():
            shutil.copytree(path, target / name)
        elif path.is_file():
            shutil.copy2(path, target / name)

def audit():
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = set()
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "a" and a.get("href", "").startswith("https://"):
                self.links.add(a["href"].split("#")[0])
    urls = set()
    for path in ROOT.glob("**/*.html"):
        if any(part in {"_site", "tmp", "templates", ".git"} for part in path.parts):
            continue
        parser = Links()
        parser.feed(path.read_text())
        urls.update(parser.links)
    for page in ("https://alexagriffith.com/links/", "https://alexasinputai.com/", "https://www.attentiondeficit.ai/"):
        try:
            parser = Links()
            parser.feed(fetch(page))
            urls.update(parser.links)
        except Exception as exc:
            print("Unverified source page:", page, type(exc).__name__)
    def probe(url):
        try:
            with urlopen(Request(url, headers={"User-Agent": "AlexaGriffith-LinkAudit/1.0"}), timeout=20) as response:
                return {"url": url, "status": response.status, "final_url": response.url, "result": "reachable"}
        except HTTPError as exc:
            return {"url": url, "status": exc.code, "result": "broken" if exc.code in (404, 410) else "unverified"}
        except Exception as exc:
            return {"url": url, "result": "unverified", "error": type(exc).__name__}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, sorted(urls)))
    report = {"checked_at": dt.datetime.now(dt.timezone.utc).isoformat(), "links": results}
    write_json(ROOT / "reports/link-audit.json", report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as out:
            out.write("## Public link audit\n\n")
            for result in results:
                if result["result"] != "reachable":
                    out.write("- " + result["result"] + ": " + result["url"] + " (" + str(result.get("status", result.get("error"))) + ")\n")
            out.write("\nReachable: " + str(sum(r["result"] == "reachable" for r in results)) + "; total: " + str(len(results)) + ". Auth restrictions and rate limits are unverified, never counted as valid.\n")
    for result in results:
        if result["result"] != "reachable":
            print(json.dumps(result))
    print(json.dumps({status: sum(r["result"] == status for r in results) for status in ("reachable", "broken", "unverified")}))
    if any(r["result"] == "broken" for r in results):
        raise SystemExit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=("personal", "podcast"), required=True)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--audit-links", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        refresh(args.site)
    check(args.site)
    if args.package:
        package(args.site)
    if args.audit_links:
        audit()
