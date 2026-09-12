import json
from ingestion_layer import file_upload
from detector_layer import detector, valid_check, boundary_checkor
from normalizer_layer import normalizer
from purpose_layer import purpose_info
from pprint import pprint


with open('knowledge/dpdpa_sections.json', 'r') as f:
    dpdpa_info = json.load(f)


def main_assess(purpose_info_data):
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
    return purpose_info_data


# load file
file_content = file_upload('file_kyc_doc.txt')

detected_data = detector(file_content)

boundary_checked_data = boundary_checkor(file_content, detected_data)

validated_checked_data = valid_check(boundary_checked_data)

normalized_data = normalizer(validated_checked_data)

# pprint(normalized_data)

purpose_info_data = purpose_info(normalized_data)

# pprint(purpose_info_data)
output = main_assess(purpose_info_data)
pprint(output)