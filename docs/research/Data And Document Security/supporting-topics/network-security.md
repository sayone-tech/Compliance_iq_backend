# Network Security

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](../future-scope/future-and-optional-scope.md).

Not named by the PRD. Everything here is **[PROPOSED]**: it is how the tenant isolation requirement (isolation), the EU residency requirement (EU residency) and the availability target (availability) survive contact with the internet. Compute, orchestration and mesh products are **not** selected — the patterns below are stated in terms of tiers and policies, not products.

## Best practices

- **Nothing customer-facing is directly reachable.** Public entry is limited to a CDN/WAF and a load balancer. Compute, databases and storage have no public addresses and no route to the internet gateway.
- **Default-deny in both directions.** Ingress deny-by-default is standard. **Egress deny-by-default is the control that actually stops exfiltration** and is the one most often skipped.
- **Segment by blast radius, not by convenience.** Separate accounts and networks per environment; separate subnets and security groups per tier; separate policy per workload.
- **Private connectivity to cloud services.** Private service endpoints with policies, so traffic to storage, key management and secrets never traverses the internet and cannot be redirected to an attacker-controlled resource.
- **The network is not a trust boundary.** It reduces attack surface and provides defence in depth; identity carries the actual trust decisions (`zero-trust-architecture`).
- **Log flows and use the logs.** Flow logs, DNS query logs, WAF logs and load-balancer logs routed to monitoring with detections attached, not archived and forgotten.

## Regulatory implications

- **GDPR Art. 32(1)(b)** — ongoing confidentiality, integrity, availability and resilience of processing systems.
- **Delegated Reg. (EU) 2024/1774** — network security management: segmentation according to criticality, isolation of processing systems, protection against intrusion and data misuse, security of network traffic. *(Design reference.)*
- **Residency (`data-residency`)** — CDN edge locations, DNS resolution paths and any globally replicated network service must be constrained so request metadata does not leave the EU (the EU residency requirement).

## Recommended architecture

### Account and network topology

```
Client-owned cloud organisation (the confirmed cloud decision), region policy denying non-EU regions
├── management         — organisation, policy, billing. No workloads
├── security-tooling   — detection services, monitoring ingestion
├── log-archive        — immutable log and evidence storage; write-only from other accounts
├── backup             — no trust path from production
├── shared-services    — registries, egress control, CI runners
├── dev                — synthetic data only
├── staging            — synthetic data only
├── sandbox-processing — untrusted document parsing, no credentials, no egress
└── prod               — no network path to or from dev/staging, ever
```

### Production network layout (three availability zones)

| Tier | Contents | Route to internet |
|---|---|---|
| **Public** | Load balancer only, NAT gateways | Internet gateway |
| **Private-app** | Application workloads | Egress only via the controlled egress path |
| **Private-data** | Database, cache, search index | **None at all** |
| **Private-endpoints** | Private service endpoints | Not applicable |

- **No public subnet contains compute.** The load balancer is the only public-facing resource.
- **The data tier has no NAT route.** A compromised database instance cannot call out. This single decision defeats a large class of exfiltration and command-and-control techniques.
- **Private service endpoints** for object storage, key management, secrets, container registry, token service, logging and the AI inference endpoint, each with a policy restricting to the platform's own resources and organisation.

### Edge

```
Client ──▶ DNS (signed, query logging)
       ──▶ CDN (TLS 1.3 per the encryption requirement, EU points of presence for authenticated content)
       ──▶ WAF (managed rule groups + custom rules + rate limiting)
       ──▶ Load balancer (re-encrypt to targets)
       ──▶ Application ingress ──▶ services
```

WAF configuration:

- Managed rule groups covering common web attack classes, known-bad inputs, SQL injection and reputation lists.
- Custom rules: per-firm and per-IP rate limits; a stricter limit on authentication endpoints (credential stuffing against the phone-based second factor requirement accounts) and on evidence upload and download endpoints (bulk exfiltration, and denial of service by upload — note the accepted evidence file type list permits video and ZIP files, and the configurable file-size limit makes the maximum size configurable).
- Request size limits aligned with the configured evidence file-size ceiling (the configurable file-size limit); reject unexpected content types on JSON endpoints.
- **Deploy in count mode first**, tune against real traffic, then switch to blocking. Blocking a firm's legitimate evidence upload mid-test is its own incident.
- WAF logs to monitoring with detections for scanning and credential stuffing.

Advanced managed DDoS protection with a response team is **[FUTURE]** — worth revisiting only if availability commitments carry penalties, and the 99.5% availability target is not yet contracted (the open uptime-SLA question open).

### Egress control — the exfiltration control

- All outbound HTTP/HTTPS from application subnets routes through a controlled egress path with domain-based filtering.
- **Default deny.** An allowlist of destination hostnames maintained in version control and reviewed on change: the AI inference endpoint (preferably reached by a private endpoint so it never leaves the provider network), the email sending service (the report distribution requirement report distribution, the PRD's notifications section alerts), the regulatory monitoring sources for the Portal (the regulatory monitoring requirement — EUR-Lex, EBA, ESMA feeds), package registries at build time only, and nothing else.
- Every allowed and denied egress connection is logged with the requesting workload identity. **Denied egress is a high-signal alert.**
- **DNS egress control:** resolver firewall blocking known-malicious and newly registered domains and blocking encrypted-DNS bypass; query logging catches tunnelling.

### Intra-cluster / intra-service

- Default-deny network policy for both ingress and egress in every namespace or equivalent isolation unit; explicit allow rules per service dependency.
- Workload identity restricts *who* may call; network policy restricts *reachability*. Both must pass.
- The document service, which handles plaintext evidence, is isolated with the tightest policy set.
- Hardened workload runtime: no privileged containers, no host namespaces, read-only root filesystem, non-root user, dropped capabilities, restrictive syscall profile.

### Administrative access

- **No bastion hosts, no SSH, no open management ports.** Administrative access through an identity-authorised, fully session-logged session service (`insider-threat-protection`).
- Orchestrator and database control endpoints are private-only; access is via that same logged path under break-glass.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Security group misconfiguration exposes a database | Direct data exposure; breach of the tenant isolation requirement | Infrastructure-as-code-only changes; policy rules blocking open ingress; continuous conformance scanning; no public subnet for the data tier |
| Egress control bypassed via an allowlisted domain | Slow exfiltration through a legitimate channel | Registry access allowed only from build accounts; volume anomaly detection; egress classification checks (`data-loss-prevention`) |
| WAF false positives block a legitimate evidence upload | Customer-impacting incident during a firm's testing cycle; pressure to disable the WAF | Count-mode tuning period; per-rule metrics; documented exception process; never disable wholesale |
| Denial of service on the API | Availability incident against the availability target | CDN, rate limiting, autoscaling, graceful degradation |
| Lateral movement after a single workload compromise | Broad internal access | Default-deny network policy, mutual TLS with identity-based authorisation, no shared service accounts, hardened runtime |
| DNS exfiltration | Undetected data loss | Resolver firewall, query logging, volumetric detection |
| Network path opened from a lower environment to production | Environment isolation collapse; synthetic-only guarantee broken | No peering to production, ever; enforced by organisation policy |
| Large evidence uploads used as a resource-exhaustion vector | Availability incident | Size limits enforced at the pre-signed-upload step, aligned to the configurable file-size limit |

## Trade-offs

- **Egress proxy vs. open egress.** The proxy is real exfiltration control at the cost of allowlist maintenance and an availability dependency. Recommendation: implement it, starting with domain-based filtering without TLS interception — most of the value without the certificate and privacy complications. **[PROPOSED]**
- **Managed egress firewall vs. self-managed proxy.** Recommendation: managed — the availability burden of a self-managed proxy in the critical egress path is not worth the saving. **[PROPOSED]**
- **Service mesh vs. network policy plus per-service TLS.** A mesh gives uniform mutual TLS and identity-based authorisation at a real operational cost. **No mesh product is selected here.** Recommendation: adopt one only if the operational cost is genuinely low for the chosen platform. **[OPEN]**
- **Single network per environment with strict segmentation vs. multiple networks.** Recommendation: one network per environment with rigorous subnet, security-group and workload-policy segmentation; account-level separation already provides the strongest boundary. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-11-01 | Multi-account organisation with policies enforcing EU-only regions; no network path from dev or staging to production | **[PROPOSED]** — implements the EU residency requirement |
| DD-11-02 | Three-tier subnet model; the data tier has no route to the internet under any configuration | **[PROPOSED]** |
| DD-11-03 | Private service endpoints with restrictive policies for all cloud service access, including AI inference | **[PROPOSED]** — implements the EU residency requirement |
| DD-11-04 | Default-deny egress with a version-controlled hostname allowlist; denied egress raises a high-priority alert | **[PROPOSED]** |
| DD-11-05 | DNS resolver firewall enabled with query logging | **[PROPOSED]** |
| DD-11-06 | CDN plus WAF at the edge; WAF in count mode before blocking, with per-rule metrics and a documented exception process | **[PROPOSED]** |
| DD-11-07 | No bastion hosts, no SSH, no inbound management ports; administrative access via a fully session-recorded service | **[PROPOSED]** |
| DD-11-08 | Default-deny workload network policy in every namespace; hardened workload runtime profile | **[PROPOSED]** |
| DD-11-09 | Mutual TLS between internal services where the chosen platform provides it at acceptable operational cost; no mesh product selected | **[PROPOSED / OPEN]** |
| DD-11-10 | Flow logs, DNS query logs, WAF logs and load-balancer logs delivered to monitoring with active detections | **[PROPOSED]** |

## References

- Commission Delegated Regulation (EU) 2024/1774 — network security management, segmentation *(design reference)*
- Regulation (EU) 2016/679 (GDPR) Art. 32
- NIST SP 800-41 Rev. 1 — Guidelines on Firewalls and Firewall Policy
- NIST SP 800-125B — Secure Virtual Network Configuration
- CIS Foundations Benchmarks (cloud and container platforms)
- Kubernetes Pod Security Standards and NetworkPolicy documentation — one implementation option

## Confidence level

**High** — topology, segmentation, egress control, endpoint policies and the no-bastion administrative model are standard, well-tested patterns.

**Medium** — the ongoing cost of egress allowlist maintenance, which is the control most likely to be weakened under delivery pressure.
