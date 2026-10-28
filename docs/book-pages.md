# Dedicated book pages — 28 October 2026

## Content and provenance

- 94 dedicated book/reference pages and a crawlable books directory.
- 21 existing Telegram resources retain their original post links on their detail pages.
- 67 files were inspected in 15 subject Books folders; no Notes or presentation folders were imported.
- Two objective packs were excluded from textbook additions: Micro mcq and Toxicology Objectives.
- 65 book/reference files form 62 works; multiple copies/editions stay available from the relevant work page.
- 11 existing reading recommendations have no verified copy: they offer a resource request, never a fake download.

## Files by year

| Year | Source files | Book/reference files |
|---|---:|---:|
| 1 | 8 | 8 |
| 2 | 12 | 11 |
| 3 | 14 | 13 |
| 4 | 33 | 33 |

## Images and accuracy

- 50 checked images: 21 bibliographic reference covers, 2 covers verified from linked files and 27 first-page/source previews.
- Reference covers and previews are labeled explicitly. They do not establish the edition of a linked copy.
- 44 pages have no verified usable image. They show “Cover unavailable”; no invented covers or stock covers are substituted.
- Rejected provider placeholders and an erroneous Goodman & Gilman author attribution are recorded in data/book-curation.json.
- Animal Nutrition author details were checked against its actual cover. D. V. Reddy’s source files are two distinct works, not duplicate parts.
- Original Telegram links, all 65 allowed Drive links, old notes, course outlines and canonical subject routes are preserved.

## Search and machine retrieval

- 623 resource records plus 11 reading-guide records in search (634 total).
- 130 reachable indexable pages, unique titles/descriptions, canonical URLs and Markdown mirrors.
- Each book has Book/LearningResource schema where applicable, real image metadata, original summaries and related subject reading.
- A source ReadAction points to Telegram or Drive; no fake direct PDF endpoint, ISBN, rating or edition is claimed.
- Sitemap, llms.txt, llms-full.txt and per-book 1200 × 630 social cards are generated from the same registry.
- These changes improve crawlability and resource identity; indexing, rich-result eligibility and ranking are controlled by search providers.

## Verification

Static checks pass locally: provenance, source-copy accounting, links, SEO reachability, headings, mirrors, course PDF hashes, source URLs, contrast tokens and payload budgets. Browser and production results are recorded separately in the workflow artifacts.

## Source research

Public Books folder snapshots and original Telegram post links are retained in data. Bibliographic evidence is retained in data/book-details.json and data/book-curation.json, including Open Library work records, Google Books references, a publisher listing and NLM catalogue records. A bibliographic edition is always distinguished from the linked source copy.

## Measured review build

- Browser suite: 236 book-page views, zero layout or interaction errors.
- Shared regression: 40 additional views, zero serious/critical axe violations, no overflow, no small touch targets or heading errors.
- Lighthouse mobile: library index 98/100/100/100; four book examples 99/100/100/100 (Performance/Accessibility/Best Practices/SEO).
- Measured CLS: 0.0057. LCP: 1.95–2.33 seconds; the index and image-heavy Animal Nutrition example exceed the earlier 2.0-second target despite passing the score threshold.
- Full browser, Lighthouse and screenshot evidence: https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/40643471778
