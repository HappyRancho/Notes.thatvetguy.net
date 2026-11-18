# Books library

The bottom navigation opens the compact Books library in place of Search. Search remains accessible through More and the existing search controls.

The library includes all 95 existing canonical book titles: 74 subject books and 21 objective/clinical resources. It uses seven broad categories, without year groups or expandable subject sections. Cover cards reuse the subject-page markup, with three columns on phones and five on larger screens, a small handwritten heading and restrained shelf accents.

Category controls show counts and filter in place. Title, author and subject search combines with the selected category. The initial 24-book batch expands through Show more; all 95 books are present in the static HTML and remain browsable without JavaScript. Full titles remain in the link accessible names even when the compact visual label is shortened. Images are lazy loaded; the small script runs only on /books/ and fetches no separate catalogue.

Validation: full npm run check; 10 browser views at 360/390/430/768/1280 pixels in both themes, with no axe violations, page errors or horizontal overflow; navigation to book details; title/author/subject searches; empty state; Clear/Escape; category keyboard use; Show more reaching all 95 books; and no-JavaScript browsing.

| Route | Performance | Accessibility | Best practices | SEO | LCP |
|---|---:|---:|---:|---:|---:|
| /books/ | 98 | 100 | 100 | 100 | 2.34s |
| / | 98 | 100 | 100 | 100 | 2.26s |

Scores are local mobile lab measurements with compressed delivery; production results can differ. Browser previews are included for light/dark themes at 390 and 1280 pixels.
