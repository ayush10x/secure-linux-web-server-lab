# Recruiter brief

**Owner:** Ayush Kaushik  
**Environment:** Ubuntu 26.04 LTS ARM64, VirtualBox, Apple M2 Pro  
**Delivery:** Git-tracked configuration, Bash tools, CI, test evidence, and recovery documentation.

| Skill | Implementation | Evidence |
|---|---|---|
| Linux administration | Named sudo administrator, locked regular account, systemd startup | [Lab record](lab-record.md) |
| Networking | NAT and host-only adapters; fixed addresses outside DHCP pool | [Report](project-report.md) |
| Remote-access security | Ed25519 key, `AllowUsers`, denied root/password login | [SSH tests](verification-evidence.md) |
| Firewall management | Default deny; source-limited SSH; negative host test | [Firewall tests](verification-evidence.md) |
| Operations | Health script, logs, archives, SHA-256 check, restoration | [Operations guide](operations-guide.md) |
| Troubleshooting | ARM64 mismatch, stalled GUI launch, SSH precedence, paused-VM clock | [Action log](action-log.md) |
| Delivery discipline | ShellCheck and syntax CI; reproducible guide; explicit limitations | [CI](https://github.com/ayush10x/secure-linux-web-server-lab/actions) |

## Suggested resume entry

> Built and validated an assisted two-VM Ubuntu ARM64 web-server lab using Nginx, Ed25519 SSH authentication, and source-restricted UFW rules. Automated health and backup checks, verified checksum-based recovery, and documented positive and negative access tests with GitHub CI.

Use this wording when you can explain and reproduce the implementation. Codex assisted the build and troubleshooting; this is a lab project, not a production deployment.

## Interview walkthrough

1. Explain why NAT and host-only networking serve different purposes.
2. Show the allowed Client key session and the denied Mac-host SSH probe.
3. Explain why `00-lab-hardening.conf` must precede `50-cloud-init.conf`.
4. Demonstrate the health script and extract a backup into a temporary directory.
5. Discuss production improvements: TLS, protected keys, off-host backups, monitoring, and patch policy.

See the [test evidence](verification-evidence.md) and [report](project-report.md) for supporting results and limits.
