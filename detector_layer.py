import logging
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
import regex as re

from recognizers import ALL_RECOGNIZERS
from ingestion_layer import file_upload

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

nlp = spacy.load("en_core_web_sm")

text = "Dr. John Smith is a Professor at ABC Technologies. His Aadhaar number is 2345-6789-1234 and his PAN card number is ABCDE1234F. His passport number is A1234567 and voter ID is ABC1234567. His driving license number is MH-12-20210012345. The bank IFSC code is SBIN0001234. You can send money to his UPI ID john.smith@oksbi. His registered vehicle number is MH 12 AB 1234. Contact him at john.smith@gmail.com or call him at +91 9876543210. His office IP address is 192.168.1.100."

doc = nlp(text)
tokens = []
for token in doc:
    # print(token.text)
    tokens.append(token)

def validation(detected_data):
    # token check
    for each_entity in detected_data['entities']:
        if each_entity['entity'] in tokens:
            each_entity['score'] = 0.9
        else:
            each_entity['score'] -= 0.2
    return detected_data

data = file_upload('text.txt')
detected_data = detector(data)
validated_data = validation(detected_data)

print(validated_data)


# text = "Dr. John Smith is a Professor at ABC Technologies. His Aadhaar number is 2345-6789-1234 and his PAN card number is ABCDE1234F. His passport number is A1234567 and voter ID is ABC1234567. His driving license number is MH-12-20210012345. The bank IFSC code is SBIN0001234. You can send money to his UPI ID john.smith@oksbi. His registered vehicle number is MH 12 AB 1234. Contact him at john.smith@gmail.com or call him at +91 9876543210. His office IP address is 192.168.1.100."

# results = detector(text)
# print(results)
# print(registry.get_country_codes())