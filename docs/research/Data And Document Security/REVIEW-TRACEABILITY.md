# REVIEW-TRACEABILITY

**Review of:** `docs/research/Data And Document Security/` — 35 research documents plus README and CLAUDE.md
**Against:** `docs/requirement-specification/PRD.md` — ComplianceIQ PRD v4.0, treated as the **sole source of truth**
**Outcome:** research set revised in place, then restructured so the top level maps onto the confirmed MVP security scope. This document records what was kept, what was reclassified, what was deferred, what was removed, how the folder was reorganised (§7a), and what the PRD cannot answer.

---

## 1. Executive verdict

The research set was technically strong and materially **over-scoped relative to the PRD**. Its security engineering — tenant isolation, key hierarchy, immutability, audit design, upload handling, pipeline security — maps cleanly onto what the PRD requires and has been retained largely intact.

Three classes of defect required correction:

1. **Unapproved decisions presented as settled.** A full technology stack (region, compute platform, database engine, service mesh, authorisation engine, AI provider and model), recovery objectives, a 99.9% availability figure, certification dates, staffing and on-call arrangements, and a delivery topology the PRD never states. ADRs carried "Accepted" status with invented deciders.
2. **Commercial and product scope the PRD does not contain.** Three-tier key custody, hold-your-own-key/external key store, EU sovereign-cloud paid tiers, an open-source evidence verifier CLI, eIDAS qualified timestamping, Merkle-root publication, enterprise assurance features, auditor roles, and a Phase 2/3 budget model. The PRD prices seat-based plans (CC-01) with no security tiering at all.
3. **Two substantive contradictions with the PRD.**
   - **Retention.** Earlier drafts adopted crypto-shredding as the answer to GDPR erasure, plus deletion sagas and soft-delete grace periods. NFR-07 and §2 state that evidence, results, reports and audit records **cannot be deleted by anyone including administrators**. Crypto-shredding achieves deletion by another name. This has been withdrawn everywhere and the underlying erasure conflict is now recorded as an open legal question rather than resolved.
   - **AI scope.** Earlier drafts described the product as producing "compliance assessments" and "regulator-ready AI conclusions". The PRD contains exactly one AI feature — AI-assisted WSP-to-rule mapping (§6.2) — whose output is explicitly advisory (FR-31) and gated by two-person approval (FR-32, FR-33). All assessment language has been removed.

Additionally, the regulatory perimeter was widened beyond the PRD: NIS2 was asserted as applicable, the AI Act as classified, and DORA critical-or-important-function designation as universal. All three are now marked conditional and requiring legal confirmation.

**The revised set is internally consistent and traceable to PRD requirement IDs.** No decision in it is presented as approved unless the PRD itself states it. Nothing was added to MVP scope.

---

## 2. Verification sweep

Checked across the final set for unsupported "accepted" decisions. Result: **none remain.**

| Term checked | Status in final set |
|---|---|
| AWS regions | No region named. Selection is **[OPEN]** (ADR-002, `open-questions` P-1). Only "AWS, EU data centre, Client-owned account" is asserted — TI-01 |
| Named AWS services (compute platform, database engine, mesh, policy engine, log/analytics services) | None selected. `reference-cloud-architecture` §3 lists selection criteria; ADR-002/ADR-008/DD-07-08/DD-10-11/DD-11-09 keep them open |
| Bedrock / Claude | No inference provider or model selected. ADR-008 is **PROPOSED (properties) / OPEN (provider)**. The one remaining "Claude Code" reference in `ai-governance` is a **developer tooling** citation, correctly scoped |
| EKS / Linkerd / Cedar / Aurora | Not present as selections. Referenced only as unselected categories |
| HYOK / XKS / customer-managed keys | **[FUTURE]** only — `customer-managed-encryption` (marked out of scope in its title) and `future-and-optional-scope` §1 |
| eIDAS / qualified timestamps / QTSP | **[FUTURE]** only — `future-and-optional-scope` §2, cross-referenced from `audit-logging`, `immutable-evidence-retention`, `architecture-diagrams`. Marked "not required by the PRD" |
| Post-quantum cryptography | **[FUTURE]** only. `encryption-architecture` retains algorithm-and-version identifiers (crypto agility), which is a PRD-neutral engineering practice, and explicitly makes no migration commitment |
| Merkle roots / external anchoring / verifier CLI | **[FUTURE]** only — `future-and-optional-scope` §2. `future-and-optional-scope` also notes CC-03 makes publication a Client decision |
| 99.9% uptime | Appears only as the **unresolved TI-02 question**. NFR-08's 99.5% *target* is the only figure stated |
| RTO / RPO | **No value proposed anywhere.** `disaster-recovery` states plainly that the PRD sets none; DD-16-02 and DD-16-05 are **[OPEN]**; DD-16-12 forbids committing an unmeasured figure |
| Warm standby / active-active | Not selected. Listed as one option the Client chooses once targets and costs are known (DD-16-05) |
| EU on-call staffing | Not asserted. DD-03-07 and `open-questions` P-8 record it as **[OPEN]** with a cost the PRD does not fund |
| India / offshore production access | No country named. `cross-border-data-processing` is explicitly **conditional** on an unanswered question (`open-questions` L-1) |
| Certification dates | None. NFR-09's roadmap placement is retained; `security-roadmap` and `open-questions` A-2 record the timeline as "to be agreed with the Client" |
| Enterprise security tiers | Removed. `customer-managed-encryption` states the PRD has no security tiering; CC-01 pricing is seat-based |
| "Accepted" ADR status | Removed. `architecture-decision-records` states explicitly that there is no "Accepted" status. No deciders are named |
| Crypto-shredding / soft delete / deletion sagas | Present only as **explicitly not adopted** — `document-confidentiality`, `key-management`, `immutable-evidence-retention`, `architecture-decision-records`, `future-and-optional-scope` §8 |
| Staffing (CISO, DPO, SRE, MDR, Head of Security, engineer counts) | Removed. Owners in `security-roadmap`, `risk-register` are "roles to be assigned"; `open-questions` P-9 records naming an owner as open |
| Budgets / durations / headcount | Removed. `security-roadmap` states it deliberately contains none, citing CC-04 |

---

## 3. Required findings retained — **[PRD REQUIRED]**

Every item below is retained because the PRD explicitly requires it. These are non-negotiable before real client data.

| Finding | PRD anchor | Where |
|---|---|---|
| Complete data isolation between firms, multi-tenant from day one | NFR-01, §2 | `document-confidentiality`, `identity-and-access-management`, `zero-trust-architecture`, `reference-cloud-architecture`, `security-control-matrix` §E |
| AES-256 at rest | NFR-02, §2 | `encryption-architecture` (DD-07-01), `security-control-matrix` §D |
| TLS 1.3 in transit | NFR-02 | `encryption-architecture` (DD-07-02), `security-control-matrix` §D |
| A distinct encryption key per firm; evidence in encrypted object storage under it | NFR-02, §2 | `encryption-architecture` (DD-07-03), `key-management`, `security-control-matrix` §D |
| All client data in EU data centres | NFR-03 | `data-residency` (DD-02-01), `security-control-matrix` §B |
| AWS, EU-resident data centre, account owned solely by the Client | TI-01 | `data-residency` (DD-02-02), `reference-cloud-architecture`, ADR-001 |
| Immutable append-only audit log; no modify or delete for any principal including SayOne administrators | NFR-04, FR-13, §2 | `audit-logging` (DD-14-01/02), ADR-004 |
| Audit record of actor, action, time and originating device for every user action | FR-13 | `audit-logging` (DD-14-01) |
| Minimum six-year retention across results, findings, evidence, remediation evidence, reports, audit and notification logs | NFR-07, §2 | `immutable-evidence-retention` (DD-15-01), `audit-logging` (DD-14-03), `security-control-matrix` §F |
| No deletion path for protected classes, for any user including administrators | NFR-07, §2 | `immutable-evidence-retention` (DD-15-02), `document-confidentiality` (DD-06-04), ADR-004 |
| Key destruction cannot become a deletion route — per-firm key deletion blocked while records are in retention | NFR-07 read with NFR-02 | `key-management` (DD-08-06), ADR-005 |
| Signed-off results correctable only by amendment with written explanation; original retained | FR-27 | `immutable-evidence-retention` (DD-15-03) |
| Issued reports permanently archived exactly as issued | FR-61 | `immutable-evidence-retention` (DD-15-04) |
| Every WSP version and every mapping change retained permanently | FR-37 | `immutable-evidence-retention` (DD-15-05) |
| N/A responses and sample-selection changes immutable and audited | FR-21b, FR-21c | `immutable-evidence-retention`, ADR-004 |
| Requirement ID and test procedure version history kept in full | SA-01, SA-02 | `immutable-evidence-retention` (DD-15-06) |
| Eight fixed system roles; firm role names map to exactly one system role | §3, §3.1, §3.2 | `identity-and-access-management` (DD-10-01) |
| Role-based access enforced automatically on every request | FR-09 | `identity-and-access-management` (DD-10-02) |
| Invitation-only account creation; role assigned before any access | FR-12 | `identity-and-access-management` (DD-10-03) |
| Email and password plus a phone-based second factor | FR-11 | `identity-and-access-management` (DD-10-04) |
| Users deactivated, never deleted; history preserved; reassignment documented and audited | FR-14 | `identity-and-access-management` (DD-10-06) |
| Minimum two Firm Super Admins, with a warning at one | FR-15 | `identity-and-access-management` (DD-10-07) |
| Platform Admin Portal on a separate login and interface, invisible to firm users | §1.1, §4 | `identity-and-access-management` (DD-10-08) |
| Exactly the FR-24 evidence file types accepted; anything else rejected at upload | FR-24 | `secure-media-storage` (DD-13-01) |
| Maximum file size as Portal configuration, changeable without a code release | FR-24, NFR-11 | `secure-media-storage` (DD-13-02) |
| Uploaded evidence non-deletable and permanently linked to its test | §7.1 step 5, NFR-07 | `secure-media-storage` (DD-13-03) |
| AI mapping output is advisory; a compliance officer confirms or adjusts | FR-31 | `ai-governance` (DD-05-06), ADR-007 |
| Two independent senior approvers; the policy author cannot be one | FR-32 | `ai-governance`, ADR-007 |
| Reversal of a confirmed mapping follows the same two-person process, permanently recorded | FR-33 | `ai-governance` (DD-05-07) |
| Mapping re-runs automatically on a new labelled WSP version; manual overrides visibly tagged | §6.3 (GAP-09 answer) | `ai-governance` (DD-05-08) |
| Minimum 85% verified mapping accuracy at UAT against pre-defined verification text vectors | §6.2 (accepted 3 Jul 2026) | `ai-governance` (DD-05-09), `security-control-matrix` §I |
| GDPR processor obligations under a DPA | NFR-06 | `regulatory-obligations` (DD-01-01), `security-control-matrix` §A |
| MiCA and DORA treated as customer-domain regulations the product serves | Title block, §1 | `regulatory-obligations` (DD-01-02) |
| Availability *target* of 99.5%, planned maintenance communicated in advance | NFR-08 | `disaster-recovery` (DD-16-01) |
| Dashboard within two seconds; 100 concurrent users per firm as the load-test figure | NFR-05 | `reference-cloud-architecture`, `open-questions` T-2/T-3 |
| Single cloud provider (AWS) with a documented concentration analysis | TI-01 | `supply-chain-security` (DD-18-09) |
| Licence deny-list derived from CC-03's exclusive assignment of all code to the Client | CC-03 | `supply-chain-security` (DD-18-08) |

## 4. Recommendations retained, marked **[PROPOSED]**

These are reasonably necessary to implement a PRD requirement, but the PRD does not select them. **None is a commitment.** Representative set — the full list is the `DD-nn-nn` tables in each topic document and the `[PROP]` rows in `security-control-matrix`.

| Area | Recommendation | Implements |
|---|---|---|
| Isolation | Layered enforcement — repository scoping, forced row-level security, per-firm key with firm-bound encryption context, per-request authorisation | NFR-01 |
| Isolation | Cross-firm negative test matrix (every system role × every action) as a **blocking CI gate** | NFR-01 |
| Cryptography | Envelope encryption; AES-256-GCM with mandatory additional authenticated data binding the firm identifier; single approved crypto module | NFR-02 |
| Cryptography | Algorithm and version identifier on every ciphertext and signature (crypto agility, no migration committed) | NFR-02 + NFR-07 horizon |
| Keys | Separate keys with distinct administrative roles for audit, backup and evidence sealing; separation of key administration from data-plane decrypt | NFR-02, NFR-04 |
| Residency | Region restriction enforced by organisation and resource policy, not convention; residency applied to observability, error tracking, email, support tooling and CI | NFR-03 |
| Residency | Extracted text, OCR output, embeddings, search index entries and filenames treated as client data for residency purposes | NFR-03 |
| Audit | Operational logs separated from audit events; redaction by construction enforced by static analysis; hash-chained writes to write-once storage; per-endpoint coverage tests | NFR-04 |
| Retention | Retention service as the single source of truth, with per-class minimums and legal hold; write-once object retention derived from it | NFR-07 |
| Uploads | Quarantine-scan-promote; multi-engine scanning, fail closed; parsing in a separate account with no credentials and no egress; content-type by inspection | FR-24, FR-30 |
| Access | Watermarked server-side preview as the default access mode; raw download separately granted and logged; short-lived single-use signed URLs | NFR-01 |
| Access | Zero standing production privilege; dual-approved, time-boxed, session-recorded elevation | NFR-04, FR-13 |
| WSP mapping | EU-resident inference under no-training, no-retention terms; untrusted-content delimiting; schema-constrained output; deterministic verification that each cited span exists at the stated offset | FR-31, NFR-03 |
| WSP mapping | Evaluation harness against the agreed verification vectors, gating promotion at the 85% bar | §6.2 |
| Supply chain | Signed artefacts with provenance and attestations; admission verification; bill of materials with continuous re-evaluation; pinned dependencies | integrity of NFR-01/NFR-04 |
| CI/CD | Zero long-lived credentials; ephemeral EU-resident runners; separate build and deploy identities, neither able to read client data | integrity of the platform |
| Backups | Backup account with no trust path from production; immutable retention lock; automated restore verification with decryption and chain assertions | protects NFR-07 |
| Detection | Detections as code with tests; cross-firm and protected-record tripwires; canary records per firm | NFR-01, NFR-04, NFR-07 |
| Insider | Mutually exclusive capability matrix; dual authorisation on irreversible actions; per-role access rate limits | NFR-04, NFR-01 |
| Assurance | Data protection impact assessment; published sub-processor list; independent penetration test before real client data | NFR-06 |

## 5. Moved to future scope — **[FUTURE]**, indexed in `future-and-optional-scope`

Retained as background, **not planned, priced or approved**. Bringing any of it back requires the `future-and-optional-scope` §"How to bring something back into scope" process and, per CC-04 and the §16 baseline-freeze note, a contract amendment.

| Item | Reason for deferral |
|---|---|
| T1/T2/T3 encryption and sovereignty product tiers | The PRD has no security tiering; CC-01 pricing is seat-based |
| Customer-managed keys, hold-your-own-key, external key store (HYOK/XKS) | Not in the PRD; and would let a firm make its own six-year records unreadable, colliding with NFR-07 |
| EU sovereign-cloud paid offerings | Not in the PRD; TI-01 fixes AWS on a Client-owned account |
| Post-quantum cryptography migration | No PRD requirement, no timeline to align to. Crypto agility (the expensive part) is retained |
| Nitro Enclaves / enclave-based decryption | Not in the PRD |
| Open-source evidence-verification CLI | Not in the PRD; CC-03 makes publication of any platform code a Client decision |
| eIDAS-qualified timestamp integration | Not in the PRD. Noted as the strongest single available upgrade to the evidence story if the Client ever wants a differentiator |
| Merkle-root publication and external cryptographic anchoring | Not in the PRD |
| Steganographic watermarking | Visible per-user watermarks are proposed; steganographic marking is not |
| Advanced behavioural analytics, customer lockbox access, purple-team programmes | Recurring staffing cost the PRD does not fund; lockbox also depends on the unresolved SA-06/SA-08 boundary |
| TIBER-EU / TLPT participation | A customer-side obligation that may or may not reach the platform by contract; unconfirmed |
| Private bug-bounty programme | Recurring cost and triage capacity the PRD does not fund |
| ISO 27701, EU Cloud Code of Conduct | Not in the PRD |
| Enterprise APIs, external auditor/regulator roles, customer-facing assurance features | TI-05 leans "later phase"; an auditor role would add a ninth role and a new authorisation surface |
| On-premise or customer-hosted deployment | Contradicts TI-01 |
| Travel Rule data architecture | A customer-domain obligation; no PRD requirement reaches the platform |
| Firm-visible exportable audit trail, firm-granular point-in-time restore, degraded modes, entity pseudonymisation | Genuinely valuable and **[PROPOSED]** for post-MVP in `security-roadmap` — but outside the MVP baseline |

## 6. Removed or corrected deviations

| Deviation in earlier drafts | Why it was wrong | Correction |
|---|---|---|
| **Crypto-shredding adopted as the GDPR erasure answer** | Renders six-year records unreadable — contradicts NFR-07 and §2 on their face | Withdrawn everywhere. Explicitly **not adopted** (`document-confidentiality`, `key-management`, `immutable-evidence-retention`, `architecture-decision-records`, `future-and-optional-scope` §8). Erasure conflict recorded as **[OPEN — LEGAL]** (`open-questions` L-3) |
| Deletion sagas, 30-day soft deletion, five-year and seven-year retention defaults, twelve-month backup caps | Not PRD figures; several weaken NFR-07 | All removed. Six years is a **minimum**, not a ceiling; whether retention ever ends is **[OPEN — LEGAL]** (`open-questions` L-4) |
| Product described as producing "compliance assessments" and "regulator-ready AI conclusions" | The PRD's only AI feature is advisory WSP-to-rule mapping (FR-31) | All assessment language removed; `ai-governance` opens by stating what the AI feature actually is |
| Bedrock / Claude named as the inference path | The PRD names no provider or model | ADR-008 keeps the *properties* (EU-resident, no-training, no-retention) **[PROPOSED]** and the *provider* **[OPEN]** (`open-questions` P-6) |
| `eu-central-1` primary with `eu-north-1` warm standby | The PRD names no region and no recovery architecture | No region named; ADR-002 **[OPEN]**. Recovery architecture is a Client selection (DD-16-05) |
| EKS + Linkerd + Aurora + Cedar named as the stack | The PRD selects none of them | Replaced with role-labelled components and explicit selection criteria (`reference-cloud-architecture` §3); diagrams relabelled (`architecture-diagrams`) |
| RTO/RPO values and a warm-standby commitment | The PRD sets no RTO, no RPO and no DR obligation | No figure proposed. DD-16-12 forbids committing an unmeasured figure |
| 99.9% availability treated as the target | NFR-08 states 99.5% as a *target*; TI-02 records the choice as an open estimation blocker | 99.9% appears only as the open question |
| ISO 27001 / SOC 2 delivery dates in a phased roadmap | NFR-09 places them on the roadmap with the timeline "to be agreed with Sosinna's team" | Dates removed; timing is **[OPEN]** (`open-questions` A-2) |
| Three-tier key custody as an accepted architecture and commercial differentiator | Unsupported by the PRD; no security tiering exists | Withdrawn; `customer-managed-encryption` retitled **FUTURE / OUT OF MVP SCOPE** and reduced to background |
| eIDAS qualified timestamps + Merkle roots + open-source verifier as a "load-bearing decision" and "competitive moat" | Not required by the PRD; CC-03 affects publication | Moved to `future-and-optional-scope` §2; `audit-logging`, `immutable-evidence-retention`, `architecture-diagrams` reference it as **[FUTURE]** only |
| NIS2 asserted as directly applicable; AI Act classification asserted; every customer assumed to designate the platform as supporting a DORA critical or important function | The PRD confirms none of this | All three now conditional and requiring legal confirmation (`regulatory-obligations`, `open-questions` L-5/L-6, ADR framing) |
| Development in India stated as fact; EU→India transfer analysis presented as the operating model | The PRD does not state where development, support or administration happens | `cross-border-data-processing` reframed as **conditional** on the unanswered question (`open-questions` L-1) with no country named |
| "EU-resident production on-call hiring" as a required lead-time item; a 6–10 engineer team plus a security lead | The PRD does not staff the project | Removed. Owners are "roles to be assigned"; funding out-of-hours response is **[OPEN]** (`open-questions` P-8) |
| Named deciders (CEO, CTO, Head of Security, DPO, SRE Lead, Head of Product) on ADRs and maintenance tables | Fabricated approvals | All removed. Naming an owner is **[OPEN]** (`open-questions` P-9) |
| ADRs marked "Accepted" | No such approval exists | Status vocabulary replaced with PRD REQUIRED / PROPOSED / OPEN — STAKEHOLDER DECISION REQUIRED / FUTURE. `architecture-decision-records` states there is no "Accepted" |
| Phase 2/3 budgets, durations and commercial security tiers | Misrepresents a fixed-price milestone contract (CC-04) | `security-roadmap` now states it deliberately contains no durations, headcount or budget |
| Risks marked accepted | Nobody accepted them | `risk-register` §"Residual risks proposed for acceptance" is explicitly **NOT YET ACCEPTED** |
| "Sell into tier-1 CASPs" as a fixed launch target driving DORA voluntary compliance | Not a PRD statement | Removed |

## 7. PRD traceability — by research document

| Doc | Dominant content | Classification | PRD anchor | Conflict / gap | Action taken |
|---|---|---|---|---|---|
| [executive-summary](executive-summary.md) | Whole-set framing | Mixed | NFR-01→NFR-09, TI-01, §6 | Asserted stack, tiers, eIDAS moat, India, on-call, crypto-shredding, NIS2/AI Act | **Rewritten** around what the PRD fixes; deviations listed in its §9 |
| [regulatory-obligations](regulatory-obligations.md) | Two regulatory personas; obligation register | PRD REQUIRED + OPEN — LEGAL | NFR-06, MiCA/DORA scope, NFR-08, NFR-09 | NIS2/AI Act/CRA asserted | **Rewritten**: perimeter is GDPR (platform) + MiCA/DORA (customer). Others conditional |
| [data-residency](data-residency.md) | Every copy, index, cache, log, key in the EU | PRD REQUIRED + PROPOSED | NFR-03, TI-01 | Region was pre-selected | **Kept**; region made **[OPEN]** (DD-02-03) |
| [cross-border-data-processing](supporting-topics/cross-border-data-processing.md) | Offshore access analysis | PROPOSED, conditional | NFR-03, NFR-06 | PRD does not state delivery location | **Reframed as conditional**; no country named; L-1/L-2 opened |
| [secure-sdlc](secure-sdlc.md) | Gates, review, vulnerability SLAs, pen test | PROPOSED | supports NFR-01/04/07 | TIBER-EU and bug bounty asserted | **Kept**; those two moved to **[FUTURE]** |
| [ai-governance](ai-governance.md) | Dev tooling vs. WSP mapping path | PRD REQUIRED + PROPOSED + OPEN | FR-30, FR-31, FR-32, FR-33, §6.2, §6.3 | Assessment language; provider pre-selected | **Rewritten**: mapping-only, advisory, 85% harness; provider **[OPEN]** |
| [document-confidentiality](document-confidentiality.md) | Tenant isolation layers, classification, derivatives | PRD REQUIRED + PROPOSED | NFR-01, NFR-07 | Soft delete / shredding | **Kept**; deletion mechanisms explicitly not adopted |
| [encryption-architecture](encryption-architecture.md) | AES-256, TLS 1.3, envelope encryption, agility | PRD REQUIRED + PROPOSED | NFR-02 | Post-quantum commitment; mesh product named | **Kept**; PQC **[FUTURE]**; mesh **[OPEN]** |
| [key-management](key-management.md) | Per-firm keys, policies, deletion denial | PRD REQUIRED + PROPOSED + OPEN | NFR-02, NFR-07 | Crypto-shredding as erasure | **Kept**; DD-08-07 records shredding as not adopted |
| [secrets-management](secrets-management.md) | Zero long-lived credentials | PROPOSED | supports NFR-01/04 | none material | **Kept** |
| [identity-and-access-management](identity-and-access-management.md) | Eight roles, invitation-only, MFA, zero standing privilege | PRD REQUIRED + PROPOSED + OPEN | §3, FR-09→FR-15 | Policy engine named; auditor role assumed | **Kept**; engine **[OPEN]**; auditor role **[FUTURE]** |
| [network-security](supporting-topics/network-security.md) | Tiering, egress control, no bastions | PROPOSED | supports NFR-01/03 | Mesh product named | **Kept**; DD-11-09 **[OPEN]** |
| [zero-trust-architecture](supporting-topics/zero-trust-architecture.md) | Layered enforcement, device posture, purpose binding | PROPOSED | implements NFR-01 | Firm-user device trust assumed | **Kept**; that item **[FUTURE]** |
| [secure-media-storage](secure-media-storage.md) | Quarantine-scan-promote, sandboxed parsing | PRD REQUIRED + PROPOSED + OPEN | FR-24, NFR-11, FR-30 | File-size ceiling asserted | **Kept**; ceiling **[OPEN]** (P-4) |
| [audit-logging](audit-logging.md) | Append-only, hash-chained, coverage-tested | PRD REQUIRED + PROPOSED | NFR-04, FR-13, NFR-07 | External anchoring asserted | **Kept**; anchoring **[FUTURE]** |
| [immutable-evidence-retention](immutable-evidence-retention.md) | Six-year non-deletable classes, sealing, legal hold | PRD REQUIRED + PROPOSED + OPEN — LEGAL | NFR-07, §2, FR-27, FR-61, FR-37 | Shredding; retention ceilings; verifier tool | **Kept**; conflicts opened as L-3/L-4; verifier **[FUTURE]** |
| [disaster-recovery](disaster-recovery.md) | Recovery shape and how to set targets | PRD REQUIRED + PROPOSED + OPEN | NFR-08, TI-02, NFR-07 | RTO/RPO/warm standby/99.9% asserted | **Rewritten**: no figure proposed; DD-16-02/05 **[OPEN]** |
| [insider-threat-protection](supporting-topics/insider-threat-protection.md) | Prevention-first, separation of duties, dual authorisation | PRD REQUIRED + PROPOSED + OPEN — LEGAL | NFR-04, NFR-01 | Lockbox and behavioural analytics asserted | **Kept**; both **[FUTURE]**; monitoring lawfulness **[OPEN — LEGAL]** (L-8) |
| [supply-chain-security](supply-chain-security.md) | Pinning, signing, attestation, SBOM, vendor intake | PROPOSED + PRD REQUIRED (provider) | TI-01, CC-03 | Register-of-information extract asserted | **Kept**; that item **[FUTURE]** |
| [secure-cicd](secure-cicd.md) | Trust zones, federation, ephemeral runners | PROPOSED | supports platform integrity | none material | **Kept** |
| [customer-managed-encryption](future-scope/customer-managed-encryption.md) | Key custody tiers | **[FUTURE]** | contradicted CC-01, NFR-02 | Whole document was out of scope | **Retitled and reduced** to background; withdrawal stated in the document |
| [secure-backups](secure-backups.md) | Isolated backup account, immutable lock, restore verification | PROPOSED + OPEN | protects NFR-07 | Twelve-month cap; RPO | **Kept**; schedule **[OPEN]** (DD-21-04); no RPO |
| [security-monitoring](security-monitoring.md) | Detections as code, high-fidelity alerting | PROPOSED | detects NFR-01/04/07 breach | MDR/on-call staffing asserted | **Kept**; response funding **[OPEN]** (P-8) |
| [data-loss-prevention](supporting-topics/data-loss-prevention.md) | Eliminate paths, inspect the remainder | PROPOSED | serves NFR-01, NFR-03 | Steganographic watermarking asserted | **Kept**; steganography **[FUTURE]** |
| [threat-modelling](supporting-topics/threat-modelling.md) | Three-tier programme, methodology | PROPOSED | supports all | Bug bounty and recurring adversarial exercises asserted | **Kept**; both **[FUTURE]** |
| [reference-cloud-architecture](reference-cloud-architecture.md) | Account topology, data plane, residency boundary | PRD REQUIRED (§0) + PROPOSED + OPEN | TI-01, NFR-01/02/03/04/05/07/10 | Full stack pre-selected | **Rewritten**: §0 lists what the PRD fixes; everything else unselected with criteria |
| [security-control-matrix](security-control-matrix.md) | 141 controls, A–K | **[PRD]** / **[PROP]** / **[OPEN]** per control | mapped per row | Controls existed for out-of-scope features | **Rewritten**: classification column added, PRD anchors added, out-of-scope controls removed to `future-and-optional-scope` |
| [threat-model](threat-model.md) | Assets, boundaries, actors, scored threats, attack trees | Analysis | Assets anchored to PRD IDs | Threats against removed features | **Rewritten**: assets anchored to PRD, threats rescored, top residual list reflects unresolved decisions |
| [architecture-diagrams](architecture-diagrams.md) | Mermaid set | Illustrative | mirrors `reference-cloud-architecture` | Diagrams showed named products | **Rewritten**: role-labelled, not product-labelled; future items shown dashed |
| [deployment-recommendations](deployment-recommendations.md) | Build order, staged rollout, go/no-go | PROPOSED | gates NFR-01/02/04/07, §6.2 | Certification dates, staffing | **Kept**; §11 now includes the 85% measurement and the non-deletability negative tests |
| [security-roadmap](security-roadmap.md) | Two MVP phases, gated by capability | Mixed, per row | per row | Four dated phases with budgets | **Rewritten**: no durations, headcount or budget; post-MVP list explicitly uncommitted |
| [open-questions](open-questions.md) | Questions this set cannot settle | **[OPEN]** | PRD-flagged items carried through | Earlier version supplied "recommended defaults" | **Rewritten**: interim positions explicitly labelled *not decisions*; PRD-flagged items grouped as section A |
| [risk-register](risk-register.md) | Scored risks | Analysis | controls traced to `security-control-matrix` | Risks marked accepted; named owners | **Rewritten**: owners are roles to assign; acceptance section marked NOT YET ACCEPTED |
| [architecture-decision-records](architecture-decision-records.md) | 14 ADRs | PRD REQUIRED / PROPOSED / OPEN / FUTURE | cited per ADR | All were "Accepted" with invented deciders | **Rewritten**: status vocabulary replaced; every PRD-required ADR cites its requirement ID |
| [future-and-optional-scope](future-scope/future-and-optional-scope.md) | Everything deferred | **[FUTURE]** | none — that is the point | — | **New document** |
| README | Index and conventions | — | — | Stale scope, stale counts, invented owners | **Rewritten** around the confirmed scope list |
| CLAUDE.md | Project context for tooling | — | — | Stale | **Rewritten** |
| [supporting-topics/README](supporting-topics/README.md) | Why the moved topics still matter and what they support | — | — | — | **New document** |
| [future-scope/README](future-scope/README.md) | What is deferred and on what terms | — | — | — | **New document** |

---

## 7a. Restructure applied after the content review

Following Client instruction, the folder was reorganised so that the top level maps one-to-one onto the confirmed security scope for the MVP. **No document was deleted and no content was dropped in the move.**

**Filenames:** leading `NN-` numeric prefixes removed throughout. Every internal cross-reference — markdown links, prose "doc NN" references, and the "Doc" columns of the control matrix and roadmap — was rewritten to the new names. `05-ai-assisted-development-governance.md` became `ai-governance.md`, because the document is mainly about the WSP mapping feature rather than developer tooling and the old name obscured that.

**Top level — the confirmed scope:**

| Confirmed scope item | Document |
|---|---|
| EU-only storage of client data | `data-residency` |
| AWS as the selected cloud provider; Client-owned AWS account | `reference-cloud-architecture` (ADR-001) |
| AES-256 at rest and TLS 1.3 in transit | `encryption-architecture` |
| Per-tenant encryption keys | `key-management`, `encryption-architecture` |
| Strong multi-tenant isolation | `document-confidentiality`, `identity-and-access-management` |
| Immutable audit logging | `audit-logging` |
| Non-deletable evidence and signed-off records | `immutable-evidence-retention` |
| MFA and least-privilege role enforcement | `identity-and-access-management` |
| Secure document upload, malware inspection, sandboxed parsing | `secure-media-storage` |
| Secure backups and tested recovery — SLA/RTO/RPO remain proposals | `secure-backups`, `disaster-recovery` |
| Human approval of AI-generated WSP mappings | `ai-governance` |
| Prompt-injection and hallucination controls for WSP mapping | `ai-governance` |
| Secure SDLC, secrets management, vulnerability scanning, supply chain | `secure-sdlc`, `secrets-management`, `supply-chain-security`, `secure-cicd` |
| EU residency checks for AI inference over customer documents | `data-residency`, `ai-governance` |
| Incident monitoring and customer notification for DORA support | `security-monitoring`, `regulatory-obligations` |

Plus the consolidated deliverables, which serve the whole list: `reference-cloud-architecture`, `security-control-matrix`, `threat-model`, `architecture-diagrams`, `deployment-recommendations`, `security-roadmap`, `open-questions`, `risk-register`, `architecture-decision-records`.

**`supporting-topics/`** — MVP-relevant depth outside the confirmed list, moved rather than removed because the control matrix, threat model and risk register still cite it: `network-security`, `zero-trust-architecture`, `insider-threat-protection`, `data-loss-prevention`, `threat-modelling`, and the conditional `cross-border-data-processing`.

**`future-scope/`** — nothing in the MVP: `future-and-optional-scope` and `customer-managed-encryption`.

**Scope effect of the restructure: none.** No requirement was added or removed, no classification changed, and no proposal became a commitment. In particular, `secure-backups` and `disaster-recovery` remain at the top level *with* their SLA, RTO and RPO positions unchanged — none is proposed as a value, and DD-16-12 still forbids committing an unmeasured figure.

---

## 8. Remaining stakeholder and legal questions

These **cannot be resolved from the PRD**. Nothing in the revised set answers them by default. Full detail, with interim engineering positions marked as non-decisions, is in [Open Questions](open-questions.md).

### Recorded as open by the PRD itself

| PRD ref | Question | Security consequence |
|---|---|---|
| **TI-02** | 99.5% or 99.9% availability? | Determines the entire recovery investment. No RTO/RPO can be set until this is answered |
| **TI-03** | Are ISO 27001 / SOC 2 Type II required by clients to sign? | NFR-09 timing; assurance planning |
| **TI-05** | Public API in v1 or later? | A new authenticated surface with its own authorisation model |
| **TI-06** | How many firms in Year 1? | Key-service volume, storage growth over six non-deletable years, monitoring cost |
| **SA-06 / SA-08** | How much firm data may the Platform Admin Portal team see? | **An authorisation boundary. It cannot be built twice cheaply** |
| **FR-52 vs GAP-07** | Remediation Owner: own tasks only, or view everything? *(the PRD flags this contradiction itself)* | The permission set for one of the eight system roles |
| **GAP-09** | Who may initiate a manual override of a WSP mapping? | Who can change a mapping that two people must then approve |
| **GAP-11** | Does deactivation force-prompt reassignment of open items? | The FR-14 flow and its audit trail |
| **FO-07** | Who may complete the onboarding wizard? | Authorisation on a high-impact flow |
| **RE-05** | News feed sourcing — manual, automated, or commercial? | Any automated source is an outbound integration needing an egress allowlist entry and a residency review |

### Legal — require qualified counsel

| # | Question |
|---|---|
| L-1 | **Where will development, support and production administration be performed?** The PRD does not say. Everything in `cross-border-data-processing` is conditional on this |
| L-2 | If any of it is outside the EU/EEA: is the transfer position defensible, and with what supplementary measures? |
| L-3 | **How do GDPR erasure requests interact with the PRD's non-deletability rule?** (§2, NFR-07 vs GDPR Art. 17). A genuine conflict. **Not resolved here, and not resolved by overriding the PRD** |
| L-4 | When, if ever, does retention end after the six-year minimum? NFR-07 sets a floor and no ceiling |
| L-5 | Is the platform in NIS2 scope, and in which member state? |
| L-6 | AI Act classification of AI-assisted WSP mapping |
| L-7 | Does the platform ship anything that would trigger CRA scope? |
| L-8 | Employment-law constraints on security monitoring where staff are employed |
| L-9 | What incident-notification deadline to client firms will be contracted? |
| L-10 | Will any customer contractually impose DORA Chapter V terms (audit rights, exit assistance, subcontractor inspection)? |

### Client and product decisions

| # | Question |
|---|---|
| P-1 | **Which EU region?** Blocks completion of the foundation phase |
| P-2 | How is infrastructure provisioned into and handed over inside the Client-owned AWS account (TI-01)? Who holds root and break-glass custody? |
| P-3 | Is a second EU region funded for record copies and/or recovery? |
| P-4 | What is the configured maximum evidence file size (NFR-11)? |
| P-5 | What concrete second factor satisfies FR-11's "verification step on their phone"? |
| P-6 | **Which AI inference provider and model**, with what residency, no-training and no-retention terms? |
| P-7 | Does FR-59 distribute the report as an attachment or as an authenticated link? |
| P-8 | Is out-of-hours alert response funded, and in what form? |
| P-9 | **Who is the named owner accountable for platform security?** |
| P-10 | Is a coordinated vulnerability disclosure policy published, given CC-03? |
| P-11 | Are firms' own auditors or regulators expected to be given direct scoped access? |

### Technical — require a spike or benchmark

`open-questions` §D. The one that carries contractual exposure: **T-4 — what retrieval and prompting architecture actually reaches 85% on the agreed verification vectors.** That is a commitment under §6.2, not a stretch goal, and it should be spiked against real WSP documents before the approach is fixed.

---

## 9. Constraints observed in this review

- `PRD.md` was **not modified**.
- **No requirement was added to the MVP.** Every retained item is either PRD-required or an implementation recommendation clearly labelled as such.
- **No recommendation was converted into a commitment**, and no stakeholder approval was fabricated.
- Citations supporting removed material were removed with it; citations supporting retained material were preserved.
- Where the PRD leaves a question open, the revised set leaves it open — including where that is inconvenient for engineering.
