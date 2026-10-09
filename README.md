# Project 1: Design and Implementation of a Secure Linux Web Server

## Start here for this VirtualBox lab

This repository contains runnable files and a guided build. The actual test record is in [docs/lab-record.md](docs/lab-record.md), while [docs/action-log.md](docs/action-log.md) records actions taken and why. Test rows stay marked pending until they are observed on both VMs.

On an Apple Silicon Mac, use an ARM64 Ubuntu Server installer. The existing VirtualBox machines in this lab are named `ubunutu server` (Server VM) and `ubuntu 26.04 ` (Client VM). Those are VirtualBox labels; the installed Server VM booted with Linux hostname `kapserver`.

The installer account should be a named sudo administrator; this guide uses `labadmin`. Set its password yourself and do not put it in this repository. If you chose a different username, replace `labadmin` in the commands and SSH policy before applying them. With working NAT and host-only networking, copy this repository to the Server VM, take a `clean-install` snapshot, then run:

```bash
sudo bash scripts/install-server.sh --apply
```

This installs Nginx, OpenSSH, UFW, rsync, curl, the example site, and operations scripts. It does **not** activate SSH hardening or UFW; follow phases 4–6 below only after key login works in a second session. On the Client VM, run `bash scripts/verify-client.sh SERVER_PRIVATE_IP` after the site is installed.

## Summary and problem statement

Build an Ubuntu Server VM that hosts a static site with Nginx, is administered remotely with SSH keys, and accepts only required inbound traffic. The project addresses the risk of an unpatched, overexposed server with weak remote access and no recovery procedure.

## Objectives and completion criteria

The server is complete when it has a predictable lab IP and hostname, separate administrator and regular accounts, a working site, automatic service startup, key-based SSH with root login disabled, a default-deny firewall, useful logs, a tested backup/restore procedure, a health check, and successful tests from a second VM.

## Scope

Included: one Ubuntu Server 26.04 LTS server, one Linux client, Nginx, OpenSSH, UFW, a static site, local backup, logging, and lab testing. The existing local installer is Ubuntu 26.04 ARM64; apply all available updates after installation.

Excluded: public DNS, production TLS certificates, internet exposure, databases, application frameworks, load balancing, and penetration testing outside the private lab.

## Prerequisites and VM sizing

- Host: Apple Silicon Mac (this lab uses an M2 Pro), VirtualBox 7.2 or later, and enough free RAM/storage for both guests. Do not use an AMD64 Ubuntu ISO on Apple Silicon VirtualBox.
- Server VM: Ubuntu Server 26.04 ARM64, 2 virtual CPUs, 3 GB RAM, 25 GB dynamically allocated virtual disk. The existing `ubunutu server` VM matches this sizing.
- Client VM: an ARM64 Linux installation, 2 virtual CPUs and 4 GB RAM are sufficient for this lab; allow at least 20 GB disk. The existing `ubuntu 26.04 ` VM has 5 CPUs, about 4.4 GB RAM, and a 25 GB disk; preserve its existing installation.
- Networking on **both** VMs: Adapter 1 = NAT for package downloads; Adapter 2 = the same VirtualBox host-only network (`HostNetwork`) for SSH and HTTP lab traffic. Confirm the assigned private addresses with `ip -br address` on each guest before substituting them into commands.
- Keep installer ISO images and any VM snapshots outside the Git repository. Never publish passwords, private SSH keys, guest disk images, or raw logs containing secrets.

## Architecture

```text
Client VM (CLIENT_HOST_ONLY_IP)
       | SSH 22, HTTP 80
       v
Server VM (SERVER_HOST_ONLY_IP, hostname kapserver)
  +-- OpenSSH: remote administration
  +-- UFW: default deny incoming
  +-- Nginx: /var/www/lab-site
  +-- systemd/journal + /var/log/nginx
  +-- /var/backups/lab-site
```

Required software: `openssh-server`, `nginx`, `ufw`, `rsync`, and `curl`. Use a VM snapshot named `clean-install` before starting. The ARM64 installer is required for Apple Silicon VirtualBox.

## Milestones and schedule

| Phase | Outcome | Time |
|---|---|---:|
| 1. Baseline | Network, hostname, updates, accounts | 1.5 h |
| 2. Web service | Nginx and static site work locally | 1.5 h |
| 3. Remote access | SSH keys work in a second session | 1.5 h |
| 4. Hardening | SSH and UFW safely restricted | 1.5 h |
| 5. Operations | Logs, backup, restore, health check | 2 h |
| 6. Evidence | Tests, screenshots, report | 1-2 h |

## Implementation

Replace example IP addresses and usernames before running commands. Commands labeled **server** run on the Server VM; commands labeled **client** run on the Client VM. The example addresses below are not yet verified for the actual VMs.

### 1. Establish a recoverable baseline

- **Objective:** Identify the host, patch it, and retain a recovery path.
- **Why:** Later network changes can interrupt remote access.
- **Actions (server console):** create a VM snapshot, then run:

```bash
hostnamectl
sudo apt update
sudo apt upgrade
sudo apt install openssh-server nginx ufw rsync curl
hostnamectl
ip -br address
```

- **Expected result:** Hostname is `kapserver`; the private adapter has the expected address; packages install successfully. If you intentionally rename the host, use `sudo hostnamectl set-hostname NEW_NAME` and update the record.
- **Verify:** `systemctl is-active ssh nginx` and `systemctl is-enabled ssh nginx` both report active/enabled.
- **Common mistakes:** Updating the wrong VM, confusing NAT and private-adapter addresses, or continuing after package errors.
- **Rollback:** Restore the `clean-install` snapshot if the baseline is unusable.

For a predictable IP, prefer a DHCP reservation in the hypervisor lab network. If unavailable, configure Ubuntu's existing Netplan file with the actual interface name from `ip -br link`. Keep the YAML indentation exact, run `sudo netplan try`, and accept only after connectivity is confirmed. `netplan try` automatically rolls back if confirmation is not received.

### 2. Create separate accounts

- **Objective:** Use named accounts instead of routine root access.
- **Why:** Individual accounts improve accountability and support least privilege.
- **Actions:**

```bash
sudo adduser webuser
id labadmin
id webuser
sudo -l -U labadmin
```

- **Expected result:** `labadmin` belongs to `sudo`; `webuser` does not.
- **Verify:** From the VM console, log in as `labadmin` and run `sudo whoami`; output should be `root`.
- **Common mistakes:** Omitting `-a` in `usermod -aG`, which can remove existing group membership.
- **Rollback:** If the installer account lacks sudo, use an existing administrator or recovery console to correct its membership. Do not create a duplicate account with the same name.

### 3. Publish the static website

- **Objective:** Serve a site from a dedicated document root.
- **Why:** Separating site data from package-owned defaults makes ownership and backup clear.
- **Actions:** Copy `site/index.html` and `config/lab-site.nginx` from this project to the server, then:

```bash
sudo install -d -o root -g www-data -m 0750 /var/www/lab-site
sudo install -o root -g www-data -m 0640 index.html /var/www/lab-site/index.html
sudo install -o root -g root -m 0644 lab-site.nginx /etc/nginx/sites-available/lab-site
sudo ln -s /etc/nginx/sites-available/lab-site /etc/nginx/sites-enabled/lab-site
sudo mv /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default.lab-disabled
sudo nginx -t
sudo systemctl reload nginx
curl -I http://127.0.0.1/
```

- **Expected result:** `nginx -t` succeeds and the local request returns `HTTP/1.1 200 OK`.
- **Verify:** `curl http://127.0.0.1/` displays the page title; `systemctl is-enabled nginx` returns `enabled`.
- **Common mistakes:** Reloading before `nginx -t`, wrong `root` path, or directories that Nginx cannot traverse.
- **Rollback:** Move the saved default symlink back to `/etc/nginx/sites-enabled/default`, validate with `sudo nginx -t`, and reload.

### 4. Configure and prove SSH key access

- **Objective:** Authenticate the administrator with a key.
- **Why:** Strong keys resist password guessing and can be rotated independently.
- **Actions (client):**

```bash
ssh-keygen -t ed25519 -a 64 -f ~/.ssh/server_labadmin
ssh-copy-id -i ~/.ssh/server_labadmin.pub labadmin@SERVER_HOST_ONLY_IP
ssh -i ~/.ssh/server_labadmin labadmin@SERVER_HOST_ONLY_IP
```

Keep the private key on the client with mode `0600`; only the `.pub` file may be shared. On the server, `~/.ssh` should be `0700` and `authorized_keys` should be `0600`.

- **Expected result:** A new client terminal logs in with the key and `sudo -v` succeeds.
- **Verify:** Keep the original session open; open a second session and run `whoami`, `hostname`, and `sudo -v`.
- **Common mistakes:** Copying the private key, wrong home-directory ownership, or testing only in the existing session.
- **Rollback:** Use the still-open session or VM console to repair ownership and permissions.

### 5. Harden SSH safely

> **Lockout warning:** Do not disable password or root login until key login and `sudo` work in a second session. Keep a console and existing SSH session open.

- **Objective:** Limit SSH to named administrators using keys.
- **Actions:** Check `AllowUsers` matches the actual administrator account, then copy `config/99-lab-hardening.conf` to `/etc/ssh/sshd_config.d/` and run:

```bash
sudo sshd -t
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|pubkeyauthentication|allowusers'
sudo systemctl reload ssh
```

- **Expected result:** Syntax validation is silent; effective settings show root/password login disabled and `labadmin` allowed.
- **Verify:** In a new client terminal, confirm key login works and password-only/root attempts fail. Do not close the recovery session until both results are recorded.
- **Common mistakes:** Editing `/etc/ssh/sshd_config` without a backup, misspelling the username, or restarting before validation.
- **Rollback:** From the console/open session, move the drop-in out of `/etc/ssh/sshd_config.d`, run `sudo sshd -t`, then reload SSH.

### 6. Enable UFW without losing access

> **Lockout warning:** Add the SSH allow rule before enabling UFW. Keep the VM console available.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from CLIENT_HOST_ONLY_IP to any port 22 proto tcp comment 'SSH from Client VM'
sudo ufw allow from 192.168.56.0/24 to any port 80 proto tcp comment 'HTTP lab network'
sudo ufw logging medium
sudo ufw enable
sudo ufw status verbose
```

- **Expected result:** Incoming policy is deny; only lab SSH and HTTP rules are present.
- **Verify:** From the client, start a new SSH session and run `curl -I http://SERVER_HOST_ONLY_IP/` with the observed address substituted. On the server, run `sudo ss -lntup` and confirm only intended listeners.
- **Common mistakes:** Enabling UFW before adding SSH, using the wrong client IP, or accidentally allowing a service from `Anywhere`.
- **Rollback:** At the VM console run `sudo ufw disable`, correct rules, then repeat verification before re-enabling.

### 7. Logs, health, backup, and restore

Install the included scripts:

```bash
sudo install -o root -g root -m 0755 health-check.sh /usr/local/sbin/lab-health-check
sudo install -o root -g root -m 0755 backup-site.sh /usr/local/sbin/backup-lab-site
sudo /usr/local/sbin/lab-health-check
sudo /usr/local/sbin/backup-lab-site
```

Review events with:

```bash
sudo journalctl -u ssh --since today
sudo journalctl -u nginx --since today
sudo journalctl -k --grep='UFW' --since today
sudo tail -n 50 /var/log/nginx/access.log
sudo tail -n 50 /var/log/nginx/error.log
sudo grep -E 'Failed password|Invalid user' /var/log/auth.log | tail
```

Restore test: note the newest archive from `/var/backups/lab-site`, extract it into a temporary directory, compare it with the live site, and only then restore a deliberately changed test file. Never extract over the live site without first listing the archive with `tar -tzf`.

```bash
sudo mkdir -p /tmp/lab-site-restore-test
sudo tar -xzf /var/backups/lab-site/lab-site-YYYYMMDD-HHMMSS.tar.gz -C /tmp/lab-site-restore-test
sudo diff -ru /var/www/lab-site /tmp/lab-site-restore-test/var/www/lab-site
```

## Validation and acceptance

Use [docs/test-plan.md](docs/test-plan.md). The project passes only when web access, reboot persistence, authorized key login, denied root/password login, firewall restriction, log generation, backup integrity, and a test restoration all pass.

## Risks and recovery

| Risk | Prevention | Recovery |
|---|---|---|
| SSH lockout | Validate with `sshd -t`; keep two sessions and console | Remove hardening drop-in from console and reload |
| Firewall lockout | Add narrow SSH rule first | Disable UFW from console and repair rules |
| Broken Nginx config | Run `nginx -t` before reload | Restore known-good site link/config |
| Bad Netplan | Use `netplan try` | Allow timeout rollback or restore snapshot |
| Data loss during restore | Extract to `/tmp` and compare first | Restore VM snapshot or known-good archive |

## Troubleshooting quick guide

- **Connection refused:** Check `systemctl status ssh nginx`, `ss -lntup`, and the VM's private adapter.
- **Connection timeout:** Check IP/subnet, hypervisor network, and `ufw status numbered`.
- **SSH key rejected:** Check `ssh -vvv`, server ownership, `0700`/`0600` permissions, and `journalctl -u ssh`.
- **403 from Nginx:** Check parent-directory traversal permission, file ownership, and Nginx error log.
- **Site unchanged:** Check which server block answered with `sudo nginx -T`, then clear browser cache or use `curl`.

## Evidence and final report

Follow [docs/evidence-checklist.md](docs/evidence-checklist.md) and [docs/report-template.md](docs/report-template.md). Suggested README sections for a completed portfolio submission: overview, architecture, prerequisites, build, security decisions, testing, recovery proof, screenshots, lessons learned, and future work.

## Version 2 ideas

Add a private certificate authority and HTTPS, unattended security updates with a maintenance policy, integrity monitoring, centralized logs, configuration management with Ansible, and remote backups. These are extensions—not prerequisites for a successful beginner project.
