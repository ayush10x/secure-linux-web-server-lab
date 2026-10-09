# Lab record

Fill this out with observations from your own VMs. Leave secrets out of GitHub.

| Field | Server VM | Client VM |
|---|---|---|
| VirtualBox name | `ubunutu server` | `ubuntu 26.04 ` (confirm) |
| Ubuntu version | Ubuntu 26.04 ARM64 installer in progress; installed version pending | Pending guest login |
| Hostname | Pending | Pending |
| NAT IP | Pending | Pending |
| Host-only IP | Installer DHCP observed `192.168.56.3/24`; post-install confirmation pending | Pending |
| Host-only network | `HostNetwork` | `HostNetwork` |
| Administrator account | Installer profile completed by user; username not yet confirmed in the record | N/A |
| Snapshot name/date | Pending | Pending |

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
