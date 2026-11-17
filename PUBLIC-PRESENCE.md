# Keeping Alexa's public websites current

The existing URLs stay in place. No rebrand or new domain is required.

## Sources and ownership
- `data/presence.json` in the personal website is the canonical registry of approved names, host bios, profile URLs, show destinations and roles.
- Keep the established Alexa's Input show description from Spotify for Creators. A shorter search description has its own field; it is not a replacement show bio.
- `scripts/maintain-presence.py` reads only public, already-published feeds and the Red Hat Developer author page. It does not read email, private customer material or unpublished drafts.
- The personal homepage updates only marked latest-episode and recent-writing regions. Historical writing, talks and layouts stay intact.
- Alexa's Input retains its verified video gallery and refreshes the latest published release, related Attention Deficit releases and technical writing.
- Attention Deficit already imports published Substack episodes via its existing validated workflow. Do not introduce a second episode registry or a competing importer there.

## Automatic maintenance
Both static sites run Public website checks daily and after repository changes. It has read-only repository permission: it validates public content, prepares proposed changes in a temporary checkout, and uploads a patch plus a link report. It cannot commit or deploy. Failed feeds preserve the last good content instead of publishing empty sections. Automatic write/deploy was blocked by approval review and has not been activated.

The link-audit step follows every external link exposed in the checked HTML, plus the three live home/link pages. Its report distinguishes reachable, broken (404/410) and unverified (login, rate limit, timeout, server restriction) destinations. A blocked site is never counted as verified. Download the public-website-review artifact or read the Actions job summary. Existing historical-link failures do not bypass content validation or erase the archive.

## Publishing checklist
1. Approve and publish the episode or article on its established publishing platform.
2. Let the daily refresh import its actual title, date and public link. Use Run workflow when an immediate check is needed. Review and apply its proposed-update.patch through the normal authorized repository update.
3. For a new video without a linked feed item, verify its YouTube title and duration before adding it to the video gallery.
4. Confirm the normal hosting deployment succeeded and spot-check the live page. These checks do not deploy.
5. Names, employer, show branding, credentials and roles change only from verified evidence or Alexa's instruction. Update the central registry when those actually change.

## Account-only items
The following need the relevant signed-in account; repository edits cannot change them:
- GitHub profile Company and Twitter/X fields (profile README is separate).
- Spotify for Creators show Website metadata and platform-only bios.
- Linktree admin, Blogger site introduction and Search Console.
Do not claim those are updated merely because website source was changed.

## Linktree and the old blog
Use https://alexagriffith.com/links/ as the owned, maintained hub. Keep Linktree alive for old bios and QR codes, with direct links to the same destinations when account access is available. No mass URL migration.

Keep the old Blogger articles at their original URLs and dates. Add an archive/current-work notice when Blogger access is available. Do not automatically cross-post full articles to another destination: link to the original or use an explicitly approved canonical syndication process. A second manually maintained publication is not required.
