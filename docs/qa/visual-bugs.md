# Measured visual bugs and fixes

Audit: GitHub Actions run 38579467856, commit 1a5fad802c125d1e99828bf08d66c899b64a73d5. Eight pages × five widths × two themes (80 screenshots/axe/geometry checks). This is the first measurable after pass, not a fabricated local baseline. The untouched baseline was measured separately in run 38579895204.

| Bug | Measured evidence | Fix |
|---|---|---|
| Brand target too short | 32px height across routes | 44px minimum height |
| About/Home text targets too narrow | About 35.48px; breadcrumb Home 35.44px | 44px minimum width on interactive anchors |
| BVSc subject-title links too short | Single-line title links 21px high | Inline-flex title links with 44px minimum height |
| Email targets too short | Contact email 16px high | Inline-flex, centred 44px target |
| About ecosystem text/icon wrapping | Main/Blog links ~40.8px tall | Keep label/icon in inline-flex 44px actions |
| Search status flagged as clipped | Visually hidden count was 1px wide | Visible result-count region on Search |
| Search shifts on initial load | Lighthouse CLS 0.1053; viewport tests up to 0.0916 | Preserve static browsing until a query; avoid initial all-results replacement |
| Occasional home layout shift | Dark 768px viewport CLS 0.0818 | Reserve enhanced tab/JS layout in head before first paint |

No page-level overflow, overlapping resource cards, axe violations or uncaught page errors were measured in the initial full matrix. Final rerun checks these fixes. The screenshot artifact contains the visual record.
