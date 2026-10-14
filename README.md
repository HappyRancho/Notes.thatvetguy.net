# Notes.ThatVetGuy

Free academic resources, thoughtfully made for future vets. The existing static site now indexes only the supplied Google Drive library, with on-site study guides and two clearly separated Telegram channels.

## Build

```sh
python3 scripts/build.py
npm run check
python3 -m http.server 8000
```

`data/drive_manifest.json` is the inspected source inventory. `scripts/library.py` generates `data/resources.json`, which drives the year overview, year/subject pages, counts and search. `data/subject-map.json` holds folder aliases and reviewed overrides. Unmatched files remain in a visible Unsorted bucket; no title, source credit, size or date is invented.

`DRIVE_API_KEY` is optional and build-only. When configured, `scripts/drive_manifest.py` uses Drive API v3 with 1,000-item pages and recursive folder enumeration. Without a key, normal builds read the saved manifest. The owner's public links can be refreshed by the Drive library workflow using `crawl-public-drive.py` and the public UI continuation audit; no frontend key is extracted and no gdown dependency is used.

Deploy the generated root files and route directories. Every page remains static HTML with a Markdown mirror. `build-info.json` and the `site-build` meta marker identify the generated content through CDN HTML injection. The app has no runtime framework, accounts, analytics or animation library.

## Content and presentation

- `data/site-content.json`: homepage copy and existing curriculum structure.
- `data/subjects.json`: original subject summaries and revision outlines.
- `data/microcopy.json`: requested humour and alternatives; one selected block per section.
- `data/design-tokens.json`, `assets/site.css`: light/dark design tokens, compact rows and colour panels.
- `scripts/library_pages.py`: Drive file cards, source collections and text-only on-site tools.
- `scripts/build.py`, `scripts/geo.py`: shared layout, metadata, schemas and discovery files.

The original routes remain available. New routes are `/bvsc/year-1/` through `/bvsc/year-4/`, then the existing subject slug. File cards appear on exactly one canonical subject page, with group counts, known source credit, size/date, Open and a Download action only for known binary files below 25 MB. Legacy subject guides link to those collections without duplicating file cards.

## Link policy

Generated navigation permits only the two specified Telegram URLs, exact Drive URLs from the manifest (and generated downloads for those IDs), and ThatVetGuy main/blog links in the footer. Other resource providers are removed from the library and machine indexes. Software names in the on-site guides are plain text. Developer documentation and historical QA artifacts are not application navigation.

## Accessibility, search and retrieval

The site retains native dialog navigation, visible focus, reduced-motion support, saved light/dark override, bookmarks, recently opened resources and studied-subject progress. Phone navigation lives in the bottom bar; the header contains only the wordmark and theme toggle. Search supports keyboard shortcuts, arrows, Enter, loading/empty states and a count; its four preset sections work without JavaScript.

`llms.txt`, `llms-full.txt`, `search-index.json`, the dated sitemap and per-route Markdown derive from the same content. JSON-LD describes the site, author, breadcrumbs, visible FAQs, collections and individual files. File ownership and medical review are not implied. Search remains intentionally noindex.

## QA and publication

```sh
npm install
npx playwright install --with-deps chromium
npm run check
npm run qa -- task2-after
python3 scripts/check-links.py --limit 12
```

Static checks enforce every manifest ID appearing once on a canonical subject page and in search, strict external domains, heading outlines, valid local anchors, retrieval metadata, dark/light contrast and the runtime JS budget. API tests cover pagination and nested folders without real credentials.

The Drive publication workflow inspects the actual public folders, verifies continuation pages, builds and checks the site, then commits the generated inventory/pages with the Actions bot. It runs responsive screenshots and axe at 360/390/412/768/1024/1440 in both themes and mobile Lighthouse on the eight core routes. Production verification reports cache headers, byte differences and build markers. Cloudflare purge is performed only if its token and zone are configured as repository secrets.

Lighthouse's SEO category penalises the intentionally noindex search page; this exception is reported explicitly. Link checks distinguish redirects, HTTP errors and network failures, and the default command can audit every URL; CI samples links rather than issuing thousands of download requests.
