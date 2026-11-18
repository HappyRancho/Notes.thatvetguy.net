# Notes.ThatVetGuy

Free academic resources, thoughtfully made for future vets. A static, accessible BVSc library with the Study Clinic visual identity, on-site study guides and two clearly separated Telegram channels.

## Build

```sh
python3 scripts/build.py
npm run check
python3 -m http.server 8000
```

`data/drive_manifest.json` is the inspected source inventory. `scripts/catalogue.py` generates `data/resources.json`, which drives year and subject pages, counts and search. `data/subject-map.json` holds subject aliases; `data/curation.json` controls reviewed collection membership and corrections. Camera photographs become folder-level sets, exact title/size duplicates are hidden, and alternate formats share rows. Every original ID remains accounted for in `data/duplicates-report.json`. Resources without a confirmed subject stay in collapsed year-level Extras.

`DRIVE_API_KEY` is optional and build-only. When configured, `scripts/drive_manifest.py` uses Drive API v3 with 1,000-item pages and recursive folder enumeration. Without a key, normal builds read the saved manifest. The owner's public links can be refreshed by the Drive library workflow using `crawl-public-drive.py` and the public UI continuation audit; no frontend key is extracted and no gdown dependency is used.

Deploy the generated root files and route directories. Every page remains static HTML with a Markdown mirror. `build-info.json` and the `site-build` meta marker identify the generated content through CDN HTML injection. The app has no runtime framework, accounts, analytics or animation library.

## Content and presentation

- `data/site-content.json`: homepage copy and existing curriculum structure.
- `data/subjects.json`: original subject summaries and revision outlines.
- `data/microcopy.json`: requested humour and alternatives; one selected block per section.
- `data/study-clinic-tokens.json`, `assets/site.css`: the current light/dark palette, spacing, typography and motion tokens.
- `scripts/library_views.py`: subject cards, paged file accordions, curated collections and text-only guides.
- `scripts/site_shell.py`: homepage, navigation, search and footer.
- `scripts/build_site.py`, `scripts/geo.py`: static output, metadata, schemas and discovery files.
- `scripts/prepare-fonts.py`: self-hosted OFL font subsets; used when building fresh assets.

The original routes remain available. New routes are `/bvsc/year-1/` through `/bvsc/year-4/`, then the existing subject slug. File cards appear on exactly one canonical subject page, with group counts, known source credit, size/date, Open and a Download action only for known binary files below 25 MB. Legacy subject guides link to those collections without duplicating file cards.

## Link policy

Resource links come from reviewed inventories: the two specified Telegram channels, exact Drive URLs and generated downloads, and the checked public PDF URLs in `data/vet-ebooks-books.json`. ThatVetGuy main/blog links appear in the footer. Study-tool and roadmap citations remain scoped to their corresponding pages. Provider URLs are explicitly recorded rather than allowing arbitrary links from a whole domain. Developer documentation and historical QA artifacts are not application navigation.

## Accessibility, search and retrieval

The site retains native dialog navigation, visible focus, reduced-motion support, saved light/dark override, bookmarks, recently opened resources and a studied toggle on subject pages. Phone navigation lives in the bottom bar; the header contains only the wordmark and theme toggle. Search supports keyboard shortcuts, arrows, Enter, loading/empty states and a count; its four preset sections work without JavaScript. No local preferences are sent to a server.

`llms.txt`, `llms-full.txt`, `search-index.json`, the dated sitemap and per-route Markdown derive from the same content. JSON-LD describes the site, author, breadcrumbs, visible FAQs, collections and individual files. File ownership and medical review are not implied. Search remains intentionally noindex.

## QA and publication

```sh
npm install
npx playwright install --with-deps chromium
npm run check
npm run qa -- after
python3 scripts/check-links.py --limit 12
```

Static checks reconcile every original manifest ID through files, formats, photo sets or duplicates. Visible resources appear once on a canonical subject/year page and in search. Checks also enforce external domains, heading outlines, local anchors, retrieval metadata, contrast and payload budgets. API tests cover pagination and nested folders without real credentials. The browser audit covers 360/375/390/412/430/768/1024/1280/1440 px in both themes, including a year and subject page. Its local server uses gzip so Lighthouse delivery matches a compressed static host.

The Drive publication workflow can refresh the original public folders. The Study Clinic workflow builds and checks the saved inventory, commits generated output to its review branch, and captures screenshots, axe and Lighthouse results. Production verification checks both hostnames and the exact deployed build. Cloudflare purge is possible only when its token and zone are connected. See `docs/qa/task3/report.md` for measured results and limitations.

Lighthouse's SEO category penalises the intentionally noindex search page; this exception is reported explicitly. Link checks distinguish redirects, HTTP errors and network failures, and the default command can audit every URL; CI samples links rather than issuing thousands of download requests.

## Advertising verification and performance

While ads are disabled, each page uses the `google-adsense-account` meta tag for publisher verification. The AdSense SDK is included only when both approval and rendering are enabled in `data/adsense.json`. The ads.txt seller record and placement approval gates remain in place. `scripts/check-crawlability.py` validates canonical sitemap pages and their static internal-link paths as part of `npm run check`.

Minimal manual banner layout: at most one unit per eligible notes page, after a complete content section. The ad frame reserves 100px in height, caps its width at 728px and has 24px vertical separation. It stays in document flow with an Advertisement label. Activation requires an approved site, real display slot IDs and confirmation that Auto ads are off. Inactive placements emit no visible placeholder.

Configured AdSense display slot: `9530493668` (Notes – Minimal Banner), publisher `ca-pub-3524774459480835`. Both reserved placements use this unit, with at most one placement per eligible page. The supplied dashboard screenshot shows Getting ready and Ads.txt not found, so approval/rendering flags remain disabled until approval is confirmed.

## Books library

The Books item in the bottom navigation opens `/books/`. The library draws all current canonical books from the same catalogue as the subject bookshelves. Seven broad subject categories have count filters, with title/author/subject search and 24-book batches through Show more. The compact covers reuse the subject-page card markup. With JavaScript disabled, the full catalogue and category anchor links remain available. `assets/books-directory.js` is loaded only on the library page and does not fetch another catalogue. Run `node scripts/books-library-qa.mjs` for the responsive, accessibility and browsing checks.

## Verified clinical PDF references

`data/vet-ebooks-books.json` supplies 25 clinical and practical references, selected for concise coverage and smaller public PDF downloads. Entries include a provider URL, checked byte size, PDF signature, author, cover, original overview and study topics. The catalogue merges existing works by canonical ID. Our own book pages remain the search, sitemap and Markdown targets; Download PDF opens the verified public provider endpoint directly. No PDF is downloaded while browsing the library. Availability is controlled by the external provider.
