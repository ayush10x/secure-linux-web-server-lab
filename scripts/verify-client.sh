#!/usr/bin/env bash
# Run on the separate Client VM, targeting the Server VM's private lab IP.
set -u

server_ip=${1:-}
if [[ ! "$server_ip" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then
  printf 'Usage: %s SERVER_PRIVATE_IP\n' "$0" >&2
  exit 64
fi

failures=0
check() {
  local label=$1
  shift
  if "$@"; then
    printf 'PASS: %s\n' "$label"
  else
    printf 'FAIL: %s\n' "$label" >&2
    failures=$((failures + 1))
  fi
}

check 'ICMP reaches the Server VM' ping -c 2 -W 2 "$server_ip"
check 'HTTP returns the lab page' curl --fail --silent --show-error --max-time 5 "http://$server_ip/"
printf 'For SSH, separately open a new terminal and test your approved administrator key.\n'
exit "$failures"
