# Test Plan

Record date, tester, command/action, expected result, actual result, and pass/fail for every case.

| ID | Test | Expected result |
|---|---|---|
| WEB-01 | From client: `curl -I http://SERVER_HOST_ONLY_IP/` | HTTP 200 |
| WEB-02 | Reboot server, then repeat WEB-01 | Nginx starts automatically; HTTP 200 |
| SSH-01 | Log in as `ayush` with the approved key | Success; `sudo -v` succeeds |
| SSH-02 | Attempt direct root login | Denied |
| SSH-03 | Attempt password-only login after hardening | Denied |
| SSH-04 | Attempt login as `webuser` | Denied by `AllowUsers` |
| FW-01 | Inspect `sudo ufw status verbose` | Default deny incoming; only intended rules |
| FW-02 | Try SSH from an unauthorized lab IP | Denied or times out; authorized client still works |
| LOG-01 | Request a known and missing page | Access and 404 entries appear in Nginx logs |
| LOG-02 | Make one controlled failed SSH attempt | Failure appears in authentication logs |
| OPS-01 | Run health check | All checks pass; exit status 0 |
| BAK-01 | Run backup script and verify checksum | Archive lists cleanly; checksum passes |
| BAK-02 | Extract newest archive to `/tmp` and compare | Restored files match source |

Do not perform repeated password guesses or scans outside the private lab. After firewall tests, restore the client to its normal authorized IP and confirm access.
