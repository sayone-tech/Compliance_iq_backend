# ComplianceIQ – Localization Architecture

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, AI & Document Intelligence v1.1, Notification Architecture v1.0, Configuration Architecture v1.0
**Audience:** Frontend Engineers, Backend Engineers, AI Engineers, Product

> This document defines how localization actually works across ComplianceIQ — UI strings, regulatory content, reports, notifications, and AI prompts — for the confirmed Phase 1 languages (English, German, French) and the confirmed extensibility to all official EU languages (TAB v2.0 §17). Prior documents referenced localization in passing; none defined the mechanism.

---

# 1. Purpose

TAB v2.0 confirms EN/DE/FR as Phase 1 languages and states the architecture "supports all official EU languages," and the Domain Model states Requirement IDs are language-independent — but nothing previously defined how content actually gets translated, stored, rendered, or kept consistent across the five surfaces that need it: UI strings, regulatory/legal text, generated reports, notifications, and AI prompts. Each of these has genuinely different correctness requirements — a mistranslated UI button label is a minor UX issue; a mistranslated regulatory requirement is a legal liability — so this document treats them as distinct problems sharing infrastructure, not one uniform "translate everything" mechanism.

---

# 2. The Core Principle: Requirement IDs Are Language-Independent, Content Is Not

Per Domain Model §10, `REQ-MICA-001` means the same thing regardless of UI language — it's a stable, canonical key. Everything in this document is about localizing the **content attached to** that stable key (the Requirement's descriptive text, a report's narrative, a notification's wording), never the key itself. This is what makes cross-language consistency possible: a finding, a test result, or an audit log entry references `REQ-MICA-001` regardless of which language generated or is viewing it, so switching a user's UI language never changes what data means, only how it's displayed.

---

# 3. Localization Layers

```
Shared UI Strings  →  Regulatory Content  →  Reports  →  Notifications  →  AI Prompts
```

Each layer has a different translation source, update cadence, and correctness bar — covered individually below.

---

# 4. UI String Localization

- **Mechanism:** `react-i18next` (already the confirmed frontend library, TAB v2.0 §7) across all three React surfaces — Firm App, Admin Portal (Marketing Site uses Next.js's own i18n routing, separately, since it's a fully decoupled application per TAB v2.0 §6).
- **Storage:** translation key/value files (`en.json`, `de.json`, `fr.json`) version-controlled alongside the frontend codebase — UI copy is a code-review-governed change, not a runtime-editable configuration, since it ships with a frontend deployment regardless.
- **Fallback:** a missing key in `de.json`/`fr.json` falls back to the English value rather than rendering a raw key string or blank space — a translation gap should never break the UI, only temporarily under-localize it.
- **Locale resolution:** `platform_user.locale` field (introduced in Notification Architecture §6.1, formalized here as the canonical source) drives UI language selection, defaulting to a firm-level default locale (a new `firm_profile.default_locale` field) at user creation, itself defaulting to English if unset.

---

# 5. Regulatory Content Localization

## 5.1 Decision: Source Official Translations, Never Machine-Translate Legal Text

**MiCA and DORA, as EU regulations, are officially published in every EU official language via EUR-Lex.** This means Requirement and Article text for the currently supported languages should be **ingested from the official-language source directly** (per language, during the regulatory monitoring pipeline — TAB v2.0 §9), not machine-translated from an English source.

**Rationale:** machine translation of legal/regulatory text is a genuine liability risk — a subtly wrong translation of an obligation could mislead a firm into believing it's compliant when it isn't, or vice versa. Since the EU already produces and legally authenticates translations for its own regulations, there's no reason to introduce translation risk where an authoritative source exists.

## 5.2 Storage

`article.text_content` (Database Architecture §4.1) gains a `locale` column; each `article` row is one specific language's official text, keyed to the same `regulation_version_id` and `article_number` across languages — so `REQ-MICA-001`'s underlying Article text exists as one row per supported language, all pointing at the same canonical Requirement.

## 5.3 Embeddings — Per-Language, Not Cross-Lingual Reliance

**Decision:** `regulatory_embedding` (Database Architecture §4.3) is generated **once per (Requirement, language) pair**, embedding the official-language text for that language directly — not relying on a multilingual embedding model's cross-lingual generalization to match, say, a German WSP section against an English-only Requirement embedding.

**Rationale:** cross-lingual embedding matching is meaningfully less precise than same-language matching, and the exact-match value BM25 keyword search contributes (AI & Document Intelligence §5.1) is entirely language-specific — a German WSP section's exact terminology should be BM25-matched against German Article text, not English. Since official translations already exist (Section 5.1), there's no reason to accept degraded matching quality when the correct-language source is available. If a firm's WSP is authored in a language without an official regulatory translation (uncommon, but possible for a non-EN/DE/FR-market firm in future expansion), that pairing falls back to the best available cross-lingual embedding match with a lower confidence ceiling — flagged as reduced-confidence in the UI rather than silently treated as equivalent to a same-language match.

## 5.4 WSP Content Is Never Translated

A firm's WSP is authored and processed **in whatever language the firm wrote it in** — ComplianceIQ never machine-translates a firm's own compliance documentation. This preserves the legal fidelity of the firm's actual internal document (a translated WSP is not the WSP the firm's regulator would inspect). The AI mapping suggestion's **rationale text** shown to a human reviewer (AI & Document Intelligence §5.2) is localized to the reviewer's UI language preference — that's a generated explanation, not the underlying legal content, so translating it carries none of the Section 5.1 risk.

---

# 6. Report Localization

- Report generation (TAB v2.0 §11) selects a language at generation time via a `report.locale` field, independent of the underlying data — the same test results and findings can be rendered in a German or English report without re-running any analysis, since the Report Data Model (`report.report_data_snapshot`, Database Architecture §5.6) stores structured data, and only the *rendering* layer (WeasyPrint/docxtpl/openpyxl templates) is locale-specific.
- Report templates themselves (headers, section labels, standard narrative boilerplate) are translated content, versioned the same way as any other template (`prompt_template`/`notification_template` governance pattern, Configuration Architecture §3) — a new `report_template` registry entry per locale.
- **Firm-specific data embedded in a report** (finding descriptions, remediation notes — free text a compliance officer typed) is rendered as-authored, in whatever language it was written in, regardless of the report's overall locale — same principle as Section 5.4: user-authored content is never machine-translated.

---

# 7. Notification & Email Localization

Recap and formalization of Notification Architecture §6.1's `notification_template.locale` field: template rendering resolves the recipient's `platform_user.locale` at delivery time, falling back to English on a missing locale-specific template (Notification Architecture §6.2) — this document adds no new mechanism here, only confirms `platform_user.locale` (Section 4 above) as the single canonical source both documents draw from, so they can't drift into two different locale-resolution implementations.

---

# 8. AI Prompt Localization

- **Internal AI Service prompts** (the instructions sent to the LLM, `prompt_template.prompt_text`, AI & Document Intelligence §7.1) are **not** localized per user — they operate in whichever language matches the content being processed (a German WSP section is processed with a German-appropriate prompt/matching against German regulatory embeddings, per Section 5.3), independent of which UI language the reviewing compliance officer happens to have selected.
- **User-facing AI output** (the mapping rationale, gap analysis summaries) is localized per Section 5.4 above — the distinction is: the AI's internal working language matches the content's language for accuracy; what's shown to the human is localized to their preference for usability. These are two different, deliberately decoupled localization decisions.

---

# 9. Formatting (Dates, Numbers, Currency)

Purely a presentation-layer concern, no backend storage impact: the `Intl` API (native browser, used via `react-i18next`'s formatting helpers) handles locale-aware date, number, and currency formatting client-side. The backend always stores and transmits dates/numbers in a canonical, locale-neutral format (ISO 8601 for dates, plain numeric types) — formatting is never baked into stored data, only applied at render time, so a locale change never requires a data migration.

---

# 10. Adding a New Language (Operational Process)

Since TAB v2.0 already commits to supporting all official EU languages as a future extension point, this section makes that concrete:

1. Add the new locale to `react-i18next` resource files (UI strings) — translation vendor/process is a content decision, not architectural.
2. Ingest the new language's official EUR-Lex text for existing Requirements/Articles (Section 5.1–5.2) via the regulatory monitoring pipeline (TAB v2.0 §9), generating new `regulatory_embedding` rows for that language (Section 5.3).
3. Add `report_template` and `notification_template` entries for the new locale (Sections 6, 7) — falls back to English automatically for any not-yet-translated template in the interim (no big-bang cutover required).
4. No database migration is required for the language addition itself — `locale` is already a value in an existing column, not a schema change, for every table this document touches.

---

# 11. Open Items Carried Forward

| Item | Status |
|---|---|
| `firm_profile.default_locale` / `platform_user.locale` schema additions | Minor additions, tracked here and in Notification Architecture — not yet formally added to Database Architecture's table listing |
| Translation vendor/process for UI strings and report templates | Content/operational decision, not architectural |
| Fallback confidence handling for non-EU-official-language WSPs (Section 5.3) | Low-priority Phase 1 concern given confirmed EN/DE/FR scope; revisit if/when market expansion changes this |

---

# 12. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Localization Architecture: five-layer model (UI, Regulatory Content, Reports, Notifications, AI Prompts); official-EUR-Lex-translation-sourcing decision for regulatory content (never machine-translated); per-language regulatory embedding generation rather than cross-lingual reliance; WSP/user-authored content never translated; canonical `platform_user.locale` resolution shared across UI, reports, and notifications; formatting handled client-side via Intl API with locale-neutral backend storage; operational process for adding a new language. |
