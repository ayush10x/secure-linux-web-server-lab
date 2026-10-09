# Lab record

Fill this out with observations from your own VMs. Leave secrets out of GitHub.

| Field | Server VM | Client VM |
|---|---|---|
| VirtualBox name | `ubunutu server` | `ubuntu 26.04 ` (confirm) |
| Ubuntu version | Ubuntu 26.04 LTS ARM64; installer reported complete and VM booted from disk | Pending guest boot/login; start attempt returned to powered off |
| Hostname | `kapserver` (observed at tty1) | Pending |
| NAT IP | Pending | Pending |
| Host-only IP | Installer DHCP observed `192.168.56.3/24`; post-install confirmation pending | Pending |
| Host-only network | `HostNetwork` | `HostNetwork` |
| Administrator account | Installer profile completed by user; username not yet confirmed in the record | N/A |
| Snapshot name/date | `clean-install`, 2026-10-09 (UUID `033862de-0f8f-480f-a849-acccfd2622ee`) | Pending |

## Acceptance results

| Test | Result | Evidence |
|---|---|---|
| Server package installation | Not run | |
| Nginx syntax and local HTTP | Not run | |
| Client to server HTTP | Not run | |
| Approved SSH key and sudo | Not run | |
| Root/password SSH denied | Not run | |
| Default-deny UFW with narrow rules | Not run | |
| Reboot persistence | Not run | |
| Backup creation and temporary restoration | Not run | |

Do not mark a test passed until it has run on the named VMs.
