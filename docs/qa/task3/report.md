# Task 3: Study Clinic redesign

Work is based on the existing static site and the original public-folder manifest. No Drive files were deleted or invented.

## Catalogue reconciliation

| Year | Original files | Files retained after dedupe | Browse rows | Extras rows |
| --- | ---: | ---: | ---: | ---: |
| 1 | 698 | 693 | 453 | 0 |
| 2 | 631 | 630 | 325 | 1 |
| 3 | 956 | 951 | 549 | 0 |
| 4 | 669 | 664 | 371 | 8 |

Original manifest: **2,954 files**. Hidden duplicates: **16**. Merged alternate-format rows: **39**. **1,221 camera images** are represented by **20 photo sets**.

A resource count means one browse row: alternate formats share a row and a photo batch counts as one set. Individual named diagrams remain accessible. Every original ID is accounted for by a visible file, an alternate format, a photo set or a recorded duplicate.

The Year 4 “var one mark 2” paper is assigned to Surgery using the identical file in `Surgery/Others`. The reviewed correction is recorded in `data/curation.json`. Two Anatomy full-book volumes are classified as Books even though their parent folder is Lecture Notes.

## Subject counts

| Year | Subject | Browse rows |
| --- | --- | ---: |
| 1 | Veterinary Anatomy | 244 |
| 1 | Veterinary Physiology | 82 |
| 1 | Livestock Production Management | 127 |
| 2 | Veterinary Biochemistry | 44 |
| 2 | Veterinary Microbiology | 74 |
| 2 | Veterinary Pathology | 101 |
| 2 | Animal Genetics and Breeding | 75 |
| 2 | Animal Nutrition | 30 |
| 3 | Veterinary Pharmacology and Toxicology | 155 |
| 3 | Veterinary Parasitology | 120 |
| 3 | Veterinary Public Health and Epidemiology | 64 |
| 3 | Livestock Products Technology | 82 |
| 3 | Veterinary and Animal Husbandry Extension Education | 123 |
| 3 | Veterinary Clinical Practices I | 2 |
| 3 | Livestock Farm Practices | 3 |
| 4 | Veterinary Medicine | 163 |
| 4 | Veterinary Surgery and Radiology | 144 |
| 4 | Veterinary Gynaecology and Obstetrics | 56 |
| 4 | Veterinary Clinical Practices II | 0 |

## Extras requiring content review

No public Unsorted subject exists. These items stay inside collapsed year-level Extras; their titles and parent folders do not establish a reliable subject.
- Year 2: Photo set — Year 2 revision — 136 images (`photos-1udDFWQDlMiRVWpnho39SbhQIvZW9shqY`).
- Year 4: Board question paper (`1DBGhjon8Jq1PEDAJ1mHIYdYx8cj9ITxf`).
- Year 4: missing ques doc (`1iONOgTAXim48x_xLv-49pNEGkD9PhSm8`).
- Year 4: New Doc 2022-02-10 17.57.35 (`1DeyRni66rcmbsUU5cjIGBqiFsDZCGEO-`).
- Year 4: Scan 31 Aug 22 · 08·36·24 (`1cCjRsAG9oTFysgaSv74AORrctyOAVtkf`).
- Year 4: Scan 31 Aug 22 · 08·39·46 (`1r6moeL6ZOxdMHgpmtMuV_cSeSh8DSlT6`).
- Year 4: Scan 31 Aug 22 · 08·40·53 (`1YwUkP-lYlStOvMtgWXcSE5tZw76KZNtW`).
- Year 4: vet Questions (`1YEfRXibZlDDa7rFuQkEf36beZNfvs7ZI`).
- Year 4: Veterinary science 2022- p1 & p2 (`1ym0is2skylb4qdffl62nzaIbm7GJ5lcv`).

## What changed

- Home: compact search, three computed statistics, four year tiles, study bento, two Telegram tiles, a request strip and a slim footer.
- BVSc overview contains only year cards; year pages contain subject cards; subject pages contain search, filters and paged accordions.
- No visible flat file list exceeds 30 rows. Additional batches use native details controls, including when JavaScript is disabled.
- Subject summaries, syllabus outlines, original file names, alternate formats, known credit, update dates, downloads and report links remain available.
- Objective resources are curated by subject. The ICAR projects presentation is excluded; no unverified file is presented as an ICAR PYQ.
- Clinical contains handbooks, a 12-item pharmacology starting list and four subject links. The broad Other dump is removed.
- Menu is one compact More sheet; background scroll, Escape, outside tap and focus return are handled. Header/mobile navigation duplication is removed.
- Bookmarks, recently opened resources and studied states remain local to the device; legacy saved IDs map to merged files and photo sets.
- Bricolage Grotesque, Inter and Caveat are self-hosted subsets with OFL licences. Warm paper, high-contrast ink and pastel year colours work in both themes.
- Motion is finite and optional: entry, filters, search, presses, section reveals, count-up and view transitions. Reduced motion removes nonessential animation.
- llms.txt, llms-full.txt, page Markdown, search JSON, sitemap, metadata and visible-content JSON-LD are regenerated from the catalogue.
- Strict external navigation policy is retained: the two Telegram channels, provenance-backed Drive links, and the main/blog ecosystem links in the footer. No additional third-party domains were removed in Task 3 because Task 2 had already removed them.

## Verification

The final browser audit covered **180 views**: ten core/representative pages at 360, 375, 390, 412, 430, 768, 1024, 1280 and 1440 px, in light and dark. It found **zero serious/critical axe issues, zero horizontal overflow, zero clipped headings/paragraphs and zero visible targets below 48px**. One H1 and valid heading outlines are checked across all 51 generated routes.

The home is **3,026 px at 390×844**, down from **4,723 px** (36% shorter), or 3.59 screens. Search is visible above the fold. Visible subject file rows measure **56px**. Static checks reconcile every group and enforce bounded file batches.

The final source payload is **18,719 bytes gzip for home HTML/CSS/JS**, fonts excluded; runtime JavaScript is **6,963 bytes gzip**. All 31 contrast pairs pass: body text ≥7:1, secondary ≥4.5:1 and functional borders ≥3:1.

Before/after Lighthouse below uses the **same gzip-enabled local server**. The initial plain-server Anatomy baseline was 64 performance because its HTML was uncompressed; that result is not used to claim an artificial improvement. P = performance; A = accessibility; BP = best practices.

| Page | Before P/A/BP/SEO | After P/A/BP/SEO | After LCP | After CLS |
| --- | --- | --- | ---: | ---: |
| `/` | 100/100/100/100 | 99/100/100/100 | 1.70s | 0.0018 |
| `/bvsc/` | 100/100/100/100 | 99/100/100/100 | 1.66s | 0.0000 |
| `/bvsc/year-1/` | 100/100/100/100 | 99/100/100/100 | 1.66s | 0.0000 |
| `/bvsc/year-1/veterinary-anatomy/` | 100/100/100/100 | 100/100/100/100 | 1.65s | 0.0003 |
| `/objective/` | 100/100/100/100 | 99/100/100/100 | 1.71s | 0.0143 |
| `/clinical/` | 100/100/100/100 | 99/100/100/100 | 1.66s | 0.0000 |
| `/study-tools/` | 100/100/100/100 | 99/100/100/100 | 1.66s | 0.0261 |
| `/search/` | 100/100/100/66 | 99/100/100/66 | 1.85s | 0.0160 |
| `/about/` | 100/100/100/100 | 99/100/100/100 | 1.66s | 0.0020 |
| `/request-resource/` | 100/100/100/100 | 99/100/100/100 | 1.70s | 0.0119 |

Interactions verified: menu Escape/outside close and scroll lock; Ctrl/Cmd+K and slash search; arrows/Enter; theme persistence; bookmarks/studied persistence; subject filtering; empty results; no-JavaScript preset topics; reduced motion. A focused final test additionally covers a 55-item saved shelf and the corrected Year 4 resource.

Screenshot/measurement artifacts:

- [Before screenshots, including 390/1280 light/dark](https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/39112821979) — artifact `task3-before`.
- [Comparable compressed baseline](https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/39113574488) — artifact `task3-before` contains the performance baseline.
- [Final full responsive audit and screenshots](https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/39114614476) — artifact `task3-after`.

Home, BVSc overview, Year 1, Anatomy, Objective and Clinical each have 390px and 1280px screenshots in both themes. Extremely tall baseline pages use viewport captures when the full document exceeds 20,000px; this is recorded in the audit script. Current pages have full captures. Desktop/mobile screenshot previews were visually inspected, leading to corrections to the Telegram heading and the subject toolbar.

Production verification is recorded in the deployment addendum after publication.


## Limits and deliberate choices

- The 136 Year 2 one-mark photographs have no reliable subject in their folder names. They remain one Extras photo set. Eight Year 4 papers also need inspection of their contents before a subject can be assigned safely.
- There are no confirmed ICAR PYQs in the catalogue. The request state remains visible instead of mislabelling a lecture.
- Search remains noindex as requested; Lighthouse therefore deducts its crawlability points. This is incompatible with demanding a 95+ SEO score for that particular page.
- The four explicitly requested year colours are shown together in the year picker; the rest of the layout uses restrained accents.
- An automated schema structure check is included. Google Rich Results Test and Schema.org’s remote validator have not been separately certified.
- Link syntax, local targets, manifest provenance and domain policy are checked. The entire set of Drive downloads has not been re-fetched; external availability and permissions may change.
- A Cloudflare cache purge requires account credentials that are not connected here. Versioned CSS/JS URLs are used to prevent old assets being reused.

## Implementation commits

1. `1c1b390` — data cleanup
2. `6fe8dac` — information architecture/pages
3. `e8d2884` — theme tokens
4. `db58446` — components
5. `cb7e02a` — motion


## Contrast pairs

| Theme | Foreground | Surface | Ratio | Required |
| --- | --- | --- | ---: | ---: |
| light | text | paper | 15.42:1 | 7:1 |
| light | muted | paper | 8.86:1 | 4.5:1 |
| light | border | paper | 15.42:1 | 3:1 |
| light | text | surface | 16.28:1 | 7:1 |
| light | muted | surface | 9.35:1 | 4.5:1 |
| light | border | surface | 16.28:1 | 3:1 |
| dark | text | paper | 16.13:1 | 7:1 |
| dark | muted | paper | 11.87:1 | 4.5:1 |
| dark | border | paper | 5.58:1 | 3:1 |
| dark | text | surface | 14.35:1 | 7:1 |
| dark | muted | surface | 10.56:1 | 4.5:1 |
| dark | border | surface | 4.96:1 | 3:1 |
| both | sticker ink | sun | 11.77:1 | 7:1 |
| both | sticker secondary | sun | 6.76:1 | 4.5:1 |
| both | sticker border | sun | 11.77:1 | 3:1 |
| both | sticker ink | coral | 7.87:1 | 7:1 |
| both | sticker secondary | coral | 4.52:1 | 4.5:1 |
| both | sticker border | coral | 7.87:1 | 3:1 |
| both | sticker ink | sky | 9.79:1 | 7:1 |
| both | sticker secondary | sky | 5.63:1 | 4.5:1 |
| both | sticker border | sky | 9.79:1 | 3:1 |
| both | sticker ink | mint | 11.34:1 | 7:1 |
| both | sticker secondary | mint | 6.52:1 | 4.5:1 |
| both | sticker border | mint | 11.34:1 | 3:1 |
| both | sticker ink | lime | 12.59:1 | 7:1 |
| both | sticker secondary | lime | 7.23:1 | 4.5:1 |
| both | sticker border | lime | 12.59:1 | 3:1 |
| both | sticker ink | telegram | 12.08:1 | 7:1 |
| both | sticker secondary | telegram | 6.94:1 | 4.5:1 |
| both | sticker border | telegram | 12.08:1 | 3:1 |
| both | primary label | primary button | 12.59:1 | 7:1 |

## Added source and audit files

- `scripts/catalogue.py`, `data/curation.json`, `data/drive-folders.json`, `data/duplicates-report.json`
- `scripts/build_site.py`, `scripts/site_shell.py`, `scripts/library_views.py`, `scripts/ui.py`
- `data/study-clinic-tokens.json`, `assets/motion.js`, three self-hosted WOFF2 fonts and their OFL licences
- `scripts/prepare-fonts.py`, `scripts/contrast-check.mjs`, `scripts/task3-static.py`, `scripts/task3-browser.mjs`, `scripts/task3-hosting.py`, `scripts/qa-server.py`
- `_headers`, `.github/workflows/task3.yml`, `docs/qa/task3/`

Generated HTML, page Markdown, social cards and retrieval files are updated in place. Existing subject-guide URLs remain available; retired Unsorted routes redirect to their year’s Extras.
