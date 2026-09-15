import json
from ingestion_layer import file_upload
from detector_layer import detector, valid_check, boundary_checkor
from normalizer_layer import normalizer
from purpose_layer import purpose_info
from pprint import pprint


with open('knowledge/dpdpa_sections.json', 'r') as f:
    dpdpa_info = json.load(f)

child_sensitive_data = ["school", "student", "minor", "child", "under_18", "kindergarten", "primary", "secondary", "edtech", "kids", "juvenile"]

def assessment(purpose_info_data):
    count  = 1
    for entity in purpose_info_data['entities']:
        # 1st lookup
        if entity['entity_type'] in dpdpa_info:
            # print(entity, entity['entity_type'])
            entity_data_info = dpdpa_info[entity['entity_type']]
            processing_purpose = entity['processing_purpose']
            # count += 1
            # print(count)
            # pprint(entity_data_info)
            entity['dpdpa_assessment'] = {
                'government_sections': entity_data_info['purpose_assessments'][processing_purpose]['governing_sections'],
                'sensitivity': entity_data_info['base_sensitivity'],
                'consent_required': entity_data_info['purpose_assessments'][processing_purpose]['consent_required'],
                'purpose_valid':entity_data_info['purpose_assessments'][processing_purpose]['purpose_valid'],
                'voilation_flags': entity_data_info['purpose_assessments'][processing_purpose]['violation_flags'],
                'penalty_exposure_crore': entity_data_info['purpose_assessments'][processing_purpose]['penalty_exposure_crore'],
                'recommended_actions': entity_data_info['purpose_assessments'][processing_purpose]['recommended_actions']
            }
            if entity['dpdpa_assessment']['purpose_valid']:
                entity['dpdpa_assessment']['risk_level'] = 'LOW'
            else:
                if entity['dpdpa_assessment']['sensitivity'] == "LOW":
                    entity['dpdpa_assessment']['risk_level'] = 'MEDIUM'
                if entity['dpdpa_assessment']['sensitivity'] == "MEDIUM":
                    entity['dpdpa_assessment']['risk_level'] = 'HIGH'
                if entity['dpdpa_assessment']['sensitivity'] == "HIGH":
                    entity['dpdpa_assessment']['risk_level'] = 'CRITICAL'
                if entity['dpdpa_assessment']['sensitivity'] == "CRITICAL":
                    entity['dpdpa_assessment']['risk_level'] = 'CRITICAL'
        for word in child_sensitive_data:
            if (word in purpose_info_data['metadata']['source_tag']) or (word in purpose_info_data['metadata']['source']):
                purpose_info_data['metadata']['children_data_entities_requiring_review'] = {
                        "children_data_detected": True,
                        "children_data_signal": "source_tag_keyword",
                        "children_data_keywords_found": word,
                        "children_data_disclaimer": "Heuristic detection based on source path keywords. \n Cannot confirm which specific data subjects are children. \n Manual review required to identify child data principals and apply Section 9 DPDPA obligations including verifiable parental consent before any processing."
                }
                break
            else:
                purpose_info_data['metadata']['children_data_entities_requiring_review'] = {"children_data_detected": False}
    return purpose_info_data

def report(assessment_data):
    no_of_entities = len(assessment_data['entities'])
    assessment_data['metadata']['total_entities_found'] = no_of_entities
    entities_with_voilation = 0
    voilation_flags_overall = set({})
    max_penality_exposure = 0
    # risk_level calculaiton variables
    critical = 0
    high = 0
    low = 0
    medium = 0
    is_urgent = False
    for entity in assessment_data['entities']:
        voilation_flags_overall = {x for x in entity['dpdpa_assessment']['voilation_flags']}
        if entity['dpdpa_assessment']['risk_level'] == "CRITICAL":
            critical += 1
        elif entity['dpdpa_assessment']['risk_level'] == "HIGH":
            high += 1
        elif entity['dpdpa_assessment']['risk_level'] == "MEDIUM":
            medium += 1
        else:
            low += 1
        if entity['dpdpa_assessment']['penalty_exposure_crore'] > max_penality_exposure:
            max_penality_exposure = entity['dpdpa_assessment']['penalty_exposure_crore']
        if entity['dpdpa_assessment']['purpose_valid']:
            entities_with_voilation += 1
        if entity['dpdpa_assessment']['penalty_exposure_crore'] > 100 or entity['dpdpa_assessment']['purpose_valid'] == False:
            is_urgent = is_urgent and True
        else:
            is_urgent = is_urgent and False
    assessment_data['metadata']['compliance_summary'] = {
        "total_entities_assessed": no_of_entities,
        "entities_with_violations": entities_with_voilation,
        "violation_types_found": set(voilation_flags_overall),
        "max_penalty_exposure_crore": max_penality_exposure,
        "requires_immediate_action": is_urgent,
    }
    if max (critical, high, medium, low) == critical:
        assessment_data['metadata']['compliance_summary']['overall_risk_level'] = 'CRITICAL'
    if max (critical, high, medium, low) == high:
        assessment_data['metadata']['compliance_summary']['overall_risk_level'] = 'HIGH'
    if max (critical, high, medium, low) == medium:
        assessment_data['metadata']['compliance_summary']['overall_risk_level'] = 'MEDIUM'
    else:
        assessment_data['metadata']['compliance_summary']['overall_risk_level'] = 'LOW'
    return assessment_data

# load file
file_content = file_upload('school_data_info_comparision.txt')

detected_data = detector(file_content)

boundary_checked_data = boundary_checkor(file_content, detected_data)

validated_checked_data = valid_check(boundary_checked_data)

normalized_data = normalizer(validated_checked_data)

# pprint(normalized_data)

purpose_info_data = purpose_info(normalized_data)

# pprint(purpose_info_data)
assessment_data = assessment(purpose_info_data)

output = report(assessment_data)

pprint(output)