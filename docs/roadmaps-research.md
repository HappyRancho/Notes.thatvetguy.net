# Four professional-year roadmaps — research and implementation

Reviewed 24 October 2026. Scope: the 2016 MSVE professional-year scheme used by the site's existing year/subject grouping. The guide does not claim to replace a university's current scheme or calendar.

## Primary academic sources

1. [Veterinary Council of India: official MSVE Gazette, 12 July 2016](https://vci.dahd.gov.in/sites/default/files/IVPR/MSVE-Gazette-2016.pdf). Printed page numbers below are Gazette numbers; PDF viewer page numbers may differ by one.
2. [ICAR–IVRI: Undergraduate Programme](https://ivri.nic.in/academics/ugprog.aspx), especially system of education, professional-year distribution and examinations. This is a cross-check, not a substitute for the Gazette: its rendered second-year subject list omits a Pathology line although its total includes it.
3. [VCI: Information Bulletin for academic year 2025–26](https://vci.dahd.gov.in/sites/default/files/Counseling/INFORMATION%20BULLETIN%20AY%202025-26.pdf), introduction identifying the MSVE 2016 framework. This does not establish the absence of every later university-specific instruction.
4. The user's four original professional-year PDFs, hosted unchanged at `/assets/course-outlines/`. The existing SHA-256 checks continue to verify their bytes. These supply course-topic detail and are retained exactly as requested.

## Academic claims and their verification

| Claim shown | Verification |
| --- | --- |
| 1st Year: 12 theory + 6 practical = 18 credits | VCI regulation 11(1), printed p.95; Annexure I transcript, p.173; IVRI course table. Anatomy 4+3, Physiology 4+1, LPM 4+2. |
| 2nd Year: 15+7 = 22 | Same sources. Pathology 4+2, Microbiology 3+2, Genetics 3+1, Nutrition 3+1, Biochemistry 2+1. |
| 3rd Year: 15+9 = 24 | Same sources and the uploaded third-year outline. Pharmacology 4+1, Parasitology 3+2, Public Health 3+1, Extension 3+1, LPT 2+1, Clinical Practices I 0+1, Farm Practices 0+2. |
| 4th professional: 8+9 = 17 | Same sources; transcript p.174. Medicine 4+1, Surgery 2+1, Gynaecology 2+1, Clinical Practices II 0+6. |
| Full curriculum: 81 credits | Regulation 11(1); sum 18+22+24+17. |
| Professional duration: 1, 1, 1 and 1.5 years | Regulation 11(1) and professional examinations under 13(7). |
| Minimum teaching days: 210 for each of first three, 315 for fourth | Regulation 2(1)(j); annual examination days excluded. |
| Minimum attendance: 75% theory and practical separately | Regulation 15(1)–(2), p.101. This is a baseline, not advice to assume a waiver or miss classes. |
| Pass requirement: 50% theory and practical separately | Regulation 16(2), p.101; theory combines internal and external components. |
| Internals: three coverage checkpoints at 30%, 60%, 90%; 40 marks each | Regulation 13(6), p.99; IVRI assessment table. These are coverage milestones, not asserted chapter ranges or examination predictions. |
| Best two internal assessments count | Regulation 13(8) and (13), p.100. Local implementation/weighting must be checked with the university. No claim that 3×40 is the final course score is made. |
| LFC/VCC practical assessment has a separate schedule | Regulation 13(8), p.100: assessments at half-course and full-course completion. Generic theory checkpoints are not presented as the complete Clinical Practices II assessment. |
| Practical preparation includes records, observed skills and viva | Regulation 13(10), p.100. |
| Separate compulsory 12-month rotating internship after fourth professional/credit completion | Regulation 12(1), (3), p.95. Clinical Practices II is not relabelled as internship. |

The phase labels in the navigation are editorial navigation aids, not additional VCI course classifications. Credit bars represent credits, not predicted exam marks or the time a student must allocate.

## Conflicts corrected or explicitly disclosed

- The reference screenshot's third-year chart itemises only 22 of 24 credits. The new chart includes Livestock Farm Practices 0+2, so all seven courses and all 24 credits are visible.
- The uploaded first-year outline prints 14+7=21 and includes Biochemistry. The site's professional-year grouping and VCI transcript place Biochemistry in second year. The PDF is not edited; a visible note on both relevant roadmaps explains the difference. The Gazette's professional distribution and transcript are used for credit totals rather than silently mixing schemes.
- The IVRI page's second-year rendered list misses Pathology; its year total and the Gazette establish the complete five-subject list. A missing web line is not treated as absence of that subject.
- The fourth year is 18 months, followed by a separate internship. The chart includes all six practical credits of Clinical Practices II and does not invent a generic theory mark for it.
- Starting the academic year on a fixed September date is not presented as a current timetable promise. University calendars determine actual dates.

## Study strategy: source type and limits

Reviewed [Dr. Bhupender's first-person account, published 28 January 2023](https://www.vetextension.com/toppers-talk-tips-and-tricks-to-crack-icar-pg-examination-in-animal-sciences/). The article identifies him as Rank 1 in AIEEA Animal Science 2022. Its status is personal preparation advice; it is not an academic regulation, independent rank verification or a guarantee of results.

Only general habits were adapted: make revision material manageable, use earlier papers to understand the task, revisit mistakes and diagnose why an answer went wrong. The guide does not copy the article, claim its PG topic priorities apply to professional exams, promise repeated questions, prescribe unsafe guessing, or claim a fixed MCQ count guarantees a rank.

Subject-specific study methods, weekly rhythms and short margin notes are original editorial guidance informed by the attached course topics. The UI labels advice separately from academic rules. No anonymous anecdote or invented topper quote establishes a fact. Clinical study advice stays at the level of supervised learning and does not provide drug doses or treatment instructions.

## Website implementation

- Four new static routes: `/bvsc/year-1/roadmap/` through `/bvsc/year-4/roadmap/`.
- Homepage and year-page Road Map CTAs, plus Study Tools/Tips links, open the appropriate roadmap. Existing `/bvsc/year-N/#road-map` disclosures remain valid for old links.
- Approved Rx Notes header, blue/pastel palette, handwritten subtitles, white rounded cards, footer and fixed bottom navigation are shared unchanged.
- Each roadmap includes a five-stage journey, four glance tiles, credit chart with subject links, exam checkpoints, subject disclosures, weekly study guidance and compact sources. Internship is an on-page section in fourth year, not a fabricated fifth-year course page.
- The same source data feeds all four roadmaps. Static checks verify course names, reconciled credits, correct routes, framework notes, sitemap/Markdown discovery and external-link policy. Existing 520 resource entries and the original course PDF bytes remain intact.
- Metadata, sitemap, Markdown mirrors and `LearningResource` JSON-LD are generated through the existing build pipeline. No new production dependency or additional JavaScript is required by the roadmap.
- Source URLs are recorded here and in the data file. Public roadmap source credits are bibliographic text and local outline links, preserving the site's restricted outbound-link policy.

## Verification

`npm run build`, `npm run check`, `scripts/roadmaps-qa.mjs` (360/390/430/768/1024/1440 px in light and dark), the existing homepage regression suite and Lighthouse checks run through the review workflow. The browser suite checks subject links, all four year CTAs, accordions, internship navigation, no-JavaScript access, reduced motion, overflow and axe violations. Results and screenshots are workflow artifacts under `docs/qa/roadmaps/`.

Publication must be distinguished from deployment. The previous audit found that Cloudflare was serving an older build despite newer commits; verify the current build marker rather than assuming a successful repository update is live.
