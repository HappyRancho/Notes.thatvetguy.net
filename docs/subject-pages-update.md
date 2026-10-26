# Subject pages and TANUVAS notes

The four professional-year pages are now short directories. Each links to the other years, its existing roadmap and the original course-outline PDF. Subject cards open one of 19 canonical subject readers. The redundant bottom roadmap disclosures have been removed; the researched roadmap pages remain available.

Each subject reader brings together highlighted topic-wise and TANUVAS notes, bounded unit accordions, search/filter controls, recommended books and authors, course-outline links and study guidance. Original file URLs are preserved. Books without linked copies remain honest reading recommendations. Empty clinical/practical subjects show availability information and a useful outline, without invented downloads.

Old year/notes links and file hashes still resolve through a noindex gateway. Search, saved/recent links, redirects, sitemap, Markdown mirrors, llms files and JSON-LD now point to canonical subject pages.

## Catalogue

| Year | Subjects | All notes | TANUVAS-labelled resources |
| --- | ---: | ---: | ---: |
| 1 | 3 | 63 | 11 |
| 2 | 5 | 223 | 16 |
| 3 | 7 | 195 | 16 |
| 4 | 4 | 59 | 4 |

The source pass reviewed 42 unique TANUVAS entries: 40 PDFs/Drive resources and two verified Word documents. One entry was already in the existing catalogue, so 41 new resources were added. Including six existing TANUVAS-labelled entries, 47 resources are now grouped as TANUVAS notes. Total catalogue: 540 academic note resources plus the unchanged 21 Telegram collection resources.

## Source corrections and limits

- VetBVSc’s fourth-year TANUVAS landing link currently returns to the fourth-year index without a course collection. The four existing fourth-year notes already explicitly credited to TANUVAS remain available. No missing fourth-year collection was invented.
- The source’s VAE-511 entrepreneurship link points to the same VPE-511 public-health PDF. It is retained once under Public Health, with the conflicting label logged.
- The source labels VPA-211 as general parasitology/helminthology, but its linked DOCX opens with Arthropoda/Insecta. The display title is corrected to Veterinary Entomology; the original URL and source title remain recorded.
- Course codes in the older TANUVAS collection do not define current professional-year placement. Explicit subject mapping preserves the existing academic grouping.
- Public file-access settings and source availability can change. Linking a resource does not assert authorship, endorsement or medical review.

## Verification

Static checks pass: all 499 original notes accounted for; 561 catalogue/search rows; one canonical file row per resource; 19 subject routes; all old file aliases; 35 reachable indexable sitemap pages; no broken internal file/anchor targets; original course PDF hashes; strict reviewed-link policy; heading/schema/metadata checks; 64 approved contrast pairs.

Full browser regression: 130 academic views (all four years at 360/390/430/768/1024/1280/1440, all 19 subjects at 390 in light/dark, plus representative subjects at the other widths), zero overflow or serious/critical axe findings. Homepage regression: 12 views, all interactions passed. General page regression: 32 views, no bugs.

Lighthouse mobile on Year 1, Year 4, Anatomy and Pharmacology: 99 performance, 100 accessibility, 100 best practices, 100 SEO on all four. LCP 1.96–2.11 seconds; CLS 0–0.006. The 2.0-second LCP target was slightly exceeded by the two year directories in this lab pass; no faster score is claimed.

Full QA: https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/40301657298

Final compact-copy/empty-state refinement: 30 focused browser views and 32 general views passed. Four Lighthouse audits again scored 99/100/100/100. Subject LCP improved to 1.81–1.89s; year-directory LCP was 2.04–2.11s. TANUVAS collection keywords are now included in the public search index and verified against every one of the 47 TANUVAS-labelled entries using the production search function. Unit groups sort numerically (Units 1–6 before Unit 7).

Refinement QA: https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/40303028852 Production verification then compares the deployed build marker and asset versions, including new year and subject routes.

## Wider regression

The main-branch audit measured 198 views and 11 Lighthouse audits. All academic, objective, clinical, tools, search, about and request views passed. It caught a pre-existing homepage font-load shift at 768px (CLS 0.119): the cursive fallback wrapped the academic subtitle to two lines before Caveat loaded. The approved final typography is unchanged. A locally available fallback is adjusted to 76.09%, measured from the actual Caveat and Liberation Sans advance widths for that subtitle; the correction receives a focused nine-width light/dark CLS regression. Search remains intentionally noindex (Lighthouse SEO 66); all indexable audited pages scored 100 SEO and accessibility, performance 97–99.
