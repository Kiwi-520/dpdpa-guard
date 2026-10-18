"""
Tests for Layer 6 — Linkage Risk Analysis
==========================================
Run with: pytest test_linkage_layer.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from linkage_layer import linkage_check, RULES, RISK_PRIORITY


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_entity(entity_type: str, purpose: str = "identity_verification") -> dict:
    """Create a minimal entity dict for testing."""
    return {
        "entity":            "TEST_VALUE",
        "entity_type":       entity_type,
        "raw_entity_type":   "TEST_RAW",
        "processing_purpose": purpose,
        "score":             0.9,
        "boundary_status":   "complete",
        "dpdpa_assessment": {
            "purpose_valid":          True,
            "risk_level":             "HIGH",
            "penalty_exposure_crore": 250,
            "voilation_flags":        []
        }
    }


def make_data(entity_types: list, purpose: str = "identity_verification") -> dict:
    """Create a minimal data dict with given entity types."""
    return {
        "metadata": {
            "source_tag":       f"test_{purpose}_file.txt",
            "source":           purpose.replace("_", ""),
            "source_type":      "file",
            "scanned_at":       "2026-10-01 10:00:00",
            "business_purpose": purpose,
            "total_entities_found": len(entity_types),
            "compliance_summary": {
                "total_entities_assessed":    len(entity_types),
                "entities_with_violations":   0,
                "violation_types_found":      set(),
                "max_penalty_exposure_crore": 250,
                "overall_risk_level":         "HIGH",
                "requires_immediate_action":  False,
                "children_data_detected":     False
            }
        },
        "entities": [make_entity(et, purpose) for et in entity_types]
    }


# ── Test 1: No combinations — NONE risk ───────────────────────────────────────

def test_no_linkage_risk_with_single_entity():
    """Single entity type — no combinations possible — should return NONE."""
    data   = make_data(["EMAIL"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    assert lr["overall_linkage_score"]  == "NONE"
    assert lr["re_identification_risk"] == False
    assert lr["rules_fired"]            == 0
    assert lr["combinations_found"]     == []


def test_no_linkage_risk_with_two_unrelated_entities():
    """Two entities that don't form any rule combination."""
    data   = make_data(["EMAIL", "IP_ADDRESS"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    assert lr["overall_linkage_score"] == "NONE"
    assert lr["rules_fired"]           == 0


# ── Test 2: Known HIGH combination fires ──────────────────────────────────────

def test_pan_upi_ifsc_fires_high():
    """PAN + UPI + IFSC should fire QI_002 at HIGH risk."""
    data   = make_data(["PAN", "UPI", "IFSC"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    assert lr["overall_linkage_score"]  == "HIGH"
    assert lr["re_identification_risk"] == True
    assert lr["rules_fired"]            >= 1

    rule_ids = [r["rule_id"] for r in lr["combinations_found"]]
    assert "QI_002" in rule_ids


def test_aadhaar_pan_fires_high():
    """AADHAAR + PAN should fire QI_001 at HIGH risk."""
    data   = make_data(["AADHAAR", "PAN"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    assert lr["overall_linkage_score"] == "HIGH"
    rule_ids = [r["rule_id"] for r in lr["combinations_found"]]
    assert "QI_001" in rule_ids


# ── Test 3: CRITICAL combination ──────────────────────────────────────────────

def test_credit_card_upi_fires_critical():
    """CREDIT_CARD + UPI should fire QI_005 at CRITICAL risk."""
    data   = make_data(["CREDIT_CARD", "UPI"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    assert lr["overall_linkage_score"]  == "CRITICAL"
    assert lr["re_identification_risk"] == True

    rule_ids = [r["rule_id"] for r in lr["combinations_found"]]
    assert "QI_005" in rule_ids


def test_full_government_stack_fires_critical():
    """AADHAAR + PASSPORT + VOTER_ID should fire QI_006 at CRITICAL."""
    data   = make_data(["AADHAAR", "PASSPORT", "VOTER_ID"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    assert lr["overall_linkage_score"] == "CRITICAL"
    rule_ids = [r["rule_id"] for r in lr["combinations_found"]]
    assert "QI_006" in rule_ids


# ── Test 4: Multiple rules can fire simultaneously ────────────────────────────

def test_multiple_rules_fire_for_rich_document():
    """
    Document with many entity types should fire multiple rules.
    AADHAAR + PAN + UPI + IFSC + PERSON + EMAIL + PHONE
    """
    entity_types = ["AADHAAR", "PAN", "UPI", "IFSC", "PERSON", "EMAIL", "PHONE"]
    data   = make_data(entity_types)
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    # Many rules should fire for this combination
    assert lr["rules_fired"] >= 3
    assert lr["overall_linkage_score"] in ("HIGH", "CRITICAL")

    # Check affected types are a subset of what we passed in
    for affected in lr["affected_entity_types"]:
        assert affected in entity_types


# ── Test 5: Context escalation ────────────────────────────────────────────────

def test_medium_risk_escalates_for_marketing_purpose():
    """
    PERSON + EMAIL + PHONE is MEDIUM in KYC context.
    In marketing context it should escalate to HIGH.
    """
    # KYC context — stays MEDIUM
    kyc_data   = make_data(["PERSON", "EMAIL", "PHONE"], purpose="identity_verification")
    kyc_result = linkage_check(kyc_data)
    kyc_lr     = kyc_result["metadata"]["linkage_risk"]

    # Marketing context — should escalate
    mkt_data   = make_data(["PERSON", "EMAIL", "PHONE"], purpose="marketing_outreach")
    mkt_result = linkage_check(mkt_data)
    mkt_lr     = mkt_result["metadata"]["linkage_risk"]

    # Marketing context must not be lower risk than KYC context
    assert RISK_PRIORITY[mkt_lr["overall_linkage_score"]] >= RISK_PRIORITY[kyc_lr["overall_linkage_score"]]

    # At least one rule should be escalated in marketing context
    escalated = [r for r in mkt_lr["combinations_found"] if r.get("context_escalated")]
    assert len(escalated) >= 1


def test_unknown_purpose_escalates_medium_risk():
    """Unknown purpose should also escalate MEDIUM to HIGH."""
    data   = make_data(["PERSON", "EMAIL", "PHONE"], purpose="unknown_purpose")
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    # Should be HIGH after escalation from MEDIUM
    assert lr["overall_linkage_score"] in ("HIGH", "CRITICAL")


# ── Test 6: Compliance summary updated correctly ──────────────────────────────

def test_high_linkage_sets_requires_immediate_action():
    """HIGH linkage risk should set requires_immediate_action to True."""
    data   = make_data(["AADHAAR", "PAN"])
    result = linkage_check(data)

    summary = result["metadata"]["compliance_summary"]
    assert summary["requires_immediate_action"] == True
    assert summary["linkage_risk_level"] in ("HIGH", "CRITICAL")


def test_no_linkage_does_not_change_compliance_summary():
    """No linkage risk should not flip requires_immediate_action."""
    data = make_data(["EMAIL"])
    # Start with False
    data["metadata"]["compliance_summary"]["requires_immediate_action"] = False

    result  = linkage_check(data)
    summary = result["metadata"]["compliance_summary"]

    assert summary["requires_immediate_action"] == False


# ── Test 7: Output structure is correct ──────────────────────────────────────

def test_linkage_risk_structure_complete():
    """linkage_risk dict must have all required keys."""
    data   = make_data(["AADHAAR", "PAN", "EMAIL"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    required_keys = [
        "overall_linkage_score",
        "re_identification_risk",
        "combinations_found",
        "rules_checked",
        "rules_fired",
        "affected_entity_types",
        "detected_entity_types",
        "processing_purpose",
        "recommended_actions"
    ]

    for key in required_keys:
        assert key in lr, f"Missing key in linkage_risk: {key}"


def test_each_fired_rule_has_required_fields():
    """Every fired rule must have all required fields."""
    data   = make_data(["AADHAAR", "PAN"])
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    for rule in lr["combinations_found"]:
        assert "rule_id"             in rule
        assert "name"                in rule
        assert "combination"         in rule
        assert "risk_level"          in rule
        assert "description"         in rule
        assert "dpdpa_reference"     in rule
        assert "recommended_actions" in rule


# ── Test 8: Rules config sanity checks ───────────────────────────────────────

def test_all_rules_have_required_fields():
    """Every rule in the config must have required fields."""
    for rule in RULES:
        assert "rule_id"             in rule, f"Missing rule_id in {rule}"
        assert "name"                in rule
        assert "combination"         in rule
        assert "risk_level"          in rule
        assert "description"         in rule
        assert "dpdpa_reference"     in rule
        assert "recommended_actions" in rule
        assert rule["risk_level"] in RISK_PRIORITY, f"Unknown risk level in {rule['rule_id']}"
        assert len(rule["combination"]) >= 2, f"Rule {rule['rule_id']} needs at least 2 entity types"


def test_rule_ids_are_unique():
    """All rule IDs must be unique."""
    ids = [r["rule_id"] for r in RULES]
    assert len(ids) == len(set(ids)), "Duplicate rule IDs found"


def test_detected_types_is_superset_of_affected_types():
    """Affected entity types must be a subset of detected entity types."""
    entity_types = ["AADHAAR", "PAN", "UPI", "EMAIL"]
    data   = make_data(entity_types)
    result = linkage_check(data)
    lr     = result["metadata"]["linkage_risk"]

    detected = set(lr["detected_entity_types"])
    affected = set(lr["affected_entity_types"])

    assert affected.issubset(detected), (
        f"Affected types {affected} must be subset of detected types {detected}"
    )
