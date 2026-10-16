"""Offline regression fixtures, not tests against a real SSH daemon or VM."""
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOCK = r'''#!/usr/bin/env python3
import os, sys
from pathlib import Path
tool = Path(sys.argv[0]).name
args = sys.argv[1:]
if os.getenv('REQUIRE_C_LOCALE') and os.getenv('LC_ALL') != 'C':
    print('Expected C locale', file=sys.stderr)
    sys.exit(98)
if tool == 'curl':
    url = args[-1]
    status = '404' if url.endswith('/lab-validation-missing') else '403' if url.endswith('/.git/config') else os.getenv('HTTP_STATUS', '200')
    print(status, end='')
    sys.exit(int(os.getenv('CURL_EXIT', '0')))
if tool == 'ssh':
    target = next(x for x in args if '@' in x)
    username = target.split('@')[0]
    if username not in ('root', 'webuser') and username != os.getenv('EXPECTED_ADMIN', 'labadmin'):
        print('Unexpected administrator target', file=sys.stderr)
        sys.exit(99)
    if 'PubkeyAuthentication=no' in args:
        offered = os.getenv('OFFERED_METHODS', 'publickey')
        print('debug1: Authentications that can continue: ' + offered, file=sys.stderr)
        print(username + '@server: Permission denied (' + offered + ').', file=sys.stderr)
        sys.exit(255)
    if any(x.startswith(('root@', 'webuser@')) for x in args):
        failure = os.getenv('DENIAL', 'auth')
        print({'auth': 'user@server: Permission denied (publickey).',
               'timeout': 'ssh: connect to host server port 22: Connection timed out',
               'hostkey': 'Host key verification failed.'}[failure], file=sys.stderr)
        sys.exit(255)
    if args[-1] == 'id -un':
        print(os.getenv('REMOTE_USER', username))
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

    def run_script(self, name, admin_user=None, **settings):
        env = os.environ.copy()
        env.update(settings)
        env['PATH'] = str(self.bin) + os.pathsep + env['PATH']
        args = ['bash', str(ROOT / 'scripts' / name), '192.168.56.200', str(self.key)]
        if admin_user is not None:
            args.append(admin_user)
        return subprocess.run(args,
                              env=env, capture_output=True, text=True, timeout=10)

    def test_secure_fixture_passes(self):
        result = self.run_script('verify-security.sh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_or_octal_ipv4_addresses_are_rejected(self):
        for bad_ip in ('999.168.56.200', '192.168.56.256', '192.168.056.200', '010.0.0.1'):
            for script in ('verify-client.sh', 'verify-security.sh'):
                with self.subTest(script=script, bad_ip=bad_ip):
                    env = os.environ.copy()
                    env['PATH'] = str(self.bin) + os.pathsep + env['PATH']
                    result = subprocess.run(
                        ['bash', str(ROOT / 'scripts' / script), bad_ip, str(self.key)],
                        env=env, capture_output=True, text=True, timeout=10,
                    )
                    self.assertEqual(result.returncode, 64)

    def test_password_enabled_is_not_a_pass(self):
        for methods in ('publickey,password', 'publickey,keyboard-interactive'):
            with self.subTest(methods=methods):
                self.assertNotEqual(self.run_script('verify-security.sh', OFFERED_METHODS=methods).returncode, 0)

    def test_custom_administrator_is_used_for_all_ssh_probes(self):
        result = self.run_script('verify-security.sh', admin_user='operator', EXPECTED_ADMIN='operator')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.run_script('verify-security.sh', admin_user='operator', EXPECTED_ADMIN='operator', OFFERED_METHODS='publickey,password')
        self.assertNotEqual(result.returncode, 0)

    def test_unexpected_authenticated_account_fails(self):
        result = self.run_script('verify-security.sh', REMOTE_USER='someone_else')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('negative SSH checks skipped', result.stderr)

    def test_invalid_or_probe_accounts_are_rejected(self):
        for username in ('root', 'webuser', '-option', 'user@host', 'user;id'):
            with self.subTest(username=username):
                self.assertEqual(self.run_script('verify-security.sh', admin_user=username).returncode, 64)

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

    def test_verifiers_force_c_locale(self):
        for script in ('health-check.sh', 'verify-client.sh', 'verify-security.sh'):
            with self.subTest(script=script):
                result = self.run_script(script, LC_ALL='POSIX', REQUIRE_C_LOCALE='1')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class BackupTests(unittest.TestCase):
    """Offline filesystem fixture; no sudo, guest access, or real backup paths.

    Substitute only paths and the root guard in a temporary script copy.
    Mock install ownership and date; use real tar and filesystem operations.
    This checks permissions/retention logic, not deployment or root ownership.
    """

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'site'
        self.source.mkdir()
        (self.source / 'index.html').write_text('offline backup fixture\n')
        self.backups = self.root / 'backups'
        self.backups.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        helpers = {
            'date': '#!/usr/bin/env python3\nprint("20261016-120000")\n',
            'install': '''#!/usr/bin/env python3
import os, sys
os.makedirs(sys.argv[-1], exist_ok=True)
os.chmod(sys.argv[-1], 0o700)
''',
            'sha256sum': '''#!/usr/bin/env python3
import hashlib, pathlib, sys
path = pathlib.Path(sys.argv[1])
print(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + str(path))
''',
        }
        for name, code in helpers.items():
            path = self.bin / name
            path.write_text(code)
            path.chmod(0o755)
        script = (ROOT / 'scripts/backup-site.sh').read_text()
        for original, replacement in (
            ('source_dir="/var/www/lab-site"', f'source_dir="{self.source}"'),
            ('backup_dir="/var/backups/lab-site"', f'backup_dir="{self.backups}"'),
            ('if [[ $EUID -ne 0 ]]; then', 'if false; then'),
        ):
            self.assertEqual(script.count(original), 1)
            script = script.replace(original, replacement, 1)
        self.script = self.root / 'backup-fixture.sh'
        self.script.write_text(script)
        self.archive = self.backups / 'lab-site-20261016-120000.tar.gz'

    def run_backup(self):
        env = os.environ.copy()
        env['PATH'] = str(self.bin) + os.pathsep + env['PATH']
        return subprocess.run(['bash', str(self.script)], env=env,
                              capture_output=True, text=True, timeout=10)

    def test_backup_retains_ten_pairs_and_private_permissions(self):
        for day in range(1, 13):
            archive = self.backups / f'lab-site-202610{day:02d}-120000.tar.gz'
            archive.write_text('older fixture')
            Path(str(archive) + '.sha256').write_text('older checksum')
        unrelated = self.backups / 'keep.txt'
        unrelated.write_text('keep')
        result = self.run_backup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        archives = sorted(self.backups.glob('lab-site-*.tar.gz'))
        self.assertEqual(len(archives), 10)
        self.assertEqual(archives[0].name, 'lab-site-20261004-120000.tar.gz')
        self.assertEqual(len(list(self.backups.glob('*.sha256'))), 10)
        self.assertTrue(unrelated.exists())
        for path in (self.archive, Path(str(self.archive) + '.sha256')):
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.backups.stat().st_mode & 0o777, 0o700)
        listed = subprocess.run([shutil.which('tar'), '-tzf', str(self.archive)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn('index.html', listed.stdout)

    def test_archive_or_checksum_collision_preserves_existing_file(self):
        for suffix in ('', '.sha256'):
            with self.subTest(suffix=suffix):
                collision = Path(str(self.archive) + suffix)
                collision.write_text('must not overwrite')
                result = self.run_backup()
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertEqual(collision.read_text(), 'must not overwrite')
                collision.unlink()


if __name__ == '__main__':
    unittest.main()
