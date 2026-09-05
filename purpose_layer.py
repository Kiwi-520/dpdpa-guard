from ingestion_layer import file_upload
from detector_layer import detector, boundary_checkor, valid_check
from normalizer_layer import normalizer
# from knowledge import purpose_map
import json
from pprint import pprint

with open("knowledge/purpose_map.json", 'r') as f:
    config = json.load(f)

def purpose_info(normalized_data):
    metadata = normalized_data['metadata']
    source_tag = metadata['source_tag']

    for source in config:
        if source in source_tag:
            normalized_data['metadata']['source'] = config[source]['source']
            normalized_data['metadata']['business_purpose'] = config[source]['business_purpose']
            break
    else:
        normalized_data['metadata']['source'] = "UNKNOWN"
        normalized_data['metadata']['business_purpose'] = "unknown_purpose"

    for entity in normalized_data['entities']:
        entity['processing_purpose'] = normalized_data['metadata']['business_purpose']

    return normalized_data

# load file
file_content = file_upload('file_kyc_doc.txt')

detected_data = detector(file_content)

boundary_checked_data = boundary_checkor(file_content, detected_data)

validated_checked_data = valid_check(boundary_checked_data)

normalized_data = normalizer(validated_checked_data)

pprint(normalized_data)

purpose_info_data = purpose_info(normalized_data)

pprint(purpose_info_data)