"""Execute published-workflow version resolution against the official helper."""
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def resolution_shell(requested):
    """Read the actual workflow block, including its previous fixed-version form."""
    workflow = (ROOT / '.github/workflows/published.yml').read_text()
    name = ('Resolve published application version'
            if 'name: Resolve published application version' in workflow
            else 'Verify published assets and install actual public formula')
    step = workflow.split('      - name: ' + name + '\n', 1)[1]
    step = step.split('\n      - ', 1)[0]
    shell = textwrap.dedent(step.split('        run: |\n', 1)[1])
    # The original block also installed Homebrew; execute only its setup prefix.
    shell = shell.split('python3 -m unittest discover', 1)[0]
    environment = {'REQUESTED_VERSION': requested}
    previous = re.search(r"RELEASE_VERSION: \$\{\{ inputs.version \|\| '([^']+)' \}\}", step)
    if previous:
        environment['RELEASE_VERSION'] = requested or previous[1]
        shell += '\nprintf "RELEASE_VERSION=%s\\n" "$RELEASE_VERSION" >> "$GITHUB_ENV"\n'
    return shell, environment


class PublishedVersionTests(unittest.TestCase):
    def execute(self, requested):
        source = pathlib.Path(os.environ.get('PUBLISHED_TEST_APPLICATION', ROOT / 'application'))
        helper = source / 'scripts/release.py'
        self.assertTrue(helper.is_file(), 'Check out the application or set PUBLISHED_TEST_APPLICATION')
        shell, values = resolution_shell(requested)
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            scripts = root / 'application/scripts'; scripts.mkdir(parents=True)
            shutil.copyfile(helper, scripts / 'release.py')
            (root / 'application/VERSION').write_text('2.0.1\n')
            environment = {key: value for key, value in os.environ.items() if not key.startswith('AWS_')}
            environment.update(values, HOME=str(root / 'home'), RUNNER_TEMP=str(root), GITHUB_ENV=str(root / 'environment'))
            script = root / 'resolution.sh'; script.write_text(shell)
            subprocess.run(['/bin/bash', '-n', str(script)], check=True, timeout=10)
            result = subprocess.run(['/bin/bash', str(script)], cwd=root, env=environment,
                                    capture_output=True, text=True, timeout=10)
            exported = (root / 'environment').read_text() if (root / 'environment').exists() else ''
            return result, exported

    def test_automatic_formula_push_uses_checked_out_next_version(self):
        result, exported = self.execute('')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(exported, 'RELEASE_VERSION=2.0.1\n')

    def test_matching_manual_version_preserves_checked_out_version(self):
        result, exported = self.execute('2.0.1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(exported, 'RELEASE_VERSION=2.0.1\n')

    def test_mismatched_manual_version_fails_before_export(self):
        result, exported = self.execute('2.0.0')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(exported, '')


if __name__ == '__main__':
    unittest.main()
