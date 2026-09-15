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