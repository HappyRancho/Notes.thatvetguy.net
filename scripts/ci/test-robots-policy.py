#!/usr/bin/env python3
"""Regression cases for the actual production-only Cloudflare injection failure."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('robots_policy', ROOT / 'scripts/ci/check-live-robots.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class RobotsPolicyTests(unittest.TestCase):
    def setUp(self):
        self.expected = (ROOT / 'robots.txt').read_text()

    def test_original_site_policy_passes(self):
        self.assertTrue(policy.inspect(self.expected, self.expected)['passed'])

    def test_cloudflare_production_prefix_fails_with_actionable_cause(self):
        prefix = ('# BEGIN Cloudflare Managed content\nUser-agent: *\n'
                  'Content-Signal: search=yes,ai-train=no,use=reference\nAllow: /\n'
                  'User-agent: GPTBot\nDisallow: /\n# END Cloudflare Managed Content\n')
        report = policy.inspect(self.expected, prefix + self.expected)
        self.assertFalse(report['passed'])
        self.assertTrue(report['cloudflareManaged'])
        self.assertIn('unrecognised-directive', [i['code'] for i in report['issues']])
        self.assertIn('Enable Bot Preference Sync', policy.summary({**report, 'url': policy.PUBLIC_URL}))

    def test_missing_sitemap_is_not_ignored(self):
        actual = '\n'.join(l for l in self.expected.splitlines() if not l.startswith('Sitemap:'))
        self.assertIn('missing-sitemap', [i['code'] for i in policy.inspect(self.expected, actual)['issues']])

    def test_changed_bot_or_global_policy_fails(self):
        for actual in [self.expected.replace('Allow: /', 'Disallow: /', 1), self.expected + '\nUser-agent: GPTBot\nDisallow: /\n']:
            self.assertFalse(policy.inspect(self.expected, actual)['passed'])

    def test_comments_bom_line_endings_and_user_agent_case_are_not_errors(self):
        actual = '\ufeff# Plain-text origin policy\r\n' + self.expected.replace('User-agent:', 'USER-AGENT:').replace('GPTBot', 'gptbot').replace('\n', '\r\n')
        self.assertTrue(policy.inspect(self.expected, actual)['passed'])

    def test_html_challenge_cannot_look_like_a_pass(self):
        report = policy.inspect(self.expected, '<html>Challenge</html>', 'text/html')
        self.assertFalse(report['passed'])
        self.assertIn('not-plain-text', [i['code'] for i in report['issues']])


if __name__ == '__main__':
    unittest.main()
