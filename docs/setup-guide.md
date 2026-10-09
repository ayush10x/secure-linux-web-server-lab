# Setup and reproduction guide

## Start here for this VirtualBox lab

Run these reproduction commands from the repository root. The actual test record is in [lab-record.md](lab-record.md), and [action-log.md](action-log.md) records actions and reasons.

On Apple Silicon, use an ARM64 installer. The VirtualBox labels are `ubunutu server` and `ubuntu 26.04 `; Linux hostnames are `kapserver` and `ubuntu26`. Static host-only addresses are `192.168.56.200/24` for Server and `192.168.56.201/24` for Client, both on `enp0s9`.

The installer account is the named sudo administrator `ayush`. Keep its password out of this repository. The Server VM has a `clean-install` snapshot, and the web-service installation below has run successfully. To reproduce from the snapshot or on a fresh VM, copy this repository to the Server VM and run:

```bash
sudo bash scripts/install-server.sh --apply
```

Choose **one** web installation path: use the installer above after phases 1–2 and skip the manual commands in phase 3, or omit the installer and follow phase 3. Do not run both paths against the same VM. The installer deliberately refuses an already-enabled lab site.

The installer installs Nginx, OpenSSH, UFW, rsync, curl, the site, and operations scripts. It does **not** activate SSH hardening or UFW; follow phases 4–6 only after key login works in a second session. In phase 7, installer users skip script installation but run the checks. On the Client VM, run `bash scripts/verify-client.sh SERVER_PRIVATE_IP` after the site is installed.

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
- Client VM: ARM64 Linux, 2 virtual CPUs, about 4.4 GB RAM, and a 25 GB disk. The existing installation is preserved and boots headlessly; SSH provides administration.
- Networking on **both** VMs: Adapter 1 = NAT for package downloads; Adapter 2 = the same VirtualBox host-only network (`HostNetwork`) for SSH and HTTP lab traffic. The Server uses `192.168.56.200/24`, outside this host-only network's DHCP range (`192.168.56.1`–`192.168.56.199`). Confirm both guest addresses with `ip -br address` before running tests.
- Keep installer ISO images and any VM snapshots outside the Git repository. Never publish passwords, private SSH keys, guest disk images, or raw logs containing secrets.

## Architecture

```text
Client VM (CLIENT_HOST_ONLY_IP)
       | SSH 22, HTTP 80
       v
Server VM (192.168.56.200, hostname kapserver)
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

Replace placeholder addresses before running commands. Server IPv4 is `192.168.56.200`; Client IPv4 is `192.168.56.201`. Both are verified, static, and outside the lab DHCP pool. Check your own network before reusing them.

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

For a predictable IP, prefer a DHCP reservation in the hypervisor lab network. Here, the Server uses a static `192.168.56.200/24` address outside `HostNetwork`'s DHCP pool. It was set with Netplan on `enp0s9`, then accepted with `sudo netplan try --timeout 60` only after private-network ping and HTTP checks succeeded. The NAT interface `enp0s8` remains on DHCP. When reproducing, check your own DHCP pool first and use `netplan try` so connectivity changes can roll back.

#### Static networking example (customize before applying)

These are reproduction templates, not newly executed VM evidence. Use the VM console, not the connection you are changing. Inspect `ip -br link`, `ip -br address`, and existing `/etc/netplan/*.yaml` first; interface names may differ. Do not overlay conflicting Netplan definitions or replace working NAT settings. Save the existing configuration outside the repository before editing. The example assumes `enp0s8` is NAT and `enp0s9` is host-only, and no other file configures those interfaces:

```yaml
# Server: /etc/netplan/60-lab-network.yaml (root-owned, mode 0600)
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s8:
      dhcp4: true
    enp0s9:
      dhcp4: false
      addresses: [192.168.56.200/24]
```

Run `sudo netplan generate`, then `sudo netplan try --timeout 60` from the console. Verify NAT internet access and private-interface ping from the Client before accepting; if access fails, let the timeout revert and repair the saved configuration. Do not add a default gateway or DNS to the host-only interface.

On the desktop Client, inspect `nmcli -f NAME,DEVICE connection show` first. In this lab `Wired connection 1` controls `enp0s9`; substitute your actual host-only connection, never the NAT connection:

```bash
nmcli connection show 'Wired connection 1'
sudo nmcli connection modify 'Wired connection 1' ipv4.method manual ipv4.addresses 192.168.56.201/24 ipv4.gateway '' ipv4.dns '' ipv4.never-default yes
sudo nmcli connection up 'Wired connection 1'
ip -br address
ip route
ping -c 2 192.168.56.200
```

Keep a console and record the old NetworkManager values before changing them. For a previously DHCP-only host-only connection, rollback is `sudo nmcli connection modify 'Wired connection 1' ipv4.method auto ipv4.addresses '' ipv4.gateway '' ipv4.dns ''`, followed by `sudo nmcli connection up 'Wired connection 1'`. Restore your recorded `ipv4.never-default` value as well. A connection activation can interrupt SSH.

This basic template is not the complete recovery recipe for the existing Client: competing profiles/networkd boot adoption required additional fixes. See the [operations guide's startup and snapshot recovery instructions](operations-guide.md) before restoring the Client snapshot or changing its active configuration. Validate the address again after reboot.

### 2. Create separate accounts

- **Objective:** Use named accounts instead of routine root access.
- **Why:** Individual accounts improve accountability and support least privilege.
- **Actions:**

```bash
sudo adduser --disabled-password --gecos '' webuser
id ayush
id webuser
sudo -l -U ayush
```

- **Expected result:** `ayush` belongs to `sudo`; `webuser` does not.
- **Verify:** From the VM console, log in as `ayush` and run `sudo whoami`; output should be `root`.
- **Common mistakes:** Omitting `-a` in `usermod -aG`, which can remove existing group membership.
- **Rollback:** If the installer account lacks sudo, use an existing administrator or recovery console to correct its membership. Do not create a duplicate account with the same name.

### 3. Publish the static website

- **Objective:** Serve a site from a dedicated document root.
- **Why:** Separating site data from package-owned defaults makes ownership and backup clear.
- **Actions (manual path only):** From the complete repository root on a fresh Server, run the following. Skip this block if you used `install-server.sh`. Existing lab/default-backup paths must be inspected rather than overwritten:

```bash
sudo install -d -o root -g www-data -m 0750 /var/www/lab-site
sudo install -o root -g www-data -m 0640 site/index.html /var/www/lab-site/index.html
sudo install -o root -g root -m 0644 config/lab-site.nginx /etc/nginx/sites-available/lab-site
sudo ln -s /etc/nginx/sites-available/lab-site /etc/nginx/sites-enabled/lab-site
sudo mv /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default.lab-disabled
sudo nginx -t
sudo systemctl enable --now nginx ssh
sudo systemctl reload nginx
curl -I http://127.0.0.1/
```

- **Expected result:** `nginx -t` succeeds and the local request returns `HTTP/1.1 200 OK`.
- **Verify:** `curl http://127.0.0.1/` displays the page title; `systemctl is-enabled nginx` returns `enabled`.
- **Common mistakes:** Reloading before `nginx -t`, wrong `root` path, or directories that Nginx cannot traverse.
- **Rollback:** First remove only the lab enablement link: `sudo unlink /etc/nginx/sites-enabled/lab-site`. Then move the saved default symlink back to `/etc/nginx/sites-enabled/default`, validate with `sudo nginx -t`, and reload. Leaving both enabled would create duplicate `default_server` listeners. Retain site files/configuration for diagnosis. If no default symlink existed originally, do not invent one.

### 4. Configure and prove SSH key access

- **Objective:** Authenticate the administrator with a key.
- **Why:** Strong keys resist password guessing and can be rotated independently.
- **Actions (client):**

```bash
ssh-keygen -t ed25519 -a 64 -f ~/.ssh/server_ayush
```

Before the first Client connection, obtain the Server host-key fingerprint through its trusted VM console:

```bash
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Then on the Client connect and compare the displayed ED25519 fingerprint with that console value before accepting it into `known_hosts`:

```bash
ssh -o HostKeyAlgorithms=ssh-ed25519 ayush@SERVER_HOST_ONLY_IP true
ssh-copy-id -i ~/.ssh/server_ayush.pub ayush@SERVER_HOST_ONLY_IP
ssh -o IdentitiesOnly=yes -i ~/.ssh/server_ayush ayush@SERVER_HOST_ONLY_IP
```

Keep the private key on the client with mode `0600`; only the `.pub` file may be shared. On the server, `~/.ssh` should be `0700` and `authorized_keys` should be `0600`.

Do not treat `ssh-keyscan` alone as identity verification. The automated security verifier uses `StrictHostKeyChecking=yes` and requires this prior trusted enrollment. A changed host key is a failure to investigate at the console, not a reason to disable checking. Use a key passphrase for normal interactive administration; the historical lab's unencrypted key is disclosed as a limitation.

For noninteractive `BatchMode` tests with a protected key, first unlock it in your SSH agent (`ssh-add ~/.ssh/server_ayush`) through an interactive trusted terminal. Do not remove the key's passphrase to satisfy an automated check.

- **Expected result:** A new client terminal logs in with the key and `sudo -v` succeeds.
- **Verify:** Keep the original session open; open a second session and run `whoami`, `hostname`, and `sudo -v`.
- **Common mistakes:** Copying the private key, wrong home-directory ownership, or testing only in the existing session.
- **Rollback:** Use the still-open session or VM console to repair ownership and permissions.

### 5. Harden SSH safely

> **Lockout warning:** Do not disable password or root login until key login and `sudo` work in a second session. Keep a console and existing SSH session open.

- **Objective:** Limit SSH to named administrators using keys.
- **Actions:** Check `AllowUsers` matches the actual administrator account, then copy `config/00-lab-hardening.conf` to `/etc/ssh/sshd_config.d/` and run. The `00-` prefix precedes Ubuntu's `50-cloud-init.conf`: OpenSSH uses the first value found for these directives.

```bash
sudo install -o root -g root -m 0644 config/00-lab-hardening.conf /etc/ssh/sshd_config.d/00-lab-hardening.conf
sudo sshd -t
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|pubkeyauthentication|allowusers'
sudo systemctl reload ssh
```

- **Expected result:** Syntax validation is silent; effective settings show root/password login disabled and `ayush` allowed.
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
sudo install -o root -g root -m 0755 scripts/health-check.sh /usr/local/sbin/lab-health-check
sudo install -o root -g root -m 0755 scripts/backup-site.sh /usr/local/sbin/backup-lab-site
sudo /usr/local/sbin/lab-health-check
sudo /usr/local/sbin/backup-lab-site
```

Review events with:

```bash
sudo journalctl -u ssh --since today
sudo journalctl -u nginx --since today
sudo journalctl -k --grep='UFW' --since today
sudo tail -n 50 /var/log/nginx/lab-site.access.log
sudo tail -n 50 /var/log/nginx/lab-site.error.log
# auth.log is optional on installations without rsyslog; the journal above
# remains the primary SSH evidence source.
```

Restore test: note the newest archive from `/var/backups/lab-site`, extract it into a temporary directory, compare it with the live site, and only then restore a deliberately changed test file. Never extract over the live site without first listing the archive with `tar -tzf`.

```bash
sudo sha256sum -c /var/backups/lab-site/lab-site-YYYYMMDD-HHMMSS.tar.gz.sha256
sudo tar -tzf /var/backups/lab-site/lab-site-YYYYMMDD-HHMMSS.tar.gz
restore_dir=$(mktemp -d /tmp/lab-site-restore.XXXXXX)
sudo tar -xzf /var/backups/lab-site/lab-site-YYYYMMDD-HHMMSS.tar.gz -C "$restore_dir"
sudo diff -ru /var/www/lab-site "$restore_dir/var/www/lab-site"
```

## Validation and acceptance

Use [test-plan.md](test-plan.md) and run `bash scripts/verify-security.sh 192.168.56.200 ~/.ssh/server_ayush` on the Client after hardening. The project passes when web access, reboot persistence, key login, access denials, firewall restriction, logs, backup integrity, and restoration pass.

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

See [evidence-checklist.md](evidence-checklist.md), [project-report.md](project-report.md), and [verification-evidence.md](verification-evidence.md) for the completed portfolio record.

## Version 2 ideas

Add a private certificate authority and HTTPS, unattended security updates with a maintenance policy, integrity monitoring, centralized logs, configuration management with Ansible, and remote backups. These are extensions—not prerequisites for a successful beginner project.
