# ComplianceIQ – Domain Model & Ubiquitous Language

**Version:** 1.0 (Draft)  
**Depends On:** Technical Architecture Baseline (TAB) v1.0

---

# 1. Purpose

This document establishes the common business language used across ComplianceIQ. Every stakeholder—including product owners, compliance experts, architects, developers, QA, AI engineers, and DevOps—must use these terms consistently.

The objectives are:

- Eliminate ambiguous terminology.
- Define the core business entities.
- Establish ownership boundaries.
- Define entity lifecycles.
- Identify relationships.
- Prepare the foundation for the database model and backend architecture.

---

# 2. Domain Principles

- Every business concept has a single canonical definition.
- Every entity has a unique identifier.
- Business logic references canonical IDs rather than localized text.
- Regulatory content is versioned and immutable once published.
- AI augments business workflows but never replaces regulatory decisions.

---

# 3. Bounded Contexts

## Identity & Access
- User
- Role
- Permission
- Session
- MFA

## Organization
- Firm
- Department
- Office
- Staff
- Service Line

## Regulatory Library
- Regulation
- Regulation Version
- Article
- Requirement
- Guidance
- Test Library
- Evidence Checklist

## WSP Management
- WSP
- WSP Version
- Section
- AI Mapping
- Gap Analysis

## Compliance Testing
- Test
- Test Schedule
- Test Execution
- Test Step
- Evidence
- Observation

## Findings & Remediation
- Finding
- Recommendation
- Action Plan
- Remediation
- Validation

## Reporting
- Dashboard
- Report
- Report Template
- Export

## AI
- Document
- Chunk
- Embedding
- Prompt
- Retrieval
- AI Evaluation

## Platform Administration
- Notification
- Audit Event
- Regulatory Update
- Background Job

---

# 4. Canonical Domain Entities

## Firm

Represents a regulated organization using ComplianceIQ.

Owns:

- Users
- WSPs
- Findings
- Reports
- Evidence
- Tests

Lifecycle

Prospect → Active → Suspended → Archived

---

## User

Authenticated person using the platform.

Attributes

- Firm
- Role
- MFA
- Status

Lifecycle

Invited → Active → Disabled

---

## Service Line

Business capability provided by a firm.

Examples

- Custody
- Exchange
- Trading
- Advisory

Determines applicable regulatory requirements.

---

## Regulation

Top-level regulation such as MiCA or DORA.

Contains:

- Versions
- Articles
- Requirements

---

## Requirement

Smallest compliance obligation tracked by the system.

Canonical identifier example:

REQ-MICA-001

Requirement IDs are language independent.

---

## WSP

Written Supervisory Procedure.

Represents the firm's internal compliance documentation.

Contains:

- Versions
- Sections
- AI mappings

---

## WSP Section

Logical subdivision of a WSP.

Each section may map to multiple requirements.

---

## Test

Verification activity used to validate compliance.

Contains:

- Steps
- Evidence requirements
- Frequency

---

## Test Execution

Single execution instance of a Test.

States

Draft → Assigned → In Progress → Review → Approved → Closed

---

## Evidence

Artifacts supporting a Test Execution.

Examples

- PDF
- DOCX
- Image
- Spreadsheet
- Audio
- Video

---

## Finding

Compliance issue identified during testing.

States

Open → Assigned → Remediation → Validation → Closed

---

## Remediation

Corrective activity addressing a Finding.

Contains:

- Owner
- Due Date
- Validation

---

## Report

Generated compliance output.

Immutable after publication.

---

## Audit Event

Immutable record describing a business action.

Examples

- Login
- Approval
- Role Change
- WSP Upload
- Report Publication

---

# 5. Core Relationships

Firm
- owns Users
- owns WSPs
- owns Tests
- owns Findings
- owns Reports

Regulation
- contains Articles
- Articles contain Requirements

Requirement
- maps to Tests
- maps to WSP Sections
- maps to Evidence Checklists

Test
- produces Test Executions

Test Execution
- produces Findings
- collects Evidence

Finding
- produces Remediation

---

# 6. Domain Events

Examples

- FirmCreated
- UserInvited
- WSPUploaded
- RequirementPublished
- TestAssigned
- EvidenceUploaded
- FindingCreated
- FindingClosed
- ReportGenerated
- ReportPublished
- RegulatoryUpdateDetected

These events form the basis for asynchronous processing.

---

# 7. Entity Ownership

Platform Administration

Owns:

- Regulations
- Requirement Library
- Test Library
- Prompt Templates

Firm

Owns:

- WSP
- Evidence
- Findings
- Reports
- Users

---

# 8. Versioning Strategy

Versioned Entities

- Regulation
- Requirement
- WSP
- Report
- Prompt
- Embedding

Published versions are immutable.

---

# 9. AI Boundaries

AI may:

- Parse documents
- Compare requirements
- Suggest mappings
- Generate summaries
- Identify potential gaps

AI may NOT:

- Approve regulations
- Publish requirements
- Close findings
- Make compliance decisions

---

# 10. Ubiquitous Language Rules

- Always use "Requirement" instead of "Rule".
- Always use "WSP" instead of generic "Policy Document".
- Always use canonical Requirement IDs.
- "Finding" means a validated compliance issue.
- "Observation" is not a Finding until confirmed.
- "Regulation" is the legal source.
- "Requirement" is the actionable obligation.
- "Test" validates a Requirement.
- "Evidence" proves Test completion.

---

# 11. Follow-on Documents

This document is the foundation for:

1. Database Architecture
2. Backend Architecture
3. Workflow Architecture
4. Module Specifications
5. AI & Document Intelligence
