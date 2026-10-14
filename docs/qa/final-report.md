# P0–P3 QA and redesign report

Date: 2026-10-14. Repository: HappyRancho/Notes.thatvetguy.net. Existing static site retained; original eight route URLs, category anchors and all 31 original external resource URL strings preserved (compared directly with the pre-task resource and subject data). Nineteen subject routes are additive.

## Changes delivered

**P0 — correctness.** Navigation drawer titles/groups no longer disrupt the heading outline. Header navigation uses real pages and active states. Search links to its real route. Removed duplicate Zotero/eClinPath category membership; renamed undated tools and the two-link drug section accurately. Objective Books now uses styled Coming soon entries; missing LFP books have a secondary request action. Replaced internal grouping commentary with a university-syllabus note, styled the clinical disclaimer and removed orphan Objective copy. Added static preset search results, consistent external link attributes/icons, HTTP audit and visible email/contact/contribution/report fallbacks.

**P1 — content and composition.** Homepage order now matches the requested study flow. Canonical catalogue metadata generates resource cards, source/type/date badges, descriptive actions and per-resource report links. Each BVSc year has one shared book collection, plus Notes/Books choices by subject. Preserved all requested subject/book names and both distinct Telegram destinations. Added page last-checked dates. Source dates describe source review, not successful file downloads.

**P2 — UI and local study features.** Added semantic design tokens, warm light/dark themes, saved override, matching theme-colour metadata, self-hosted subset serif, year accents, refined responsive compositions, compact search, command palette, bottom navigation, motion/focus/reduced-motion rules, bookmarks, recently opened resources, studied subjects and progress. No accounts, analytics, animation library or production framework. Storage failure falls back to the current visit.

**P3 — retrieval and original content.** Added 19 subject guides with 40–80 word original summaries, revision topics, credited reading and related subjects. Generated 27 Markdown mirrors, root search JSON, full/concise LLM files, explicit crawler allow policy, dated sitemap and eight section WebP previews (1200×630). Unique canonical metadata and visible FAQs match JSON-LD for the website/search action, ThatVetGuy, author, collections, breadcrumbs, FAQs and learning resources. Search remains noindex.

## Measured local checks

| Check | Result |
|---|---|
| Static pages / exactly one H1 / sequential outline | 27 pages pass |
| Local routes, anchors, IDs and discovery-file syntax | Pass |
| Original subject summaries / outlines | 19 pass; 47–57 words each |
| Canonical external resource duplication | No duplicate catalogue URLs; Zotero/eClinPath each in one category |
| Light/dark representative text contrast | 34 pairs pass; minimum 4.86:1 |
| Production search/storage unit checks | Pass, including empty/preset/multiword/corrupt/blocked/quota-limited cases |
| Runtime JavaScript | 6,125 bytes gzip |
| Display font | 29,708-byte self-hosted Latin-subset WOFF, swap, one preload |
| Static no-JS preset destinations | Four present, linked to real source cards |
| Social previews | Eight WebP files, all 1200×630 |
| Outbound HTTP from sandbox | 33 unverified; proxy unavailable |

## Browser measurements

The sandbox blocked local HTTP sockets/Chromium and could not install Lighthouse/axe. GitHub Actions provides the browser-capable runner. The source defects were logged before fixes in [baseline.md](baseline.md). Local measurements were blocked, then GitHub Actions completed a genuine 80-viewport/16-Lighthouse run against the untouched baseline commit; see measured-baseline.json. A GitHub Actions runner can execute these measurements and is running the after matrix. A separate job now checks the untouched baseline commit with the same audit tooling. The initial P2 CI run failed because the checker included dependency sample HTML; that audit-scope bug is fixed.

| Page | Before P/A/BP/SEO | After P/A/BP/SEO |
|---|---|---|
| / | Pending remote baseline | Pending CI |
| /bvsc/ | Pending remote baseline | Pending CI |
| /objective/ | Pending remote baseline | Pending CI |
| /study-tools/ | Pending remote baseline | Pending CI |
| /clinical/ | Pending remote baseline | Pending CI |
| /search/ | Pending remote baseline | Pending CI; intentional noindex may lower SEO |
| /about/ | Pending remote baseline | Pending CI |
| /request-resource/ | Pending remote baseline | Pending CI |

P=performance, A=accessibility, BP=best practices. No scores are inferred from bundle size or static contrast tests. After CI, screenshots/axe/geometry/Lighthouse reports are available as Actions artifacts. This document will be updated with obtainable measurements.

## Added files and editing points

- Data: `catalogue.json`, `page-meta.json`, `design-tokens.json`; expanded `subjects.json` and category membership.
- Runtime: `assets/theme.js`, `assets/logic.js`, rewritten `assets/site.js`/`site.css`, licensed subset font.
- Content: 19 `/bvsc/<subject>/index.html` guides; 27 `index.md` mirrors; `llms-full.txt`, `search-index.json`; eight `assets/social/*.webp` previews.
- Build/audit: `scripts/resources.py`, `geo.py`, `social-cards.py`, `check-links.py`, `qa-browser.mjs`, expanded checks; `.github/workflows/qa.yml`, development-only audit dependencies.
- Evidence: `docs/qa/baseline.md`, baseline matrix, link report, implementation notes, browser reports/artifacts.

## Limits and remaining acceptance gates

Rendered overflow, overlaps, tap sizes, LCP/CLS, axe, Lighthouse ≥95 and visual smoothness require completed browser results. Static checks cannot establish them. Live HTTP availability remains unverified until CI checks finish; an external access block/redirect is reported separately, not silently repaired by changing a URL. Google Rich Results Test and the hosted Schema.org validator have not been run; JSON-LD syntax and expected fields pass locally. Search noindex intentionally conflicts with a perfect Lighthouse SEO score. The font is WOFF rather than WOFF2 because Brotli tooling was unavailable; the subset remains small.
