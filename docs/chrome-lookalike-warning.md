# Chrome lookalike warning on Notes.ThatVetGuy

## What was reported

The owner reports an Android Chrome warning when opening `https://notes.thatvetguy.net/`. The screenshot says “Did you mean thatvetguy.net?” and describes the visited site as looking fake. The screenshot displays `about:blank`, so the attempted URL was confirmed separately by the owner.

The owner reports that manually entering the Notes URL in a new Incognito tab does **not** show the warning. The affected Android Chrome version has not been supplied.

This matches Chrome's lookalike-URL warning, which is a client-side check and can depend on browsing history and site engagement. It is separate from the earlier robots.txt SEO audit. A site cannot hide Chrome's interstitial with HTML, CSS, JavaScript or a meta tag.

## Verified live evidence — 28 October 2026

Audit: https://github.com/HappyRancho/Notes.thatvetguy.net/actions/runs/40693331797

- The exact HTTPS Notes URL returns HTTP 200 without a redirect.
- The canonical URL is `https://notes.thatvetguy.net/`.
- The HTTP URL redirects once, with HTTP 301, to that HTTPS URL.
- The Notes hostname is ordinary ASCII, without an IDN/punycode substitution.
- Certificate hostname validation succeeds with TLS 1.3. The sampled certificate expires on 25 January 2027.
- Temporary normal Google Chrome 156.0.8078.47 profiles opened Notes without a lookalike warning, both directly and after visiting the main ThatVetGuy site. Both views loaded the actual page and its one H1.
- These browser checks used the desktop engine, including a narrow viewport. They do not reproduce the affected Android installation or its existing private history. They do not prove that every visitor is unaffected.

The audit did not identify a redirect or certificate change needed on the Notes homepage. Its result is **not** a malware or Safe Browsing classification, and does not mean the reported profile-specific warning has been removed.

## Practical next steps

1. Update Chrome on the affected Android device, fully close it, reopen it and retest the exact HTTPS address in a normal tab.
2. If the warning persists, use **Chrome → ⋮ → Help & feedback → Send feedback** on the affected device. Include the URL, screenshot and the report text in `docs/chrome-lookalike-report.txt`. That route can include the affected Chrome version and diagnostic information.
3. For a reproducible Chrome issue, https://crbug.com/new is the Chromium issue-reporting entry point. Route the report to **UI > Browser > LookalikeChecks**.
4. Retest the affected regular profile after a Chrome update or a response from Chrome maintainers. Do not claim the issue is globally fixed based only on the clean-profile test.

No feedback or external issue was submitted on the owner's behalf. No domain, URL, site theme or security protection was changed to conceal the warning. Do not ask visitors to switch off Safe Browsing or Chrome's lookalike protections.

## Sources

- Chrome lookalike warning behavior: https://chromium.googlesource.com/chromium/src/+/main/docs/security/lookalikes/lookalike-domains.md
- Chrome for Android feedback instructions: https://support.google.com/chrome/answer/95315?co=GENIE.Platform%3DAndroid&hl=en

The diagnostic workflow and scripts are under `.github/workflows/domain-warning.yml` and `scripts/ci/`. Its screenshots, TLS information and redirect observations are in the `chrome-domain-warning-evidence` Actions artifact. The public site’s presentation and resource links are unchanged.
