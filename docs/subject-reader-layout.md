# Subject reader layout

All 19 subject readers now use a single white reading panel in the approved Rx Notes theme.

- One collection switcher: Topic-wise, TANUVAS and Books. The old large jump cards and duplicate All/Topic-wise/TANUVAS filters are removed.
- Topic units use compact UI typography and hairline dividers. The first unit opens by default. Unit and file anchors remain available.
- TANUVAS resources are direct file rows, with one Open action. A single-file course no longer needs a second accordion click.
- Recommended books have a dedicated view with titles, authors and the existing reading guidance. No unavailable downloads are invented.
- Search sits inside the reader and appears for collections with at least 12 notes. It filters by title and unit, exposes an empty state and keeps result announcements accessible.
- Source/course-code context is available in a compact disclosure. Course outlines, study guidance, studied state and year navigation remain accessible.
- Keyboard tabs, URL fragments, Back/Forward, reload, original shared links, and full no-JS content remain supported.
- The header logo has natural word boundaries and a literal T beneath its syringe glyph, preserving the visible design while aligning its accessible name. Tab state colours change immediately to avoid low-contrast intermediate colours.

The academic catalogue is unchanged: 540 resources across 19 subjects; all 561 catalogue and search entries (including the 21 Telegram collection resources) remain accounted for. Routes, external resource URLs, recommended book data, course PDFs and the approved overall theme remain unchanged.

The reader enhancement adds 1.4 KB gzip of JavaScript, loaded only on subject pages.

Validation uses real Chromium at 360, 390, 430, 768, 1280 and 1440px, light and dark, with all 19 subjects at 390px. It covers collection switching, file counts, direct TANUVAS access, readable unit headings, search/empty/reset states, keyboard tabs, bookmarks/recent/studied compatibility, old file hashes, no-JS content and reduced motion. The existing static provenance, URL, heading, schema, course-PDF and discovery checks pass.

Review run: https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/40312885281
