# Future and Optional Scope

> **Nothing in this document is part of the ComplianceIQ MVP.**
>
> Everything listed here appeared in earlier drafts of this research set as an accepted decision, a roadmap commitment or a product tier. **None of it is supported by PRD v4.0.** It is collected here so the material is not lost and so any of it can be scoped quickly if the Client later wants it — not because any of it is planned, priced or approved.
>
> Adding any item to scope would be a change to a fixed-price milestone contract (the fixed-price milestone engagement model) and requires Client approval.

---

## 1. Encryption and key custody

| Item | Why it was proposed | Why it is out of scope | Blocking consideration |
|---|---|---|---|
| **Customer-managed keys (BYOK)** | Lets a firm revoke access unilaterally | The PRD's encryption requirement is per-firm **platform-managed** keys (the encryption requirement) | See `customer-managed-encryption` |
| **Hold-your-own-key / external key store (HYOK/XKS)** | Complete technical answer to third-country access concerns | Not in the PRD; not needed given the account is Client-owned (the confirmed cloud decision) | Would let a firm make its own six-year records unreadable, colliding with the non-deletable retention requirement |
| **T1 / T2 / T3 encryption or sovereignty tiers** | A commercial differentiator | The PRD's pricing model is seat-based with two plan structures (the pricing model decision) and contains no security tiering | Would require a pricing-model amendment |
| **Post-quantum cryptography** — hybrid key exchange, dual-signed long-lived records, a migration status field in the key register | Harvest-now-decrypt-later is a real concern for long-retained records | No PRD requirement; no committed timeline exists to align to | **Partially mitigated already:** `encryption-architecture` requires an algorithm and version identifier on every ciphertext and signature, which is the expensive part of crypto agility. The swap itself becomes cheap later |
| **Confidential computing enclaves** for key brokering and document decryption | Would prevent even infrastructure administrators from reading plaintext | Significant operational complexity and platform lock-in for a team of this size | Would strengthen `insider-threat-protection`'s insider position materially if ever funded |
| **Dedicated single-tenant hardware security modules** | Answers "shared HSM" objections | Roughly an order of magnitude more cost and real operational burden; not required by the encryption requirement | — |

## 2. Evidence verifiability

| Item | Why it was proposed | Why it is out of scope |
|---|---|---|
| **eIDAS qualified timestamps from a trust service provider** | Would convert the platform's technical integrity claim into a legal presumption under Regulation (EU) 910/2014 Art. 41 | Not required by the PRD. Genuinely the strongest single upgrade available to the evidence story, and the best candidate on this list if the Client wants a differentiator |
| **Daily Merkle-root computation and publication to a customer-visible append-only feed** | Lets firms verify inclusion without trusting the platform | Not required by the PRD |
| **External cryptographic anchoring to a public ledger** | Independent technical anchoring | Not required; adds an awkward "which chain" conversation with crypto-firm customers; a qualified timestamp gives a *legal* presumption where a public chain gives only a technical one |
| **Open-source `evidence-verify` command-line tool** | Converts "trust us" into "check it yourself" | Not required by the PRD — **and the IP ownership term assigns all platform code 100% exclusively to the Client, so publishing anything is the Client's decision, not the delivery team's** |

The MVP does implement hash chaining plus write-once retention (`immutable-evidence-retention`), which gives internal tamper evidence and tamper resistance. What is deferred is *third-party verifiability without trusting the platform*.

## 3. Deployment and sovereignty

| Item | Why it is out of scope |
|---|---|
| **EU sovereign-cloud offering as a paid tier** | The PRD selects AWS on a Client-owned account (the confirmed cloud decision). No tiering exists |
| **On-premise or customer-hosted deployment** | Not in the PRD; would break several controls, change the update model and potentially bring the Cyber Resilience Act into scope |
| **Multi-cloud** | Would roughly double operational surface and degrade every control to the weaker provider's capability. Portability is maintained as a design discipline instead (`data-residency`) |
| **Per-firm regional placement** | Multiplies operational surface; the PRD requires only "EU data centres" (the EU residency requirement) |

## 4. Customer-facing security and assurance features

| Item | Why it is out of scope |
|---|---|
| **External auditor / regulator role** — time-boxed, scoped, fully logged access for a firm's own auditors | Not among the eight system roles in the PRD's system-role table. Would be a genuine differentiator and is the strongest candidate in this section |
| **Customer enterprise single sign-on and automated provisioning** | Not in the PRD; the invitation-only account requirement's invitation-only model assumes platform-native accounts |
| **Machine-readable residency and sub-processor attestation endpoint** | Useful for customers' DORA registers; not a PRD feature |
| **Structured register-of-information extract per firm** | Same |
| **Customer-approved (lockbox) support access** | Not in the PRD; depends on first resolving the Portal firm-visibility statement/the Portal system settings requirement visibility boundary |
| **Cryptographically signed audit-trail exports** | The MVP proposes an exportable firm audit trail (`audit-logging`); signing it is the deferred part |
| **Public API** | Open public-API question keeps it a later phase |

## 5. Security programme activities with recurring cost

| Item | Why it is out of scope |
|---|---|
| **Recurring internal adversarial / purple-team exercises** | A recurring staffing cost the PRD does not fund. An independent penetration test before accepting real client data **is** proposed (`secure-sdlc`) |
| **Private bug-bounty programme** | Recurring cost and triage capacity the PRD does not fund |
| **Participation in customer threat-led penetration testing (TIBER-EU / TLPT)** | A customer-side DORA obligation that may or may not reach the platform by contract; not confirmed |
| **Broad user and entity behaviour analytics** | Cost, false positives, employee-privacy intrusion, and triage capacity. The MVP proposes a small set of high-signal detections plus canary records instead (`insider-threat-protection`) |
| **Continuous 24/7 managed detection and response** | A funding decision, not an engineering one — recorded as open question P-8 rather than assumed |

## 6. Certifications and codes of conduct

| Item | Status |
|---|---|
| **ISO 27001, SOC 2 Type II** | **On the roadmap per the certification roadmap item** — but the PRD says the timeline is to be agreed with the Client, and the open certification question leaves the requirement itself open. **No delivery date is assumed anywhere in this research set.** Not future scope; open scope |
| **ISO 27701 (privacy information management)** | Not in the PRD |
| **EU Cloud Code of Conduct adherence** | Not in the PRD |
| **Any national cloud certification scheme** | Not in the PRD |

## 7. Regulatory scope not driving the MVP

These may become relevant. **None may drive MVP architecture without stakeholder approval and, where marked, legal confirmation.**

| Regime | Position |
|---|---|
| **NIS2** | Adjacent. Applicability to the platform vendor is **undetermined** and requires a national-law opinion (`open-questions`, L-5). No reporting commitment is made |
| **Cyber Resilience Act** | Conditional. Triggered only by shipping an installable or embeddable artefact. The PRD ships none |
| **AI Act** | Classification **undetermined** (`open-questions`, L-6). AI-suggested mappings are labelled as a matter of good practice regardless |
| **AMLR / Travel Rule (TFR)** | Customer-domain. **No Travel Rule data architecture is required** — The IT system inventory requirement explicitly excludes PII and customer-level data from the ICT monitoring intake |
| **eIDAS 2** | Relevant only if qualified timestamping (section 2) is ever adopted |
| **EU Data Act** | Adjacent; mainly concerns the Client's own contract with the cloud provider, which the Client owns (the confirmed cloud decision) |

## 8. Data-handling techniques explicitly **not** adopted

Listed separately because these were previously written up as accepted mechanisms and would each **conflict with the PRD** if implemented:

| Technique | Why it is not adopted |
|---|---|
| **Crypto-shredding as an erasure mechanism** | Would render six-year records unreadable, contradicting the non-deletable retention requirement and the PRD's data and retention table on its face. See ADR-005, ADR-006 |
| **Deletion sagas / soft delete with a grace period for protected classes** | Same conflict. Deletion capability exists only for classes with no retention obligation |
| **A fixed backup retention cap** | The PRD sets no backup policy; inventing a cap risks undercutting the non-deletable retention requirement. The schedule is an open Client decision (`secure-backups`, `open-questions` L-4) |
| **Five-year or seven-year retention defaults** | The PRD's baseline is a **six-year minimum**. MiCA's five-year floor is lower and does not displace it |
| **Steganographic watermarking** | Visible per-user watermarks are proposed; steganographic marking is deferred |

---

## How to bring something back into scope

1. Identify which PRD requirement it serves, or state plainly that it adds new scope.
2. Cost it, including any recurring cost.
3. Obtain Client approval — noting that the fixed-price milestone engagement model is a fixed-price milestone contract and the PRD's baseline-freeze note's baseline-freeze note requires an executed amendment for changes after sign-off.
4. Move the item into the relevant topic document with a status of **PROPOSED**, and record the approval in `architecture-decision-records` with the approver named.
5. Update the control matrix (`security-control-matrix`), the threat model (`threat-model`) and the risk register (`risk-register`) so the set stays internally consistent.
