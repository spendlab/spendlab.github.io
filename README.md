# SPEND website

A small English app introduction and privacy page for `app.spendlab.net`.

- `/`: app introduction, all nine approved App Store images, current App Store listing link. Images are explicitly labeled as an upcoming update preview. Android, live sharing/sync, advanced statistics and photos/maps appear separately as future plans.
- `/privacy/`: the existing policy, unchanged in content and design.
- `/spend/2019/01/30/privacy-policy.html`: compatibility redirect to `/privacy/`.

Plain HTML/CSS and `theme.js`; dark by default with an icon-only light switch. No build dependencies or external page assets. Geist and its OFL license are hosted locally. App Store artwork provenance is in `docs/work_history/landing-image-sources-2026.09.07.json`.

Preview: `python3 -m http.server 4175 --bind 127.0.0.1`.

The active Pages host remains `blog.spendlab.net` until the app-subdomain cutover is verified. Existing apex services remain unchanged. The landing work is prepared on a separate branch; merging it alone does not finish the domain migration. See `docs/work_history/2026.09.07-app-introduction.md`.

The privacy wording remains the January 30, 2019 policy. The ongoing app release owns policy-content updates; this website task preserves the requested existing text.
