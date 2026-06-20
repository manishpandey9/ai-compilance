# ADR-0004 — Document generation pipeline

- **Status:** Accepted
- **Date:** 2026-06-14
- **Deciders:** Engineering
- **Related:** [technical-design.md §5.4, §7.4](../technical-design.md) · PRD §7.2 F5/F6, §10.3, §17

## Context

The paid output is a review-ready evidence-preparation pack: ~11 artifacts across MD, DOCX, CSV, XLSX, and PDF, each source-cited, editable, version-stamped, and assembled into a ZIP (PRD §7.2 F6). PDF rendering is the most resource-sensitive piece and must be cheap and reliable in a serverless/worker context.

## Decision

A **unified renderer abstraction** driven by a typed `DocumentSpec`:
- **PDF:** **Typst** as primary engine for polished artifacts (risk memo, procurement summary); **WeasyPrint** (HTML/CSS→PDF) as fallback for simpler PDFs.
- **DOCX:** **python-docx** (editable templates, FR-DG-002).
- **XLSX:** **openpyxl** (evidence tracker).
- **Markdown:** **Jinja2** templates.
- Renderers are **pure functions** `render(spec) -> bytes`, living in `documents/` with templates in `documents/templates/`, isolated from the legal DB (PRD §11.5).
- Generation runs in **async, retryable workers** (PRD §11.4); output uploaded to R2; download via short-lived signed URL.
- Every artifact records `rule_version` + `source_version` (FR-DG-004); inputs frozen at purchase (PRD §9.2).

## Alternatives considered

| Option | Why rejected |
|---|---|
| Headless Chrome (Puppeteer/Playwright) for PDF | High memory (200–400MB/instance), slow cold start, costly in serverless. |
| LibreOffice headless for DOCX→PDF | Heavy dependency, slow, brittle in containers. |
| Single format only (e.g., PDF) | Violates editability requirement (FR-DG-002) and pack spec (PRD §7.2 F6). |

## Consequences

- **Positive:** low per-pack compute (cost-model §3), polished output, editable templates, clean isolation, byte-reproducible packs.
- **Negative:** Typst is a separate markup language to learn; mitigated by keeping it confined to a few premium templates with WeasyPrint as the HTML-based fallback.
- **Guardrail:** renderer fails the build if any obligation/section lacks a `LegalReference` (FR-DG-001); missing variables surface as explicit "⚠ needs input" (PRD §21.2).
