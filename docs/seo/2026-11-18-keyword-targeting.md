# Veterinary notes and books: keyword targeting, 18 November 2026

The target is better relevance for veterinary notes, veterinary books and the specific study tasks this library serves. The accompanying [keyword map](2026-11-18-keyword-map.csv) assigns 31 existing landing pages a primary query family and related examples. These are editorial targets based on the actual collection, not measured search volumes or reported Google positions.

## Page focus and implementation

| Search intent | Main destination | What the reader gets |
|---|---|---|
| Veterinary notes, free vet notes, veterinary study material | `/` | Clear notes/books heading and direct study shortcuts |
| BVSc notes by year or subject | `/bvsc/` and the four year hubs | Actual subject navigation, available materials and syllabus links |
| Veterinary books, vet books, veterinary book PDF | `/books/` | Broad book categories, title/author search and canonical book detail pages |
| Anatomy, physiology, pathology, pharmacology, medicine and other subject notes | The existing subject URLs | Subject-specific titles, notes or study-guide headings, original study tips and source-backed collections |
| TANUVAS veterinary notes | `/bvsc/tanuvas-notes/` | Four-year directory matching the current 59-PDF, 16-subject inventory |
| BVSc syllabus, MSVE 2016 checklists | `/bvsc/syllabus/` | Existing theory/practical checklists and source curriculum |
| Veterinary objective notes and question banks | `/objective/` | The actual objective collections, not an invented PYQ archive |
| Veterinary clinical handbooks and drug references | The existing clinical collections | Named references and their available source access |
| A named book or author | Its canonical `/books/{id}/` page | Edition/source details and the available download or request action |

27 search titles were improved. Home and book-library headings now name the resource types directly. The current theme, cover shelves, broad categories, tab navigation and stable URLs remain in use. A compact book-library shortcut appears beside BVSc notes, TANUVAS and syllabus shortcuts. The 19 subject introductions now expose their existing distinct study tips; the subject awaiting notes is described as a study guide. Year descriptions name the actual subject areas. Titles, descriptions and visible headings carry the context naturally; related query examples are not pasted into the pages.

Canonical HTML, Open Graph, structured data and Markdown remain generated from the same content. Changes update the existing sitemap dates through content fingerprints. Source-check dates remain independent: a wording change does not claim that external PDFs were reverified. Search remains intentionally noindex, while the useful landing and book pages remain indexable. No extra landing pages, hidden keyword lists, meta-keywords, ratings or affiliation claims were added.

## Evidence and limits

The public pre-change probes returned HTTP 200 for Home, BVSc, Books, Anatomy, robots.txt, sitemap.xml and build-info.json. These are public accessibility checks; they cannot establish Google's indexed status or rankings. The baseline served build `a61928145199`. The implementation is prepared in a review branch; this audit does not claim it is deployed.

Review evidence is in [docs/qa/keyword-visibility](../qa/keyword-visibility/): metadata before/after, mobile screenshots, static checks, responsive accessibility/navigation checks and local Lighthouse measurements. The 119-book library and all existing source inventories are preserved. These local checks measure implementation quality, not search-engine placement.

## Measure results after publication

Use the existing Search Console property with a **Page → URLs starting with `https://notes.thatvetguy.net/`** filter. The domain property also contains unrelated main-site and blog URLs; their exclusions are not evidence about this repository. Record the preceding 28 days before deployment and compare equivalent periods after recrawling. Separate branded ThatVetGuy searches from non-branded queries, and compare mobile/desktop and India/all countries consistently.

Track impressions, clicks, CTR, average position, indexed canonical URLs and query-to-page matches. Use these query groups individually: veterinary notes/vet notes; veterinary books/vet books; BVSc notes; year-specific notes; TANUVAS; syllabus; individual subjects; named books/authors. A Search Console query regex such as `(?i)(veterinary|vet|bvsc|tanuvas)` can provide a broad first pass; use individual query filters to assess a specific family.

Inspect the canonical Home, Books and important subject pages after publication, and request indexing once where appropriate. Keep the current sitemap submission. No Search Console indexing request or external account change was made in this task. If a page is indexed but earns few impressions, improve its useful original content and genuinely relevant references using the observed queries. Links from willing teaching staff, college resource pages and the main site's relevant pages are an owner opportunity; no outreach was sent.

A top position for every veterinary search cannot be guaranteed. Relevance, competition, useful content and search-engine assessment remain material. Google also does not use meta-keywords; adding them would not address the request.

## Primary guidance

- [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide): help users and crawlers understand useful content; no guaranteed first position.
- [Google title-link guidance](https://developers.google.com/search/docs/appearance/title-link): concise, descriptive titles, clear headings and no keyword repetition.
