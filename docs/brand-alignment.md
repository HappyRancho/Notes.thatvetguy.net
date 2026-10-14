# Alignment with the main ThatVetGuy site

Reference: [thatvetguy.net](https://www.thatvetguy.net/) and its [shared theme source](https://github.com/HappyRancho/Thatvetguy/blob/main/theme.css), inspected 14 October 2026. `home-theme.css` is loaded after `theme.css`, so the old dark tokens in the main page's initial inline stylesheet are not its current rendered palette.

Shared cues adopted for Notes:

- Cream `#fffaf2`, forest `#183c36`, white paper panels and muted green `#59706b`.
- Coral `#ef6a50` actions, pastel coral `#fff0ea`, and the main hero's lime `#dbf07d` for Backbenchers.
- Inter body text and Playfair Display section headings, using `display=swap` and local/system fallbacks.
- Restrained rounded surfaces, fine dividers, a forest footer and short transitions.

Accessibility adaptation: white text on the main site's coral would have only 3.07:1 contrast. Notes uses dark forest `#102c26` on coral (4.86:1), with a lighter coral hover. Small coral links use darker `#a93c2b`. The compact Notes layout and original content are preserved. Main-site marketing claims, clinical credentials, testimonials and statistics are not imported into Notes.

There are exactly three original, unattributed student asides, stored in `data/section-asides.json`. They supplement the existing text in Objective Resources, Backbenchers and the AI study guide. Clinical reference copy stays factual. The existing content contract, credited sources and AI discovery files remain in place.

Interaction refinements: menu closing resolves before in-page navigation or search focus, duplicate drawer-search handlers are avoided, Escape and outside click retain dismissal, and reduced motion skips the closing animation. Search examples have 44px targets. Empty search content is outside the listbox; system high-contrast modes have explicit focus/selection treatment.

Browser visual verification remains unavailable in this sandbox. The interaction checks use a DOM test harness for logic; they are not a substitute for a real-browser accessibility or layout audit.
