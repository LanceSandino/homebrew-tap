"""Offline regressions for scoped tag API authentication and redirect privacy."""
import ast
import fnmatch
import importlib.util
import io
import os
import pathlib
import re
import unittest
from unittest import mock
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('published_http', ROOT / 'scripts/published.py')
published = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(published)
TOKEN = 'synthetic-ephemeral-ci-token'
API = 'https://api.github.com/repos/LanceSandino/aws-sso-profile-sync/git/'


def headers(request):
    return {name.lower(): value for name, value in request.header_items()}


class PublishedHTTPTests(unittest.TestCase):
    def test_documentation_changes_trigger_both_published_workflow_events(self):
        workflow = (ROOT / '.github/workflows/published.yml').read_text()
        changed = ('README.md', 'docs/aws-sso-profile-sync.md', 'docs/guides/new-tool.md')
        for event in ('pull_request', 'push'):
            block = re.search(r'^  ' + event + r':\n((?:    .*\n)+)', workflow, re.MULTILINE)
            self.assertIsNotNone(block, event)
            expression = re.search(r'^\s+paths:\s*(\[.*\])\s*$', block[1], re.MULTILINE)
            self.assertIsNotNone(expression, event)
            patterns = ast.literal_eval(expression[1])
            self.assertIn('README.md', patterns, event)
            self.assertIn('docs/**', patterns, event)
            for path in changed:
                with self.subTest(event=event, path=path):
                    self.assertTrue(any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns),
                                    'Documentation change would not trigger published validation')

    def test_verifier_changes_trigger_both_published_workflow_events(self):
        workflow = (ROOT / '.github/workflows/published.yml').read_text()
        changed = ('Formula/aws-sso-profile-sync.rb', '.github/workflows/published.yml',
                   'scripts/published.py', pathlib.Path(__file__).relative_to(ROOT).as_posix())
        for event in ('pull_request', 'push'):
            block = re.search(r'^  ' + event + r':\n((?:    .*\n)+)', workflow, re.MULTILINE)
            self.assertIsNotNone(block, event)
            expression = re.search(r'^\s+paths:\s*(\[.*\])\s*$', block[1], re.MULTILINE)
            self.assertIsNotNone(expression, event)
            patterns = ast.literal_eval(expression[1])
            for path in changed:
                with self.subTest(event=event, path=path):
                    self.assertTrue(any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns),
                                    'Verifier change would not trigger published validation')

    def request(self, url, token=TOKEN):
        opener = mock.Mock()
        opener.open.return_value = io.BytesIO(b'{}')
        with mock.patch.dict(os.environ, {'PUBLISHED_GITHUB_TOKEN': token}), \
                mock.patch.object(published.urllib.request, 'build_opener', return_value=opener):
            self.assertEqual(published.download(url, 1024), b'{}')
        opener.open.assert_called_once()
        request = opener.open.call_args.args[0]
        self.assertEqual(opener.open.call_args.kwargs, {'timeout': 30})
        return request

    def test_token_is_scoped_to_exact_canonical_tag_api_requests(self):
        for url in (API + 'ref/tags/v2.0.0', API + 'ref/tags/v2.0.1', API + 'tags/' + 'a' * 40,
                    API.replace('api.github.com/', 'api.github.com:443/') + 'ref/tags/v2.0.0'):
            with self.subTest(url=url):
                self.assertEqual(headers(self.request(url)).get('authorization'), 'Bearer ' + TOKEN)

    def test_assets_other_routes_and_absent_token_remain_anonymous(self):
        urls = [API + 'ref/tags/v02.0.0', API + 'ref/tags/v2.0.0-rc.1', API + 'ref/tags/v2.0.0+build',
                API + 'ref/tags/v2.0.0?extra=1', API + 'ref/tags/v2.0.0?', API + 'ref/tags/v2.0.0#fragment',
                API + 'ref/tags/v2.0.0/', API + 'tags/' + 'A' * 40, API + 'tags/' + 'a' * 39,
                API.replace('LanceSandino/', 'OtherOwner/') + 'ref/tags/v2.0.0',
                'https://api.github.com/user', 'https://github.com/LanceSandino/aws-sso-profile-sync/releases/download/v2.0.0/SHA256SUMS',
                'https://release-assets.githubusercontent.com/archive', 'https://objects.githubusercontent.com/archive']
        for url in urls:
            with self.subTest(url=url):
                self.assertNotIn('authorization', headers(self.request(url)))
        self.assertNotIn('authorization', headers(self.request(API + 'ref/tags/v2.0.0', token='')))

    def test_absent_scoped_token_ignores_other_token_variables(self):
        opener = mock.Mock(); opener.open.return_value = io.BytesIO(b'{}')
        with mock.patch.dict(os.environ, {'GITHUB_TOKEN': TOKEN, 'GH_TOKEN': TOKEN}, clear=True), \
                mock.patch.object(published.urllib.request, 'build_opener', return_value=opener):
            self.assertEqual(published.download(API + 'ref/tags/v2.0.0', 1024), b'{}')
        self.assertNotIn('authorization', headers(opener.open.call_args.args[0]))

    def test_forbidden_origin_is_rejected_before_opener_creation(self):
        for url in ('https://api.github.com.evil.invalid/tag', 'http://api.github.com/tag',
                    API.replace('api.github.com', 'userinfo@api.github.com') + 'ref/tags/v2.0.0',
                    API.replace('api.github.com', 'api.github.com:8443') + 'ref/tags/v2.0.0',
                    'https://example.invalid/tag'):
            with self.subTest(url=url), mock.patch.object(published.urllib.request, 'build_opener') as opener:
                with self.assertRaises(ValueError):
                    published.download(url, 1024)
                opener.assert_not_called()

    def test_all_redirects_strip_authorization_and_proxy_authorization(self):
        for target in (API + 'tags/' + 'a' * 40, API + 'ref/tags/v2.0.0',
                       'https://github.com/archive', 'https://release-assets.githubusercontent.com/archive',
                       'https://objects.githubusercontent.com/archive'):
            with self.subTest(target=target):
                original = urllib.request.Request(API + 'ref/tags/v2.0.0', headers={
                    'Authorization': 'Bearer ' + TOKEN, 'Proxy-Authorization': 'Basic synthetic-proxy',
                    'User-Agent': 'synthetic-agent'})
                original.add_unredirected_header('Authorization', 'Bearer ' + TOKEN)
                original.add_unredirected_header('Proxy-Authorization', 'Basic synthetic-proxy')
                redirected = published.GitHubRedirects().redirect_request(original, None, 302, 'Found', {}, target)
                self.assertEqual(redirected.full_url, target)
                self.assertNotIn('authorization', headers(redirected))
                self.assertNotIn('proxy-authorization', headers(redirected))
                self.assertEqual(headers(redirected)['user-agent'], 'synthetic-agent')

    def test_forbidden_redirect_is_rejected_before_following(self):
        original = urllib.request.Request(API + 'ref/tags/v2.0.0', headers={'Authorization': 'Bearer ' + TOKEN})
        with mock.patch.object(urllib.request.HTTPRedirectHandler, 'redirect_request') as follow:
            with self.assertRaises(ValueError):
                published.GitHubRedirects().redirect_request(original, None, 302, 'Found', {}, 'https://example.invalid/tag')
            follow.assert_not_called()

    def test_download_failures_never_echo_token(self):
        failures = [urllib.error.HTTPError(API + 'ref/tags/v2.0.0', 403, TOKEN, {}, None),
                    urllib.error.URLError(TOKEN), ValueError('invalid header ' + TOKEN)]
        for failure in failures:
            opener = mock.Mock(); opener.open.side_effect = failure
            with self.subTest(failure=type(failure).__name__), \
                    mock.patch.dict(os.environ, {'PUBLISHED_GITHUB_TOKEN': TOKEN}), \
                    mock.patch.object(published.urllib.request, 'build_opener', return_value=opener):
                with self.assertRaises(Exception) as caught:
                    published.download(API + 'ref/tags/v2.0.0', 1024)
                self.assertNotIn(TOKEN, str(caught.exception))
                opener.open.assert_called_once()

    def test_download_size_bound_is_unchanged(self):
        opener = mock.Mock(); opener.open.return_value = io.BytesIO(b'12345')
        with mock.patch.object(published.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaisesRegex(ValueError, 'size bound'):
                published.download(API + 'ref/tags/v2.0.0', 4)


if __name__ == '__main__':
    unittest.main()
