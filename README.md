# SPEND website

A static multilingual app introduction and the existing English privacy page for `app.spendlab.net`.

- `/`: a neutral entry with a complete English fallback document. It selects the first supported browser language, or a remembered manual language choice, and redirects to a dedicated language URL. It retains query parameters and section fragments.
- `/en/`, `/en-gb/`, `/ko/`, `/ja/`, `/zh-hans/`, `/zh-hant/`, `/de/`, `/fr/`, `/es/`, `/it/`, `/nl/`, `/pt-br/`, `/pt-pt/`, `/id/`, `/vi/`, `/th/`: directly readable localized introductions, seven current feature sections, three concrete usage guides and three questions. Direct language URLs remain fixed, even when the browser or remembered preference differs.
- All localized pages retain the nine approved English screenshots and official App Store and Google Play badge originals. Their adjacent text and image alternatives are localized, and a note identifies English screenshots. Live sharing/sync, advanced statistics and photos/maps remain separate future plans. No actual money transfer or current live shared editing is promised.
- `/privacy/`: the existing policy, with preserved text and the shared home header, footer and page width.
- `/spend/2019/01/30/privacy-policy.html`: compatibility redirect to `/privacy/`.

Published files are plain HTML/CSS and small JavaScript files; dark by default with an icon-only light switch. No runtime framework, analytics, geolocation lookup or third-party page assets are added. Geist and its OFL license are hosted locally. Current App Store artwork provenance is in `docs/work_history/landing-image-sources-2026.09.23.json`; the 2026-09-07 manifest remains as the prior approved snapshot.

The locale choice uses `navigator.languages`. Brazilian and European Portuguese, simplified and traditional Chinese, and US/UK English have distinct routes. Unsupported language lists fall back to US English. A manual language link saves only the locale preference in local storage; if storage is unavailable the link still works. No browser-language redirect, translated content, locale picker or new stylesheet/script is added to `/privacy/`. Its original HTML, shared CSS and theme script are preserved.

Editorial sources are `content/locales/*.json`. Seven feature paragraphs reuse the reviewed app description meaning. The complete source text is rendered into each HTML file so reading does not require JavaScript. `site-language.js` owns the language registry. `content/site-assets.json` preserves the approved image sources, theme button, roadmap icons and publisher trademark text. The root canonical points to `/en/`, alternate-language links cover all 16 pages plus the neutral `x-default`, and `sitemap.xml` lists the 16 dedicated URLs. `robots.txt` only advertises this sitemap and adds no new training preference or bot-specific security rule.

Authoring and verification require Python 3 and Node.js, with no package installation:

```sh
python3 scripts/build_site.py
node --test tests/site-language.test.js
python3 scripts/validate_site.py
git diff --check
```

For an editorial preview of selected languages, run `python3 scripts/build_site.py --locales en-US ko-KR`. Always generate and validate all 16 before publication. GitHub Pages serves the committed generated HTML directly; it does not run the generator. The validator compares every protected pre-existing file with the published baseline `f1f33fbe38c1f4e64c05211f0ef86920568282bf` and checks local links, dedicated URLs, unchanged policy and approved asset identity.

Preview: `python3 -m http.server 4175 --bind 127.0.0.1`.

GitHub Pages serves `https://app.spendlab.net/`. Cloudflare redirects all `blog.spendlab.net` paths to `https://app.spendlab.net/privacy/` for existing app links. Existing apex services remain unchanged. See `docs/work_history/2026.09.07-app-introduction.md`.

The privacy wording remains the January 30, 2019 policy. The ongoing app release owns policy-content updates; this website task preserves the requested existing text.

The locally hosted store badges retain the official publisher files unchanged. Source URLs, SHA-256 hashes, sizing, clear space and attribution notes are recorded in `assets/store-badges/provenance.json`.
