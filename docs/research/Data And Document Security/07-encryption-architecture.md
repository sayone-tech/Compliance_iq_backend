# 07 — Encryption Architecture

## Best practices

- **Encrypt everything by default; make the exception require justification.** At rest, in transit, in backups, in logs, in queues, in caches, in search indexes.
- **Envelope encryption everywhere.** A KEK in a KMS/HSM wraps per-tenant or per-object DEKs. Never let a long-lived key material leave the HSM boundary; never encrypt bulk data directly with a KMS key.
- **Use one approved crypto module.** All application cryptography goes through a single internal library exposing only high-level, misuse-resistant operations (`encryptDocument(tenantId, plaintext)`), never raw primitives. Enforce with SAST (doc 04).
- **Authenticated encryption only.** AES-256-GCM or XChaCha20-Poly1305. No unauthenticated modes, no CBC without HMAC, no ECB, no home-rolled constructions.
- **Bind ciphertext to context.** Use AAD/encryption context containing `tenant_id` and `document_id` so a ciphertext moved to another tenant's record fails to decrypt. This turns a data-mixing bug into a hard failure rather than a silent leak.
- **Plan the post-quantum migration now.** Not because the threat is imminent for session traffic, but because *harvest-now-decrypt-later* is a live risk for 7-year-retained financial records, and because EU roadmaps set dates.
- **Never invent. Never disable certificate validation. Never log key material or plaintext.**

## EU regulatory implications

- **GDPR Art. 32(1)(a)** names encryption explicitly as an appropriate measure. **Art. 34(3)(a)** — notification to data subjects is not required if the data was rendered unintelligible (i.e. properly encrypted with keys not compromised). **Strong encryption with separated key custody is therefore a direct breach-cost control.**
- **GDPR Chapter V** — encryption with EU-held keys is the central *technical supplementary measure* recognised by EDPB Recommendations 01/2020 for transfers to non-adequate countries (doc 03).
- **DORA Art. 9(2)** — protection of data at rest, in transit and **in use**. "In use" points at confidential computing for the highest-sensitivity processing. **Delegated Reg. (EU) 2024/1774** requires a documented **cryptographic control policy**, including approved algorithms, key lifecycles, and a process to monitor cryptographic developments — explicitly anticipating algorithm obsolescence and quantum risk.
- **NIS2 Art. 21(2)(h)** — policies on the use of cryptography and encryption.
- **MiCA Art. 68** — resilient ICT systems and security access protocols, assessed against DORA.
- **eIDAS 2 (Reg. (EU) 2024/1183)** — qualified electronic signatures/seals and qualified timestamps for evidentiary integrity (doc 15).
- **EU PQC roadmap** — the NIS Cooperation Group's coordinated implementation roadmap (June 2025) sets the expectation that member states begin the post-quantum transition by **end 2026**, complete high-risk use cases by **end 2030**, and complete the transition by **2035**. Financial-sector supervisors are aligning to this. A 2035 deadline with 7-year retention means data written in 2028 is still in scope.

## Recommended architecture

### Algorithm baseline

| Purpose | Algorithm | Notes |
|---|---|---|
| Symmetric bulk | AES-256-GCM | FIPS-approved, hardware-accelerated. XChaCha20-Poly1305 acceptable where nonce management is risky |
| Key wrapping | AES-256-GCM via KMS/HSM | Envelope pattern |
| Transit | TLS 1.3 only (TLS 1.2 with AEAD suites only for legacy customer integrations, time-limited) | Disable TLS ≤1.1 entirely |
| Key exchange | X25519 now; **hybrid X25519MLKEM768** as soon as the full path (CDN, ALB, client libraries) supports it | Harvest-now-decrypt-later defence |
| Signatures (artefacts, evidence) | Ed25519 or ECDSA P-256; plan **ML-DSA (FIPS 204)** hybrid for long-lived evidence signatures | Long-lived signatures are the highest-priority PQC target |
| Hashing | SHA-256 / SHA-384; SHA-3 acceptable | No MD5/SHA-1 anywhere, including in ETags used for integrity |
| Password storage | Argon2id (or scrypt); bcrypt only for legacy | Prefer no passwords at all — SSO + passkeys (doc 10) |
| Randomness | OS CSPRNG only | Never `Math.random`, never a seeded PRNG for security purposes |
| Token/ID generation | 128-bit CSPRNG (UUIDv4/ULID with a CSPRNG source) | Opaque, non-enumerable |

### Layered encryption model

```
Layer 4  Field-level (application)   Highly sensitive fields — national IDs, wallet keys/addresses,
                                     bank details, biometric refs. AES-256-GCM with per-tenant DEK.
                                     Ciphertext in the DB column; searchable via blind index (HMAC).
Layer 3  Object/document (application) Per-document DEK, wrapped by per-tenant CMK.
                                     AAD = {tenant_id, document_id, classification}.
Layer 2  Service-managed at rest      S3 SSE-KMS, RDS/Aurora storage encryption, EBS, EFS,
                                     OpenSearch, SQS/SNS, backups — all with customer-managed keys.
Layer 1  Transit                      TLS 1.3 externally; mTLS between all internal services
                                     (SPIFFE identities, doc 12). No plaintext hop anywhere.
Layer 0  In use (selective)           AWS Nitro Enclaves / confidential VMs for the key-handling and
                                     document-decryption service. Addresses DORA "in use".
```

Layers 2 and 1 are baseline and cheap. Layer 3 is the control that makes per-tenant crypto-shredding and true isolation possible — do not skip it on the assumption that SSE-KMS is sufficient (SSE-KMS alone means the storage service sees plaintext and a single over-broad IAM grant exposes everything).

### Field-level encryption and searchability

The hard problem: encrypted fields cannot be queried with `LIKE` or range predicates.

- **Exact-match search:** deterministic **blind index** — `HMAC-SHA256(tenant_index_key, normalise(value))` stored alongside the ciphertext, indexed. Enables equality lookup without exposing plaintext. Accept that it leaks equality/frequency; use a per-tenant index key so frequency analysis cannot cross tenants.
- **Range/sort:** keep in plaintext only if the field is not sensitive alone (e.g. a date); otherwise decrypt-and-filter in the application over a bounded candidate set.
- **Full-text search over documents:** the search index itself is encrypted at rest with the tenant key, in-region, with per-tenant index isolation. Do not attempt searchable symmetric encryption schemes in production — the leakage profiles are poorly understood and the operational complexity is severe.

### Transit specifics

- Public endpoints: TLS 1.3, HSTS with `max-age=63072000; includeSubDomains; preload`, OCSP stapling, certificate transparency monitoring, ACM-managed certificates with automatic rotation.
- Internal: **mTLS everywhere** via service mesh with SPIFFE/SPIRE workload identities and short-lived (≤24h, ideally ≤1h) certificates. No service trusts network position.
- Database connections: TLS with certificate verification (`verify-full`), not `require`.
- **Certificate pinning** for the highest-value integrations only (customer-managed key endpoints); pinning elsewhere creates outage risk exceeding its benefit.

### Confidential computing (Layer 0)

Run the document decryption/rendering service and the key-brokering service inside **AWS Nitro Enclaves**. Attestation documents are used in KMS key policies (`kms:RecipientAttestation:ImageSha384`), so the CMK can only be used by a cryptographically-attested enclave image. Result: plaintext documents exist only inside an enclave with no persistent storage, no interactive access, and no operator shell — a materially stronger insider-threat and DORA "in use" position.

### Post-quantum migration plan

| Phase | Target | Action |
|---|---|---|
| Now | Crypto agility | Central crypto module; algorithm identifiers stored with every ciphertext and signature; inventory of all cryptographic usage |
| 2026 | Transit | Enable hybrid X25519MLKEM768 on all endpoints where the full path supports it |
| 2026–2027 | Long-lived signatures | Dual-sign evidence records (Ed25519 + ML-DSA); ensure verification accepts both |
| 2027–2029 | Data at rest | AES-256 is already considered quantum-resistant for confidentiality; the exposure is key *transport*. Re-wrap DEKs under PQC-protected KEKs as HSM support lands |
| By 2030 | High-risk use cases complete | Per NIS Cooperation Group roadmap |

**Crypto agility is the deliverable now**; algorithm swaps are the deliverable later. Every ciphertext and signature must carry a version/algorithm identifier from day one — retrofitting this is extremely painful.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Misuse of primitives (nonce reuse in GCM, missing AAD, ECB) | Catastrophic, silent confidentiality failure | Single crypto module, no raw primitives exposed, SAST rules, random 96-bit nonces or a counter with strict per-key uniqueness, code review by a named crypto owner |
| Envelope encryption implemented without AAD | Ciphertext substitution across tenants goes undetected | AAD mandatory in the module signature — impossible to call without it |
| Layer-3 skipped ("SSE-KMS is enough") | One over-broad IAM grant exposes all tenants; no crypto-shredding | Architecture rule; per-tenant CMK + per-document DEK enforced in the storage service |
| Key material or plaintext in logs, traces, core dumps or error messages | Total compromise from a low-severity bug | Redaction library; `@Sensitive` field registry; SAST log rule; disable core dumps; scrub crash reports |
| Blind index frequency analysis | Partial plaintext inference | Per-tenant index keys; only for low-cardinality-risk fields; document the residual leakage |
| Performance regression from field-level encryption | Latency, cost, pressure to disable | Encrypt selectively (documented field list), cache decrypted values in-memory only, benchmark early |
| PQC transition deferred until mandated | Rushed migration; 7-year data already exposed to harvest-now-decrypt-later | Crypto agility now; hybrid transit in 2026 |
| Certificate expiry outage | Availability incident, DORA reportable | ACM auto-renewal; expiry monitoring at 30/14/7 days; no manual certificates |

## Trade-offs

- **Field-level encryption (strong, complex, breaks queries) vs. storage-level only (simple, weaker).** **Recommendation: field-level for a short, explicit list of high-sensitivity fields; storage-level for everything else.**
- **Nitro Enclaves (best-in-class in-use protection; significant complexity, AWS lock-in, debugging difficulty) vs. standard compute.** **Recommendation: enclaves for the key-broker and document-decryption services only, in phase 2 of the roadmap — not at MVP, but designed for.**
- **mTLS everywhere (strong, mesh operational cost) vs. TLS + network policy.** A service mesh (Istio/Linkerd) adds real operational burden. **Recommendation: mTLS via mesh — it is the backbone of the Zero Trust model (doc 12) and the cost is front-loaded.**
- **Hybrid PQC now (future-proof, marginal compatibility risk and CPU cost) vs. wait.** **Recommendation: enable when the full path supports it and monitor error rates; do not block launch on it.**
- **Per-document DEK (fine-grained shredding, more KMS/metadata overhead) vs. per-tenant DEK only.** **Recommendation: per-document for `RESTRICTED`/`PRIVILEGED`, per-tenant otherwise.**

## Design decisions

- **DD-07-01:** Single approved crypto module; raw primitives are inaccessible to application code and blocked by SAST.
- **DD-07-02:** AES-256-GCM for all symmetric encryption, with mandatory AAD binding `tenant_id` and object identity. Function signatures make AAD non-optional.
- **DD-07-03:** Every ciphertext and signature carries an explicit algorithm/version identifier to enable crypto agility.
- **DD-07-04:** Envelope encryption: per-document DEK → per-tenant CMK → KMS/HSM. No customer data encrypted directly by a KMS key.
- **DD-07-05:** TLS 1.3 externally; mTLS with SPIFFE identities and ≤24h certificates internally; `verify-full` on all database connections.
- **DD-07-06:** Field-level encryption applied to an explicit, reviewed field list; exact-match search via per-tenant HMAC blind index; documented residual leakage.
- **DD-07-07:** Nitro Enclaves for the key-broker and document-decryption services in roadmap phase 2, with KMS key policies bound to enclave attestation.
- **DD-07-08:** Post-quantum: crypto agility from day one; hybrid X25519MLKEM768 in transit during 2026; dual signatures on long-lived evidence from 2026–2027.
- **DD-07-09:** Documented cryptographic control policy (algorithms, lifecycles, review cadence, deprecation process) as required by Delegated Reg. (EU) 2024/1774.

## References

- Regulation (EU) 2016/679 (GDPR) Art. 32, 34
- Regulation (EU) 2022/2554 (DORA) Art. 9; Commission Delegated Regulation (EU) 2024/1774 (cryptographic controls)
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(h)
- NIST FIPS 197 (AES), FIPS 186-5, SP 800-38D (GCM), SP 800-57 Part 1 Rev. 5 (key management)
- NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), August 2024
- NIS Cooperation Group — Coordinated Implementation Roadmap for the Transition to Post-Quantum Cryptography (June 2025)
- BSI TR-02102-1 — Cryptographic Mechanisms: Recommendations and Key Lengths; ANSSI cryptographic guidance
- AWS Nitro Enclaves and KMS attestation-based key policy documentation
- RFC 8446 (TLS 1.3); RFC 9106 (Argon2)

## Confidence level

**High** — algorithm selection, envelope pattern, AAD binding, layered model, TLS/mTLS design, and crypto-agility priority. These are settled engineering.

**Medium** — the precise timing and ecosystem readiness for hybrid PQC across CDN/load balancer/client libraries, and the operational maturity cost of Nitro Enclaves in a small team. Both should be validated with a spike before committing roadmap dates.
