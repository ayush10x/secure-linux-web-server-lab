# Action log and reasons

This is a factual record of work performed for this lab. Planned steps are not recorded as completed. Secrets and private keys are excluded.

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
