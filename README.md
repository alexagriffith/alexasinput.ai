# Alexa’s Input (AI)

Podcast website: https://alexasinputai.com/

GitHub Pages publishes the repository root from `main`.

## Content and sources

- `data/site.json` holds the podcast bio, platform links, Attention Deficit episodes, and published writing. Source URLs and the verification date are recorded alongside the content.
- The podcast bio is verbatim from the public YouTube and Spotify show descriptions, verified 2026-09-14. Update it from the established platform bio when it changes.
- `data/episodes.json` contains 12 recent full-length uploads in YouTube Videos-tab order, with verified titles and durations. The full archive remains linked on YouTube. Yan’s published Substack link is retained. His previously saved Spotify episode URL returned 404 and the Spotify show page did not list Yan during this review; that broken episode link was removed. The verified Spotify show link remains in Listen & follow.
- Attention Deficit titles, descriptions, and dates come from its public Substack feed. Writing titles and dates come from Alexa’s Red Hat Developer author page.
- `assets/alexas-input-logo.png` is the existing podcast artwork, used for social previews.

The page is a reviewed snapshot, not an automatic feed. Update the source data when publishing an episode. The older sync workflow and unpublished redesign branch are not deployed here; do not replace this page with their stale episode data.

## Build and check

Edit `templates/index.html` for structure, the JSON files for content, and `styles.css` / `site.js` for appearance and interaction. Do not edit generated `index.html` directly.

```sh
python3 scripts/build-site.py
python3 scripts/build-site.py --check
python3 scripts/check-site.py
node --check site.js
git diff --check
python3 -m http.server 8765
```

Open http://localhost:8765 to preview. Before publishing, verify desktop and mobile layouts, keyboard navigation, carousel boundaries, and video playback. JavaScript adds carousel controls, localized dates, and click-to-load YouTube players; all content and destination links remain usable without it.

## Search and accessibility

The homepage includes a canonical URL, social preview tags, and JSON-LD identifying the website, host, podcast, and visible episode collection. Structured content matches the page; it does not claim ratings, audience size, or guarantee search placement. `robots.txt` and `sitemap.xml` use the production domain.

The carousel has no autoplay rotation. It supports native touch scrolling, labeled buttons, arrow/Home/End keys when focused, visible focus rings, and reduced motion. YouTube players load only after a visitor presses Play. Starting another video removes the previous player; direct YouTube links remain available.
