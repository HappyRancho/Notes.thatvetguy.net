# Content restoration and source review

Reviewed 14 October 2026. The preservation baseline is the homepage and resource data before the rebuild: commit `3ddc70ce92894bd6f8fb2c1a108257f282fb73bc`. `data/content-contract.json` records the required copy, categories, year grouping, objective book names and Telegram destinations. The build check detects accidental changes to them.

## Product model

Notes.ThatVetGuy is a free veterinary academic and study-resource platform primarily for BVSc & AH students. Its primary flow is **year → subject → Notes / Books**. The homepage introduces its own resource categories; it is not a promotional directory of competing platforms. Source references remain credited where users open the material. Source content is not copied or rehosted.

Restored: the compact tagline; supporting sentence; four search examples including Surgery books; original year titles/descriptions; full section copy; three exact Objective options; original tools and clinical categories; Backbenchers short notes; both correctly separated Telegram destinations; resource request; ecosystem links. Recently Added stays removed.

## Source findings

| Source | Reviewed pages / role | Applied finding |
| --- | --- | --- |
| Vetscraft | [Year-wise subjects](https://www.vetscraft.com/bvscah/), [anatomy](https://www.vetscraft.com/bvscah/veterinary-anatomy/), [physiology](https://www.vetscraft.com/bvscah/veterinary-physiology/), [pharmacology](https://www.vetscraft.com/bvscah/veterinary-pharmacology/), [parasitology](https://www.vetscraft.com/bvscah/veterinary-parasitology/), [medicine](https://www.vetscraft.com/bvscah/veterinary-medicine/), [surgery](https://www.vetscraft.com/bvscah/veterinary-surgery-and-radiology/), [gynaecology/obstetrics](https://www.vetscraft.com/bvscah/veterinary-gynaecology-and-obstetrics/) | Subject-specific note links and terminology. Some subject links in its year index lead to an under-development page, so those were not presented as complete notes. |
| DrVet | [First Year](https://www.drvet.in/p/first-year.html), [Book Bank](https://www.drvet.in/p/veterinary-book-bank.html) | Retain the earlier first-year anatomy/physiology/LPM grouping. Its PDF links were not assumed to work: comments on the page report unavailable files. |
| Vets Duo | [Subject notes](https://www.vetsduo.com/pages/notes.html), [second-year notes](https://www.vetsduo.com/pages/notes2.html), [third-year notes](https://www.vetsduo.com/pages/notes3.html), [first](https://www.vetsduo.com/pages/books1.html), [second](https://www.vetsduo.com/pages/books2.html), [third](https://www.vetsduo.com/pages/books3.html), [fourth-year books](https://www.vetsduo.com/pages/books4.html) | Confirmed subject/unit groups and book sections. Dedicated notebooks may require university selection; labels say so. A Medicine link in its subject index returned the general notes page, so Medicine uses a verified Vetscraft page instead. |
| Vet Study / JourneyWithASR | [ICAR papers](https://vetstudy.journeywithasr.com/p/previous-years-icar-aieea-question.html), [practical manuals](https://vetstudy.journeywithasr.com/p/veterinary-practical-manuals-pdf.html), [question banks](https://vetstudy.journeywithasr.com/p/veterinary-question-banks-pdf.html) | Retain separate PYQ and objective categories. Clinical Practices and Farm Practices point to labelled manual collections. Replaced the old question-bank link to a general materials/app page with the question-bank URL. The question-bank page appeared in current search results but could not be retrieved directly during review; no file-level availability is claimed. |
| GreatVets | [Notes](https://greatvets.in/notes), [books](https://greatvets.in/books) | Year/subject navigation reference. Its search preview described a fifth year; that was not adopted into this site's four professional-year tabs. |
| VetBVSc | [Notes platform](https://vetbvsc.in/), [fourth-year material](https://vetbvsc.in/bvsc-ah-4th-year-notes/) | Reference for veterinary study categories. No unchecked file links imported. |
| Vet Med Note | [Site](https://vetmednote.com/) | Paid bundle positioning reviewed as a reference only. Not labelled as a free resource. |
| Vet Study Bundle | [Site](https://www.vetstudybundle.com/) | Concise revision presentation reviewed as a reference only. No commercial bundle, quizzes or flashcards imported. |
| Merck Veterinary Manual | [Manual](https://www.merckvetmanual.com/), [NSAID overview](https://www.merckvetmanual.com/pharmacology/inflammation/nonsteroidal-anti-inflammatory-drugs-in-animals), [analgesics](https://www.merckvetmanual.com/therapeutics/pain-assessment-and-management/analgesics-used-in-animals) | Clinical/pharmacology source attribution. Meloxicam opens an analgesic reference that includes it; the site does not claim this is a locally authored drug monograph. |
| Cornell eClinPath | [Online textbook](https://eclinpath.com/) | Accurately described as an online clinical pathology textbook, not a downloadable PDF. |
| Vetlexicon | [Reference platform](https://www.vetlexicon.com/) | Access varies; do not describe the entire service as free. |
| TeachMeAnatomy | [Site](https://teachmeanatomy.info/) | Navigation/readability reference only; human anatomy content not imported as veterinary notes. |
| Studocu | [Site](https://www.studocu.com/) | Subject/document discovery reference only; no uploaded material or access claims imported. |

## Year grouping and title accuracy

The earlier subject grouping is deliberately preserved: Biochemistry is under 2nd Year, as in the reviewed DrVet/Vetscraft/Vets Duo layouts. The [VCI MSVE 2016 document](https://www.vci.dahd.gov.in/sites/default/files/IVPR/MSVE-Gazette-2016.pdf#page=103) has a discrepancy: section 20 places it in first professional, while the annexed transcript and the reviewed student resources place it in second. Accordingly, the page no longer claims that its grouping is an exact reproduction of section 20. Students are directed to their university timetable. No LFP is added to 4th Year.

The five requested Objective Books labels are preserved exactly, including `Dhruv N Desi`. Vet Study's indexed question-bank page uses the spelling `Dhruv N Desai`; the preserved display label is not represented as a verified bibliographic title. No edition, author or download is invented for any book.

## Availability boundary

Source review confirms page identity and relevant subject coverage, not the operation of every linked third-party PDF. The site uses “subject notes,” “book listings” or “manual collection” where those are the actual destinations. No “Download PDF” button is attached to an unverified file. Missing book-specific resources are clearly labelled and retain the resource-request action.

The AI/search metadata and optional `llms.txt` describe the same platform and visible content. They do not claim authorship, professional review, ownership of third-party material or guaranteed search placement.
