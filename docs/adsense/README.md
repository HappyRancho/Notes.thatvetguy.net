# Rx Notes AdSense integration

Publisher: `ca-pub-3524774459480835`. Registered site: `thatvetguy.net`.

The global head includes the requested asynchronous verification script exactly once. Verification is separate from manual ad rendering. `data/adsense.json` is the only placement configuration. Approval and rendering are false, every placement is disabled, and every slot ID is null. Inactive placements produce only an HTML comment: no label, empty space, `ins` element, initialization script or ad request from our code.

## Parent domain

The parent repository already includes the same verification script in its homepage. Both hosts need the following plain-text seller record at `/ads.txt`:

```
google.com, pub-3524774459480835, DIRECT, f08c47fec0942fa0
```

The parent file can also explicitly reference `subdomain=notes.thatvetguy.net`. Google starts ads.txt discovery at the registered root. A subdomain referral is optional when the publisher ID is the same; it is useful when maintaining a separate subdomain file.

## Account actions and future activation

Confirm Auto ads and Auto optimize/experiments are OFF in AdSense's Ads settings. The global Google script can load account-controlled Auto ads independently of this repository. Website switches cannot override the AdSense dashboard. This integration never enables Auto ads or any overlay format.

In AdSense Sites, verify `thatvetguy.net` and request review. Public HTML checks establish that the publisher code is present, not that Google has approved the site. Check the account's site and ads.txt statuses after Google crawls them.

Before enabling units: obtain Ready status, use actual responsive display-unit IDs from this publisher account, confirm Auto ads remain off, and review applicable privacy disclosures and Google consent requirements. This task does not add a privacy notice or alter navigation. Approval is Google's decision and includes content and policy review.

Only after an explicit activation request: set approved, renderEnabled and autoAdsOffConfirmed to true; enable an intended placement and supply its real ten-digit slot ID. Missing/invalid IDs fail closed. The allowlist limits every page to one unit. Homepage: immediately after BVSc Resources. Long guides/directories: after their first major content section. Book pages, download pages, short pages and other routes have no placement.

The responsive component reserves 250px creative height from first paint, adapts to the content width, and has a small Advertisement label. It has no sticky positioning, overlays, full-width expansion or collapse-on-no-fill. Validate actual creatives before activation; current browser tests exercise only an inert shell, never invented ad units.

Official references: [Connect your site](https://support.google.com/adsense/answer/7584263), [ads.txt guide](https://support.google.com/adsense/answer/12171612), [subdomain handling](https://support.google.com/adsense/answer/9785052), [Auto ads settings](https://support.google.com/adsense/answer/9305577).
