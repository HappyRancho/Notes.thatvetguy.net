# Keyword visibility QA — 18 November 2026

27 search titles improved across the 31 mapped landing pages. Existing page URLs and resource inventories are retained; the generated site has 204 pages, 198 indexable sitemap entries and 119 canonical books.

- Full `npm run check`: passed (see static-checks.txt).
- `scripts/keyword-visibility-qa.mjs`: 24 light/dark views at 360 and 1280 px, covering Home, Books, BVSc, Year 4, a long subject heading and the subject awaiting notes. No accessibility violations, clipping, overflow, undersized visible controls or JavaScript errors. Before/after titles and headings are in metadata-audit.json.
- Without JavaScript, home shortcuts reach the entire book library, a named book and its download action, and the BVSc directory leads to the Anatomy notes. All 119 library entries remain available.
- Public pre-change curl probes returned 200 for seven representative pages/discovery endpoints (live-before.json). These are accessibility probes, not authenticated crawler evidence, indexing proof or a measured rank report.

## Local mobile Lighthouse

| Page | Performance | Accessibility | Best practices | SEO | CLS |
|---|---:|---:|---:|---:|---:|
| / | 98 | 100 | 100 | 100 | 0 |
| /books/ | 98 | 100 | 100 | 100 | 0 |
| /bvsc/year-1/veterinary-anatomy/ | 99 | 100 | 100 | 100 | 0 |

These are local review-build measurements. They do not measure live field performance, Google rankings or AI citations. The changes remain in a review branch until merged and published.
