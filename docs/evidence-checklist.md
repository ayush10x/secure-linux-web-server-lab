# Evidence Checklist

Completed command evidence is recorded in [verification evidence](verification-evidence.md) and [the lab record](lab-record.md). The following original checklist describes evidence categories, not missing work. VM configuration, accounts, service state, permissions, sockets, logs, positive/negative access, health, backup recovery and Server reboot were checked. Client web access was tested with curl, not a desktop-browser screenshot; the Client GUI limitation is disclosed.

- [ ] VM settings showing isolated/private network (redact host details if needed)
- [ ] `hostnamectl` and `ip -br address`
- [ ] Separate account and group results from `id`
- [ ] Nginx syntax test and active/enabled status
- [ ] Website viewed from the client VM
- [ ] Successful key login and successful `sudo -v`
- [ ] Effective SSH settings; never capture private-key contents
- [ ] Denied root/password login
- [ ] UFW default policy and narrow allow rules
- [ ] Intended listening sockets from `ss -lntup`
- [ ] Authentication, firewall, and Nginx log samples
- [ ] Passing health check
- [ ] Backup archive, checksum verification, and temporary restore comparison
- [ ] Reboot persistence test
- [ ] Completed test matrix with failures and fixes
