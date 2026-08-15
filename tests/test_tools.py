import pytest

from professional_productivity_lab import BilingualTemplateManager, build_kpi_report, redact_confidential_text


def test_confidentiality_redactor_combines_standard_and_custom_rules():
    result = redact_confidential_text(
        "Email help@example.com, call 514-555-0123, server 192.168.1.20, project North Star.",
        custom_terms=["North Star"],
    )
    assert result["redaction_count"] == 4
    assert "help@example.com" not in result["text"]
    assert "North Star" not in result["text"]


def test_kpi_report_handles_invalid_rows_and_target_direction():
    report = build_kpi_report(
        [{"resolution_hours": 3}, {"resolution_hours": "4.5"}, {"resolution_hours": "unknown"}],
        value_field="resolution_hours",
        target=5,
        direction="at_most",
    )
    assert report["count"] == 2
    assert report["average"] == 3.75
    assert report["target_met"] is True
    assert report["rejected_rows"] == [3]


def test_kpi_report_rejects_unknown_direction():
    with pytest.raises(ValueError):
        build_kpi_report([], value_field="value", target=1, direction="approximately")


def test_bilingual_templates_require_matching_fields_and_render_both_languages():
    manager = BilingualTemplateManager()
    manager.add(
        "status",
        "Hello {name}, request {request_id} is ready.",
        "Bonjour {name}, la demande {request_id} est prête.",
    )
    assert manager.list_templates() == ["status"]
    assert manager.render("status", "en", {"name": "Sam", "request_id": "R-10"}).startswith("Hello Sam")
    assert manager.render("status", "français", {"name": "Sam", "request_id": "R-10"}).startswith("Bonjour Sam")


def test_bilingual_templates_reject_field_drift_and_missing_values():
    manager = BilingualTemplateManager()
    with pytest.raises(ValueError):
        manager.add("bad", "Hello {name}", "Bonjour {personne}")
    manager.add("good", "Hello {name}", "Bonjour {name}")
    with pytest.raises(ValueError):
        manager.render("good", "fr", {})
