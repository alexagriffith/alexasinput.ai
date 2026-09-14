#!/usr/bin/env python3
"""Render the static homepage from reviewed, source-attributed content."""
import argparse
import html
import hashlib
import json
from pathlib import Path
from string import Template
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / 'data/site.json').read_text())
EPISODES = json.loads((ROOT / 'data/episodes.json').read_text())
esc = lambda value: html.escape(str(value), quote=True)

def safe_url(value):
    assert urlparse(value).scheme == 'https', f'Expected HTTPS URL: {value}'
    return esc(value)

def episode_card(ep, featured=False):
    video_id = ep['id']
    assert len(video_id) == 11 and all(c.isalnum() or c in '_-' for c in video_id)
    title = esc(ep['title'])
    description = f'<p class="episode-description">{esc(ep["description"])}</p>' if ep.get('description') else ''
    links = f'<a href="{safe_url(ep["url"])}">Watch on YouTube</a>'
    if ep.get('spotify'):
        links += f'<a href="{safe_url(ep["spotify"])}">Listen on Spotify</a>'
    if ep.get('notes'):
        links += f'<a href="{safe_url(ep["notes"])}">Read the takeaways</a>'
    return f'''<article class="episode-card{' featured' if featured else ''}" id="episode-{video_id}">
          <div class="video-shell" data-video-id="{video_id}">
            <img src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" alt="" width="480" height="360" loading="{'eager' if featured else 'lazy'}" {'fetchpriority="high"' if featured else ''}>
            <button class="video-play" type="button" aria-label="Play {title}" hidden><span aria-hidden="true">▶</span></button>
            <span class="duration" aria-label="Duration {esc(ep['duration'])}">{esc(ep['duration'])}</span>
          </div>
          <div class="episode-content">
            <h3>{title}</h3>
            {description}
            <div class="episode-links">{links}</div>
          </div>
        </article>'''

def duration_iso(value):
    parts = [int(p) for p in value.split(':')]
    seconds = sum(p * 60**i for i, p in enumerate(reversed(parts)))
    return f'PT{seconds}S'

def build():
    assert EPISODES and len({e['id'] for e in EPISODES}) == len(EPISODES)
    base = SITE['url']
    series_id = base + '#podcast'
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': base + '#website', 'url': base, 'name': SITE['name'], 'inLanguage': 'en'},
        {'@type': 'Person', '@id': 'https://alexagriffith.com/#person', 'name': 'Alexa Griffith', 'url': 'https://alexagriffith.com/'},
        {'@type': 'PodcastSeries', '@id': series_id, 'url': base, 'name': SITE['name'], 'description': SITE['bio'], 'author': {'@id': 'https://alexagriffith.com/#person'}, 'inLanguage': 'en', 'image': base + 'assets/alexas-input-logo.png', 'sameAs': [p['url'] for p in SITE['platforms'][:5]]},
        {'@type': 'CollectionPage', '@id': base + '#webpage', 'url': base, 'name': SITE['name'], 'isPartOf': {'@id': base + '#website'}, 'about': {'@id': series_id}, 'mainEntity': {'@id': base + '#episode-list'}},
        {'@type': 'ItemList', '@id': base + '#episode-list', 'name': 'Recent podcast episodes', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'PodcastEpisode', '@id': base + '#episode-' + ep['id'], 'url': ep['url'], 'name': ep['title'], 'image': f'https://i.ytimg.com/vi/{ep["id"]}/hqdefault.jpg', 'timeRequired': duration_iso(ep['duration']), 'partOfSeries': {'@id': series_id}, **({'description': ep['description']} if ep.get('description') else {})}}
            for i, ep in enumerate(EPISODES)]}
    ]}
    attention = '\n'.join(f'''<article class="text-card"><time datetime="{esc(ep['date'])}">{esc(ep['date'])}</time><h3><a href="{safe_url(ep['url'])}">{esc(ep['title'])}</a></h3><p>{esc(ep['description'])}</p></article>''' for ep in SITE['attention']['episodes'])
    writing = '\n'.join(f'''<article class="writing-item"><time datetime="{esc(a['date'])}">{esc(a['date'])}</time><h3><a href="{safe_url(a['url'])}">{esc(a['title'])}</a></h3><span class="publication">Red Hat Developer</span></article>''' for a in SITE['writing'])
    platforms = '\n'.join(f'''<a class="platform-link" href="{safe_url(p['url'])}"><span>{esc(p['name'])}<span aria-hidden="true">↗</span></span><small>{esc(p['label'])}</small></a>''' for p in SITE['platforms'])
    # Use the existing opening sentence verbatim for concise search/social snippets.
    description = SITE['bio'].split('. ')[0] + '.'
    rendered = Template((ROOT / 'templates/index.html').read_text()).substitute(
        name=esc(SITE['name']), description=esc(description), bio=esc(SITE['bio']),
        style_version=hashlib.sha256((ROOT / 'styles.css').read_bytes()).hexdigest()[:12],
        script_version=hashlib.sha256((ROOT / 'site.js').read_bytes()).hexdigest()[:12],
        schema=json.dumps(schema, ensure_ascii=False, indent=2).replace('<', '\\u003c'),
        featured=episode_card(EPISODES[0], True), archive='\n'.join(episode_card(ep) for ep in EPISODES[1:]),
        attention_bio=esc(SITE['attention']['bio']), attention=attention, writing=writing, platforms=platforms)
    return '\n'.join(line.rstrip() for line in rendered.splitlines()) + '\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Fail if the rendered homepage is stale')
    args = parser.parse_args()
    rendered = build()
    if args.check:
        assert (ROOT / 'index.html').read_text() == rendered, 'Run python3 scripts/build-site.py to update index.html'
        print('Homepage matches reviewed data.')
    else:
        (ROOT / 'index.html').write_text(rendered)
        print(f'Rendered {len(EPISODES)} episodes.')
