# SPEND privacy page

One Korean/English page at https://blog.spendlab.net/.

Plain HTML, CSS and a small language switch. No build dependencies, cookies, analytics or external page assets. The app’s Geist font is hosted locally with its OFL license. Without JavaScript, both languages remain readable.

- `index.html`: existing policy and approved contact.
- `style.css`: responsive styling.
- `language.js`: hash-based language selection, browser back/forward support, and a dark/light toggle (dark on every load).
- `/privacy/` and `/spend/2019/01/30/privacy-policy.html`: compatibility redirects.
- `.nojekyll`: direct static publishing; old blog files remain in Git history.
- `CNAME`: existing custom domain, unchanged.

Preview: `python3 -m http.server 4175 --bind 127.0.0.1`.
Publish: push verified changes to `master`; GitHub Pages publishes the repository root without a Jekyll build.

This September 2026 delivery changes presentation only. English retains the January 30, 2019 policy wording; Korean is a translation. Review policy accuracy separately before releasing the new Flutter app. The publication date is not a new effective date.
