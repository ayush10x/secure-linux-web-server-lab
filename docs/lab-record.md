# Lab record

Fill this out with observations from your own VMs. Leave secrets out of GitHub.

| Field | Server VM | Client VM |
|---|---|---|
| VirtualBox name | `ubunutu server` | `ubuntu 26.04 ` (confirm) |
| Ubuntu version | Ubuntu 26.04 LTS ARM64; installer reported complete and VM booted from disk | Existing Ubuntu desktop installation reached its login screen in a headless boot; guest version not yet checked |
| Hostname | `kapserver` (observed at tty1) | Pending |
| NAT IP | `10.0.2.15/24` on `enp0s8` | Pending |
| Host-only IP | Static `192.168.56.200/24` on `enp0s9`, verified by host ping and HTTP 200 | `192.168.56.2`, observed by host ARP/ping/SSH probe; guest confirmation pending |
| Host-only network | `HostNetwork` | `HostNetwork` |
| Administrator account | `ayush`, confirmed in `sudo` group with `id` | Login screen lists `ayush`; SSH login pending |
| Regular account | `webuser`, no sudo membership, password locked | N/A |
| Snapshot name/date | `clean-install`, 2026-10-09 (UUID `033862de-0f8f-480f-a849-acccfd2622ee`) | Pending |

## Acceptance results

| Test | Result | Evidence |
|---|---|---|
| Server package installation | Pass | Install script completed; Nginx and SSH enabled |
| Nginx syntax and local HTTP | Pass | `nginx -t` succeeded; local and host-only HTTP returned 200 |
| Client to server HTTP | Not run | |
| Approved SSH key and sudo | Not run | |
| Root/password SSH denied | Not run | |
| Default-deny UFW with narrow rules | Not run | |
| Reboot persistence | Not run | |
| Backup creation and temporary restoration | Pass | Archive created, extracted under `/tmp/lab-restore-check`, `diff -ru` returned no differences |

The health check currently reports UFW inactive, as expected before Client key access and firewall rules are validated. Do not mark its overall result passed yet. The Client boots headlessly with 2 virtual CPUs, but its GUI launch still stalls; SSH is reachable on its host-only address.

Do not mark a test passed until it has run on the named VMs.
