# Evidence Checklist

Completed command evidence is recorded in [verification evidence](verification-evidence.md) and [the lab record](lab-record.md). The following original checklist describes evidence categories, not missing work. VM configuration, accounts, service state, permissions, sockets, logs, positive/negative access, health, backup recovery and Server reboot were checked. Client web access was tested with curl, not a desktop-browser screenshot; the Client GUI limitation is disclosed.

- [x] Private VM network settings recorded from VirtualBox
- [x] Guest hostnames and interface addresses checked
- [x] Separate account and group results checked
- [x] Nginx syntax and active/enabled status checked
- [x] Website requested with curl from the Client
- [x] Fresh key login and sudo checked
- [x] Effective SSH settings checked; no private-key contents captured
- [x] Root/password/regular-account login denied
- [x] UFW default policy and narrow rules checked
- [x] Listening sockets checked
- [x] Authentication, firewall and Nginx logs reviewed
- [x] Health check passed
- [x] Backup checksum and temporary restoration comparison passed
- [x] Server reboot persistence checked
- [x] Acceptance matrix, failures and fixes documented
