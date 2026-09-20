import json
from ingestion_layer import file_upload
from detector_layer import detector, valid_check, boundary_checkor
from normalizer_layer import normalizer
from purpose_layer import purpose_info
from pprint import pprint

with open('knowledge/dpdpa_sections.json', 'r', encoding='utf-8') as f:
    dpdpa_info = json.load(f)

CHILD_KEYWORDS = [
    "school", "student", "minor", "child", "under_18",
    "kindergarten", "primary", "secondary", "edtech", "kids", "juvenile"
]

RISK_PRIORITY = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


def assessment(purpose_info_data):
    for entity in purpose_info_data['entities']:

        if entity['entity_type'] not in dpdpa_info:
            entity['dpdpa_assessment'] = {
                'governing_sections':     ['UNKNOWN'],
                'sensitivity':            'UNKNOWN',
                'consent_required':       'UNKNOWN',
                'purpose_valid':          False,
                'voilation_flags':        ['UNKNOWN_ENTITY_TYPE'],
                'penalty_exposure_crore': 50,
                'recommended_actions':    ['Entity type not in knowledge base — review manually'],
                'risk_level':             'MEDIUM'
            }
            continue

        entity_info        = dpdpa_info[entity['entity_type']]
        purpose            = entity['processing_purpose']
        base_sensitivity   = entity_info['base_sensitivity']

        if purpose not in entity_info['purpose_assessments']:
            purpose = 'unknown_purpose'

        purpose_data = entity_info['purpose_assessments'][purpose]

        entity['dpdpa_assessment'] = {
            'governing_sections':     purpose_data['governing_sections'],
            'sensitivity':            base_sensitivity,
            'consent_required':       purpose_data['consent_required'],
            'purpose_valid':          purpose_data['purpose_valid'],
            'voilation_flags':        purpose_data['violation_flags'],
            'penalty_exposure_crore': purpose_data['penalty_exposure_crore'],
            'recommended_actions':    purpose_data['recommended_actions']
        }

        # Step 5 — risk level
        if purpose_data['purpose_valid']:
            entity['dpdpa_assessment']['risk_level'] = base_sensitivity
        else:
            escalation = {
                'LOW':      'MEDIUM',
                'MEDIUM':   'HIGH',
                'HIGH':     'CRITICAL',
                'CRITICAL': 'CRITICAL'
            }
            entity['dpdpa_assessment']['risk_level'] = escalation.get(base_sensitivity, 'MEDIUM')

    return purpose_info_data


def report(assessment_data):

    # --- Step 6: Children data detection ---
    matched_keywords = []
    source_tag_lower = assessment_data['metadata']['source_tag'].lower()
    source_lower     = assessment_data['metadata']['source'].lower()

    for word in CHILD_KEYWORDS:
        if word in source_tag_lower or word in source_lower:
            matched_keywords.append(word)

    if matched_keywords:
        assessment_data['metadata']['children_data_entities_requiring_review'] = {
            "children_data_detected":       True,
            "children_data_signal":         "source_tag_keyword",
            "children_data_keywords_found": matched_keywords,
            "children_data_disclaimer": (
                "Heuristic detection based on source path keywords. "
                "Cannot confirm which specific data subjects are children. "
                "Manual review required to identify child data principals "
                "and apply Section 9 DPDPA obligations including verifiable "
                "parental consent before any processing."
            )
        }
    else:
        assessment_data['metadata']['children_data_entities_requiring_review'] = {
            "children_data_detected": False
        }

    # --- Step 7: Compliance summary ---
    no_of_entities          = len(assessment_data['entities'])
    entities_with_violation = 0
    max_penalty             = 0
    is_urgent               = False
    violation_flags_overall = set()
    highest_risk            = "LOW"

    for entity in assessment_data['entities']:
        a = entity['dpdpa_assessment']

        # Accumulate all violation flags
        violation_flags_overall.update(a['voilation_flags'])

        # Track highest risk level
        current_risk = a['risk_level']
        if RISK_PRIORITY.get(current_risk, 0) > RISK_PRIORITY.get(highest_risk, 0):
            highest_risk = current_risk

        # Track max penalty
        if a['penalty_exposure_crore'] > max_penalty:
            max_penalty = a['penalty_exposure_crore']

        # Count violations
        if not a['purpose_valid']:
            entities_with_violation += 1

        # Urgent: violation AND penalty >= 100 crore
        if not a['purpose_valid'] and a['penalty_exposure_crore'] >= 100:
            is_urgent = True

    assessment_data['metadata']['compliance_summary'] = {
        "total_entities_assessed":    no_of_entities,
        "entities_with_violations":   entities_with_violation,
        "violation_types_found":      violation_flags_overall,
        "max_penalty_exposure_crore": max_penalty,
        "overall_risk_level":         highest_risk,
        "requires_immediate_action":  is_urgent,
        "children_data_detected":     bool(matched_keywords)
    }

    return assessment_data


# --- Pipeline ---
file_content         = file_upload('school_data_info_comparision.txt')
detected_data        = detector(file_content)
boundary_checked     = boundary_checkor(file_content, detected_data)
validated            = valid_check(boundary_checked)
normalised           = normalizer(validated)
purpose_data         = purpose_info(normalised)
assessed             = assessment(purpose_data)
output               = report(assessed)
pprint(output)