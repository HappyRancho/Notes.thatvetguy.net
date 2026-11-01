# Rx Notes primary storage

Owner-designated root: https://drive.google.com/drive/folders/1CtC2aBVwE6J2ss1NJdCxOKCizaumSbiw

`data/primary-drive-links.json` maps a canonical book ID to one specific file, reviewed against `primary-drive-inventory.json` and `primary-drive-verification.json`. The owner separately supplied the Ultimate Vet Handbook file. Apply these mappings after historical source and Telegram overrides. Preserve resource IDs, book routes and saved links.

All 21 curated Objective and Clinical downloads and five Anatomy titles use the matched primary files. Existing Vetverse copies remain available as alternate copies. Other notes and practical folders keep their working URLs until matching content is supplied; empty primary folders must never replace those resources. The additional Saunders PDF is inventoried but is not silently substituted for another handbook.

For additions: inspect the root, confirm subject and resource identity, add an explicit mapping, and run the PDF access check. Do not infer a replacement solely from a generic filename. Public-folder inventory checks flag possible pagination or incomplete listings. File availability can change after review.

Verification: `check-primary-storage.py` reconciles every mapping, stable catalogue ID and provider label; `primary-storage-qa.mjs` exercises all subject panels/checklists at mobile and desktop widths, stored ticks, direct links, search and no-JavaScript navigation. The broader book, collection and career browser suites remain enabled.
