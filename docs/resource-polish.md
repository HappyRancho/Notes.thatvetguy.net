# Subject resources refinement — 28 October 2026

The approved Rx Notes header, homepage composition, fixed navigation and other academic routes are preserved. Shared asset version identifiers change when source code changes.

## Changed

- Subject Books use one shared section with a cover-and-title grid, without individual boxed cards. Removed “Course focus & study tips” from all 19 subject hubs.
- Practical Vaults show 39 original Drive folders across 14 subjects. The 324 observed underlying files remain in the source audit; individual practical files and photo previews are excluded from public lists and search. Old file anchors and saved IDs point to the corresponding folder. Five subjects without a Practical source folder display an honest empty state.
- Assessment guidance uses the owner-provided DUVASU-hosted VCI MSVE 2016 curriculum. Subject-specific practical paper coverage is recorded separately from general attendance, pass and assessment rules. Clinical Practices and Farm Practices retain their distinct internal assessment scheme.
- Re-extracted 19 syllabus checklists: 169 theory/practical units and sections, 1,651 source-text checklist items. Theory and Practical use distinct section accents, unit accordions and device-local progress. Source page links use physical PDF page numbers. The original four year-outline PDFs remain unchanged.
- Search uses the current public catalogue, real pre-rendered subject suggestions, resource-type filters, keyboard navigation, bounded results, an empty state and a request link. Reading recommendations with no accessible copy are excluded. Individual practical files resolve to their original folders rather than cluttering results.
- All 95 book/reference pages use a cover/title/access layout, a concise description, original editorial reading guidance, truthful provider labels and expandable edition/source details. No ratings or personal reading experiences are fabricated.
- Added the two private Anatomy Telegram posts exactly as provided: Primary Veterinary Anatomy by R. K. Ghosh (`https://t.me/c/4312433672/2`) and Essentials of Veterinary Histology & Embryology by R. K. Ghosh (`https://t.me/c/4312433672/3`). The latter’s bibliographic title was cross-checked against Current Books International. Private-collection access is explained.
- Added 14 researched reference images, bringing cover/preview coverage to 64 of 95 pages. Covers may depict a different edition; captions say so. Three unsuitable research candidates were rejected. No screenshots or invented book covers are used.
- Updated HTML, Markdown mirrors, sitemap, search index and LLM retrieval files through the existing renderer. Corrected curriculum-source structured-data URLs and excluded hidden source records from visible-page resource schema.

## Source

https://upvetuniv.edu.in/wp-content/uploads/2020/12/BVSc-AH-Syllabus-and-Course-curriculum-MSVE-2016.pdf

The retained extraction records the source URL, 47 physical PDF pages, 12,050,469 bytes and its SHA-256. Ordinary builds regenerate checklists from that retained extraction without a network dependency.

## Verification

- `npm run build` and `npm run check`: provenance, internal destinations, source hashes, heading outlines, unique metadata, canonical Markdown, sitemap/schema consistency, link allowlist, search logic and contrast tokens.
- Browser suite: 360, 390, 430 and 1280px, light and dark; eight representative routes (64 views). Tests real Notes/TANUVAS drawers, unboxed covers, checklist persistence, folder links and assessment, exact Telegram destinations, current search results, filtering/pagination, keyboard operation, no-JS presets and reduced motion.
- First browser pass identified a 39px-wide search chip and one low-contrast dark-mode practical link. Both were corrected; folder text containment was added as a regression assertion.
- Final browser and Lighthouse results are recorded in the GitHub Actions “Approved homepage QA” artifact under `docs/qa/resource-polish/` and `docs/qa/task3/mockup-after/`.

## Limits

31 resources still have no verified cover/preview after source and bibliographic research. These include informal compilations and reference sheets, as well as books whose retrieved images could not be verified. The UI states “Cover unavailable” rather than presenting a fabricated or mismatched cover. The exact remaining IDs are generated in `docs/qa/book-pages/data-report.json`.

Private Telegram membership and university-specific updates cannot be inferred from public link availability. The linked edition and current university instructions must be checked by the reader. Existing hosting-level crawler/robots behavior is outside this UI change.

## Measured review build

Browser run: 64 views, no overflow, clipped text, undersized targets, folder text overflow, JavaScript errors, broken visible images or serious/critical axe violations. All seven interaction journeys passed.

| Sample page | Performance | Accessibility | Best practices | SEO | LCP | CLS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Anatomy subject | 98 | 100 | 100 | 100 | 2.34s | 0.0066 |
| Anatomy checklist | 99 | 100 | 100 | 100 | 1.97s | 0.0057 |
| Anatomy Practical Vault | 99 | 100 | 100 | 100 | 1.97s | 0.0057 |
| Primary Veterinary Anatomy book | 99 | 100 | 100 | 100 | 1.96s | 0.0057 |
| Search | 99 | 100 | 100 | 66 | 1.81s | 0.0057 |

Search’s SEO score reflects its deliberate `noindex` policy. The Anatomy subject sample exceeded the aspirational 2.0-second LCP target; it met the 95+ performance score and CLS target. These are measured review-server scores, not a claim about production network conditions.

The subsequent metadata-only correction fixes an absolute curriculum URL and removes hidden image-album entities from structured data. It does not change the tested page layout or interactions and runs the complete static check suite again.
