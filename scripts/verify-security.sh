#!/usr/bin/env bash
# Run on the authorized Client VM after Server hardening.
set -u
export LC_ALL=C
server_ip=${1:-}
key_path=${2:-$HOME/.ssh/server_lab}
admin_user=${3:-labadmin}
ipv4_regex='^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$'
if [[ ! $server_ip =~ $ipv4_regex || ! -f $key_path || ! $admin_user =~ ^[a-z_][a-z0-9_-]{0,31}$ || $admin_user == root || $admin_user == webuser ]]; then
  printf 'Usage: %s SERVER_IPV4 CLIENT_PRIVATE_KEY [ADMIN_USER]\n' "$0" >&2
  printf 'ADMIN_USER defaults to labadmin; use your named administrator, not root or webuser.\n' >&2
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
# Called indirectly by check(), which invokes its argument list.
# shellcheck disable=SC2317,SC2329
http_status() {
  local path=$1 expected=$2 actual
  actual=$(curl --silent --show-error --max-time 5 --output /dev/null --write-out '%{http_code}' "http://$server_ip$path") || return 1
  [[ $actual == "$expected" ]]
}
# Called indirectly by check(), which invokes its argument list.
# shellcheck disable=SC2317,SC2329
ssh_denied() {
  local output status
  output=$("$@" 2>&1)
  status=$?
  printf '%s\n' "$output"
  [[ $status == 255 && $output == *"Permission denied ("* ]]
}
# No password is submitted: inspect the methods offered by the remote daemon.
# shellcheck disable=SC2317,SC2329
password_disabled() {
  local output status methods
  output=$(ssh -v -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=yes -o PubkeyAuthentication=no -o PreferredAuthentications=password,keyboard-interactive "$admin_user@$server_ip" true 2>&1)
  status=$?
  methods=$(printf '%s\n' "$output" | sed -n 's/^debug1: Authentications that can continue: //p')
  [[ $status == 255 && $output == *"Permission denied ("* && -n $methods ]] || return 1
  if printf '%s\n' "$methods" | grep -Eq '(^|,)(password|keyboard-interactive)(,|$)'; then
    printf 'Server still advertises password or keyboard-interactive authentication.\n' >&2
    return 1
  fi
}
ssh_args=(-o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=yes -i "$key_path")
check 'HTTP 200' http_status / 200
check 'Missing page returns 404' http_status /lab-validation-missing 404
check 'Dotfile path returns 403' http_status /.git/config 403
# Check the authenticated account without requiring a particular hostname.
if remote_user=$(ssh "${ssh_args[@]}" "$admin_user@$server_ip" 'id -un') && [[ $remote_user == "$admin_user" ]]; then
  printf 'PASS: Administrator key login works\n'
  check 'Root SSH denied by authentication policy' ssh_denied ssh "${ssh_args[@]}" "root@$server_ip" true
  check 'Regular account SSH denied by authentication policy' ssh_denied ssh "${ssh_args[@]}" "webuser@$server_ip" true
  check 'Password and keyboard-interactive authentication not offered' password_disabled
else
  printf 'FAIL: Administrator key login; negative SSH checks skipped\n' >&2
  failures=$((failures + 1))
fi
printf 'Failures: %s\n' "$failures"
exit "$failures"
