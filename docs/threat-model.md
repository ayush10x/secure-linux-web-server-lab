# Threat model and trust boundaries

This is a design analysis, not an attack simulation or certification. Assets are administrative access, site integrity, service availability and recoverable content. The Mac/hypervisor, Ubuntu packages and authorized Client are trusted.

| Threat | Lab control and evidence | Residual risk / boundary |
|---|---|---|
| Unnecessary remote exposure | UFW default deny; SSH from `.201` only; HTTP from lab subnet; blocked Mac SSH probe | Host-only networking does not defend against a compromised Mac/hypervisor. NAT outbound traffic remains allowed. |
| Password guessing / unauthorized identities | Effective `sshd -T` disables root/password/interactive access and restricts `AllowUsers`; denial logs | Source IP is not user identity. Compromised Client/key and spoofing conditions on the trusted network require separate defenses. |
| Server impersonation | Reproduction guide requires console fingerprint comparison; verifier fails unknown/changed host keys | Historical enrollment was not separately captured as fingerprint evidence. Successful connection alone is not trusted enrollment proof. |
| Site tampering by worker | Root-owned site; Nginx group read but no write permissions | Root compromise bypasses permissions. No file-integrity monitoring or exploit-resistance assessment. |
| Content loss | Root-only archive, SHA-256 check, temporary restore comparison | Checksum detects accidental alteration, not attacker authenticity. Archive and checksum share one host; no off-host/full-VM recovery. |
| Disclosure or availability loss | Static private HTTP; reboot/access checks | HTTP is unencrypted; no TLS, denial-of-service testing, high availability or performance guarantee. |

The Client key is unencrypted: restrictive permissions help against other local users, not its owner or root. Protected keys, TLS, off-host backups and monitoring are future work, not implemented controls.

Root/webuser rejection with the administrator key alone cannot isolate the reason for rejection. Effective daemon settings and `AllowUsers` journal entries support the policy claim; Client probes are complementary behavioral evidence. See [verification evidence](verification-evidence.md).
