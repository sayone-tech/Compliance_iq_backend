# Supporting Topics

Research that is **relevant to the MVP** but sits outside the confirmed security scope list in the parent [README](../README.md). It was moved here to keep the top level aligned to that list — **not** because it is future work and **not** because it was withdrawn.

The [security control matrix](../security-control-matrix.md), the [threat model](../threat-model.md) and the [risk register](../risk-register.md) still reference these documents, because several controls that implement PRD requirements are detailed here.

| Document | Why it is still relevant | PRD requirements it supports |
|---|---|---|
| [network-security.md](network-security.md) | Egress control, private service endpoints and the three-tier network are how exfiltration paths stop existing rather than being watched | Tenant isolation requirement, the EU residency requirement |
| [zero-trust-architecture.md](zero-trust-architecture.md) | The layered enforcement model on the path to evidence plaintext — the concrete shape of "strong multi-tenant isolation" and least privilege | Tenant isolation requirement, the automatic role enforcement requirement |
| [insider-threat-protection.md](insider-threat-protection.md) | Immutable audit requirement says not even SayOne administrators can alter the audit log. This document is what makes that structurally true | Immutable audit requirement, the non-deletable retention requirement, the tenant isolation requirement |
| [data-loss-prevention.md](data-loss-prevention.md) | Which exfiltration paths were eliminated, and what watermarking and rate limiting cover on the paths that must stay open | Tenant isolation requirement, the EU residency requirement |
| [threat-modelling.md](threat-modelling.md) | The method behind the threat model — how threat modelling stays a habit rather than a one-off document | supports all |
| [cross-border-data-processing.md](cross-border-data-processing.md) | **Conditional.** The PRD does not state where development, support or production administration happens. If any of it is outside the EU/EEA, this applies. Tied to open question L-1 | EU residency requirement, the GDPR processor requirement |

Nothing here adds MVP scope. Classification labels (**[PRD REQUIRED]** / **[PROPOSED]** / **[OPEN]** / **[FUTURE]**) apply exactly as in the parent set.
