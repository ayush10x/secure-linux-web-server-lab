# Operations and recovery guide

Administer the Server from the authorized Client VM:

```bash
ssh -i ~/.ssh/server_ayush ayush@192.168.56.200
sudo /usr/local/sbin/lab-health-check
sudo systemctl status nginx ssh --no-pager
sudo ufw status verbose
sudo sshd -t
```

The Mac host is excluded from new Server SSH sessions. Use the Server VM console if the Client becomes unavailable.

## Logs

```bash
sudo journalctl -u ssh --since today
sudo journalctl -k --grep='UFW' --since today
sudo tail -n 30 /var/log/nginx/lab-site.access.log
sudo tail -n 30 /var/log/nginx/lab-site.error.log
```

This virtual host uses `lab-site.access.log`, rather than the packaged default access log. Export only reviewed, sanitized samples.

## Backup and restoration

```bash
sudo /usr/local/sbin/backup-lab-site
sudo ls -l /var/backups/lab-site
```

Choose an exact archive path and inspect it before extraction. Replace `ARCHIVE` with that path:

```bash
sudo sha256sum -c ARCHIVE.sha256
sudo tar -tzf ARCHIVE
restore_dir=$(mktemp -d /tmp/lab-restore.XXXXXX)
sudo tar -xzf ARCHIVE -C "$restore_dir"
sudo diff -ru /var/www/lab-site "$restore_dir/var/www/lab-site"
```

For a live restoration, back up the current site first. Install the reviewed restored `index.html` with owner `root`, group `www-data`, and mode `0640`; run `nginx -t`, reload Nginx, and confirm Client HTTP 200. The backup covers site content, not the whole VM or system configuration. Production recovery needs off-host copies.

## Lockout recovery

At the Server console, temporarily disable UFW only if it caused the lockout. Repair the authorized Client source rule, re-enable UFW, and verify a new key session. For an SSH configuration issue, move the lab drop-in outside `sshd_config.d`, run `sshd -t`, and reload SSH. Restore the secure policy after correction.

Use `netplan try` for Server network changes. The Client's host-only connection uses NetworkManager with static `.201`; its NAT connection remains DHCP. Confirm the Client source address before changing UFW.

## Updates and paused VMs

Check the guest clock before updating, especially after a long VirtualBox pause. This Server uses chrony. Inspect `timedatectl` and `chronyc tracking`; correct stale time before retrying repository metadata validation. Keep APT validity and signature checks enabled.

Run `sudo apt update` and `sudo apt upgrade`, review deferred packages, and reboot when required. Repeat HTTP, key login, firewall, and health checks afterwards. Use `clean-install` for baseline rollback. Powered-off snapshots `validated-secure-lab` (Server) and `validated-client` (Client) succeeded after live snapshotting stalled. Avoid live snapshots on this setup.

The Client snapshot predates the profile-priority fix. After restoring it, apply these commands from the Client console or its old DHCP address:

```bash
sudo nmcli connection modify 'Wired connection 1' connection.autoconnect yes connection.autoconnect-priority 100 connection.interface-name enp0s9
sudo nmcli connection modify enp0s9 connection.autoconnect no
sudo nmcli connection up 'Wired connection 1'
```

This Client also inherited DHCP configuration from dracut/systemd-networkd at boot, which NetworkManager adopted before choosing a persistent profile. Install `config/90-lab-client-network.conf` as `/etc/NetworkManager/conf.d/90-lab-client-network.conf` (0644) on the Client. Its device-specific `keep-configuration=no` tells NetworkManager to select the saved host-only profile rather than adopt that early DHCP state. NetworkManager is the intended desktop network manager; the ordinary networkd service/socket/wait-online units were disabled on this Client. Reboot and check the resulting address before relying on SSH firewall access. See the upstream [NetworkManager configuration reference](https://networkmanager.dev/docs/api/1.48/NetworkManager.conf.html).
