# Simulated cybersecurity recruiter review

Reviewed 10 October 2026 by two independent AI subagents at the owner's request. A third subagent implemented the changes below. These are simulated assessments, not employer feedback, a hiring guarantee or security certification. Scores use subjective rubrics, not a standardized hiring benchmark.

## Before changes

| Reviewer | Lens / score | Rationale |
|---|---|---|
| 1 | Entry-level cybersecurity portfolio: **75/100** | Supporting Linux/security project with honest evidence and disclosure; reproduction and automated-test claims needed correction. Independent understanding remains unverified. |
| 2 | Technical security / operations screening: **78/100** | Good hardening and recorded evidence; setup paths and false-positive tests weakened reproducibility and automation confidence. |

Reviewer 1: fundamentals 18/20; evidence 17/25; reproducibility 13/20; presentation 16/20; role relevance 11/15. Reviewer 2: design 17/20; evidence 17/20; reproducibility 12/20; automation 14/20; communication 18/20. Different rubrics should not be averaged as a hiring metric.

Both considered the lab credible supporting evidence for junior Linux/security-hardening discussion, not proof of SOC/incident-response or production expertise. They recommended interviewing the owner about reproduction, reasoning and limits. Codex assistance remains disclosed.

## Findings and resolution

| Priority / finding | Change | Verification boundary |
|---|---|---|
| High: broken root-relative paths; overlapping installation routes | Correct `site/`, `config/`, `scripts/`; choose installer or manual steps; unlink lab site before restoring default | Documentation inspected; no new installation performed |
| High: any SSH exit255 mistaken for policy proof | Require positive key access, dedicated identity and authentication-denial diagnostics; inspect offered password/interactive methods | Offline fixtures exercise timeout, host-key and password-enabled cases; historical guest record retained with explanation |
| Medium: HTTP200 claim accepted other statuses | Exact status in health and Client scripts | Fixtures cover 200,204,302,500 and transport failure |
| Medium: incomplete account/network/trust reproduction | Locked account creation, labeled static-network templates, recovery and console fingerprint prerequisite | Templates are not newly executed guest evidence |
| Medium: trust boundary insufficiently explained | [Threat model](threat-model.md), interview learning prompts | Design analysis, not attack simulation |
| Medium: backup tool overstated verification | Output says archive listed and checksum written; independent check/restore required | Historical checksum and restore evidence unchanged |
| Low: navigation and CI clarity | 60-second path, reusable template label, offline fixtures, read-only CI token, VM artifact ignores | CI checks repository behavior, not guests |

## Remaining limits

Both reviewers inspected the revised files and independently reran the six offline tests; both accepted the core fixes with no remaining blocker. Their minor first-connection and startup-recovery documentation suggestions were incorporated. No post-fix numeric score was assigned.

No new live features, credential changes or hiring claims were added. Revised scripts have offline coverage only in this review; deployment/rerun remains separate. TLS, protected keys, off-host recovery, GUI troubleshooting and NTP synchronization remain disclosed future work. The owner should reproduce and explain the lab before presenting it as personal proficiency.
