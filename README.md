# Notes.ThatVetGuy

Free academic resources, thoughtfully made for future vets. A static, accessible veterinary study directory for BVSc & AH students, with credited external reading and original subject outlines.

## Content and build

- `data/catalogue.json`: canonical resource metadata (one record per external URL).
- `data/resources.json`: category membership, year groups, homepage copy and shared book collections.
- `data/subjects.json`: source IDs, original summaries, revision topics and related subjects.
- `data/page-meta.json`: answer-first summaries and real, visible FAQs.
- `data/content-contract.json`: preservation checks for requested subjects, books, Telegram links and homepage structure.
- `data/design-tokens.json` and `assets/site.css`: brand colours and semantic presentation tokens.
- `scripts/build.py` and `scripts/geo.py`: static HTML, JSON-LD, Markdown and discovery files.

```sh
python3 scripts/build.py
python3 scripts/check.py
node scripts/check-interactions.cjs
python3 -m http.server 8000
```

Deploy the repository root to `notes.thatvetguy.net`. Generated HTML is committed; production needs no Node process or build service. Existing URLs and anchors remain available. New subject guides live at `/bvsc/<subject>/`.

## Design and behaviour

The warm cream, forest, coral and soft-lime palette relates to the main ThatVetGuy website. The display face is a self-hosted Latin subset of Noto Serif (licence included), with system UI text. The font uses swap and one preload; no external font request is needed. WOFF is used because the execution environment lacks WOFF2/Brotli tooling.

System light/dark preference is the default. A saved manual toggle overrides it. Native dialog navigation and command search support Escape, outside-tap closing and scroll locking. Search supports `/`, Ctrl/Cmd+K, arrows and Enter, with clear type/source labels, result count, loading and empty states. Four preset results work without JavaScript. Category listings, all years and subject reading links are static HTML.

Bookmarks, recently opened resources and studied subjects stay on the device, using localStorage; no accounts or tracking. Progress is shown by professional year. Blocked storage falls back to in-memory choices for the visit. Motion is brief and respects reduced-motion preferences.

## SEO and machine retrieval

Every page has a unique title, description, canonical and section social image. `robots.txt` explicitly permits the requested crawlers. Search is intentionally `noindex,follow`; other pages appear in the dated sitemap. JSON-LD describes the visible site, author, collections, resources, FAQs and breadcrumbs without claiming authorship of external notes.

`llms.txt`, `llms-full.txt`, `search-index.json` and each route's `index.md` derive from the same content as the HTML. These improve retrieval clarity; they do not guarantee indexing or AI citations. Original summaries are attributed to Dr. Chirag Patidar, BVSc & AH, MVSc; external resources retain their own source credit.

## QA

```sh
npm install
npx playwright install --with-deps chromium
npm run build
npm run check
npm run qa -- after
python3 scripts/check-links.py
```

Development audit dependencies are not shipped to visitors. The browser runner captures all eight core routes at 360, 390, 768, 1024 and 1440px in both themes, checks geometry/CLS and axe, runs mobile Lighthouse in both themes, and checks navigation, search, local study state and no-JS presets. GitHub Actions uploads the screenshots and reports. A separate baseline job checks the untouched pre-task commit using the current audit runner.

The static checks verify content preservation, heading outlines, local links/anchors, canonical URL uniqueness, JSON-LD syntax/fields, mirror files, image dimensions, sitemap dates, crawler access, representative contrast pairs and JavaScript gzip budget. They do not substitute for rendered accessibility or visual inspection.

HTTP auditing distinguishes healthy responses, redirects, HTTP errors and unverified network failures. A source-review date is not a promise that every linked PDF works. See [QA implementation status](docs/qa/implementation.md), [baseline](docs/qa/baseline.md), [final report](docs/qa/final-report.md) and [source decisions](docs/source-audit.md).
