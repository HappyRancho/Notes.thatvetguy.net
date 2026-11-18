# Homepage Books section — 18 November 2026

The new Books section sits directly below Backbenchers Corner and above Get Involved. It spans the desktop grid so it stays below Backbenchers visually as well as in DOM order. The Rx section heading, hand lettering, tab drawer, cover cards and library link reuse the existing design language.

Clinical Picks and Core Subjects each preview six existing canonical books. Three covers fit per row on phones and six per row on wider screens. Covers are lazy loaded; titles lead to their existing detail pages, and the footer opens the complete 119-book library. No extra JavaScript or external download request was introduced.

Validation:

- Full production build and npm run check passed. The homepage contract now accounts for the fourth tab group.
- Ten light/dark responsive views at 360, 390, 430, 768 and 1280 px passed with no overflow, broken covers, small targets, accessibility violations or JavaScript errors. Both shelves were exercised in every view.
- Tab keyboard arrows/Home work. Canonical book-detail and complete-library navigation pass. Without JavaScript, the visible preview remains available and the Core Subjects link opens the real library category with all 119 books accessible.

Local mobile Lighthouse: performance 99, accessibility 100, best practices 100, SEO 100; CLS 0. These are review-build measurements, not field Core Web Vitals or ranking claims.
