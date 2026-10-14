# QA baseline — before P0

Baseline commit: b556eb5d6a8df153ce9880539ad6dfd2978eb1c6. Date: 2026-10-14.

## Attempted measurements

The requested eight pages × five widths (360, 390, 768, 1024, 1440) × two themes require 80 screenshot runs. No screenshot, visual geometry, CLS, Lighthouse or axe result was obtained: Python's local HTTP server fails opening a socket (`PermissionError: [Errno 1] Operation not permitted`); installed Chromium fails `setsockopt` with EPERM/SIGTRAP. Lighthouse and axe-core are not installed. Outbound CLI HTTP also fails connecting to the inherited proxy. No permissions prompt or endless retry was used.

| Pages | Light screenshots | Dark screenshots | Mobile Lighthouse (4 categories) | axe | LCP / CLS / overlap / overflow |
|---|---|---|---|---|---|
| /, /bvsc/, /objective/, /study-tools/, /clinical/, /search/, /about/, /request-resource/ | Blocked at all 5 widths | Blocked; dark theme absent in baseline | Not measured | Not run | Not measured |

## Confirmed source/markup defects (not screenshot findings)

- P0-01: Mobile drawer H2 precedes the page H1; navigation groups use H3.
- P0-02: Header links use home anchors on subpages; no aria-current state; search icon links to an anchor.
- P0-03: Zotero and Cornell eClinPath occur in two collections each; “Latest” has no date.
- P0-04: Objective Books is an unavailable bullet list; LFP missing-book copy has no styled secondary action.
- P0-05: BVSc UI mentions internal grouping choices and competitor names.
- P0-06: Drug Index contains only two references; clinical caution is plain text.
- P0-07: Objective aside is separate from its header and resource group.
- P0-08: Search results require JavaScript; preset links have no static destination section; no global keyboard shortcut.
- P0-09: External link treatment is inconsistent; no automated HTTP link report.
- P0-10: Contact actions rely on email apps; no dedicated in-page fallback choice per footer action. The checked source contains direct mailto links, not Cloudflare-obfuscated links; hosting may add obfuscation.
- P1-01: Home order places Backbenchers before Study Tools/Clinical.
- P1-02: Repeated per-subject book-directory links; metadata scattered across data and generator.
- P1-03: No last-checked UI or resource-specific report action.
- P2-01: No dark theme/manual toggle; no persistence features; no bottom navigation.
- P2-02: CSS uses hard-coded colours, spacing and sizes; Google fonts are externally loaded.
- P3-01: No subject routes, Markdown mirrors, full LLM file or full-text search index; sitemap lacks lastmod.

No claims of measured clipping, overlap, viewport overflow, sub-44px rendered geometry or CLS are made without a browser. Final browser runner will log these when run in a capable environment.
