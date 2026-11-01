# Book artwork and detail pages

Every canonical book has a self-hosted cover, including objective collections and question banks. Selection order: visually reviewed cover from the linked PDF; verified reference cover from a matching publisher, retailer or bibliographic record; clearly labelled symbolic artwork using the recorded title and author. Unknown authors remain unlisted.

`data/book-cover-selections.json` records source URLs, dimensions and visual-review decisions. PDF candidates are never adopted solely because they are the first page. The unrelated Andrew Balfour result is explicitly rejected. Only selected images remain in the published assets; discarded interior-page candidates were removed.

`book_covers.resolve()` provides symbolic artwork for future entries without an approved cover. The static book check requires 100% cover coverage and verifies image dimensions and symbolic title/author metadata.

Book pages use a mobile-first cover/title layout, a full-width provider-specific action, a short description and optional source details. Original Telegram and Drive destinations remain unchanged. Symbolic artwork is identified; reference-cover editions may differ from the shared copy. No invented ratings, editions or author names are added.

Validation on 2026-10-31: 95 canonical books; 49 PDF covers, 26 reference covers and 20 symbolic covers. Book browser audit: 278 views; collection audit: 40 views. Both passed in light and dark themes. Full site static checks passed. Lighthouse on the library and four representative book pages: performance 96–99; accessibility, best practices and SEO 100. These are preview-build measurements, not guaranteed future scores.
