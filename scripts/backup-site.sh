#!/usr/bin/env bash
set -euo pipefail

source_dir="/var/www/lab-site"
backup_dir="/var/backups/lab-site"
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
tar --create --gzip --file "$archive" --directory / "${source_dir#/}"
tar --list --gzip --file "$archive" >/dev/null
sha256sum "$archive" >"$archive.sha256"
chmod 0600 "$archive" "$archive.sha256"

printf 'Backup created, archive listed, checksum written: %s\n' "$archive"
printf 'Verify separately with sha256sum -c and a temporary restore comparison.\n'
