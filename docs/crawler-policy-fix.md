# Production crawler-policy fix

The failed production run for `de7acd8`, attempt 2, deployed successfully and matched the committed build. All 30 responsive checks passed. Lighthouse measured performance 97–98, accessibility 100, best practices 100, and SEO 92 on the indexable sample pages. The SEO gate requires 95, so the overall verification job failed.

The failing Lighthouse audit was `robots-txt`. Cloudflare prepended this directive to the public response, before the valid repository file:

```
Content-Signal: search=yes,ai-train=no,use=reference
```

The installed Lighthouse version does not recognise that directive. This warning is not evidence that Google cannot index the website. The Cloudflare-managed prefix also contains AI crawler restrictions that differ from the site's committed allow policy.

## Actual fix in Cloudflare

1. Select the `thatvetguy.net` zone.
2. Go to **Security → Settings**, filter by **Bot traffic**, then **Configure AI bot policies**.
3. Turn off **Enable Bot Preference Sync**. Older dashboard versions may show **Manage robots.txt** or **Cloudflare managed robots.txt** instead.
4. Save. Keep the website's own `robots.txt` and sitemap reference.
5. Recheck `https://notes.thatvetguy.net/robots.txt`. The Cloudflare-managed prefix should be gone and the response should match the repository's directives.

Cloudflare documents that policy changes appear within seconds without a cache purge. This fix does not require disabling general website security, changing DNS or modifying page designs.

Cloudflare documentation: https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/

## Repository changes

- `scripts/ci/check-live-robots.py` compares the public response against the committed policy, identifies Cloudflare injection and unsupported directives, and writes an actionable GitHub job summary.
- `scripts/ci/test-robots-policy.py` covers the observed production failure, changed bot rules, missing sitemap, formatting differences and HTML challenge responses.
- Production verification runs this preflight before installing browser dependencies and running the longer Lighthouse audit.
- **Crawler policy verification** is a short, separately runnable workflow for checking the hosting fix.
- The Lighthouse SEO requirement remains **95**. No failures are suppressed and `/search/` retains its intentional noindex policy.

## Verification after the hosting change

Run **Actions → Crawler policy verification → Run workflow**. Once that passes, rerun **Production verification** to measure the live Lighthouse SEO score. A passing preflight confirms the response is correct; only a new Lighthouse run confirms the final SEO score.

## Access boundary

The connected environment has no Cloudflare credentials or account-management tool. The existing deployment audit also reported that Cloudflare token/zone secrets were unavailable. Repository edits cannot switch off this zone-level feature. The hosting change must be made through the Cloudflare dashboard or an authorised Cloudflare connection.
