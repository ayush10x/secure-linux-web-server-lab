# Verification evidence

Validation completed on 10 October 2026 (Asia/Kolkata). These are selected, sanitized results observed on the actual guests, rather than simulated outputs. Earlier logs used the paused guest's stale 9 October UTC clock; time was corrected before the final package refresh and reboot.

## Final recovery and Client reboot check

Live snapshotting stalled. After explicit approval for hard-reset recovery, a cold restart restored both guests. Powered-off snapshots succeeded (details in the action log). Client reboot exposed early networkd DHCP adoption; the scoped NetworkManager startup fix in `config/90-lab-client-network.conf` was installed, profile priority corrected, and another Client reboot was tested:

```text
enp0s9 UP 192.168.56.201/24
PASS: HTTP 200
PASS: Missing page returns 404
PASS: Dotfile path returns 403
PASS: Administrator key login works
PASS: Root SSH denied
PASS: Regular account SSH denied
PASS: Password-only SSH denied
Failures: 0
final_verifier_exit=0
```

Server health checks all passed again, including Nginx, SSH, UFW, local HTTP and filesystem usage (34%). `dpkg --audit` was empty and `systemctl --failed` showed zero failed units on both guests after cold recovery. These checks are not a full offline filesystem scan. Kernel error-level logs included VirtualBox display/PCI messages; a completely error-free kernel log is not claimed. Both guests were left running headlessly.

## Client web and key access

Client private interface: `enp0s9 192.168.56.201/24`.

```text
curl -I http://192.168.56.200/
HTTP/1.1 200 OK
Server: nginx/1.28.3 (Ubuntu)
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin

ssh -o BatchMode=yes -i ~/.ssh/server_ayush ayush@192.168.56.200 'whoami; hostname'
ayush
kapserver
key_login_exit=0
```

A fresh key session ran `sudo -v && sudo whoami` and returned `root`. This verified sudo without altering sudo policy.

## Negative SSH tests

```text
root@192.168.56.200: Permission denied (publickey).
root_denial_exit=255
password_denial_exit=255
webuser@192.168.56.200: Permission denied (publickey).
regular_account_denial_exit=255
```

Password-only test: `ssh -o BatchMode=yes -o PubkeyAuthentication=no -o PreferredAuthentications=password ayush@192.168.56.200 true`. No password guessing was used for this test. Positive key access was verified alongside these denials.

Effective Server configuration:

```text
permitrootlogin no
passwordauthentication no
kbdinteractiveauthentication no
allowusers ayush
```

## Firewall and logs

```text
Status: active
Logging: on (medium)
Default: deny (incoming), allow (outgoing), disabled (routed)
22/tcp ALLOW IN 192.168.56.201
80/tcp ALLOW IN 192.168.56.0/24

Mac host: nc -G 3 -zv 192.168.56.200 22
Operation timed out (exit 1)
```

Reviewed log selections:

```text
SSH: User root from 192.168.56.201 not allowed because not listed in AllowUsers
SSH: User webuser from 192.168.56.201 not allowed because not listed in AllowUsers
UFW: BLOCK SRC=192.168.56.1 DST=192.168.56.200 PROTO=TCP DPT=22
Nginx: 192.168.56.201 "HEAD / HTTP/1.1" 200
Nginx: 192.168.56.201 "GET /lab-validation-missing HTTP/1.1" 404
```

Nginx evidence came from `/var/log/nginx/lab-site.access.log`. Service journal entries showed accepted Client public keys and denied accounts. The public key fingerprint and raw machine identifiers are unnecessary for this proof and are omitted.

## Health, permissions, and recovery

```text
PASS: Nginx is active
PASS: Nginx is enabled
PASS: SSH is active
PASS: UFW is active
PASS: Local website returns HTTP 200
PASS: Site configuration is valid
PASS: Root filesystem usage is 34%
health_exit=0

750 root:www-data /var/www/lab-site
640 root:www-data /var/www/lab-site/index.html
700 ayush:ayush /home/ayush/.ssh
600 ayush:ayush /home/ayush/.ssh/authorized_keys

sha256sum -c /var/backups/lab-site/lab-site-20261009-092128.tar.gz.sha256
/var/backups/lab-site/lab-site-20261009-092128.tar.gz: OK
restore_diff_exit=0
```

The archive was extracted under a directory created by `mktemp -d /tmp/lab-restore.XXXXXX`, then compared using `diff -ru`. The live site was not overwritten during this recovery check.

## Reboot and patch validation

```text
post_reboot_http=200
kapserver
uptime: up 0 min
kernel: 7.0.0-38-generic
post_reboot_key_exit=0
post_reboot_root_denial=255
post_reboot_password_denial=255
package_update_exit=0
0 upgraded, 0 newly installed, 0 to remove and 4 not upgraded.
```

The four deferred packages were `libopeniscsiusr`, `open-iscsi`, `python3-software-properties`, and `software-properties-common`, deferred by phasing. `dpkg --audit` was empty. HTTP initially failed during boot, then returned 200; the test waited for service startup rather than treating the first transient boot failure as the final result.

GitHub CI proves repository syntax/lint checks only. It does not certify the VM firewall, SSH, backup, or reboot behavior; those were observed in this local lab.
