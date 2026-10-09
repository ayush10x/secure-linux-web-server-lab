# Lab record

Verified on the actual local VMs; completed 10 October 2026 (Asia/Kolkata). See [selected command evidence](verification-evidence.md).

| Field | Server VM | Client VM |
|---|---|---|
| VirtualBox name | `ubunutu server` | `ubuntu 26.04 ` (trailing space) |
| Ubuntu version | Ubuntu 26.04 LTS ARM64, kernel `7.0.0-38-generic` | Ubuntu 26.04 LTS ARM64, kernel `7.0.0-27-generic` |
| Hostname | `kapserver` | `ubuntu26` |
| NAT IP | `10.0.2.15/24` on `enp0s8` | `10.0.2.15/24` on `enp0s8`, separate NAT instance |
| Host-only IP | Static `192.168.56.200/24` on `enp0s9` | Static `192.168.56.201/24` on `enp0s9`, NetworkManager |
| Host-only network | `HostNetwork` | `HostNetwork` |
| Administrator account | `ayush`, sudo verified in a fresh Client key session | `ayush`, successful SSH and sudo |
| Regular account | `webuser`, no sudo membership, password locked | N/A |
| Recovery baseline | `clean-install`, 2026-10-09 | Existing disk preserved |

## Acceptance results

| Test | Result | Evidence |
|---|---|---|
| Server package installation | Pass | Install script completed; Nginx and SSH enabled |
| Nginx syntax and local HTTP | Pass | `nginx -t` succeeded; local and host-only HTTP returned 200 |
| Client to server HTTP | Pass | HTTP 200, missing page 404, dotfile path 403 |
| Approved SSH key and sudo | Pass | Client Ed25519 login returned `ayush`; sudo returned `root` |
| Root/password SSH denied | Pass | Exit 255 before and after final Server reboot; `webuser` also denied |
| Default-deny UFW with narrow rules | Pass | Client SSH allowed; Mac-host SSH timed out and UFW block logged |
| Reboot persistence | Pass | Client HTTP 200 and fresh key session after Server reboot; UFW and health remained valid |
| Backup creation and temporary restoration | Pass | Archive created, extracted under `/tmp/lab-restore-check`, `diff -ru` returned no differences |
| Backup checksum | Pass | SHA-256 check of the later archive reported OK |
| Health check | Pass | All checks pass, exit 0, including after reboot |
| Reproducible security verifier | Pass | `scripts/verify-security.sh` ran on Client with zero failures |
| Logs | Pass | SSH account denials, UFW block, and Nginx 200/404 entries reviewed |
| Package audit | Pass | APT refresh/upgrade exit 0; `dpkg --audit` empty; four updates deferred by phasing |

The Client boots headlessly with 2 CPUs and is administered over SSH; its GUI launch issue remains. Server SSH accepts only the authorized Client source and key. Passwords and private keys are excluded from this record.

The tested recovery is a site-content restoration into a temporary directory, not a full-VM disaster recovery. HTTP is private-lab only. Chrony was restarted after correcting stale guest time; monitor time synchronization after prolonged VM pauses.
