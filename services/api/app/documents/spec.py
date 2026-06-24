"""Typed document generation context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TriggeredRuleRow:
    rule_code: str
    name: str
    legal_citation: str
    legal_summary: str
    rationale: str
    source_url: str | None = None


@dataclass
class ObligationRow:
    obligation_id: str
    title: str
    description: str | None
    legal_citation: str
    legal_summary: str | None
    source_url: str | None
    mandatory: bool
    evidence_required: str | None
    document_type: str | None
    suggested_owner: str
    enforcement_note: str | None = None


@dataclass
class RenderContext:
    assessment_id: str
    generated_at: str
    company_name: str
    system_name: str
    risk_tier: str
    risk_tier_label: str
    primary_actor_role: str
    actor_role_label: str
    classification_status: str
    confidence: str | None
    rule_version: int
    source_version: str
    legal_source_title: str
    legal_source_url: str
    triggered_rules: list[TriggeredRuleRow] = field(default_factory=list)
    obligations: list[ObligationRow] = field(default_factory=list)
    answers: dict[str, Any] = field(default_factory=dict)
    answer_rows: list[tuple[str, str]] = field(default_factory=list)
    missing_variables: list[str] = field(default_factory=list)
    pack_sku: str = "evidence_pack"
    required_documents: list[str] = field(default_factory=list)
    is_high_risk: bool = False
    needs_fria: bool = False
    needs_provider_conformity: bool = False

    def template_dict(self) -> dict[str, Any]:
        from app.documents.labels import executive_summary

        d = {
            "assessment_id": self.assessment_id,
            "generated_at": self.generated_at,
            "company_name": self.company_name,
            "system_name": self.system_name,
            "risk_tier": self.risk_tier,
            "risk_tier_label": self.risk_tier_label,
            "primary_actor_role": self.primary_actor_role,
            "actor_role_label": self.actor_role_label,
            "classification_status": self.classification_status,
            "confidence": self.confidence or "not stated",
            "rule_version": self.rule_version,
            "source_version": self.source_version,
            "legal_source_title": self.legal_source_title,
            "legal_source_url": self.legal_source_url,
            "triggered_rules": [r.__dict__ for r in self.triggered_rules],
            "obligations": [o.__dict__ for o in self.obligations],
            "answers": self.answers,
            "answer_rows": self.answer_rows,
            "missing_variables": self.missing_variables,
            "pack_sku": self.pack_sku,
            "required_documents": self.required_documents,
            "has_missing": len(self.missing_variables) > 0,
            "is_high_risk": self.is_high_risk,
            "needs_fria": self.needs_fria,
            "needs_provider_conformity": self.needs_provider_conformity,
        }
        d["executive_summary"] = executive_summary(d)
        return d

    def validate(self) -> None:
        """Fail build if obligations lack legal citations (FR-DG-001)."""
        for obl in self.obligations:
            if not obl.legal_citation:
                raise ValueError(f"Obligation missing legal citation: {obl.title}")
        for rule in self.triggered_rules:
            if not rule.legal_citation:
                raise ValueError(f"Triggered rule missing legal citation: {rule.rule_code}")
