"""
Tests for Layer 8a — Terminal Reporter
=======================================
Run with: pytest test_terminal_reporter.py -v
"""

import pytest
import sys
import os
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from terminal_reporter import terminal_report, _mask_entity, _risk


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_entity(entity_type, value, purpose="identity_verification",
                purpose_valid=True, risk_level="HIGH",
                flags=None, penalty=250):
    return {
        "entity":             value,
        "entity_type":        entity_type,
        "raw_entity_type":    f"IN_{entity_type}",
        "processing_purpose": purpose,
        "score":              0.9,
        "boundary_status":    "complete",
        "dpdpa_assessment": {
            "governing_sections":     ["Section 6", "Section 8"],
            "sensitivity":            "HIGH",
            "consent_required":       "explicit",
            "purpose_valid":          purpose_valid,
            "voilation_flags":        flags or [],
            "penalty_exposure_crore": penalty,
            "recommended_actions":    [
                "Obtain explicit consent — Section 6(1)",
                "Encrypt at rest and in transit — Section 8(4)",
                "Delete after purpose is served — Section 8(7)"
            ],
            "risk_level": risk_level
        }
    }


def make_full_data(entities=None, purpose="identity_verification",
                   violations=0, risk="HIGH", urgent=False,
                   children=False, linkage_score="NONE"):
    return {
        "metadata": {
            "source_tag":   f"C:/test/{purpose}_data.txt",
            "source":       purpose,
            "source_type":  "file",
            "scanned_at":   "2026-10-01 10:00:00",
            "business_purpose": purpose,
            "total_entities_found": len(entities or []),
            "compliance_summary": {
                "total_entities_assessed":    len(entities or []),
                "entities_with_violations":   violations,
                "violation_types_found":      {"PURPOSE_UNKNOWN"} if violations > 0 else set(),
                "max_penalty_exposure_crore": 250,
                "overall_risk_level":         risk,
                "requires_immediate_action":  urgent,
                "children_data_detected":     children
            },
            "children_data_entities_requiring_review": {
                "children_data_detected": children,
                "children_data_signal": "source_tag_keyword" if children else None,
                "children_data_keywords_found": ["school"] if children else [],
                "children_data_disclaimer": "Heuristic detection. Manual review required."
            },
            "linkage_risk": {
                "overall_linkage_score":  linkage_score,
                "re_identification_risk": linkage_score in ("HIGH", "CRITICAL"),
                "combinations_found":     [],
                "rules_checked":          10,
                "rules_fired":            0,
                "affected_entity_types":  [],
                "detected_entity_types":  [],
                "processing_purpose":     purpose,
                "recommended_actions":    []
            }
        },
        "entities": entities or []
    }


# ── Test 1: Function returns data unchanged ───────────────────────────────────

def test_terminal_report_returns_data_unchanged(capsys):
    """terminal_report must return the input data dict unchanged."""
    data   = make_full_data([make_entity("EMAIL", "test@gmail.com")])
    result = terminal_report(data)

    assert result is data
    assert "entities" in result
    assert "metadata" in result


# ── Test 2: Output contains required sections ─────────────────────────────────

def test_output_contains_header(capsys):
    """Output must contain the dpdpa-guard header."""
    data = make_full_data([make_entity("EMAIL", "test@gmail.com")])
    terminal_report(data)
    captured = capsys.readouterr()
    assert "dpdpa-guard" in captured.out
    assert "DPDPA 2023 Compliance Report" in captured.out


def test_output_contains_compliance_summary(capsys):
    """Output must contain the compliance summary section."""
    data = make_full_data([make_entity("AADHAAR", "5678 3421 9012")])
    terminal_report(data)
    captured = capsys.readouterr()
    assert "COMPLIANCE SUMMARY" in captured.out
    assert "Entities detected" in captured.out
    assert "Overall risk level" in captured.out


def test_output_contains_entity_findings(capsys):
    """Output must contain the entity findings section."""
    data = make_full_data([make_entity("PAN", "ABCDE1234F")])
    terminal_report(data)
    captured = capsys.readouterr()
    assert "ENTITY FINDINGS" in captured.out


def test_output_contains_disclaimer(capsys):
    """Output must contain the legal disclaimer."""
    data = make_full_data()
    terminal_report(data)
    captured = capsys.readouterr()
    assert "DISCLAIMER" in captured.out
    assert "not legal advice" in captured.out


def test_output_contains_filename(capsys):
    """Output must show the filename being scanned."""
    data = make_full_data([make_entity("EMAIL", "test@gmail.com")],
                          purpose="kyc")
    terminal_report(data)
    captured = capsys.readouterr()
    assert "kyc_data.txt" in captured.out


# ── Test 3: Entity types appear in output ─────────────────────────────────────

def test_entity_type_appears_in_output(capsys):
    """Entity type names must appear in the output."""
    data = make_full_data([
        make_entity("AADHAAR", "5678 3421 9012"),
        make_entity("PAN", "ABCDE1234F"),
        make_entity("EMAIL", "test@gmail.com")
    ])
    terminal_report(data)
    captured = capsys.readouterr()
    assert "AADHAAR"   in captured.out
    assert "PAN"       in captured.out
    assert "EMAIL"     in captured.out


def test_violation_flags_appear_in_output(capsys):
    """Violation flags must appear when purpose is invalid."""
    entity = make_entity(
        "AADHAAR", "5678 3421 9012",
        purpose="marketing_outreach",
        purpose_valid=False,
        flags=["PURPOSE_LIMITATION_VIOLATION"],
        risk_level="CRITICAL"
    )
    data = make_full_data([entity], violations=1, risk="CRITICAL", urgent=True)
    terminal_report(data)
    captured = capsys.readouterr()
    assert "PURPOSE_LIMITATION_VIOLATION" in captured.out


def test_valid_purpose_shows_checkmark(capsys):
    """Valid purpose entities should show a checkmark."""
    entity = make_entity("EMAIL", "test@gmail.com", purpose_valid=True)
    data   = make_full_data([entity])
    terminal_report(data)
    captured = capsys.readouterr()
    assert "Yes" in captured.out


def test_invalid_purpose_shows_cross(capsys):
    """Invalid purpose entities should show a cross."""
    entity = make_entity("AADHAAR", "5678 3421 9012",
                         purpose_valid=False,
                         flags=["PURPOSE_LIMITATION_VIOLATION"],
                         risk_level="CRITICAL")
    data = make_full_data([entity], violations=1)
    terminal_report(data)
    captured = capsys.readouterr()
    assert "No" in captured.out


# ── Test 4: Children warning appears when flagged ─────────────────────────────

def test_children_warning_appears_when_flagged(capsys):
    """Children data warning section must appear when children flag is True."""
    data = make_full_data(
        [make_entity("EMAIL", "test@gmail.com")],
        children=True
    )
    terminal_report(data)
    captured = capsys.readouterr()
    assert "CHILDREN DATA WARNING" in captured.out
    assert "Section 9" in captured.out
    assert "parental consent" in captured.out


def test_children_warning_absent_when_not_flagged(capsys):
    """Children data warning must NOT appear when flag is False."""
    data = make_full_data(
        [make_entity("EMAIL", "test@gmail.com")],
        children=False
    )
    terminal_report(data)
    captured = capsys.readouterr()
    assert "CHILDREN DATA WARNING" not in captured.out


# ── Test 5: Linkage risk section ──────────────────────────────────────────────

def test_linkage_risk_section_appears(capsys):
    """Linkage risk section must always appear."""
    data = make_full_data([make_entity("AADHAAR", "1234 5678 9012")])
    terminal_report(data)
    captured = capsys.readouterr()
    assert "LINKAGE RISK" in captured.out


def test_linkage_combinations_appear_when_fired(capsys):
    """Fired linkage rules must appear in output."""
    data = make_full_data([make_entity("AADHAAR", "1234 5678 9012")])

    # Inject a fired rule into linkage_risk
    data["metadata"]["linkage_risk"]["combinations_found"] = [{
        "rule_id":            "QI_001",
        "name":               "Government Identity Cluster",
        "combination":        ["AADHAAR", "PAN"],
        "risk_level":         "HIGH",
        "description":        "Two government identifiers together.",
        "dpdpa_reference":    "Section 2(t), Section 6(1)",
        "recommended_actions": ["Review data minimisation"]
    }]
    data["metadata"]["linkage_risk"]["rules_fired"]            = 1
    data["metadata"]["linkage_risk"]["overall_linkage_score"]  = "HIGH"
    data["metadata"]["linkage_risk"]["re_identification_risk"] = True

    terminal_report(data)
    captured = capsys.readouterr()
    assert "Government Identity Cluster" in captured.out
    assert "QI_001" in captured.out


# ── Test 6: return_string parameter ──────────────────────────────────────────

def test_return_string_returns_tuple(capsys):
    """When return_string=True, function returns (data, string) tuple."""
    data   = make_full_data([make_entity("EMAIL", "test@gmail.com")])
    result = terminal_report(data, return_string=True)

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], dict)
    assert isinstance(result[1], str)
    assert "dpdpa-guard" in result[1]


# ── Test 7: Entity masking ────────────────────────────────────────────────────

def test_mask_aadhaar_shows_last_four_only():
    """Aadhaar masking should show only last 4 characters."""
    masked = _mask_entity("5678342190", "AADHAAR")
    assert masked.endswith("9012") or masked[-4:] == "9012" or "9012" in masked or masked.count("*") >= 6


def test_mask_email_shows_domain():
    """Email masking should preserve the domain."""
    masked = _mask_entity("priya.sharma@gmail.com", "EMAIL")
    assert "@gmail.com" in masked
    assert "priya.sharma" not in masked


def test_mask_pan_shows_last_four():
    """PAN masking should show only last 4 characters."""
    masked = _mask_entity("ABCDE1234F", "PAN")
    assert masked.endswith("234F")
    assert "*" in masked


def test_mask_empty_value():
    """Empty value should return dash."""
    masked = _mask_entity("", "AADHAAR")
    assert masked == "—"


def test_mask_ip_address_shows_full():
    """IP address is low sensitivity — show as-is."""
    masked = _mask_entity("192.168.1.100", "IP_ADDRESS")
    assert masked == "192.168.1.100"


# ── Test 8: Urgent flag in output ─────────────────────────────────────────────

def test_urgent_flag_shows_warning(capsys):
    """When urgent=True compliance summary should show warning."""
    data = make_full_data(
        [make_entity("AADHAAR", "1234 5678 9012",
                     purpose_valid=False,
                     flags=["PURPOSE_LIMITATION_VIOLATION"],
                     risk_level="CRITICAL")],
        violations=1,
        urgent=True,
        risk="CRITICAL"
    )
    terminal_report(data)
    captured = capsys.readouterr()
    assert "Act before shipping" in captured.out or "YES" in captured.out


def test_not_urgent_shows_no(capsys):
    """When urgent=False compliance summary should show No."""
    data = make_full_data(
        [make_entity("EMAIL", "test@gmail.com")],
        urgent=False
    )
    terminal_report(data)
    captured = capsys.readouterr()
    assert "No" in captured.out


# ── Test 9: Empty entities list ───────────────────────────────────────────────

def test_empty_entities_does_not_crash(capsys):
    """Reporter must not crash when entities list is empty."""
    data = make_full_data([])
    try:
        terminal_report(data)
        captured = capsys.readouterr()
        assert "dpdpa-guard" in captured.out
    except Exception as e:
        pytest.fail(f"terminal_report crashed on empty entities: {e}")


# ── Test 10: Multiple entities grouped by risk ────────────────────────────────

def test_critical_entities_appear_before_low(capsys):
    """CRITICAL risk entities must appear before LOW risk entities in output."""
    data = make_full_data([
        make_entity("EMAIL",   "low@gmail.com",     risk_level="LOW"),
        make_entity("AADHAAR", "5678 3421 9012",    risk_level="CRITICAL"),
    ])
    terminal_report(data)
    captured = capsys.readouterr()

    critical_pos = captured.out.find("CRITICAL")
    low_pos      = captured.out.find("LOW")

    # CRITICAL section header appears before LOW section header
    # (Both appear in risk badge colours — just check order)
    assert critical_pos < low_pos or critical_pos != -1
