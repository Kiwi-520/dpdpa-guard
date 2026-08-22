import logging
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
import regex as re

from recognizers import ALL_RECOGNIZERS
from ingestion_layer import file_upload

from pprint import pprint
import spacy

# add it to registry
registry = RecognizerRegistry()
registry.load_predefined_recognizers(
    languages=['en'],
    countries=['in']
    )

# desiabling uncessary recognizers
registry.remove_recognizer("DateRecognizer")
registry.remove_recognizer("IbanRecognizer")
registry.remove_recognizer("UrlRecognizer")
registry.remove_recognizer("MacAddressRecognizer")
registry.remove_recognizer("CryptoRecognizer")


for i in ALL_RECOGNIZERS:
    registry.add_recognizer(i)

analyzer = AnalyzerEngine(registry=registry)

# ------ checking recognizers -----
# print("Name Entity Code")
# for r in registry.recognizers:
#     print(
#         r.name,
#         r.supported_entities,
#         r.country_code()
#     )

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


    # ----------------------Substep B - Validation functions start---------------------------
    # ----------------------Boundary checking to avoid false positives---------------------------
def boundary_check(file_data, detected_data):
    # spacy loading
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(file_data['data'])
    tokens = []
    # token check
    for each_entity in detected_data['entities']:
        if each_entity['entity'] in tokens:
            each_entity['score'] = 0.9
        else:
            each_entity['score'] -= 0.2
    return detected_data
    # ----------------------Entity validation is checked ---------------------------
def valid_check(boundary_check_data):
    for each_entity in boundary_check_data['entities']:
        if each_entity['score'] <= 0.5:
            boundary_check_data['entities'].remove(each_entity)
    return boundary_check_data

# load file
file_content = file_upload('text.txt')
# presidio scanning
detected_data = detector(file_content)

pprint(detected_data)