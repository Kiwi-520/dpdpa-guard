import logging
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
import regex as re

from recognizers import ALL_RECOGNIZERS
from ingestion_layer import file_upload

from pprint import pprint

# add it to registry
registry = RecognizerRegistry()
registry.load_predefined_recognizers(
    languages=['en'],
    countries=['in']
    )

for i in ALL_RECOGNIZERS:
    registry.add_recognizer(i)

analyzer = AnalyzerEngine(registry=registry)

# print("Name Entity Code")
# for r in registry.recognizers:
#     print(
#         r.name,
#         r.supported_entities,
#         r.country_code()
#     )

    # ----------------------Substep A - Presidio Detection function starts---------------------------

def detector(input_data:dict):
    input_text = input_data['data']
    results = analyzer.analyze(text = input_text, language='en')
    obj = [result.to_dict() for result in results]
    entity_count = len(obj)
    detected_entities_details = {}
    detected_entities_details = {
        'metadata':{
                    'source_tag':input_data['source_tag'],
                    'source_type': input_data['source_type'],
                    'scanned_at':input_data['time'],
                    'total_entities_found':entity_count,
                    },
        'entities':[]
    }
    for i in range(0, entity_count):
        start = obj[i]['start']
        end = obj[i]['end']
        entity = input_text[start:end]
        obj[i]['entity'] = entity
        detected_entities_details['entities'].append({
            'entity':obj[i]['entity'],
            'raw_entity_type':obj[i]['entity_type'],
            'start':obj[i]['start'],
            'end':obj[i]['end'],
            'score':obj[i]['score']
        })
    return detected_entities_details
    # ----------------------Substep A - Presidio Detection function ends---------------------------


import spacy

def boundary_check(file_data, detected_data):
    # spacy loading
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(file_data['data'])
    tokens = []
    for token in doc:
        tokens.append(token)
    # token check
    for each_entity in detected_data['entities']:
        if each_entity['entity'] in tokens:
            each_entity['score'] = 0.9
        else:
            each_entity['score'] -= 0.2
    return detected_data

def valid_check(boundary_check_data):
    for each_entity in boundary_check_data['entities']:
        if each_entity['score'] <= 0.5:
            boundary_check_data['entities'].remove(each_entity)
    return boundary_check_data

file_content = file_upload('text.txt')
detected_data = detector(file_content)
boundary_checked = boundary_check(file_content, detected_data)
validated_data = valid_check(boundary_checked)

pprint(validated_data, sort_dicts = False)

# print(boundary_checked['entities'])


# text = "Dr. John Smith is a Professor at ABC Technologies. His Aadhaar number is 2345-6789-1234 and his PAN card number is ABCDE1234F. His passport number is A1234567 and voter ID is ABC1234567. His driving license number is MH-12-20210012345. The bank IFSC code is SBIN0001234. You can send money to his UPI ID john.smith@oksbi. His registered vehicle number is MH 12 AB 1234. Contact him at john.smith@gmail.com or call him at +91 9876543210. His office IP address is 192.168.1.100."

# results = detector(text)
# print(results)
# print(registry.get_country_codes())