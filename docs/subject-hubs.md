# Subject pages — Rx Notes structure

Only the 19 subject hubs adopt the new layout: introduction → Syllabus Checklist → Notes (Topic-wise / Unit-wise TANUVAS + Practical Vault) → Books with covers. The shared header, navigation, year pages, homepage and existing book/collection routes retain their approved design. Notes start collapsed on an ordinary visit; original note hashes still reveal the correct collection and unit. Books remain visible below Notes.

Each subject has a separate `/syllabus/` page. The 1,748 topic checkboxes cover 169 source units/sections from the four original professional-year PDFs. Checkbox progress is stored only in the current browser. Unit numbering and practical-only sections follow the source; no theory units were invented for practical courses. Original PDFs and their SHA-256 hashes are preserved. Scanned pages were read with OCR; extracted topic text is checked against each retained source unit to prevent dropped syllabus words.

Biochemistry stays in the site's existing 2nd Year group, with its source in the 1st Year PDF explained. The complete Clinical Practices II rotations come from pages 11–13 of the 3rd Year PDF; the 4th Year PDF contains only the opening part. Source links and these differences are disclosed on the corresponding checklist.

Practical Vault is a separate `/practicals/` page for every subject. Only files within real Practical folders from the four provided Drive roots were included. There are 147 documents/slides and four photo collections across 14 subjects, organised by original folder. File details use original names, formats, verified byte sizes and source-folder context; unknown authors and dates are not invented. Every file has one Open action. Five subjects without Practical-folder material have an honest coming-soon state and a working practical checklist link.

All 324 observed source files remain accounted for: 147 documents plus 177 observed images grouped into four albums. Three image folders expose a 50-item public preview. Their cards open the complete original folders; no exhaustive image count is claimed. An unrelated Medicine/Media/Spotters folder was excluded because it is outside the Practical folders. No source file, book link, Telegram post or old note hash was removed.

The new pages are included in the sitemap, llms files, clean Markdown mirrors and semantic JSON-LD. All practical resources and the 19 syllabus checklists are searchable. Static output contains 174 pages, 168 indexable pages, 774 source resource records and 804 search records (including 11 existing book reading guides and 19 checklists).

Checks: original PDF hashes, unit numbering, complete topic wording, unique topic IDs, canonical note hashes, exact Practical-folder file accounting, source URLs, strict outbound policy and stylesheet isolation. Browser measurements and screenshots are recorded under `docs/qa/subject-hubs/` in the workflow artifacts.

The previously documented Cloudflare-managed robots.txt injection remains a hosting setting; repository code cannot remove that prefix without access to the zone settings. It is unrelated to the subject-page layout.

Subjects without material in a Practical folder: Veterinary Physiology, Veterinary and Animal Husbandry Extension Education, Veterinary Clinical Practices I, Livestock Farm Practices, Veterinary Clinical Practices II.

Initial review: 156 subject, checklist and vault views passed at 360, 390, 430, 768 and 1280px, with light/dark checks and keyboard/persistence tests. Shared geometry checks passed 32 additional views. The shared interaction suite was adjusted to avoid closing a notes drawer already restored from its hash before running its existing note-search assertion.

## Final measured review

- Subject suite: 156 views, no geometry errors or serious/critical axe violations; all subject/vault/checklist link and progress tests pass.
- Shared suite: 32 views and all preserved search/menu/shelf interactions pass.
- Lighthouse mobile: Anatomy hub and Medicine hub 98/100/100/100; Anatomy checklist and Practical Vault 99/100/100/100 (Performance/Accessibility/Best Practices/SEO).
- Measured CLS 0.0057–0.0066. LCP 1.96–2.19 seconds; the two subject hubs exceed the earlier 2.0-second target despite passing the score target.
- Evidence: https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/40662345098 and https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/40661111605 .
