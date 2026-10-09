#!/usr/bin/env bash
# Run on the authorized Client VM after Server hardening.
set -u
server_ip=${1:-}
key_path=${2:-$HOME/.ssh/server_ayush}
if [[ ! $server_ip =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ || ! -f $key_path ]]; then
  printf 'Usage: %s SERVER_IPV4 CLIENT_PRIVATE_KEY\n' "$0" >&2
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
http_status() {
  local path=$1 expected=$2 actual
  actual=$(curl --silent --show-error --max-time 5 --output /dev/null --write-out '%{http_code}' "http://$server_ip$path") || return 1
  [[ $actual == "$expected" ]]
}
ssh_denied() {
  "$@"
  local status=$?
  [[ $status == 255 ]]
}
ssh_args=(-o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=yes -i "$key_path")
check 'HTTP 200' http_status / 200
check 'Missing page returns 404' http_status /lab-validation-missing 404
check 'Dotfile path returns 403' http_status /.git/config 403
check 'Administrator key login works' ssh "${ssh_args[@]}" "ayush@$server_ip" 'test "$(whoami)" = ayush && test "$(hostname)" = kapserver'
check 'Root SSH denied' ssh_denied ssh "${ssh_args[@]}" "root@$server_ip" true
check 'Regular account SSH denied' ssh_denied ssh "${ssh_args[@]}" "webuser@$server_ip" true
check 'Password-only SSH denied' ssh_denied ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=yes -o PubkeyAuthentication=no -o PreferredAuthentications=password "ayush@$server_ip" true
printf 'Failures: %s\n' "$failures"
exit "$failures"
