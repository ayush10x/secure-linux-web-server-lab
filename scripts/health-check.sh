#!/usr/bin/env bash
set -u

failures=0

check() {
  local description="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf 'PASS: %s\n' "$description"
  else
    printf 'FAIL: %s\n' "$description" >&2
    failures=$((failures + 1))
  fi
}

check "Nginx is active" systemctl is-active --quiet nginx
check "Nginx is enabled" systemctl is-enabled --quiet nginx
check "SSH is active" systemctl is-active --quiet ssh
check "UFW is active" bash -c "ufw status | grep -q '^Status: active$'"
# Called indirectly through check().
# shellcheck disable=SC2317
http_200() {
  local status
  status=$(curl --silent --show-error --max-time 5 --output /dev/null --write-out '%{http_code}' http://127.0.0.1/) || return 1
  [[ $status == 200 ]]
}
check "Local website returns HTTP 200" http_200
check "Site configuration is valid" nginx -t

root_use=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')
if [[ "$root_use" =~ ^[0-9]+$ ]] && (( root_use < 90 )); then
  printf 'PASS: Root filesystem usage is %s%%\n' "$root_use"
else
  printf 'FAIL: Root filesystem usage is %s%%\n' "${root_use:-unknown}" >&2
  failures=$((failures + 1))
fi

exit "$failures"
