"""Offline regression fixtures, not tests against a real SSH daemon or VM."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOCK = r'''#!/usr/bin/env python3
import os, sys
from pathlib import Path
tool = Path(sys.argv[0]).name
args = sys.argv[1:]
if tool == 'curl':
    url = args[-1]
    status = '404' if url.endswith('/lab-validation-missing') else '403' if url.endswith('/.git/config') else os.getenv('HTTP_STATUS', '200')
    print(status, end='')
    sys.exit(int(os.getenv('CURL_EXIT', '0')))
if tool == 'ssh':
    if 'PubkeyAuthentication=no' in args:
        offered = os.getenv('OFFERED_METHODS', 'publickey')
        print('debug1: Authentications that can continue: ' + offered, file=sys.stderr)
        print('ayush@server: Permission denied (' + offered + ').', file=sys.stderr)
        sys.exit(255)
    if any(x.startswith(('root@', 'webuser@')) for x in args):
        failure = os.getenv('DENIAL', 'auth')
        print({'auth': 'user@server: Permission denied (publickey).',
               'timeout': 'ssh: connect to host server port 22: Connection timed out',
               'hostkey': 'Host key verification failed.'}[failure], file=sys.stderr)
        sys.exit(255)
    sys.exit(int(os.getenv('ADMIN_EXIT', '0')))
if tool == 'ufw': print('Status: active')
if tool == 'df': print('Filesystem 1024-blocks Used Available Capacity Mounted on\n/dev/root 100 34 66 34% /')
sys.exit(0)
'''


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.bin = Path(self.temp.name)
        for tool in ('curl', 'ssh', 'ping', 'ufw', 'systemctl', 'nginx', 'df'):
            path = self.bin / tool
            path.write_text(MOCK)
            path.chmod(0o755)
        self.key = self.bin / 'fixture-key'
        self.key.touch()  # Empty placeholder; never an actual private key.

    def run_script(self, name, **settings):
        env = os.environ.copy()
        env.update(settings)
        env['PATH'] = str(self.bin) + os.pathsep + env['PATH']
        return subprocess.run(['bash', str(ROOT / 'scripts' / name),
                               '192.168.56.200', str(self.key)],
                              env=env, capture_output=True, text=True, timeout=10)

    def test_secure_fixture_passes(self):
        result = self.run_script('verify-security.sh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_password_enabled_is_not_a_pass(self):
        for methods in ('publickey,password', 'publickey,keyboard-interactive'):
            with self.subTest(methods=methods):
                self.assertNotEqual(self.run_script('verify-security.sh', OFFERED_METHODS=methods).returncode, 0)

    def test_transport_and_hostkey_failures_are_not_denials(self):
        for failure in ('timeout', 'hostkey'):
            with self.subTest(failure=failure):
                self.assertNotEqual(self.run_script('verify-security.sh', DENIAL=failure).returncode, 0)

    def test_failed_positive_login_skips_negative_tests(self):
        result = self.run_script('verify-security.sh', ADMIN_EXIT='255')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('negative SSH checks skipped', result.stderr)
        self.assertNotIn('PASS: Root SSH', result.stdout)

    def test_health_and_client_require_exact_200(self):
        for script in ('health-check.sh', 'verify-client.sh'):
            for status in ('200', '204', '302', '500'):
                with self.subTest(script=script, status=status):
                    result = self.run_script(script, HTTP_STATUS=status)
                    self.assertEqual(result.returncode == 0, status == '200', result.stdout + result.stderr)

    def test_curl_transport_failure_fails(self):
        for script in ('health-check.sh', 'verify-client.sh', 'verify-security.sh'):
            with self.subTest(script=script):
                self.assertNotEqual(self.run_script(script, CURL_EXIT='7').returncode, 0)


if __name__ == '__main__':
    unittest.main()
