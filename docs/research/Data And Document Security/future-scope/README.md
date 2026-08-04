# Future Scope

> **Nothing in this folder is part of the ComplianceIQ MVP.**

None of it is supported by PRD v4.0. It is kept so the material is not lost and so any of it can be scoped quickly if the Client later wants it — **not** because any of it is planned, priced or approved. Adding any item to scope would be a change to a fixed-price milestone contract (CC-04) and requires Client approval.

| Document | Contents |
|---|---|
| [future-and-optional-scope.md](future-and-optional-scope.md) | The full deferred list: sovereignty and key-custody tiers, HYOK/XKS, post-quantum cryptography, enclaves, eIDAS qualified timestamping, Merkle-root anchoring, an evidence-verifier CLI, steganographic watermarking, lockbox support access, purple-team and bug-bounty programmes, TIBER-EU/TLPT, ISO 27701, the EU Cloud Code of Conduct, enterprise APIs and auditor roles — each with why it was deferred, plus the process for bringing something back |
| [customer-managed-encryption.md](customer-managed-encryption.md) | Customer-managed keys, hold-your-own-key and external key stores. Withdrawn from the MVP: the PRD's encryption requirement is NFR-02 (AES-256, TLS 1.3, a distinct platform-managed key per firm) and the PRD contains no security tiering — CC-01 pricing is seat-based |

**Note on key custody.** A customer-held key would let a firm make its own six-year records unreadable, which collides with NFR-07 and PRD §2. That is a product and legal question, not only an engineering one — see open question L-3 in [open-questions.md](../open-questions.md).

See [future-and-optional-scope.md](future-and-optional-scope.md) §"How to bring something back into scope" for the process.
