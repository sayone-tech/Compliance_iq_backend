# Customer-Managed Encryption — **FUTURE / OUT OF MVP SCOPE**

> **Status: [FUTURE].** Nothing in this document is part of the ComplianceIQ MVP. It is retained as background for a possible later phase and is indexed in [Future and Optional Scope](future-and-optional-scope.md).

## Why this is out of scope

**The PRD's encryption requirement is NFR-02: AES-256 at rest, TLS 1.3 in transit, and a distinct encryption key per firm.** Those keys are platform-managed, inside the Client-owned AWS account (TI-01).

The PRD contains:

- no customer-managed key offering,
- no hold-your-own-key or external-key-store capability,
- no encryption or sovereignty product tiers,
- no commercial tiering of security features at all — pricing is seat-based with two plan structures (CC-01), not security-tiered.

Earlier drafts of this research described a three-tier key-custody model (platform-managed / customer-managed / hold-your-own-key) as an accepted architecture and as a commercial differentiator. **That was not supported by the PRD and has been withdrawn.** The per-firm key required by NFR-02 is implemented as described in `key-management`.

An additional consideration specific to this engagement: **the AWS account is owned solely by the Client (TI-01)**, so the "who can produce plaintext" question already has a different answer than in a conventional vendor-hosted SaaS. Any future customer-key offering would need to be designed against that ownership structure, not against the usual vendor-account assumption.

## What a future offering would require

If a client firm ever demands control of its own keys, the following would need to be worked through. This list exists so the requirement can be scoped quickly, not because any of it is planned.

### Product and commercial questions

1. Which of the two PRD plan structures (Enterprise or seat-based, CC-01) would carry it, and at what price. **This would be a change to CC-01 and would require Client approval.**
2. Whether the firm, Synergy as reseller (CC-06), or SayOne holds the operational responsibility.
3. Whether it is offered at all, given that CC-06 makes Synergy the contracting party with the CASP firm.

### The hard constraint: NFR-07

**A customer-held key gives the customer the ability to make their own records permanently unreadable.** The PRD states that evidence, results, reports and audit records **cannot be deleted by anyone** and must survive a minimum of six years (NFR-07, PRD §2). A customer key revocation or key loss would defeat that requirement, and for the firm it would also be a MiCA Art. 68(9) record-keeping failure.

**Any future customer-key design must resolve this conflict explicitly before it is offered.** Options would include excluding the immutable record classes from customer-key coverage, or obtaining an explicit contractual variation of NFR-07 for such firms. Neither can be assumed.

### Technical requirements that would apply

- **Fail closed on key unavailability.** No fallback key anywhere — a fallback destroys the entire proposition and will be found in due diligence.
- **Bounded data-key caching**, with the revocation-effect window disclosed contractually. Caching for immutable evidence classes would need to be disabled.
- **Continuous key-health monitoring** with escalation to both parties, and a defined degraded mode for the affected firm only.
- **Encryption-context binding** so the customer's key cannot be used for any other firm's data.
- **Verification that every cloud service holding firm data supports customer-key-backed encryption** before anything is sold.
- **A single key-broker abstraction** so that key custody is configuration rather than a separate code path, with one test suite covering every mode.

### Contractual requirements that would apply

- Customer solely responsible for key availability, backup and recovery.
- Explicit, separately acknowledged statement that loss of key material results in permanent, unrecoverable loss of their data including backups.
- Availability carve-out for outages caused by customer key unavailability.
- Notice period before revocation, and a documented export process available while access remains.
- Explicit statement that customer key control protects against infrastructure-level and legal-compulsion access, **not** against compromise of the running application, which legitimately holds decrypted data in memory during processing. This misunderstanding surfaces in every audit.

## References

- Regulation (EU) 2016/679 (GDPR) Art. 28(3)(a), 32, 34; Chapter V
- EDPB Recommendations 01/2020 on supplementary measures — technical measures, encryption scenarios
- Regulation (EU) 2023/1114 (MiCA) Art. 68(9) — the record-keeping consequence of key loss for the firm
- NIST SP 800-57 Part 1 Rev. 5 — key management lifecycle
- AWS KMS: cross-account grants, External Key Store, encryption context

## Confidence level

**High** that this is out of MVP scope: the PRD names per-firm platform-managed keys and nothing further.

**High** that the NFR-07 conflict above is the decisive design question for any future version of this offering.
