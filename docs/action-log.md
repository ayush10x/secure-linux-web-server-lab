# Action log and reasons

This is a factual record of work performed for this lab. Planned steps are not recorded as completed. Secrets and private keys are excluded.

## Completion session: 10 October 2026 (Asia/Kolkata)

| Action | Why | Observed result |
|---|---|---|
| Resumed both VMs and authenticated to the Client using the clarified credential | Continue after the user's Wi-Fi pause | Client shell established; existing disk preserved; no credential recorded |
| Set Client host-only IPv4 to `192.168.56.201/24`, retaining NAT as the default route | Stable firewall source outside the DHCP pool | Client `.201` could reach Server `.200` |
| Created a dedicated Client Ed25519 key and installed only its public key on the Server | Prove working administrator access before hardening | Fresh key login as `ayush` and sudo to root passed; private key stayed on Client |
| Used `00-lab-hardening.conf`, checked effective SSH settings and reloaded SSH | OpenSSH's first-value precedence requires the lab policy before Ubuntu's cloud-init drop-in | Password, keyboard-interactive and root access disabled; `AllowUsers ayush`; fresh key access passed |
| Enabled UFW default-deny incoming, allowing SSH only from `.201` and HTTP from the private subnet | Independently enforce network restrictions | Client access passed; Mac-host SSH timed out with a matching UFW block log |
| Reviewed positive/negative access, logs, sockets, accounts and file modes | Validate actual behavior as well as configuration | HTTP 200, absent page 404, dotfile 403; root, regular-account and password-only SSH denied; intended listeners and restricted file permissions confirmed |
| Corrected stale UTC after pause, restarted chrony and refreshed/upgraded APT | Restore package time checks without bypassing validation | APT exit 0; four packages deferred by Ubuntu phasing; dpkg audit empty. NTP sources remained unselected at final inspection; synchronization is a documented limitation |
| Created a backup, verified SHA-256 and compared a temporary extraction with the live site | Demonstrate recovery without overwriting the site | Checksum OK; diff exit 0; archives root-only |
| Rebooted Server and repeated access, denial, firewall and health checks | Verify persistent configuration | HTTP 200 and fresh key access returned; denials persisted; health exit 0 |
| Added and ran the Client security verifier | Make acceptance checks reproducible | Seven checks passed; failures 0; exit 0 |
| Wrote recruiter brief, report, sanitized evidence, setup/operations guides and three-page PDF | Present evidence and limitations clearly | PDF rendered and all pages visually inspected; assisted-project context and Client GUI limitation disclosed |

## Earlier setup history

Final snapshot recovery: Server and Client live snapshots stalled and were cancelled. VirtualBox reported Running while its execution logs showed SUSPENDED. Normal pause/resume and ACPI shutdown did not restore networking. Auto-review blocked hard reset; the user explicitly approved the state-loss/filesystem risk. Warm reset left invalid Virtio queues, so both named VMs were powered off and cold-started. Powered-off snapshots succeeded: Server `validated-secure-lab` (`0efb4985-710e-493e-8654-b65cbd49c5cb`) and Client `validated-client` (`d7cefa74-48eb-41a8-9ff2-5691818d4665`). Server HTTP and all seven Client security checks passed again; both guests had empty dpkg audits and no failed systemd units. Server kernel logs contained VirtualBox display/PCI messages, not a claimed clean kernel log.

Client cold boot selected the old DHCP profile instead of the static profile because `Wired connection 1` had autoconnect priority -999. Set its priority to 100, bound it to `enp0s9`, and disabled autoconnect for the competing `enp0s9` profile. Reactivated the fixed connection and repeated the seven security checks successfully. The Client snapshot predates this priority fix: apply it again after restoring that snapshot.

Published the recruiter documents and PDF, then made the repository public after explicit user approval. CI initially flagged indirect function calls and intentional remote-shell expansion; added scoped, explained ShellCheck annotations. Run `37992413462` passed for commit `d1349b9`.

Further Client reboot diagnosis showed that priority alone was insufficient: systemd-networkd's dracut default configured DHCP before NetworkManager, which then assumed the existing address. Added the Client-only, device-scoped `keep-configuration=no` configuration and disabled the ordinary networkd service/socket/wait-online units so NetworkManager can select its persistent static profile. This fix also postdates the Client snapshot.

Final Client reboot preserved `192.168.56.201/24`. All seven Client checks passed again with verifier exit 0; Server health checks all passed, dpkg audit remained empty and systemd reported zero failed units. Both VMs were left running headlessly. Updated the recovery evidence, operations instructions, action log and visually checked PDF to reflect the final observed state.

| Date (Asia/Kolkata) | Action | Why | Observed result |
|---|---|---|---|
| 2026-10-09 | Inspected existing project kit and VirtualBox inventory | Identify the starting state before changing files or VMs | Project kit present; seven VMs found; target Server VM powered off |
| 2026-10-09 | Inspected `ubunutu server` configuration | Explain the earlier UEFI boot screen | ARM64 VM had an AMD64 Ubuntu installer attached; its virtual disk contained only about 2 MB of data |
| 2026-10-09 | Inspected `ubuntu 26.04 ` configuration | Preserve the existing Client VM | ARM64 VM with a 25 GB virtual disk containing about 11 GB of data; powered off |
| 2026-10-09 | Replaced Server VM optical image with the local Ubuntu 26.04 ARM64 ISO | Boot an installer compatible with the M2 Pro | VirtualBox accepted the image; Ubuntu Server GRUB menu appeared |
| 2026-10-09 | Started the Server VM | Begin the installation | VM entered the Ubuntu Server installer boot flow |
| 2026-10-09 | Added safe installation and client-check scripts to the project kit | Make installation repeatable and keep SSH/UFW changes after working remote access is proved | Local scripts created; guest execution pending |
| 2026-10-09 | Confirmed formatting of the Server VM's previously empty 25 GB virtual disk and proceeded through profile setup | Ubuntu Server requires a formatted guest disk; the Client VM and Mac disks were outside the selected target | Installer reached SSH configuration; the user entered the account credentials privately |
| 2026-10-09 | Selected OpenSSH server in the installer | Enable remote administration over the private lab network | OpenSSH checkbox selected; installer has not yet advanced beyond this screen |
| 2026-10-09 | Reviewed and corrected the project guide and installer script | Align instructions with the existing Server/Client VM names and avoid duplicate administrator creation | Local documentation updated; no guest commands executed |
| 2026-10-09 | Created private GitHub repository `ayush10x/secure-linux-web-server-lab` | Provide the requested publication destination without public exposure | Empty private repository verified in GitHub; project files not yet uploaded |
| 2026-10-09 | Committed and pushed the project kit to the private GitHub repository | Make scripts, setup guide, test plan, and action/why log available together | Commit `7da7fb7` on `main`; GitHub repository showed all project directories and README |
| 2026-10-09 | Advanced the Server VM installer through SSH and optional snaps | Install OpenSSH for private-lab administration and avoid unrelated software | Ubuntu installer entered system installation and then security updates; completion pending |
| 2026-10-09 | Attempted to start the existing Client VM without altering its disk | Check the second guest needed for network tests | VirtualBox briefly launched a process, then the VM returned to powered off before a guest screen appeared; cause not yet established |
| 2026-10-09 | Checked the GitHub Actions workflow for the first commit | Validate script syntax and ShellCheck checks in the published repository | `Project checks` run #1 completed successfully |
| 2026-10-09 | Rebooted the Server VM after installer completion | Verify the installed ARM64 system boots from its virtual disk | Installer automatically unmounted ISO; Ubuntu 26.04 LTS reached `kapserver` login on tty1 |
| 2026-10-09 | Released a stuck Client VM launch process and retried | Clear a VirtualBox lock without modifying the Client VM disk | Client VM still reported aborted/powered off before a guest console appeared; diagnosis ongoing |
| 2026-10-09 | Took Server VM snapshot `clean-install` | Preserve a recoverable baseline before Nginx, firewall, and SSH changes | VirtualBox snapshot UUID `033862de-0f8f-480f-a849-acccfd2622ee` |
| 2026-10-09 | Confirmed the Server login, sudo membership, and both network addresses | Avoid applying account and SSH policy to the wrong identity or interface | `ayush` belongs to `sudo`; NAT `10.0.2.15`; host-only DHCP `192.168.56.3` |
| 2026-10-09 | Updated the project SSH policy and guide from example account `labadmin` to actual account `ayush` | Prevent a future `AllowUsers` mismatch and accidental administrator lockout | Local files updated; SSH hardening not yet applied to the guest |
| 2026-10-09 | Transferred a checksum-verified project archive over the host-only network | Put the reviewed project files on the Server without publishing credentials | SHA-256 matched; archive extracted in the Server home directory |
| 2026-10-09 | Ran the Server install script after sudo authentication was entered at the VM console | Install the site and required packages while leaving SSH and UFW changes for later validation | Nginx config valid; Nginx and SSH enabled; local HTTP returned 200 |
| 2026-10-09 | Reduced Client VM from 5 to 2 CPUs and booted it headlessly | Work around stalled GUI launches with the lab's documented CPU sizing, while preserving its disk | Existing Ubuntu login screen appeared; Client VM later answered ping and SSH on `192.168.56.2` |
| 2026-10-09 | Ran Server health check and created two site backups | Verify installed services and recovery tooling | Nginx/SSH/site checks passed; overall health check failed only because UFW has intentionally not yet been enabled; backup archives were created |
| 2026-10-09 | Paused both VMs at the user's request, then resumed them when asked | Wait for stable Wi-Fi without losing guest state | Both VMs reported `paused`, then resumed successfully; temporary transfer server and unfinished SSH prompt were closed |
| 2026-10-09 | Created non-admin `webuser` with a locked password | Provide a separate least-privilege account without introducing another shared credential | `id webuser` showed only its own group; `passwd -S` showed locked status |
| 2026-10-09 | Extracted a site backup to a temporary directory and compared it with the live site | Test recovery content without overwriting production files | `diff -ru` returned no differences |
| 2026-10-09 | Configured Server host-only IPv4 as static `192.168.56.200/24` using timed Netplan trial | Provide a predictable address outside the VirtualBox DHCP pool | Host ping and HTTP returned success during trial; configuration was accepted; `ip -br address` confirmed `enp0s9` at `.200` |
| 2026-10-09 | Rebooted the Server VM and requested the site at its static private address | Verify network and Nginx startup persist without manual intervention | VirtualBox boot screen observed; `http://192.168.56.200/` returned HTTP 200 afterward |
| 2026-10-09 | Pushed the updated lab documentation and checked CI | Publish only verified progress to the requested private GitHub repository | Commit `932d071` pushed; GitHub `Project checks` run `37908327407` completed successfully |
| 2026-10-09 | Opened a private-network SSH prompt for the Client VM and stopped after two denied authentication attempts | Establish guest access for cross-VM testing without risking repeated account lockouts | SSH service responded at `192.168.56.2`, but Client login was not established; no Client-side test or hardening result was claimed |
