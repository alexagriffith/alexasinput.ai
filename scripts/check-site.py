#!/usr/bin/env python3
"""Check publication-critical structure, data alignment, and local assets."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []; self.links = []; self.assets = []; self.h1s = 0; self.main = 0
    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'h1': self.h1s += 1
        if tag == 'main': self.main += 1
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'img':
            assert 'alt' in a and 'width' in a and 'height' in a, 'Image missing accessible/layout attributes'
        if tag in ('img', 'script') and a.get('src'): self.assets.append(a['src'])
        if tag == 'link' and a.get('rel') in ('stylesheet', 'icon'): self.assets.append(a['href'])
        if tag == 'meta' and a.get('property') == 'og:image': self.assets.append(a['content'])

page = Page(); source = (ROOT / 'index.html').read_text(); page.feed(source)
assert page.h1s == page.main == 1, 'Expected one h1 and one main landmark'
assert len(page.ids) == len(set(page.ids)), 'Duplicate IDs'
for link in page.links:
    assert link, 'Empty link'
    if link.startswith('#'): assert link[1:] in page.ids, f'Broken anchor: {link}'
for asset in page.assets:
    parsed = urlparse(asset)
    if not parsed.netloc or parsed.netloc == 'alexasinputai.com':
        assert (ROOT / parsed.path.lstrip('/')).is_file(), f'Missing asset: {asset}'
site = json.loads((ROOT / 'data/site.json').read_text())
episodes = json.loads((ROOT / 'data/episodes.json').read_text())
assert page.ids.index('episode-' + episodes[0]['id']) < page.ids.index('archive-title'), 'Latest episode must be featured'
assert len({ep['id'] for ep in episodes}) == len(episodes)
assert all(ep['url'] in page.links for ep in episodes)
assert all(p['url'] in page.links for p in site['platforms'])
assert '50+' not in source, 'Unverified episode count'
assert '<iframe' not in source, 'Players should load only on request'
assert 'prefers-reduced-motion' in (ROOT / 'styles.css').read_text()
print(f'Checked landmarks, anchors, assets, {len(episodes)} episode links, and {len(site["platforms"])} platform links.')
