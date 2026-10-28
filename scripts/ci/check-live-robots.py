#!/usr/bin/env python3
"""Compare public crawler instructions with the site's committed crawl policy."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_URL = 'https://notes.thatvetguy.net/robots.txt'
SETTINGS_HELP = ('Cloudflare → thatvetguy.net → Security → Settings → Bot traffic → '
                 'Configure AI bot policies → turn off Enable Bot Preference Sync '
                 '(or Manage robots.txt), then save.')


def directives(text):
    """Ignore comments and formatting, while preserving URL/path case."""
    result = []
    for number, original in enumerate(text.lstrip('\ufeff').splitlines(), 1):
        line = original.split('#', 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r'([A-Za-z][A-Za-z-]*)\s*:\s*(.*)', line)
        if not match:
            result.append({'line': number, 'key': None, 'value': line})
            continue
        key, value = match.groups()
        key = key.lower()
        if key == 'user-agent':
            value = value.lower()
        result.append({'line': number, 'key': key, 'value': value})
    return result


def inspect(expected, actual, content_type='text/plain'):
    wanted = directives(expected)
    received = directives(actual)
    issues = []
    managed = bool(re.search(r'BEGIN\s+Cloudflare\s+Managed', actual, re.I))
    unknown = [row for row in received if row['key'] not in
               {'user-agent', 'allow', 'disallow', 'sitemap', 'crawl-delay', 'host', 'clean-param'}]
    if '<html' in actual.lower() or not content_type.lower().startswith('text/plain'):
        issues.append({'code': 'not-plain-text', 'message': 'The robots URL must serve a plain-text crawler policy, not an HTML page or challenge.'})
    if managed:
        issues.append({'code': 'cloudflare-managed-content', 'message': 'Cloudflare is prepending managed crawler instructions to the committed policy.'})
    if unknown:
        issues.append({'code': 'unrecognised-directive', 'message': 'The public response contains syntax unsupported by the current Lighthouse robots audit.', 'lines': unknown})
    pairs = lambda rows: Counter((r['key'], r['value']) for r in rows)
    missing = pairs(wanted) - pairs(received)
    additional = pairs(received) - pairs(wanted)
    if missing or additional:
        issues.append({'code': 'policy-differs', 'message': 'The live crawler instructions differ from the committed allow policy.'})
    if not any(r['key'] == 'sitemap' for r in received):
        issues.append({'code': 'missing-sitemap', 'message': 'The public robots file is missing its sitemap reference.'})
    return {
        'passed': not issues,
        'cloudflareManaged': managed,
        'issues': issues,
        'missingDirectives': [{'directive': k, 'value': v, 'count': n} for (k, v), n in missing.items()],
        'additionalDirectives': [{'directive': k, 'value': v, 'count': n} for (k, v), n in additional.items()],
        'remediation': SETTINGS_HELP if managed else 'Restore the committed robots.txt response and check the public URL again.',
    }


def request_text(url):
    req = Request(url, headers={'User-Agent': 'NotesThatVetGuy-RobotsAudit/1', 'Cache-Control': 'no-cache'})
    with urlopen(req, timeout=20) as response:
        raw = response.read(256_001)
        if len(raw) > 256_000:
            raise ValueError('robots.txt response exceeds the audit size limit')
        return raw.decode('utf-8-sig'), response.headers.get('Content-Type', ''), response.status


def summary(report):
    title = 'Live crawler policy passed' if report['passed'] else 'Live crawler policy needs attention'
    lines = ['## ' + title, '', '- URL: ' + report['url'], '- Result: ' + ('PASS' if report['passed'] else 'FAIL')]
    for issue in report.get('issues', []):
        lines.append('- ' + issue['message'])
        for row in issue.get('lines', []):
            lines.append('  - Line ' + str(row['line']) + ': `' + str(row['key']) + ': ' + row['value'].replace('`', '') + '`')
    if not report['passed']:
        lines += ['', '**Required action:** ' + report['remediation'], '',
                  'This is a crawler-policy check. Its failure alone does not mean the website deployment failed. '
                  'The Lighthouse SEO threshold remains 95.']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default=PUBLIC_URL)
    parser.add_argument('--expected', type=Path, default=ROOT / 'robots.txt')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/qa/search/robots-policy.json')
    parser.add_argument('--actual-file', type=Path, help='Audit a retained public response offline.')
    args = parser.parse_args(argv)
    try:
        if args.actual_file:
            actual, mime, status = args.actual_file.read_text(), 'text/plain', 200
        else:
            actual, mime, status = request_text(args.url)
        report = inspect(args.expected.read_text(), actual, mime)
        report.update(url=args.url, status=status, contentType=mime)
    except (HTTPError, URLError, TimeoutError, UnicodeError, ValueError, OSError) as error:
        report = {'url': args.url, 'passed': False, 'cloudflareManaged': False,
                  'issues': [{'code': 'fetch-failed', 'message': 'Could not verify the public robots response: ' + type(error).__name__}],
                  'remediation': 'Check availability of the public robots URL and rerun. A network error is not proof of a crawler block.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    message = summary(report)
    print(message)
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as target:
            target.write(message + '\n')
    if not report['passed']:
        print('::error title=Live robots.txt policy mismatch::' + report['issues'][0]['message'])
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
