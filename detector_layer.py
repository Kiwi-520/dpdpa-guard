import logging
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
import regex as re

from recognizers import ALL_RECOGNIZERS
# from ingestion_layer import file_upload

from pprint import pprint
import spacy

from presidio_analyzer.predefined_recognizers.country_specific.india import(
    InAadhaarRecognizer,
    InPanRecognizer,
    InPassportRecognizer,
    InGstinRecognizer,
    InVoterRecognizer,
    InVehicleRegistrationRecognizer
)

from presidio_analyzer.predefined_recognizers import(
    PhoneRecognizer ,
    SpacyRecognizer,
    CreditCardRecognizer,
    IpRecognizer,
    EmailRecognizer
)
# add it to registry
registry = RecognizerRegistry()
registry.add_recognizer(InAadhaarRecognizer())
registry.add_recognizer(InPassportRecognizer())
registry.add_recognizer(InPanRecognizer())
registry.add_recognizer(InVehicleRegistrationRecognizer())
registry.add_recognizer(InVoterRecognizer())
registry.add_recognizer(InGstinRecognizer())
registry.add_recognizer(EmailRecognizer())
registry.add_recognizer(PhoneRecognizer())
registry.add_recognizer(IpRecognizer())
registry.add_recognizer(CreditCardRecognizer())
registry.add_recognizer(SpacyRecognizer())


# desiabling uncessary recognizers
registry.remove_recognizer("DateRecognizer")
registry.remove_recognizer("IbanRecognizer")
registry.remove_recognizer("UrlRecognizer")
registry.remove_recognizer("MacAddressRecognizer")
registry.remove_recognizer("CryptoRecognizer")


for i in ALL_RECOGNIZERS:
    registry.add_recognizer(i)

analyzer = AnalyzerEngine(registry=registry)

# # ------ checking recognizers -----
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
            'score':obj[i]['score'],
            'boundary_status':"none",
        })
    return detected_entities_details
    # ----------------------Substep A - Presidio Detection function ends---------------------------


    # ----------------------Substep B - Validation functions start---------------------------
    # ----------------------Boundary checking to avoid false positives---------------------------
def boundary_checkor(file_content, detected_data):
        # minimum confidence scores
    min_score_dict = {
        'IN_AADHAAR':0.5,
        'IND_ADHAAR':0.5,
        'IN_PAN': 0.5,
        'IND_PAN':0.5,
        'IN_PASSPORT':0.4,
        'IN_VOTER':0.4,
        'IND_UPI_ID':0.5,
        'IND_IFSC':0.5,
        'PHONE_NUMBER':0.3,
        'EMAIL_ADDRESS':0.5,
        'PERSON':0.5,
        'IP_ADDRESS':0.5,
    }

    detected_data['entities'] = [ent for ent in detected_data['entities'] if  ent['score'] >= min_score_dict.get(ent['raw_entity_type'], 0)]

    # PAN vaerification
    for ent in detected_data['entities']:
        if  (ent['raw_entity_type'] == 'IND_PAN' or ent['raw_entity_type'] == 'IN_PAN'):
            if ent['entity'][3] in ['P', 'C', 'H', 'F', 'A', 'T', 'B', 'L', 'J', 'G']:
                ent['boundary_status'] == "suspicious"
            else:
                ent['boundary_status'] == "clean"

    # removing unecessary entity
    detected_data['entities'] = [ent for ent in detected_data['entities'] if ent['raw_entity_type'] not in ["DATE_TIME", "ORGANIZATION"]]
    # spacy loading
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(file_content['data'])

    position_dict = {}
    for token in doc:
        position_dict[token.idx] = (token.idx + len(token.text))
    # pprint(position_dict)
    for word in detected_data['entities']:
        if word['start'] in position_dict and position_dict[word['start']] == word['end']:
            word['boundary_status'] = "complete"
        else:
            word['boundary_status'] = 'fragment'
    # multi token check
    for word in detected_data['entities']:
        if word['boundary_status'] == "fragment":
            if word['start'] in position_dict and (word['end'] in position_dict.values() or word['end']+1 in position_dict.values()):
                word['boundary_status'] = "multi-token"
    return detected_data

    # ----------------------Entity validation is checked ---------------------------
def valid_check(boundary_checked_data):

    boundary_checked_data['entities'] = [i for i in boundary_checked_data['entities'] if i['boundary_status'] == "complete" or i['boundary_status'] == "multi-token" ]
    # overlapping check
    priority_dict = {
        "EMAIL_ADDRESS" : 9,
        "IP_ADDRESS" : 8,
        "IND_ADHAAR" : 7,
        "IN_ADHAAR" : 7,
        "IND_PAN" : 7,
        "IN_PAN" : 7,
        "IND_PASSPORT" : 7,
        "IN_PASSPORT" : 7,
        "IND_VOTER" : 7,
        "IN_VOTER" : 7,
        "IND_IFSC" : 7,
        "IN_IFSC" : 7,
        "IND_UPI_ID" : 7,
        "IN_UPI_ID" : 7,
        "IND_DRIVING_LICENSE" : 7,
        "IN_DRIVING_LICENSE" : 7,
        "IND_VEHICLE_REGISTRATION" : 7,
        "IN_VEHICLE_REGISTRATION" : 7,
        "PERSON" : 6,
        "CREDIT_CARD" : 6,
        "PHONE_NUMBER" : 4,
    }
    to_remove = set()
    for i, wordA in enumerate(boundary_checked_data['entities']):
        for j, wordB in enumerate(boundary_checked_data['entities']):
            if i < j:
                if (wordA['start'] == wordB['start'] and wordA['end'] == wordB['end']) or (wordB['start'] >= wordA['start'] and wordB['start'] < wordA['end']) or (wordA['start'] >= wordB['start'] and wordA['start'] < wordB['end']):
                    ent1 = wordA['raw_entity_type']
                    ent2 = wordB['raw_entity_type']
                    p1 = priority_dict.get(ent1, 0)
                    p2 = priority_dict.get(ent2, 0)
                    if p1 < p2:
                        to_remove.add(i)
                    else:
                        to_remove.add(j)
    boundary_checked_data['entities'] = [ent for idx,ent in enumerate(boundary_checked_data['entities']) if idx not in to_remove]
    boundary_checked_data['entities'] = [ent for ent in boundary_checked_data['entities'] if "\n" not in ent['entity']]
    return boundary_checked_data

