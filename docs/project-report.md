# Secure Linux Web Server - Project Report

**Owner:** Ayush Kaushik  
**Validation completed:** 10 October 2026, Asia/Kolkata  
**Project type:** Assisted, private-network Linux administration lab

## Executive summary

Two Ubuntu 26.04 ARM64 VMs run in VirtualBox on an Apple M2 Pro. The Server hosts a static Nginx site and permits administration through a dedicated Ed25519 key from the Client. UFW applies default-deny inbound policy, with SSH restricted to the Client's fixed private address and HTTP restricted to the lab subnet.

Positive and negative access tests were recorded. The site and key access survived reboot; denied account probes, effective SSH settings and journal events support the policy. The original password-only BatchMode probe alone did not prove password authentication was disabled. The health check passed, a SHA-256 archive check succeeded, and an extracted backup matched the live site. CI checks Bash files and offline regression fixtures; local VM tests have a separate evidence record.

## Design

| Component | Server | Client |
|---|---|---|
| Hostname | `kapserver` | `ubuntu26` |
| OS | Ubuntu 26.04 LTS ARM64 | Ubuntu 26.04 LTS ARM64 |
| CPUs / memory | 2 / 3 GB | 2 / about 4.4 GB |
| Virtual disk | 25 GB | 25 GB, preserved existing installation |
| Private IPv4 | `192.168.56.200/24` | `192.168.56.201/24` |
| Internet access | NAT, DHCP | NAT, DHCP |
| Private network | VirtualBox `HostNetwork` | Same host-only network |

Both private addresses are outside the DHCP pool ending at `.199`. The Server uses Netplan; the Client uses NetworkManager for its host-only connection. The Mac host is `.1` and is intentionally excluded from Server SSH. Both guests can show the same NAT address because they have separate NAT instances.

## Implementation and decisions

**Accounts and permissions.** `ayush` is the named sudo administrator. `webuser` has only its own group and a locked password. The site directory is `0750 root:www-data`, and the HTML file is `0640 root:www-data`; the Nginx worker can read the site without write access.

**Web service.** Nginx serves `/var/www/lab-site` on port 80. A dedicated virtual host writes `lab-site.access.log` and `lab-site.error.log`, blocks dotfile paths, and adds content-type, frame, and referrer headers. Syntax was checked before reload, and systemd enables startup after reboot.

**SSH.** A dedicated Client key is stored in the Client's home directory. Only the public key was installed on the Server. Key login and sudo were proven before disabling passwords. `00-lab-hardening.conf` precedes Ubuntu's `50-cloud-init.conf`, because OpenSSH uses the first obtained value for these settings. The effective configuration has `PermitRootLogin no`, `PasswordAuthentication no`, and `AllowUsers ayush`.

**Firewall.** UFW denies inbound traffic by default and permits outbound traffic. Its two explicit inbound rules allow TCP 22 from `.201` and TCP 80 from `192.168.56.0/24`. A new Client key session still worked; a new Mac-host SSH connection timed out and generated a UFW block event. IPv6 listeners exist, but there are no IPv6 allow rules in this lab.

**Operations.** Bash tools install the web service, check health, verify Client access, and archive the site with a SHA-256 checksum. A temporary extraction was compared with the live document root. SSH denial events and Nginx 200/404 requests were inspected in their actual logs.

## Verification

The [evidence record](verification-evidence.md) contains observed commands and results. The [lab record](lab-record.md) maps these results to acceptance criteria. Server reboot was followed by Client HTTP 200 and a fresh key login; root and password denials were repeated after reboot. APT refresh/upgrade completed with exit 0, with four packages deferred by Ubuntu phasing. `dpkg --audit` produced no output.

## Troubleshooting and lessons

- An AMD64 installer was incompatible with Apple Silicon VirtualBox; the Server was installed from an ARM64 image.
- Client GUI startup stalled; its existing disk booted successfully through the headless frontend with 2 CPUs. Client validation was performed over SSH.
- Early UI-driven password attempts failed. Direct SSH with the clarified credential succeeded; no password is included in the repository.
- A late SSH drop-in would not override the earlier cloud-init password setting. File precedence was corrected and effective settings were checked.
- Pausing the VMs caused stale guest time and APT metadata rejection. The Server clock was corrected and chrony restarted, preserving APT validity checks.

## Limitations and next steps

The [threat model](threat-model.md) maps controls to residual risks. The [evidence interpretation](verification-evidence.md#evidence-interpretation-and-revised-tooling) separates original guest results from revised offline-tested scripts, which were not deployed/rerun in this repository-only review.

This is a learning lab with static HTTP content and no public exposure. It does not include production TLS, DNS, availability testing, scheduled/off-host backups, disaster-recovery drills, vulnerability certification, or centralized monitoring. The dedicated Client key has no passphrase, which supports unattended lab tests but is a production limitation. Add key protection, TLS, configuration automation, scheduled restore checks, and external monitoring for a stronger next version.

Backups cover site content only. Temporary restoration was tested; a complete VM disaster recovery was not simulated. The Client GUI issue remains a limitation, while headless boot and SSH access are functional. Chrony had no selected source at final inspection: the corrected clock allowed APT checks to pass, but ongoing NTP synchronization is not claimed. Configuration rollback instructions and snapshots provide a recovery path.

Codex assisted the implementation and validation. The owner should be able to reproduce and explain the commands before presenting the work as personal expertise.
