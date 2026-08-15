"""Reusable helpers for confidentiality, reporting and bilingual templates."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any, Iterable, Mapping
import re


def redact_confidential_text(text: str, custom_terms: Iterable[str] = ()) -> dict[str, Any]:
    """Redact common confidential tokens and caller-supplied organization terms."""
    rules = [
        ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
        ("phone", re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)")),
        ("ip_address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
        ("api_token", re.compile(r"\b(?:sk|api|token)[-_][A-Za-z0-9_-]{12,}\b", re.I)),
    ]
    redacted = text
    counts: dict[str, int] = {}
    for label, rule in rules:
        redacted, count = rule.subn(f"[REDACTED_{label.upper()}]", redacted)
        if count:
            counts[label] = count
    for index, term in enumerate(custom_terms, start=1):
        cleaned = term.strip()
        if not cleaned:
            continue
        redacted, count = re.subn(re.escape(cleaned), f"[REDACTED_CUSTOM_{index}]", redacted, flags=re.I)
        if count:
            counts[f"custom_{index}"] = count
    return {"text": redacted, "redaction_count": sum(counts.values()), "counts": counts}


def build_kpi_report(
    rows: Iterable[Mapping[str, Any]],
    *,
    value_field: str,
    target: float,
    direction: str = "at_least",
) -> dict[str, Any]:
    """Summarize a numeric KPI and compare it with an explicit target."""
    if direction not in {"at_least", "at_most"}:
        raise ValueError("direction must be 'at_least' or 'at_most'")
    values: list[float] = []
    rejected_rows: list[int] = []
    for row_number, row in enumerate(rows, start=1):
        try:
            values.append(float(row[value_field]))
        except (KeyError, TypeError, ValueError):
            rejected_rows.append(row_number)
    if not values:
        return {
            "count": 0,
            "average": None,
            "minimum": None,
            "maximum": None,
            "target": target,
            "target_met": False,
            "rejected_rows": rejected_rows,
        }
    average = mean(values)
    target_met = average >= target if direction == "at_least" else average <= target
    return {
        "count": len(values),
        "average": round(average, 2),
        "minimum": min(values),
        "maximum": max(values),
        "target": target,
        "target_met": target_met,
        "direction": direction,
        "rejected_rows": rejected_rows,
    }


@dataclass(frozen=True)
class Template:
    key: str
    english: str
    french: str


class BilingualTemplateManager:
    """Store and render paired French/English templates with strict fields."""

    def __init__(self, templates: Iterable[Template | Mapping[str, str]] = ()) -> None:
        self._templates: dict[str, Template] = {}
        for template in templates:
            if isinstance(template, Template):
                self.add(template.key, template.english, template.french)
            else:
                self.add(template["key"], template["english"], template["french"])

    def add(self, key: str, english: str, french: str) -> None:
        normalized = key.strip().casefold()
        if not normalized or not english.strip() or not french.strip():
            raise ValueError("key and both language versions are required")
        english_fields = _template_fields(english)
        french_fields = _template_fields(french)
        if english_fields != french_fields:
            raise ValueError("English and French templates must use the same fields")
        self._templates[normalized] = Template(normalized, english.strip(), french.strip())

    def render(self, key: str, language: str, values: Mapping[str, Any]) -> str:
        template = self._templates[key.strip().casefold()]
        selected = template.french if language.strip().casefold() in {"fr", "fra", "french", "français"} else template.english
        required = _template_fields(selected)
        missing = sorted(required - set(values))
        if missing:
            raise ValueError(f"missing template values: {', '.join(missing)}")
        return selected.format_map(values)

    def list_templates(self) -> list[str]:
        return sorted(self._templates)


def _template_fields(value: str) -> set[str]:
    return set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", value))
