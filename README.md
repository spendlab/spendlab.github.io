# SPEND website

A static multilingual app introduction and the existing English privacy page for `app.spendlab.net`.

- `/`: a neutral entry with a complete English fallback document. It selects the first supported browser language, or a remembered manual language choice, and redirects to a dedicated language URL. It retains query parameters and section fragments.
- `/en/`, `/ko/`, `/ja/`, `/zh-hans/`, `/zh-hant/`, `/de/`, `/fr/`, `/es/`, `/it/`, `/nl/`, `/pt-br/`, `/pt-pt/`, `/id/`, `/vi/`, `/th/`: directly readable localized introductions, seven current feature sections, three concrete usage guides and three questions. Direct language URLs remain fixed, even when the browser or remembered preference differs.
- Each localized page uses its own nine approved native screenshots with localized image alternatives. The English gallery keeps its existing filenames and bytes. Official App Store and Google Play badge originals are retained. Live sharing/sync, advanced statistics and photos/maps remain separate future plans. No actual money transfer or current live shared editing is promised.
- `/en-gb/`: compatibility entry for the previous UK English page. It forwards to `/en/`, preserving query parameters and section fragments; the visible English link remains usable without JavaScript.
- `/privacy/`: the existing policy, with preserved text and the shared home header, footer and page width.
- `/spend/2019/01/30/privacy-policy.html`: compatibility redirect to `/privacy/`.

Published files are plain HTML/CSS and small JavaScript files; dark by default with an icon-only light switch. No runtime framework, analytics, geolocation lookup or third-party page assets are added. Geist and its OFL license are hosted locally. Current multilingual artwork and hero-text provenance is in `content/gallery.json`, pinned to the approved 2026-10-17 store manifest. Earlier English-only artwork history remains in `docs/work_history/landing-image-sources-2026.09.23.json` and the prior 2026-09-07 manifest.

The locale choice uses `navigator.languages`. Brazilian and European Portuguese and simplified and traditional Chinese have distinct routes. All English browser variants share `/en/`; a remembered old UK English choice is also read as English. Unsupported language lists fall back to English. The website has 15 language pages while the store catalogue retains its 16 locales. A manual language link saves only the locale preference in local storage; if storage is unavailable the link still works. No browser-language redirect, translated content, locale picker or new stylesheet/script is added to `/privacy/`. Its original HTML, shared CSS and theme script are preserved.

Editorial sources are `content/locales/*.json`. Seven feature paragraphs reuse the reviewed app description meaning. The complete source text is rendered into each HTML file so reading does not require JavaScript. `site-language.js` owns the language registry. `content/site-assets.json` preserves the original English image sources, theme button, roadmap icons and publisher trademark text. `content/gallery.json` selects the nine exact native PNGs for each language and records their source IDs, order, SHA-256 hashes, sizes and destinations, plus the verified store HTML source of each hero. The generator reads these local files without depending on the app checkout or Git history. Shared original CSS/theme URLs stay fixed; the new page CSS and language script use their content hashes as cache versions. The root canonical points to `/en/`, alternate-language links cover all 15 language pages plus the neutral `x-default`, and `sitemap.xml` lists the 15 dedicated URLs. `robots.txt` only advertises this sitemap and adds no new training preference or bot-specific security rule.

Authoring and verification require Python 3 and Node.js, with no package installation:

```sh
python3 scripts/build_site.py
node --test tests/site-language.test.js
python3 scripts/validate_site.py
git diff --check
```

For an editorial preview of selected languages, run `python3 scripts/build_site.py --locales en-US ko-KR`. Always generate and validate all 15 before publication. GitHub Pages serves the committed generated HTML directly; it does not run the generator. The validator compares every protected pre-existing file with the published baseline `f1f33fbe38c1f4e64c05211f0ef86920568282bf` and checks local links, dedicated URLs, unchanged policy, the English compatibility entry and all 135 approved native image identities. To refresh the approved artwork from the separate app checkout, use `python3 scripts/import_gallery.py /path/to/spend`; this verifies the pinned source manifest and copies PNG bytes without transformations. Normal website generation needs no app checkout.

Preview: `python3 -m http.server 4175 --bind 127.0.0.1`.

GitHub Pages serves `https://app.spendlab.net/`. Cloudflare redirects all `blog.spendlab.net` paths to `https://app.spendlab.net/privacy/` for existing app links. Existing apex services remain unchanged. See `docs/work_history/2026.09.07-app-introduction.md`.

The privacy wording remains the January 30, 2019 policy. The ongoing app release owns policy-content updates; this website task preserves the requested existing text.

The locally hosted store badges retain the official publisher files unchanged. Source URLs, SHA-256 hashes, sizing, clear space and attribution notes are recorded in `assets/store-badges/provenance.json`.
