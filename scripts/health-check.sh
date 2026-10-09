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
check "Local website returns HTTP 200" curl --fail --silent --show-error --max-time 5 http://127.0.0.1/
check "Site configuration is valid" nginx -t

root_use=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')
if [[ "$root_use" =~ ^[0-9]+$ ]] && (( root_use < 90 )); then
  printf 'PASS: Root filesystem usage is %s%%\n' "$root_use"
else
  printf 'FAIL: Root filesystem usage is %s%%\n' "${root_use:-unknown}" >&2
  failures=$((failures + 1))
fi

exit "$failures"
