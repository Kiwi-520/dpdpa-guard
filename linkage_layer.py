"""
Layer 6 — Linkage Risk Analysis
================================
Detects quasi-identifier combinations that together create
re-identification risk under DPDPA 2023 Section 2(t).

Section 2(t) defines personal data as data that identifies
a person DIRECTLY OR INDIRECTLY. This layer catches the
indirect identification case — combinations of fields that
individually identify nobody but together identify one person.

Input:  Full data dict from Layer 5 (with dpdpa_assessment on every entity)
Output: Same dict with linkage_risk added to metadata
"""

import json
import os
from pprint import pprint

# ── Load rules once at module level ───────────────────────────────────────────
_rules_path = os.path.join(os.path.dirname(__file__), "knowledge", "quasi_identifier_rules.json")

with open(_rules_path, "r", encoding="utf-8") as f:
    _rules_data = json.load(f)

RULES = _rules_data["rules"]

# ── Priority map for risk level comparison ────────────────────────────────────
RISK_PRIORITY = {
    "CRITICAL": 4,
    "HIGH":     3,
    "MEDIUM":   2,
    "LOW":      1,
    "NONE":     0
}


# ── Main function ─────────────────────────────────────────────────────────────
def linkage_check(assessment_data: dict) -> dict:
    """
    Receives the full data dict from Layer 5.
    Adds linkage_risk object to metadata.
    Updates compliance_summary if high/critical linkage found.
    Returns enriched data dict.
    """

    # Step 1 — Build set of entity types present in this document
    detected_entity_types = set()
    for entity in assessment_data["entities"]:
        detected_entity_types.add(entity["entity_type"])

    # Step 2 — Check each rule against detected entity types
    fired_rules      = []
    highest_risk     = "NONE"
    affected_types   = set()

    for rule in RULES:
        rule_combination = set(rule["combination"])

        # Subset check — are ALL entity types in this rule present in the document?
        if rule_combination.issubset(detected_entity_types):

            fired_rules.append({
                "rule_id":            rule["rule_id"],
                "name":               rule["name"],
                "combination":        rule["combination"],
                "risk_level":         rule["risk_level"],
                "description":        rule["description"],
                "dpdpa_reference":    rule["dpdpa_reference"],
                "recommended_actions": rule["recommended_actions"]
            })

            # Track highest risk across all fired rules
            if RISK_PRIORITY.get(rule["risk_level"], 0) > RISK_PRIORITY.get(highest_risk, 0):
                highest_risk = rule["risk_level"]

            # Track which entity types are involved in any fired rule
            affected_types.update(rule["combination"])

    # Step 3 — Determine overall re-identification risk
    re_identification_risk = highest_risk in ("HIGH", "CRITICAL")

    # Step 4 — Context modulation
    # If purpose is unknown or invalid, escalate all MEDIUM → HIGH
    processing_purpose = assessment_data["metadata"].get("business_purpose", "unknown_purpose")
    invalid_purposes   = ["unknown_purpose", "marketing_outreach"]

    if processing_purpose in invalid_purposes and highest_risk == "MEDIUM":
        highest_risk = "HIGH"
        for rule in fired_rules:
            if rule["risk_level"] == "MEDIUM":
                rule["risk_level"]        = "HIGH"
                rule["context_escalated"] = True
                rule["escalation_reason"] = (
                    f"Risk escalated from MEDIUM to HIGH because "
                    f"processing purpose '{processing_purpose}' is not "
                    f"a valid basis for this combination under Section 6(1)"
                )

    # Step 5 — Build linkage_risk object
    assessment_data["metadata"]["linkage_risk"] = {
        "overall_linkage_score":   highest_risk,
        "re_identification_risk":  re_identification_risk,
        "combinations_found":      fired_rules,
        "rules_checked":           len(RULES),
        "rules_fired":             len(fired_rules),
        "affected_entity_types":   list(affected_types),
        "detected_entity_types":   list(detected_entity_types),
        "processing_purpose":      processing_purpose,
        "recommended_actions": _build_overall_recommendations(fired_rules, highest_risk)
    }

    # Step 6 — Update compliance_summary if linkage risk is HIGH or CRITICAL
    if "compliance_summary" in assessment_data["metadata"]:
        if highest_risk in ("HIGH", "CRITICAL"):
            assessment_data["metadata"]["compliance_summary"]["requires_immediate_action"] = True
            assessment_data["metadata"]["compliance_summary"]["linkage_risk_level"] = highest_risk

    return assessment_data


def _build_overall_recommendations(fired_rules: list, highest_risk: str) -> list:
    """
    Builds a deduplicated list of overall recommended actions
    from all fired rules, prioritised by risk level.
    """
    if not fired_rules:
        return ["No quasi-identifier combinations detected — linkage risk is low"]

    # Start with universal recommendations for any linkage finding
    recommendations = [
        "Review data minimisation across all detected entity types — Section 6(1)",
        "Verify that consent was obtained for COMBINED processing, not just individual collection",
        "Implement field-level access controls — not all roles should access all identifiers simultaneously",
    ]

    if highest_risk == "CRITICAL":
        recommendations.insert(0, "CRITICAL: Immediate security review required for this data combination")
        recommendations.insert(1, "CRITICAL: Restrict database queries that return all identifiers simultaneously")

    if highest_risk in ("HIGH", "CRITICAL"):
        recommendations.append("Implement breach notification process covering this combination — Section 8(6)")
        recommendations.append("Consider data separation — store identifier categories in separate access-controlled tables")

    return recommendations


# # ── Run standalone for testing ────────────────────────────────────────────────
# if __name__ == "__main__":
#     import sys
#     sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

#     from ingestion_layer  import file_upload
#     from detector_layer   import detector, boundary_checkor, valid_check
#     from normalizer_layer import normalizer
#     from purpose_layer    import purpose_info
#     from engine_layer     import assessment, report

#     # # Change this filename to test different scenarios
#     # filename = "sample_doc.txt"

#     # print(f"\n{'='*60}")
#     # print(f"  dpdpa-guard — Layer 6 Linkage Risk Test")
#     # print(f"  File: {filename}")
#     # print(f"{'='*60}\n")

#     # file_content          = file_upload(filename)
#     # detected_data         = detector(file_content)
#     # boundary_checked      = boundary_checkor(file_content, detected_data)
#     # validated             = valid_check(boundary_checked)
#     # normalised            = normalizer(validated)
#     # purpose_data          = purpose_info(normalised)
#     # assessed              = assessment(purpose_data)
#     # after_report          = report(assessed)
#     # final_output          = linkage_check(after_report)

#     # # Print only the linkage risk section for clarity
#     # print("LINKAGE RISK RESULT:")
#     # print("-" * 40)
#     # linkage = final_output["metadata"]["linkage_risk"]
#     # print(f"Overall score:          {linkage['overall_linkage_score']}")
#     # print(f"Re-identification risk: {linkage['re_identification_risk']}")
#     # print(f"Rules checked:          {linkage['rules_checked']}")
#     # print(f"Rules fired:            {linkage['rules_fired']}")
#     # print(f"Detected entity types:  {sorted(linkage['detected_entity_types'])}")
#     # print(f"Affected by linkage:    {sorted(linkage['affected_entity_types'])}")
#     # print()

#     # if linkage["combinations_found"]:
#     #     print("COMBINATIONS FOUND:")
#     #     print("-" * 40)
#     #     for combo in linkage["combinations_found"]:
#     #         print(f"\n[{combo['risk_level']}] {combo['name']}")
#     #         print(f"  Rule:        {combo['rule_id']}")
#     #         print(f"  Types:       {combo['combination']}")
#     #         print(f"  DPDPA ref:   {combo['dpdpa_reference']}")
#     #         print(f"  Description: {combo['description']}")
#     #         if combo.get("context_escalated"):
#     #             print(f"  ⚠ Escalated: {combo['escalation_reason']}")
#     # else:
#     #     print("No quasi-identifier combinations detected.")
#     #     print("Linkage risk: LOW / NONE")

#     # print()
#     # print("OVERALL RECOMMENDED ACTIONS:")
#     # print("-" * 40)
#     # for i, action in enumerate(linkage["recommended_actions"], 1):
#     #     print(f"  {i}. {action}")

#     # print()
#     # print("UPDATED COMPLIANCE SUMMARY:")
#     # print("-" * 40)
#     # pprint(final_output["metadata"]["compliance_summary"])
