# Supporting Topics

Research that is **relevant to the MVP** but sits outside the confirmed security scope list in the parent [README](../README.md). It was moved here to keep the top level aligned to that list — **not** because it is future work and **not** because it was withdrawn.

The [security control matrix](../security-control-matrix.md), the [threat model](../threat-model.md) and the [risk register](../risk-register.md) still reference these documents, because several controls that implement PRD requirements are detailed here.

| Document | Why it is still relevant | PRD requirements it supports |
|---|---|---|
| [network-security.md](network-security.md) | Egress control, private service endpoints and the three-tier network are how exfiltration paths stop existing rather than being watched | NFR-01, NFR-03 |
| [zero-trust-architecture.md](zero-trust-architecture.md) | The layered enforcement model on the path to evidence plaintext — the concrete shape of "strong multi-tenant isolation" and least privilege | NFR-01, FR-09 |
| [insider-threat-protection.md](insider-threat-protection.md) | NFR-04 says not even SayOne administrators can alter the audit log. This document is what makes that structurally true | NFR-04, NFR-07, NFR-01 |
| [data-loss-prevention.md](data-loss-prevention.md) | Which exfiltration paths were eliminated, and what watermarking and rate limiting cover on the paths that must stay open | NFR-01, NFR-03 |
| [threat-modelling.md](threat-modelling.md) | The method behind the threat model — how threat modelling stays a habit rather than a one-off document | supports all |
| [cross-border-data-processing.md](cross-border-data-processing.md) | **Conditional.** The PRD does not state where development, support or production administration happens. If any of it is outside the EU/EEA, this applies. Tied to open question L-1 | NFR-03, NFR-06 |

Nothing here adds MVP scope. Classification labels (**[PRD REQUIRED]** / **[PROPOSED]** / **[OPEN]** / **[FUTURE]**) apply exactly as in the parent set.
