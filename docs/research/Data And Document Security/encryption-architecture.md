# Encryption Architecture

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## What the PRD requires

**NFR-02:** *"All data is encrypted at rest… using AES-256… All data moving between the platform and users' browsers is encrypted using TLS 1.3. Each firm has its own encryption key."*
**PRD §2 (development note):** *"All data encrypted at rest using AES-256 and in transit using TLS 1.3. Evidence files stored in encrypted object storage with per-tenant encryption keys."*

Three hard requirements: **AES-256 at rest**, **TLS 1.3 in transit**, **a distinct encryption key per firm**. Everything else in this document is how to deliver them without creating new failure modes.

## Best practices

- **Encrypt everything by default; make the exception require justification.** At rest, in transit, in backups, in queues, in caches, in search indexes.
- **Envelope encryption everywhere.** A key-encryption key in a managed key service wraps per-firm or per-object data keys. Long-lived key material never leaves the hardware boundary; bulk data is never encrypted directly by the key service.
- **One approved crypto module.** All application cryptography goes through a single internal library exposing only high-level, misuse-resistant operations — `encryptEvidence(firmId, documentId, plaintext)` — never raw primitives. Enforce with static analysis (`secure-sdlc`).
- **Authenticated encryption only.** AES-256-GCM, or XChaCha20-Poly1305 where nonce management is risky. No unauthenticated modes, no ECB, no home-rolled constructions.
- **Bind ciphertext to context.** Additional authenticated data containing the firm identifier and object identifier means a ciphertext moved into another firm's record fails to decrypt. This converts a data-mixing bug into a hard failure rather than a silent leak — a direct defence of NFR-01.
- **Never invent. Never disable certificate validation. Never log key material or plaintext.**

## Regulatory implications

- **GDPR Art. 32(1)(a)** names encryption explicitly as an appropriate measure. **Art. 34(3)(a)** — notification to data subjects is not required where data was rendered unintelligible by encryption with uncompromised keys. Strong encryption with separated key custody is therefore a direct breach-cost control.
- **GDPR Chapter V** — encryption with EU-held keys is the central technical supplementary measure where any third-country access path exists (`cross-border-data-processing`).
- **Delegated Reg. (EU) 2024/1774** requires a documented cryptographic control policy — approved algorithms, key lifecycles, and a process to monitor cryptographic developments. Used here as a **design reference**; writing the policy is cheap and useful for customer security reviews. **[PROPOSED]**
- **MiCA Art. 68** (customer-side) — resilient ICT systems and security access protocols.

## Recommended architecture

### Algorithm baseline **[PROPOSED except where marked]**

| Purpose | Algorithm | Notes |
|---|---|---|
| Symmetric bulk | **AES-256-GCM** | **[PRD REQUIRED]** — NFR-02 names AES-256. GCM supplies authentication |
| Key wrapping | AES-256-GCM via the managed key service | Envelope pattern |
| Transit, external | **TLS 1.3** | **[PRD REQUIRED]** — NFR-02. Disable TLS ≤ 1.1 entirely; TLS 1.2 only if a specific legacy integration forces it, time-limited and recorded |
| Transit, internal | TLS 1.3 between services; mutual TLS where the platform runs multiple services | **[PROPOSED]** |
| Key exchange | X25519 | Post-quantum hybrid key exchange is **[FUTURE]** |
| Signatures (artefacts, audit sealing) | Ed25519 or ECDSA P-256 | Post-quantum signature migration is **[FUTURE]** |
| Hashing | SHA-256 / SHA-384 | No MD5 or SHA-1 anywhere, including in integrity checks |
| Password storage | Argon2id (or scrypt) | PRD FR-11 requires email and password plus a phone-based second factor, so password storage is in scope |
| Randomness | OS cryptographic RNG only | Never a seeded PRNG for security purposes |
| Identifier generation | 128-bit from a cryptographic RNG | Opaque and non-enumerable — supports NFR-01 |

### Layered encryption model **[PROPOSED]**

```
Layer 3  Field-level (application)   Selected high-sensitivity fields — licence numbers, staff
                                     device serials and asset tags (FR-63), any national identifiers.
                                     AES-256-GCM with a per-firm field key. Exact-match search via
                                     a per-firm keyed blind index.
Layer 2  Object/document             Per-object data key wrapped by the per-firm key.
                                     AAD = {firm_id, object_id, classification}.
Layer 1  Service-managed at rest     Object storage, database storage, block storage, search index,
                                     queues and backups — all with customer-managed keys.
Layer 0  Transit                     TLS 1.3 externally; TLS/mTLS between internal services.
                                     No plaintext hop anywhere.
```

Layers 0 and 1 are baseline and cheap. **Layer 2 is what makes the NFR-02 per-firm key a real isolation control** rather than a label: with storage-service encryption alone, the storage service sees plaintext and a single over-broad grant exposes every firm.

Confidential-computing enclaves for "data in use" are **[FUTURE]** (appendix 39).

### Field-level encryption and searchability **[PROPOSED]**

Encrypted fields cannot be queried with pattern or range predicates.

- **Exact-match search:** a deterministic blind index — a keyed HMAC of the normalised value — stored alongside the ciphertext and indexed. Enables equality lookup without exposing plaintext. It leaks equality and frequency within a firm; use a **per-firm** index key so that leakage cannot cross firms, and document the residual.
- **Range and sort:** keep in plaintext only where the field is not sensitive alone (for example a due date); otherwise decrypt-and-filter over a bounded candidate set.
- **Full-text search over documents:** encrypt the index at rest with the firm's key, keep it in-region, and isolate it per firm. Do not attempt searchable-symmetric-encryption schemes in production — the leakage profiles are poorly understood and the operational complexity is severe.

### Transit specifics **[PROPOSED]**

- Public endpoints: TLS 1.3, HSTS, OCSP stapling, certificate transparency monitoring, managed certificates with automatic rotation.
- Internal service-to-service: TLS with verified peer identity and short-lived certificates. If a service mesh is adopted it should be chosen on operational cost, not feature breadth — **no mesh product is selected here** **[OPEN]**.
- Database connections: TLS with full certificate verification, not merely "require".
- Certificate pinning only for the highest-value integrations; elsewhere it creates outage risk exceeding its benefit.

### Crypto agility **[PROPOSED]**

Every ciphertext and every signature carries an explicit algorithm and version identifier from day one. Retrofitting this into a six-year non-deletable record store (NFR-07) is extremely painful, and the store will outlive at least one algorithm review. **Agility is the deliverable now; algorithm swaps are a later, cheap operation.** No post-quantum migration commitment is made — see appendix 39.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Primitive misuse (nonce reuse in GCM, missing AAD, ECB) | Catastrophic, silent confidentiality failure | Single crypto module, no raw primitives exposed, static-analysis rules, random 96-bit nonces or a strictly unique counter, review by a named owner |
| Envelope encryption implemented without AAD | Ciphertext substitution across firms undetected — defeats NFR-01 | AAD mandatory in the module signature; impossible to call without it |
| Layer 2 skipped because storage-service encryption "is enough" | One over-broad grant exposes every firm; the NFR-02 per-firm key becomes decorative | Architecture rule; per-firm key plus per-object data key enforced in the storage service |
| Key material or plaintext in logs, traces, crash dumps or error messages | Total compromise from a low-severity bug | Redaction library, sensitive-field registry, static-analysis log rule, disable core dumps, scrub crash reports |
| Blind index frequency analysis | Partial plaintext inference within a firm | Per-firm index keys; restricted field list; residual leakage documented |
| Performance regression from field-level encryption | Latency against the NFR-05 two-second dashboard target; pressure to disable | Encrypt a short, documented field list; cache decrypted values in memory only; benchmark early against NFR-05 |
| Certificate expiry outage | Availability incident against NFR-08 | Automated renewal; expiry monitoring well ahead of the date; no manual certificates |
| Six-year records encrypted under an algorithm that later needs replacing | Expensive forced migration | Algorithm/version identifier on every ciphertext from day one |

## Trade-offs

- **Field-level encryption (strong, breaks queries) vs. storage-level only (simple, weaker).** Recommendation: field-level for a short explicit list; storage-level for everything else. **[PROPOSED]**
- **Mutual TLS between all internal services vs. TLS plus network policy.** A service mesh adds real operational burden for a team of this size. Recommendation: mutual TLS where it can be had cheaply from the chosen platform; do not adopt a heavyweight mesh purely for it. **[PROPOSED / OPEN]**
- **Per-object data keys vs. per-firm key only.** Per-object keys make rotation cheap and give finer control at the cost of metadata volume. Recommendation: per-object for `RESTRICTED` evidence, per-firm otherwise. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-07-01 | AES-256 encryption at rest for all client data | **[PRD REQUIRED]** | NFR-02, PRD §2 |
| DD-07-02 | TLS 1.3 for all traffic between the platform and users' browsers | **[PRD REQUIRED]** | NFR-02 |
| DD-07-03 | Each firm has its own encryption key; evidence is stored in encrypted object storage under that key | **[PRD REQUIRED]** | NFR-02, PRD §2 |
| DD-07-04 | Single approved crypto module; raw primitives inaccessible to application code and blocked by static analysis | **[PROPOSED]** | — |
| DD-07-05 | AES-256-GCM with mandatory AAD binding the firm identifier and object identity; the function signature makes AAD non-optional | **[PROPOSED]** | implements NFR-01/NFR-02 |
| DD-07-06 | Envelope encryption: per-object data key → per-firm key → managed key service. No client data encrypted directly by a key-service key | **[PROPOSED]** | implements NFR-02 |
| DD-07-07 | Every ciphertext and signature carries an explicit algorithm and version identifier | **[PROPOSED]** | supports NFR-07 longevity |
| DD-07-08 | Internal service traffic uses TLS with verified peer identity and short-lived certificates; no mesh product is selected | **[PROPOSED / OPEN]** | — |
| DD-07-09 | Field-level encryption applied to an explicit reviewed field list; exact-match search via a per-firm keyed blind index with documented residual leakage | **[PROPOSED]** | — |
| DD-07-10 | A documented cryptographic control policy (algorithms, lifecycles, review cadence, deprecation process) is maintained | **[PROPOSED]** | — |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 32, 34
- Commission Delegated Regulation (EU) 2024/1774 — cryptographic controls *(design reference)*
- NIST FIPS 197 (AES); SP 800-38D (GCM); SP 800-57 Part 1 Rev. 5 (key management)
- BSI TR-02102-1 — Cryptographic Mechanisms: Recommendations and Key Lengths; ANSSI cryptographic guidance
- RFC 8446 (TLS 1.3); RFC 9106 (Argon2)

## Confidence level

**High** — algorithm selection, the envelope pattern, AAD binding, the layered model and crypto-agility priority. These are settled engineering and they implement NFR-02 directly.

**Medium** — the latency cost of field-level encryption against the NFR-05 two-second dashboard target; benchmark before fixing the encrypted-field list.
