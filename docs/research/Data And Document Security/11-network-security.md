# 11 — Network Security

## Best practices

- **Nothing customer-facing is directly reachable.** Public entry is limited to a CDN/WAF and a load balancer. Compute, databases and storage have no public addresses and no internet gateway route.
- **Default-deny in both directions.** Ingress deny-by-default is standard. **Egress deny-by-default is the control that actually stops exfiltration** and is the one most often skipped — implement it.
- **Segment by blast radius, not by convenience.** Separate accounts and VPCs per environment; separate subnets and security groups per tier; separate network policy per workload within the cluster.
- **Private connectivity to cloud services.** VPC endpoints (interface and gateway) with endpoint policies, so traffic to S3/KMS/Secrets Manager never traverses the internet and cannot be redirected to an attacker's bucket.
- **The network is not a trust boundary.** It reduces attack surface and provides defence in depth; identity and mTLS carry the actual trust decisions (doc 12).
- **Log flows and actually use the logs.** VPC flow logs, DNS query logs, WAF logs, load-balancer logs — routed to the SIEM with detections attached, not archived and forgotten.

## EU regulatory implications

- **DORA Art. 9(3)/(4)** and **Delegated Reg. (EU) 2024/1774** — explicit requirements on **network security management**: segmentation of networks according to criticality, isolation of information-processing systems, protection against intrusion and data misuse, security of network traffic, and management of network devices. Segmentation is named, not implied.
- **DORA Art. 10** — detection mechanisms with multiple layers of control and defined alert thresholds; network telemetry is a primary detection source.
- **NIS2 Art. 21(2)(a)/(b)/(e)/(j)** — risk analysis, incident handling, network and information systems security, and secured emergency communication.
- **GDPR Art. 32(1)(b)** — ongoing confidentiality, integrity, availability and resilience of processing systems; network controls are core Art. 32 measures.
- **MiCA Art. 68** — resilient ICT systems, assessed against DORA's network security requirements.
- **Residency (doc 02)** — CDN edge locations, DNS resolution paths and any global network service must be constrained so that request metadata does not leave the EU.

## Recommended architecture

### Account and VPC topology

```
Organisation (AWS Organizations, SCPs + RCPs enforcing EU-only regions)
├── management         — Organizations, SCP, billing. No workloads.
├── security-tooling   — GuardDuty/Security Hub delegated admin, SIEM ingestion
├── log-archive        — WORM log storage; write-only from other accounts
├── shared-services    — ECR, transit gateway, egress proxy, CI runners
├── dev                — VPC 10.10.0.0/16
├── staging            — VPC 10.20.0.0/16
└── prod               — VPC 10.30.0.0/16   ← no peering to dev/staging, ever
```

### Production VPC layout (3 AZs in `eu-central-1`)

| Subnet tier | Contents | Route to internet |
|---|---|---|
| **Public** (`/24` × 3) | ALB only, NAT gateways | Internet gateway |
| **Private-app** (`/22` × 3) | EKS worker nodes, application pods | Egress via NAT → egress proxy only |
| **Private-data** (`/24` × 3) | Aurora PostgreSQL, ElastiCache, OpenSearch | **No route to internet at all** |
| **Private-endpoints** (`/24` × 3) | Interface VPC endpoints | N/A |

- **No public subnet contains compute.** The ALB is the only public-facing resource.
- **Private-data has no NAT route.** A compromised database instance cannot call out. This single decision defeats a large class of exfiltration and C2 techniques.
- **VPC endpoints** for S3 (gateway), KMS, Secrets Manager, ECR, STS, CloudWatch Logs, SSM, SQS, Bedrock — each with an endpoint policy restricting to our own resources and `aws:PrincipalOrgID`. This prevents a compromised workload from using our network path to reach an attacker-controlled S3 bucket.

### Edge

```
Client ──▶ Route 53 (DNSSEC signed, query logging)
       ──▶ CloudFront (TLS 1.3, EU-restricted geo where applicable, Shield Standard/Advanced)
       ──▶ AWS WAF  (managed rule groups + custom rules + rate limiting + bot control)
       ──▶ ALB (private target group, TLS re-encryption to targets)
       ──▶ EKS ingress (Envoy/NGINX) ──▶ service mesh (mTLS) ──▶ pods
```

WAF configuration:
- AWS managed rule groups: Core (OWASP-aligned), Known Bad Inputs, SQL Database, Linux, Anonymous IP List, IP Reputation.
- Custom rules: per-tenant and per-IP rate limits; a stricter rate limit on authentication endpoints (credential stuffing) and on document upload/download endpoints (bulk exfiltration and DoS by upload).
- Request size limits; block requests with unexpected content types on JSON endpoints.
- **Deploy in count mode first**, tune for two weeks against real traffic, then switch to block. Blocking a legitimate customer's compliance submission is its own incident.
- WAF logs to the SIEM with detections for scanning patterns and credential stuffing.
- **Shield Advanced** once revenue justifies it (~$3k/month) — the DDoS response team access and cost protection matter more than the mitigation itself.

### Egress control (the exfiltration control)

- All outbound HTTP/HTTPS from private-app subnets routes through a **forward proxy** (Squid or AWS Network Firewall with TLS SNI/domain filtering) in shared-services.
- **Default deny.** An allowlist of destination FQDNs, maintained in git, reviewed on change: the AI inference endpoint (or, better, a VPC endpoint to Bedrock so it never leaves the AWS network), payment provider, email provider, package registries (build-time only), and nothing else.
- Every allowed and denied egress connection is logged with the requesting workload identity. **Denied egress is a high-signal alert** — legitimate workloads rarely try to reach unlisted hosts.
- **DNS egress control:** Route 53 Resolver DNS Firewall blocking known-malicious and newly-registered domains, and blocking DNS-over-HTTPS bypass attempts. DNS query logging to the SIEM catches DNS-tunnelling exfiltration.

### Intra-cluster

- **Kubernetes NetworkPolicy default-deny** for both ingress and egress in every namespace; explicit allow rules per service dependency.
- **Service mesh with mTLS** (doc 12) — network policy restricts *reachability*, mesh authorisation policy restricts *identity*, and both must pass.
- Namespace per bounded context; the document service (which handles plaintext) is isolated in its own namespace with the tightest policy set.
- Pod security standards: `restricted` profile — no privileged containers, no host network/PID/IPC, read-only root filesystem, non-root user, dropped capabilities, seccomp `RuntimeDefault`.

### Administrative access

- **No bastion hosts, no SSH, no open management ports.** Administrative access via **AWS Systems Manager Session Manager** — no inbound ports, IAM-authorised, fully session-logged to the WORM bucket.
- EKS API server endpoint is **private-only**, reachable through the VPC; `kubectl` access is via Session Manager port forwarding or a VPN-connected admin path with SSO.
- Database access follows the same route: no public endpoint, IAM authentication, access only from the application security group or via a logged Session Manager tunnel under break-glass.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Security group misconfiguration exposing a database (`0.0.0.0/0`) | Direct data exposure | IaC-only changes; Checkov/Config rules blocking open ingress; continuous conformance scanning; no public subnet for data tier |
| Egress control bypassed via an allowlisted domain (e.g. a package registry used for exfiltration) | Slow exfiltration through a legitimate channel | Registry access allowed only from build accounts, not from prod runtime; volume anomaly detection; DLP on egress (doc 23) |
| WAF false positives blocking legitimate submissions | Customer-impacting incident, pressure to disable WAF | Count-mode tuning period; per-rule metrics; documented exception process; never disable wholesale |
| DDoS on the API | Availability incident, DORA reportable | CloudFront + Shield, rate limiting, autoscaling, graceful degradation, Shield Advanced when justified |
| Lateral movement after a single pod compromise | Broad internal access | Default-deny NetworkPolicy, mTLS with authorisation policies, no shared service accounts, restricted pod security standard |
| DNS exfiltration | Undetected data loss | DNS Firewall, query logging, volumetric detection on TXT/NULL query patterns |
| VPC peering or transit gateway route from a lower environment to prod | Environment isolation collapse | No peering to prod, ever; enforced by SCP denying `ec2:CreateVpcPeeringConnection` in the prod account outside IaC |
| IPv6 path unintentionally bypassing IPv4-only controls | Silent control gap | Disable IPv6 on all subnets unless explicitly designed for, and apply identical rules if enabled |

## Trade-offs

- **Egress proxy (real exfiltration control; ops burden, an availability dependency, and TLS inspection complexity) vs. open egress.** **Recommendation: implement it. Start with SNI/domain-based filtering without TLS interception — this gets most of the value without the certificate-management and privacy complications of full inspection.**
- **AWS Network Firewall (managed, integrated, ~$0.40/hour/endpoint + data processing) vs. self-managed Squid (cheap, more control, must be made HA ourselves).** **Recommendation: Network Firewall — the availability and maintenance burden of a self-managed proxy in the critical egress path is not worth the saving.**
- **Service mesh (mTLS, observability, fine-grained authorisation; significant operational complexity and resource overhead) vs. NetworkPolicy alone.** **Recommendation: mesh, but choose Linkerd over Istio unless Istio-specific features are needed — Linkerd's operational burden is dramatically lower and mTLS is the primary requirement.**
- **Private EKS API endpoint (secure, awkward CI/CD and developer access) vs. public endpoint with CIDR allowlist.** **Recommendation: private endpoint; CI runners live in-VPC, developers use Session Manager.**
- **Single VPC with strict subnet/SG segmentation (simpler, cheaper) vs. multi-VPC micro-segmentation (stronger isolation, complex routing).** **Recommendation: single VPC per environment with rigorous subnet/SG/NetworkPolicy segmentation. Account-level separation already provides the strongest boundary.**
- **Shield Advanced (~$3k/month) from day one vs. Standard.** **Recommendation: Standard until the first enterprise contract, then Advanced — the cost-protection and DDoS Response Team access become worth it once availability SLAs carry penalties.**

## Design decisions

- **DD-11-01:** Six-account organisation with SCPs and RCPs enforcing EU-only regions; no network path from `dev`/`staging` to `prod`.
- **DD-11-02:** Three-tier subnet model; the data tier has no route to the internet under any configuration.
- **DD-11-03:** Interface/gateway VPC endpoints with restrictive endpoint policies for all AWS service access, including Bedrock — AWS service traffic never traverses the public internet.
- **DD-11-04:** Default-deny egress via AWS Network Firewall with a git-managed FQDN allowlist; denied egress generates a high-priority alert.
- **DD-11-05:** Route 53 Resolver DNS Firewall enabled with query logging to the SIEM.
- **DD-11-06:** CloudFront + WAF at the edge; WAF deployed in count mode for two weeks before blocking, with per-rule metrics and a documented exception process.
- **DD-11-07:** No bastion hosts, no SSH, no inbound management ports. All administrative access via Session Manager with full session recording.
- **DD-11-08:** Private-only EKS API endpoint; Kubernetes NetworkPolicy default-deny in every namespace; `restricted` Pod Security Standard enforced.
- **DD-11-09:** Linkerd service mesh providing mTLS between all services (see doc 12).
- **DD-11-10:** VPC flow logs, DNS query logs, WAF logs and ALB logs delivered to the SIEM with active detections, retained per doc 14.

## References

- Commission Delegated Regulation (EU) 2024/1774 — network security management, segmentation
- Regulation (EU) 2022/2554 (DORA) Art. 9, 10
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)
- NIST SP 800-41 Rev. 1 — Guidelines on Firewalls and Firewall Policy
- NIST SP 800-125B — Secure Virtual Network Configuration
- CIS AWS Foundations Benchmark v3.0; CIS Kubernetes Benchmark
- Kubernetes Pod Security Standards; NetworkPolicy documentation
- AWS Network Firewall, Route 53 Resolver DNS Firewall, VPC endpoint policy documentation

## Confidence level

**High** — topology, segmentation model, egress control, endpoint policies, and the no-bastion administrative model. Standard, well-tested patterns for regulated AWS workloads that map directly to the DORA network-security RTS.

**Medium** — the operational cost of egress filtering in practice (allowlist maintenance can be genuinely annoying and is the control most likely to be weakened under delivery pressure), and Linkerd-versus-Istio, which depends on features needed later.
