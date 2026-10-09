# Evidence Checklist

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
