#!/usr/bin/env bash
# Install the web portion of the lab. SSH hardening and UFW are separate,
# deliberately later steps so that remote access can be verified first.
set -euo pipefail

if [[ ${1:-} != --apply ]]; then
  printf 'Usage: sudo %s --apply\n' "$0" >&2
  printf 'Review the README and take a VM snapshot before installation.\n' >&2
  exit 64
fi
if (( EUID != 0 )); then
  printf 'Run as root with sudo.\n' >&2
  exit 77
fi

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if [[ ! -f "$project_dir/site/index.html" || ! -f "$project_dir/config/lab-site.nginx" ]]; then
  printf 'Run this script from the complete project directory.\n' >&2
  exit 66
fi

if [[ -e /etc/nginx/sites-enabled/lab-site ]]; then
  printf 'The lab site is already enabled; inspect it before reinstalling.\n' >&2
  exit 73
fi
if [[ -e /etc/nginx/sites-available/default.lab-disabled || -L /etc/nginx/sites-available/default.lab-disabled ]]; then
  printf 'A saved default site already exists; inspect it before installing.\n' >&2
  exit 73
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y nginx openssh-server ufw rsync curl
install -d -o root -g www-data -m 0750 /var/www/lab-site
install -o root -g www-data -m 0640 "$project_dir/site/index.html" /var/www/lab-site/index.html
install -o root -g root -m 0644 "$project_dir/config/lab-site.nginx" /etc/nginx/sites-available/lab-site
ln -s /etc/nginx/sites-available/lab-site /etc/nginx/sites-enabled/lab-site

# Disable the packaged default before syntax checking: both sites otherwise
# claim default_server on port 80. Keep its link for easy recovery.
default_link_disabled=false
if [[ -L /etc/nginx/sites-enabled/default ]]; then
  mv /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default.lab-disabled
  default_link_disabled=true
fi
if ! nginx -t; then
  rm /etc/nginx/sites-enabled/lab-site
  if $default_link_disabled; then
    mv /etc/nginx/sites-available/default.lab-disabled /etc/nginx/sites-enabled/default
  fi
  printf 'Nginx syntax failed. The lab site was not activated.\n' >&2
  exit 78
fi

systemctl enable --now nginx ssh
systemctl reload nginx
install -o root -g root -m 0755 "$project_dir/scripts/health-check.sh" /usr/local/sbin/lab-health-check
install -o root -g root -m 0755 "$project_dir/scripts/backup-site.sh" /usr/local/sbin/backup-lab-site
curl --fail --silent --show-error --max-time 5 http://127.0.0.1/ >/dev/null
printf 'Web service installed. Test it from the Client VM before configuring SSH or UFW.\n'
