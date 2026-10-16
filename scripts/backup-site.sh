#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
umask 077

source_dir="/var/www/lab-site"
backup_dir="/var/backups/lab-site"
max_backups=10
timestamp=$(date -u +%Y%m%d-%H%M%S)
archive="$backup_dir/lab-site-$timestamp.tar.gz"

if [[ $EUID -ne 0 ]]; then
  printf 'Run this script as root.\n' >&2
  exit 1
fi

if [[ ! -d "$source_dir" ]]; then
  printf 'Source directory not found: %s\n' "$source_dir" >&2
  exit 2
fi

install -d -o root -g root -m 0700 "$backup_dir"
if [[ -e "$archive" || -L "$archive" || -e "$archive.sha256" || -L "$archive.sha256" ]]; then
  printf 'Backup archive already exists for timestamp %s; wait one second and retry.\n' "$timestamp" >&2
  exit 3
fi
tar --create --gzip --file "$archive" --directory / "${source_dir#/}"
tar --list --gzip --file "$archive" >/dev/null
sha256sum "$archive" >"$archive.sha256"
chmod 0600 "$archive" "$archive.sha256"

# Prune only after a new archive has been listed and its checksum written.
# UTC timestamp filenames sort from newest to oldest in the C locale.
find "$backup_dir" -maxdepth 1 -type f -name 'lab-site-*.tar.gz' |
  sort -r | tail -n +$((max_backups + 1)) |
  while IFS= read -r old; do
    rm -f -- "$old" "$old.sha256"
  done

printf 'Backup created, archive listed, checksum written: %s\n' "$archive"
printf 'Verify separately with sha256sum -c and a temporary restore comparison.\n'
