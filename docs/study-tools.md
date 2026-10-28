# Veterinary Tools guides

The homepage Tools drawer and `/study-tools/` link to three static guides:

- `/study-tools/vet-apps/`: four free apps with direct Google Play links and six Biosphera species anatomy entries. MSD Professional is intentionally excluded. IVRI Veterinary Clinical Care is the additional free app.
- `/study-tools/online-resources/`: twelve original website summaries, with category filters and search across the real entries.
- `/study-tools/veterinary-careers/`: twelve India-first career routes, practical preparation advice, postgraduate choices and regulator-linked overseas pathways.

`data/study-tools.json` holds the content and exact source URLs. Descriptions and suggested next steps are editorial guidance, not quotations or guaranteed recruitment criteria. The current official advertisement or regulator determines eligibility. No ratings, salary promises or store download totals are invented.

Free apps link directly to Google Play. Paid anatomy entries have no Play download CTA. Set `paidTelegramUrl` to the user-provided collection URL when it is available; until then the page shows an honest pending message, not a dead button. No APKs are hosted or fetched by the importer.

Original Play icons are retained as 128px WebP files under `assets/tools/apps/`. `data/app-icon-sources.json` records each exact listing and image source. `scripts/ci/import-app-icons.py` imports only images from Google Play and the Play image CDN. The scoped page stylesheet is `assets/study-tools.css`; existing Rx fonts, colours, header and navigation are reused.

All guide text is server-rendered and usable without JavaScript. JavaScript progressively enables filters and real-entry search. The head's existing `js` class makes filters visible before first paint to avoid content shifts. Native details disclose longer guidance. Each page has a canonical, unique search metadata, a Markdown mirror, structured data and inclusion in sitemap/LLM discovery. Three on-site guide entries are added to the existing site search.

External links are allowed by exact URL and only on these Tools routes. The rest of the site's existing link policy remains in force.

Verification: `npm run build && npm run check`, then `node scripts/study-tools-qa.mjs` for 40 mobile/tablet/desktop light/dark views and functional checks. Lighthouse uses the four Tools routes. Browser screenshots and reports are uploaded in the Approved homepage QA artifact under `docs/qa/study-tools/`.
