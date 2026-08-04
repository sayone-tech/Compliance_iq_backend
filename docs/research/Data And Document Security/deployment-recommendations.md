# Deployment Recommendations

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Practical guidance for standing this architecture up, in the order it should be done. Everything here is **[PROPOSED]** unless marked.

## 1. Foundation before features

Do not write application code that touches client data until these exist. Retrofitting them costs several times as much.

| # | Action | Why it must be first |
|---|---|---|
| 1 | **Cloud organisation and account topology** inside the Client-owned account (`reference-cloud-architecture` §1, TI-01) | Account boundaries cannot be introduced later without a migration |
| 2 | **Organisation guardrails**: EU-only regions, no long-lived access keys, no disabling audit or detection services | Every subsequent resource inherits them; this is how NFR-03 becomes technical rather than procedural |
| 3 | **Control-plane audit trail across all accounts and regions → write-only log archive with write-once retention** | You cannot recover logs you never collected, and NFR-04 starts here |
| 4 | **Infrastructure as code with remote state and no console write access in production** | Manual drift from week one is unfixable culture |
| 5 | **Workforce identity with strong second factors for the whole team** | Every access decision afterwards depends on it |
| 6 | **Key hierarchy and key policy templates** — per-firm, audit, backup, sealing, with deletion denied where `key-management` requires | Encryption context and key policy shape the data model; NFR-02 is a schema decision, not a later toggle |
| 7 | **Repository with branch protection, signed commits, ownership rules, secret scanning** | Prevents the first secret leak |
| 8 | **Synthetic data fixture factory covering every FR-24 file type** | Blocks the "just copy a bit of production data" habit before it starts |
| 9 | **Region selection recorded as a decision** (`data-residency`) **[OPEN]** | Everything else inherits it |

**The single most consequential early decision is the tenant isolation model** — repository pattern, forced row-level security, per-firm key with encryption context. Everything else can be added incrementally; this cannot.

## 2. Sequencing principle

```
Guardrails → Identity → Keys → Data model with firm isolation
   → Upload pipeline → Audit logging → Record sealing and retention
      → WSP mapping → Monitoring and detection → Backup and restore testing
```

Resist building the WSP mapping feature first because it is the interesting part. Without audit logging and record sealing beneath it, a confirmed mapping is not the durable, attributable record FR-32 and FR-37 require, and it will be rebuilt.

Note that **both applications** must be delivered — the Firm Application and the Platform Admin Portal (PRD §1.1). The Portal is not a phase-two nicety: without it there are no test procedures for firms to run. Its authorisation boundary should be built at the same time as the Firm Application's, not bolted on.

## 3. Environment build order

1. **Development account first**, with the same guardrails as production. If a control is painful in development, fix it before it reaches production.
2. **Pre-production with full architectural parity** — same network layout, same policy layer, same key structure, synthetic data. A simplified pre-production environment is a source of false confidence.
3. **Production last**, deployed from the same modules with different parameters. If production needs bespoke configuration, the modules are wrong.

## 4. Roles this architecture assumes exist

**The PRD does not staff any of these.** They are listed so the gap is visible, not because they are assumed to be funded. Each is an **[OPEN]** decision for the Client.

| Capability needed | When it bites | If it is not funded |
|---|---|---|
| A named owner accountable for platform security | Before writing code | Nobody owns the control matrix, the risk register or the customer security questionnaire |
| Data protection expertise (may be external) | Before processing personal data | The DPIA, the DPA and the erasure question have no owner |
| Platform / infrastructure engineering | Foundation phase | Guardrails do not get built |
| Someone who answers a security alert out of hours | Before real client data | Detection exists with nobody to act on it (`security-monitoring`, K-08) |
| EU-resident production access capability, if delivery is partly non-EU | Before real client data | The cross-border question in `cross-border-data-processing` stays live |

Raise these as a resourcing conversation early. They have lead time, and the fixed-fee engagement model (CC-04) means late discovery is expensive for both sides.

## 5. Rollout of high-risk controls

Several controls are **irreversible or outage-causing if misconfigured**. Roll each out in this pattern:

| Control | Staged rollout |
|---|---|
| **Write-once retention in compliance mode** | Reversible mode in pre-production → reversible in production for a settling period → compliance mode, with retention derived only from the retention service |
| **Immutable backup vault lock** | Reversible mode → verify retention calculations → lock, understanding that the cooling-off period is the last chance to change it |
| **Default-deny egress** | Log-only mode, build the allowlist from observed traffic → alert mode → enforce |
| **WAF** | Count mode → block, with per-rule metrics and a documented exception path |
| **Forced row-level security** | Enable in pre-production with the full test suite → enable in production with a monitored rollback plan (a missing firm context fails closed, which is correct but visible) |
| **Artefact admission verification** | Audit mode → enforce in pre-production → enforce in production |
| **Mutual TLS between services** | Permissive → strict, service by service |
| **Zero standing access** | Reduce standing access progressively; measure break-glass frequency; do not flip to zero before the redacted-observability work is done |
| **Key-deletion denial and retention preconditions** | Enable early — this one is safe to turn on first and dangerous to defer |

**Never enable two irreversible controls in the same change window.**

## 6. Onboarding and data import

- **First firm onboarding is a control test.** Run it as a rehearsal with a design-partner firm, with security observing, and capture every friction point. The PRD's onboarding wizard (§5) already has a defined shape; the security-relevant parts are firm provisioning and role assignment.
- **Firm provisioning must be fully automated** — key creation, key policy, row-level-security context, storage prefixes, index namespace, retention profile. Manual tenant setup guarantees inconsistency, and inconsistency in tenant isolation is a breach waiting to happen (NFR-01).
- **Bulk import of existing evidence** — firms will arrive with years of material. It needs the same quarantine-scan-promote path, rate-limited, with progress reporting and a rollback that does not leave orphaned derivatives. Note that once imported material is attached to a test it becomes non-deletable (NFR-07), so **classification and correctness at import time matter more than usual**.
- **The revenue-source Excel and staff CSV uploads** (FR-04, FR-62) are structured-file parse paths and belong on the same hardened pipeline, not on a convenience endpoint.

## 7. Measure before committing

Benchmark these specifically — they are the ones that surprise teams:

| Item | Why | What to validate |
|---|---|---|
| Key-service request rate and latency under evidence load | Per-object data key generation can throttle | p99 decrypt latency and throttling rate at multiples of projected load |
| Synchronous audit write on evidence reads | Adds latency to the hot path | p99 impact against the **NFR-05 two-second dashboard target**; adjust the action classification empirically |
| Five-layer authorisation overhead | Policy evaluation per request | p99 authorisation latency, against NFR-05 |
| Concurrency | **NFR-05 promises 100 simultaneous users per firm without degradation** | Load test at that figure with realistic evidence sizes |
| Inference cost per mapping run | Re-runs are automatic on every new WSP version (§6.3) | Cost per run at realistic manual sizes; total at expected firm count |
| Mapping accuracy | **The 85% bar is a contractual commitment (§6.2)** | Measured against the agreed verification vectors before UAT, not during it |
| Storage growth | Six-year non-deletable retention, with video and ZIP admitted by FR-24 | Model at multiples of projected volume; use it to set the NFR-11 ceiling |
| Monitoring ingestion volume | The most common budget overrun | Model at multiples of projection; tier retention |
| Restore time | Any future recovery commitment depends on it | Measure twice before any figure is quoted |

**Do not quote an availability, recovery-time or recovery-point figure to a customer until it has been measured in a full test.** NFR-08's 99.5% is a target and TI-02 is still open.

## 8. Assurance sequencing

| Milestone | Prerequisite | Note |
|---|---|---|
| Data protection impact assessment | Data flows finalised | **[PROPOSED]** |
| Transfer position settled, if any delivery is non-EU | Counsel in both jurisdictions | **[OPEN — LEGAL]** (`cross-border-data-processing`) |
| Independent penetration test | Feature-complete pre-production with parity | Before real client data |
| Customer security pack | The above in draft | Ongoing |
| ISO 27001 / SOC 2 Type II | ISMS operating; a control observation window that cannot be compressed | **NFR-09 places these on the roadmap; TI-03 leaves the requirement open and the PRD says the timeline is to be agreed with the Client. No date is assumed here.** **[OPEN]** |

## 9. Documents to produce alongside the build

Requested in essentially every enterprise security review. Having them ready shortens due diligence substantially. Note **CC-03**: all of this is the Client's material, and publication is the Client's decision.

- Security overview: sanitised architecture and control summary
- Sanitised threat model summary (`threat-model`)
- Sub-processor list
- The DPA required by NFR-06
- Data classification and retention schedule (`immutable-evidence-retention`)
- Incident response and notification procedure (`security-monitoring`)
- Backup and restore summary with the most recent verification results
- Penetration test executive summary
- Business continuity and exit information, including data export format

## 10. Common failure modes to avoid

| Failure mode | How it manifests | Prevention |
|---|---|---|
| Building features before guardrails | Retrofit costs; a culture of exceptions | The foundation phase is non-negotiable |
| Simplified pre-production | Tests pass, production breaks | Full architectural parity |
| "Temporary" production access for launch | Becomes permanent | Zero standing access from day one; build the observability that makes it viable |
| Copying production data to debug | Residency and confidentiality breach | Synthetic-only enforced technically, not by policy |
| Enabling irreversible retention before the retention logic is correct | Permanent, unremovable data | Staged rollout per §5 |
| Deferring audit logging until "later" | Cannot scope the first incident; NFR-04 unmet | Audit event schema before the first data-handling endpoint |
| Building a delete path "for admin convenience" | **Direct breach of NFR-07** | No delete API for protected classes; static-analysis rule; negative tests |
| Quoting an SLA before measuring | Immediate breach of a commitment | Measure twice, then commit; TI-02 is still open |
| Building the Remediation Owner or Portal permissions before the scope questions are answered | Rework, or shipping the wrong visibility | Escalate FR-52/GAP-07 and SA-06/SA-08 before those sprints |
| Treating the 85% accuracy bar as a UAT-time discovery | A contractual commitment missed at the worst moment | Build the evaluation harness early and run it continuously |

## 11. Go / no-go criteria for accepting real client data

Do not accept real client data until every one of these is true:

- [ ] All Phase 1 **mandatory (M)** controls in `security-control-matrix` implemented and evidenced
- [ ] Cross-firm negative test matrix passing in CI, every system role × every action, with no skipped tests
- [ ] Negative tests proving that evidence, signed-off results, issued reports and audit entries **cannot be deleted or modified by any principal**, including an administrator
- [ ] Negative test proving that a per-firm key **cannot be deleted** while records are inside retention
- [ ] Independent penetration test completed; Critical and High findings remediated
- [ ] A restore verified successfully from an immutable backup, with measured timing, including decryption with the correct firm key and chain verification
- [ ] Data protection impact assessment completed and signed off
- [ ] Delivery topology settled; if any part is non-EU, the transfer position documented and the sub-processor disclosed
- [ ] Priority detections firing correctly in test, including the cross-firm and protected-record tripwires
- [ ] Incident response procedure exercised, including the firm notification template
- [ ] Zero standing production access confirmed by an identity audit — not asserted by policy
- [ ] Sub-processor list published; the NFR-06 DPA executed
- [ ] Region selection recorded; region restriction enforced technically
- [ ] Mapping accuracy measured at or above 85% against the agreed verification vectors
- [ ] Out-of-hours alert-response arrangement agreed, whatever form it takes
