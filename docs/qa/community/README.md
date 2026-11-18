# Community upgrade QA — 18 November 2026

About, Community & Support and FAQ use the existing Rx theme with compact cards and native disclosures. The support page keeps `#contact`, `#contribute` and `#report`, adds `#request` and `#rights`, and preserves resource/file query context. The FAQ has 22 complete answers in static HTML, matching FAQPage data, Markdown, site search and the sitemap.

Five email templates cover resource requests, error reports, contact, contributions and copyright/credit concerns. Request and report drafts include the relevant resource, dates/details, remarks and optional names. Error reports also support device/browser details, reproduction steps and screenshot links. Screenshots are attached in the email app. Opening a draft does not send an email; there is no website upload or support backend. Clipboard denial opens and selects the manual preview.

Compactness: redundant introductory blocks were removed, the six support shortcuts use a two-row grid on phones, short fields are paired, and additional details stay collapsed. In both themes at 360 and 390 px, the first resource input begins 536 px from the viewport top. The scrolling student-use notice is 26 px high. Still notice text wraps when paused, when reduced motion is requested, or without JavaScript.

Validation:

- Full production build and full static/SEO/source checks.
- 32 browser views: Home, About, Support and FAQ; light/dark; 360, 390, 768 and 1280 px. No accessibility violations, clipped text, horizontal overflow or undersized visible controls.
- Entered report/request details and file/resource context survive URL encoding into the correct email body. Copy, denied-clipboard fallback and FAQ-to-report navigation pass.
- Without JavaScript, all five support sections are open, complete email templates are available and FAQ disclosures operate natively.
- Notice pause persists across reloads; resume and reduced motion work. The preference is applied before paint.

Screenshots and detailed reports are stored alongside this document. These are local review-build measurements, not claims about production deployment, search ranking or AI citations.

## Local mobile Lighthouse

| Page | Performance | Accessibility | Best practices | SEO | CLS |
|---|---:|---:|---:|---:|---:|
| / | 99 | 100 | 100 | 100 | 0 |
| /about/ | 99 | 100 | 100 | 100 | 0 |
| /request-resource/ | 99 | 100 | 100 | 100 | 0 |
| /faq/ | 99 | 100 | 100 | 100 | 0 |

The existing Books library also passed ten light/dark responsive views, filtering, batching and no-JavaScript access to all 119 titles.
