# P0–P3 implementation and acceptance status

Updated 2026-10-14. Existing repository and external resource URLs retained. P0, P1 and P2 are committed separately; P3 adds static subject/discovery content.

## Passed local checks

- 27 pages: the original eight routes plus 19 subject guides. One H1, sequential heading outlines, unique IDs, valid local links and anchors.
- 19 original subject summaries, 40–80 words, with revision topics, source credits, related subjects and FAQs.
- Canonical resource URLs deduplicated; Cornell and Zotero appear in one category each. Source-review dates are not HTTP availability claims.
- 34 light/dark text/background contrast checks pass (minimum 4.86:1). This is not a rendered axe audit.
- Real production search normalization, multiword/preset/empty query and blocked/corrupt/quota-limited storage checks pass.
- Runtime JavaScript: 6,125 bytes gzipped. Self-hosted Latin-subset serif: 29,708 bytes; system UI fallback.
- All 27 routes have Markdown mirrors, metadata, semantic JSON-LD and 1200×630 section previews. Sitemap dates, robots policy and static no-JS preset results pass local checks.

## Measurement status

Before screenshots, axe and Lighthouse were blocked by sandbox socket restrictions. The original baseline is recorded in baseline.md and baseline.json; no invented measurements are reported.

Local after measurements remain blocked, but GitHub Actions completed the first full after matrix: 80 screenshots/axe/geometry runs and 16 mobile Lighthouse runs. Zero axe violations, no page overflow and no card overlaps were measured. Small tap targets and search CLS were detected, logged and fixed; a final run is checking the fixes. Its first attempt exposed an audit-scope error: Playwright package sample HTML was included in site checks. This is fixed by excluding node_modules.

The sandbox cannot reach external URLs. A remote CI check tested all 33: 29 successful responses, one main-site canonical redirect and three Vet Study links challenged by Google/Blogger with HTTP 429. The CI checker reports redirects, HTTP failures and network failures separately.

## Final acceptance status

Remote final run 38581756208 checks commit 7f74a21. All 80 screenshots/axe/geometry runs and all browser interaction checks pass. Lighthouse mobile performance is 99–100; accessibility/best practices are 100; SEO is 100 on indexable pages and 66 on intentionally noindex Search. All measured LCP values are below 2 seconds; CLS below 0.01.

The strict link step still flags one original canonical-domain redirect and three Google/Blogger HTTP 429 challenges. No external URLs were changed. Hosted Rich Results/Schema.org validation and individual human review of every full-page screenshot were not completed. See final-report.md for full scores, artifacts, limits and file inventory.
