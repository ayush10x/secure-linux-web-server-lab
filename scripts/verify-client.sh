#!/usr/bin/env bash
# Run on the separate Client VM, targeting the Server VM's private lab IP.
set -u
export LC_ALL=C

server_ip=${1:-}
ipv4_regex='^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$'
if [[ ! "$server_ip" =~ $ipv4_regex ]]; then
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
# Called indirectly through check(); validates status, not page identity.
# shellcheck disable=SC2317,SC2329
http_200() {
  local status
  status=$(curl --silent --show-error --max-time 5 --output /dev/null --write-out '%{http_code}' "http://$server_ip/") || return 1
  [[ $status == 200 ]]
}
check 'HTTP returns exactly 200' http_200
printf 'For SSH, separately open a new terminal and test your approved administrator key.\n'
exit "$failures"
