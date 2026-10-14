# P0–P3 implementation and acceptance status

Updated 2026-10-14. Existing repository and external resource URLs retained. P0, P1 and P2 are committed separately; P3 adds static subject/discovery content.

## Passed local checks

- 27 pages: the original eight routes plus 19 subject guides. One H1, sequential heading outlines, unique IDs, valid local links and anchors.
- 19 original subject summaries, 40–80 words, with revision topics, source credits, related subjects and FAQs.
- Canonical resource URLs deduplicated; Cornell and Zotero appear in one category each. Source-review dates are not HTTP availability claims.
- 34 light/dark text/background contrast checks pass (minimum 4.86:1). This is not a rendered axe audit.
- Real production search normalization, multiword/preset/empty query and blocked/corrupt/quota-limited storage checks pass.
- Runtime JavaScript: 6,048 bytes gzipped. Self-hosted Latin-subset serif: 29,708 bytes; system UI fallback.
- All 27 routes have Markdown mirrors, metadata, semantic JSON-LD and 1200×630 section previews. Sitemap dates, robots policy and static no-JS preset results pass local checks.

## Measurement status

Before screenshots, axe and Lighthouse were blocked by sandbox socket restrictions. The original baseline is recorded in baseline.md and baseline.json; no invented measurements are reported.

The local after browser run is also blocked (missing installable browser-audit packages; browser/socket operations denied). A GitHub Actions browser run is being used for after measurements. Its first attempt exposed an audit-scope error: Playwright package sample HTML was included in site checks. This is fixed by excluding node_modules.

All 33 outbound URLs are currently unverified from the sandbox because its HTTP proxy is unreachable. They are neither confirmed broken nor confirmed healthy. The CI checker reports redirects, HTTP failures and network failures separately.

## Open acceptance gates

Rendered geometry, manual visual inspection, axe, Lighthouse, LCP/CLS, live external HTTP checks and Google Rich Results/Schema.org remote validation require the browser/CI results. Search is intentionally noindex, which can reduce its Lighthouse SEO score even when functioning correctly. JSON syntax and required schema fields are checked locally; this is not a Rich Results Test.
