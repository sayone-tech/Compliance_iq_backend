# 36 — Open Questions

Questions this research could not settle. Grouped by who must answer them and by when. Each has a recommended default so work is not blocked while the answer is obtained.

## A. Legal and regulatory — require counsel

| # | Question | Why it matters | Blocks | Recommended default |
|---|---|---|---|---|
| A-1 | **Are we in scope of NIS2 as a cloud computing service provider, and in which member state?** | Determines whether Art. 23 reporting (24h/72h/1 month) binds us directly, and registration obligations | Incident procedure; management liability | Assume in scope as an important entity; implement Art. 21 measures |
| A-2 | **Exact incident reporting time limits under the DORA 2025 RTS/ITS** (Del. Reg. 2025/301, Impl. Reg. 2025/302) | Our customer notification SLA must be tight enough for customers to meet theirs | Contractual SLA | Working assumption: initial ≤4h from classification / ≤24h from detection; intermediate ≤72h; final ≤1 month. **Verify before contracting** |
| A-3 | **AI Act classification of compliance-assessment AI** | Determines whether high-risk obligations (Art. 8–15, conformity assessment) apply from Aug 2026/2027 | Product roadmap; documentation burden | Limited-risk with Art. 50 transparency; obtain external opinion; re-run on material feature change |
| A-4 | **Will a supervisory authority accept crypto-shredding as satisfying GDPR Art. 17** where backups cannot be selectively purged? | The entire erasure-vs-immutability resolution rests on it | DPA wording | Proceed with crypto-shredding, disclosed explicitly in the DPA; document the reasoning |
| A-5 | **Current commencement status and operative detail of the Indian DPDP Rules** | Affects the TIA, the Indian entity's obligations, and employee monitoring lawfulness | TIA; India-side policies | Assume phased commencement through 2026–2027; obtain Indian counsel confirmation |
| A-6 | **Is the TIA's conclusion defensible to an EU supervisory authority** given Indian lawful-access powers, with our supplementary measures? | If not, the development model must change | Operating model | Proceed with zero-production-access + EU key custody; have both EU and Indian counsel review |
| A-7 | **Does our customer base trigger AMLR obligations flowing to us** (applicable 10 July 2027)? | Affects record content and retention for KYC evidence | Retention policy engine | Design retention to accommodate AMLR 5-year-post-relationship rule now |
| A-8 | **Do we ship anything that triggers CRA scope** (connector, SDK, desktop agent)? | CE marking, conformity assessment, 5-year update commitment | Product decisions | Gate every installable artefact behind a CRA scoping review |
| A-9 | **Works council / employment law constraints on security monitoring** in each jurisdiction where staff are employed | Endpoint DLP, session recording and UEBA may be unlawful without consultation | Monitoring deployment | Deploy only prevention-side controls until local advice obtained |
| A-10 | **Does the platform ever produce an Art. 22 automated decision** in the customer's hands, notwithstanding our human-in-the-loop? | Their obligation, our design responsibility | UI and workflow design | Mandatory named-reviewer approval; never present output as final without approval |

## B. Product and commercial — require the founders/product

| # | Question | Why it matters | Blocks | Recommended default |
|---|---|---|---|---|
| B-1 | **What is the target customer segment at launch** — SME CASPs or tier-1? | Determines whether T2/T3 key tiers, sovereignty options and SOC 2 are Phase 1 or Phase 3 | Roadmap sequencing | Assume mid-market at launch, tier-1 by month 12; build Phase 1 to satisfy mid-market and Phase 2 for tier-1 |
| B-2 | **Do customers upload documents containing special-category data** (biometric ID images, health-related PEP context) at meaningful volume? | Drives Art. 9 conditions, DPIA weight, and classification defaults | DPIA; classification model | Assume yes; design for `RESTRICTED` as a common class |
| B-3 | **Will we hold Travel Rule (TFR) originator/beneficiary data?** | Materially higher sensitivity; transaction-linked personal data | Data model; DPIA | Assume no at launch; treat as a scope-change trigger requiring re-assessment |
| B-4 | **Is single-tenant deployment (in the customer's own AWS account) a required offering?** | Fundamentally different operating model; multiplies operational surface | Architecture | Assume no; offer T3 HYOK instead as the sovereignty answer |
| B-5 | **What SLA (availability, RTO, RPO) will be contracted?** | Determines DR investment and penalty exposure | DR architecture; pricing | Do not contract until measured twice (doc 34 §7); target 99.9% with T1 RTO 4h / RPO 15min |
| B-6 | **Will we offer an on-premise or customer-hosted deployment?** | Would trigger CRA, change the update model, and break several controls | Roadmap | Assume no; revisit only with a full CRA and control-model reassessment |
| B-7 | **Bulk import volume from customers' legacy systems** | Affects pipeline capacity, cost model, and classification of imported data | Import tooling | Design the hardened import path in Phase 2 |

## C. Technical — require a spike or benchmark

| # | Question | Why it matters | Blocks | Recommended default |
|---|---|---|---|---|
| C-1 | **Cost and latency of KMS per-tenant keys with per-document DEKs at target volume** | Could force a change in the key granularity model | Key architecture | Proceed; benchmark at 5× projected load in Phase 1; class-based data-key caching |
| C-2 | **Latency impact of synchronous audit writes on `RESTRICTED` document reads** | May require reclassifying which actions are synchronous | Audit design | Implement synchronously; measure; adjust the action classification empirically |
| C-3 | **Which AWS services supporting tenant data are compatible with XKS-backed keys?** | If a required service is unsupported, T3 cannot be delivered as designed | T3 offering | Verify against live AWS documentation before selling T3; restrict the T3 architecture to supported services |
| C-4 | **Nitro Enclave operational cost and debuggability for a small team** | Could make the phase-2 enclave plan impractical | Enclave roadmap | Spike in Phase 1 before committing to the Phase 2 date |
| C-5 | **Full service parity between `eu-central-1` and `eu-north-1`** | A gap breaks failover at the worst moment | DR region choice | Automated parity check in CI; re-evaluate `eu-west-1` if gaps are material |
| C-6 | **Hybrid PQC (X25519MLKEM768) support across CloudFront, ALB and client libraries** | Determines whether the 2026 transit target is achievable | PQC roadmap | Monitor; enable when the full path supports it; do not block on it |
| C-7 | **Achievable false-positive rate for prompt-injection detection** on real customer documents | Determines whether detection can gate assessments or only flag them | AI pipeline design | Flag-and-review initially; gate only if FP rate proves acceptable |
| C-8 | **Cross-store point-in-time consistency for tenant-granular restore** (S3 versions + Aurora PITR) | Harder than it appears; determines the restore guarantee we can offer | Restore tooling | Spike in Phase 2; document the achievable consistency guarantee honestly |
| C-9 | **Cedar vs. OPA** given the team's eventual policy needs beyond AWS | Migration later is costly | Authorisation engine | Cedar, per DD-10-05; revisit if significant non-AWS policy enforcement emerges |
| C-10 | **SIEM cost at realistic log volumes** | The most common budget overrun in this domain | Monitoring architecture | Model at 5× projected; keep audit events out of the SIEM and in cheap immutable storage |
| C-11 | **Current AWS European Sovereign Cloud availability, region set and service catalogue** | Determines whether Tier 3 sovereign deployment is viable and when | Sovereignty roadmap | Verify at Phase 3 planning; portability constraints keep the option open regardless |

## D. Organisational — require leadership decision

| # | Question | Why it matters | Blocks | Recommended default |
|---|---|---|---|---|
| D-1 | **Will EU-resident production on-call be hired, contracted to an EU MSP, or deferred?** | Deferring keeps the highest-risk cross-border scenario live | Operating model; enterprise GA | Budget for 2–3 EU hires or an EU MSP before the first enterprise customer |
| D-2 | **Who is the accountable executive for ICT risk** (DORA Art. 5(2) equivalent)? | Personal accountability; board reporting | Governance | Name in Phase 0 |
| D-3 | **Is a dedicated Head of Security funded, or is this a fractional CISO?** | Determines how much of this roadmap is realistically executable | Roadmap velocity | Fractional CISO minimum from Phase 0; full-time by Phase 2 |
| D-4 | **What break-glass frequency is acceptable before it counts as a process failure?** | Sets the bar for the zero-standing-access model | Access policy | >2 per month triggers mandatory root-cause work |
| D-5 | **How much security friction will the business tolerate** (two-reviewer rule, approval gates, JIT access)? | Controls that are resented get bypassed | Control design | Start strict, measure friction, relax deliberately with documented rationale — never by erosion |
| D-6 | **Will the Indian entity's role expand to production support over time?** | Would materially change the transfer risk profile | Operating model; TIA | Treat any expansion as a change requiring TIA revision and customer notification |

## E. Assumptions made in this research that should be validated

| # | Assumption | Impact if wrong |
|---|---|---|
| E-1 | Customers are MiCA-authorised CASPs, not credit institutions or investment firms | Different lex specialis; additional CRR/MiFID II obligations would flow through |
| E-2 | We are a processor, not a joint controller, for customer document processing | Joint controllership would require an Art. 26 arrangement and change liability substantially |
| E-3 | AI-generated assessments are decision support, not automated decisions | Art. 22 obligations and potentially AI Act high-risk classification would apply |
| E-4 | AWS is the target platform | Most component decisions would change; the control model and regulatory analysis would not |
| E-5 | Team size ~6–10 engineers plus a security lead | Roadmap phasing and build-vs-buy decisions are scaled to this |
| E-6 | No customer requires on-premise deployment | Would trigger CRA and invalidate several controls |
| E-7 | Development stays exclusively in India + EU (no third jurisdiction) | Each additional jurisdiction requires its own TIA and transfer analysis |
| E-8 | Anthropic/Bedrock terms continue to provide no-training and EU-region inference | Would require migration to an alternative provider or self-hosted model |

## How to use this document

1. **Before Phase 0 completes:** answer A-1, A-5, A-6, D-1, D-2, D-3.
2. **Before Phase 1 completes:** answer A-2, A-3, A-4, A-9, B-1, B-2, C-1, C-2.
3. **Before enterprise GA:** answer A-7, B-5, C-3, C-5, C-8, C-10.
4. **Review this list quarterly.** Answered questions move to the ADR register (doc 38); new ones are added as the product and regulation evolve.
