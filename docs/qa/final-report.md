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
| Outbound HTTP from CI | 29 successful; 1 redirect; 3 rate-limit challenges |

## Browser measurements

Local sockets/Chromium were blocked, so measurements ran on GitHub Actions against the unchanged baseline and the completed site. Both runs captured all eight core pages at 360, 390, 768, 1024 and 1440px in light and dark: **80 screenshots and axe/geometry checks per version**, plus **16 mobile Lighthouse runs per version**.

- Baseline: commit `b556eb5`, [run 38579895204](https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/38579895204), baseline artifact and `measured-baseline.json`.
- Final: commit `7f74a21`, [run 38581756208](https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/38581756208), [all screenshots and HTML/JSON Lighthouse reports](https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/38581756208/artifacts/11904366509), `measured-after.json`.
- **Final browser QA: 80/80 pass**, zero axe violations (including serious/critical), zero page errors, no page overflow, clipped text, overlapping cards or targets below 44×44px. Viewport CLS is below 0.05.
- Browser checks passed: Escape/outside-tap menu close, scroll lock, Ctrl+K palette, year selection, search arrows and empty state, saved theme/bookmarks/studied state after reload, and all four no-JS preset chips.
- Homepage first-fold previews were also visually inspected at 360px and 1440px in both themes. Full-page screenshots are in the artifact. The other viewports/pages have automated geometry and accessibility checks; exhaustive human review of all 80 images was not completed.
- The initial audit found small brand, breadcrumb, email and subject-title targets, plus an initial search layout shift. These were logged in [visual-bugs.md](visual-bugs.md), fixed, and rechecked.
- Early CI setup errors (including dependency sample HTML in the audit and a test initializer overwriting the saved theme) were corrected; the final application/browser checks pass.

Scores are **P / A / BP / SEO**. Each result is a measured mobile Lighthouse run; light and dark are shown separately.

| Page | Before light | After light | Before dark | After dark |
|---|---|---|---|---|
| / | 90 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 90 / 100 / 100 / 100 | 100 / 100 / 100 / 100 |
| /bvsc/ | 91 / 100 / 100 / 100 | 99 / 100 / 100 / 100 | 92 / 100 / 100 / 100 | 100 / 100 / 100 / 100 |
| /objective/ | 91 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 88 / 100 / 100 / 100 | 100 / 100 / 100 / 100 |
| /study-tools/ | 93 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 93 / 100 / 100 / 100 | 100 / 100 / 100 / 100 |
| /clinical/ | 91 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 92 / 100 / 100 / 100 | 100 / 100 / 100 / 100 |
| /search/ | 81 / 100 / 96 / 66 | 100 / 100 / 100 / 66 | 81 / 100 / 96 / 66 | 100 / 100 / 100 / 66 |
| /about/ | 93 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 93 / 100 / 100 / 100 | 100 / 100 / 100 / 100 |
| /request-resource/ | 84 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 84 / 100 / 100 / 100 | 100 / 100 / 100 / 100 |

| Page | LCP before → after (worst theme) | CLS before → after (worst theme) |
|---|---|---|
| / | 2.89s → 1.50s | 0.0143 → 0.0000 |
| /bvsc/ | 2.74s → 1.80s | 0.0272 → 0.0000 |
| /objective/ | 2.58s → 1.65s | 0.1339 → 0.0000 |
| /study-tools/ | 2.59s → 1.65s | 0.0328 → 0.0000 |
| /clinical/ | 2.74s → 1.65s | 0.0117 → 0.0000 |
| /search/ | 2.61s → 1.51s | 0.2428 → 0.0075 |
| /about/ | 2.59s → 1.65s | 0.0322 → 0.0000 |
| /request-resource/ | 2.58s → 1.65s | 0.1915 → 0.0000 |

Search scores 66 for SEO because its only failed SEO audit is `is-crawlable`: it is intentionally `noindex,follow`, as requested. The runner explicitly records this exception; all indexable pages meet the ≥95 target in all four categories. All final measured LCP values are <2.0s and CLS values <0.05. These are synthetic local-server mobile measurements, not production field data.

### Live link audit

CI checked all 33 outbound page URLs: **29 successful, one redirect, three HTTP 429 responses, zero unverified network errors**. There were no measured 404/5xx responses. The three Vet Study links redirect to a Google/Blogger rate-limit challenge; this does not establish that their content is missing, but they cannot be reported as healthy. The existing `https://thatvetguy.net` link redirects to `https://www.thatvetguy.net/`. URLs were preserved as instructed. See `remote-links.json` and the final measured report. The workflow is red because its strict outbound-link step flags those four responses; its build, static checks and browser QA pass.

## Added files and editing points

- Data: `catalogue.json`, `page-meta.json`, `design-tokens.json`; expanded `subjects.json` and category membership.
- Runtime: `assets/theme.js`, `assets/logic.js`, rewritten `assets/site.js`/`site.css`, licensed subset font.
- Content: 19 `/bvsc/<subject>/index.html` guides; 27 `index.md` mirrors; `llms-full.txt`, `search-index.json`; eight `assets/social/*.webp` previews.
- Build/audit: `scripts/resources.py`, `geo.py`, `social-cards.py`, `check-links.py`, `qa-browser.mjs`, expanded checks; `.github/workflows/qa.yml`, development-only audit dependencies.
- Evidence: `docs/qa/baseline.md`, measured before/after matrices, link reports, implementation notes, browser reports/artifacts.
- Complete added-file inventory: [added-files.md](added-files.md).

## Limits and remaining acceptance gates

- **Strict 0 broken/redirecting links:** not claimed. Three external sources rate-limit the CI runner (429), and the existing main domain redirects. Changing their URLs would violate the preservation instruction; server-side behaviour belongs to those providers.
- **Search SEO ≥95:** incompatible with its explicitly requested noindex policy; measured score 66. Every other category/page meets the target.
- **Google Rich Results / hosted Schema.org validator:** not run. No interactive validator session was available in the local environment. JSON-LD syntax, visible FAQ agreement, entity fields and required resource properties pass local checks; this is not represented as a hosted validator result.
- **Manual review:** inspected homepage previews in both themes at phone/desktop widths. All 80 requested full screenshots were produced and machine-audited; every screenshot was not individually reviewed by a human.
- **Production performance:** CI uses a local static server with Lighthouse mobile simulation. Hosting/CDN latency, cache headers and real devices can differ.
- **Font encoding:** WOFF instead of WOFF2 because Brotli tooling was unavailable; the licensed Latin subset is 29.7 KB.

## Labeled commits

- [P0: correctness](https://github.com/HappyRancho/Notes.thatvetguy.net/commit/23d3a7c4b876177a876cc62763bddf0b9c0a4765)
- [P1: resource metadata and listings](https://github.com/HappyRancho/Notes.thatvetguy.net/commit/98963e2cbbfb19df6a12a1e16423a7d052dec190)
- [P2: themes, search and local study state](https://github.com/HappyRancho/Notes.thatvetguy.net/commit/31c11f23191c6b073c756f2014add5b6957d40e8)
- [P3: subject guides and machine retrieval](https://github.com/HappyRancho/Notes.thatvetguy.net/commit/1a5fad802c125d1e99828bf08d66c899b64a73d5)
- Labeled QA follow-ups fix the measured layout/target issues and preserve the evidence. Final tested UI: [7f74a21](https://github.com/HappyRancho/Notes.thatvetguy.net/commit/7f74a21e1a621a2ee9e771a873ca61303bbf2c29).
