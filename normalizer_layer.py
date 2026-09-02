from ingestion_layer import file_upload
from detector_layer import detector, boundary_checkor, valid_check
from pprint import pprint


def normalizer(validated_checked_data):
    entity_dicts = {
        "IN_AADHAAR" :"AADHAAR",
        "IND_ADHAAR" :"AADHAAR",
        "IN_PAN" :"PAN",
        "IND_PAN" :"PAN",
        "IN_PASSPORT" :"PASSPORT",
        "IND_PASSPORT" :"PASSPORT",
        "IN_VOTER" :"VOTER_ID",
        "IND_VOTER_ID" :"VOTER_ID",
        "IN_VEHICLE_REGISTRATION" :"VEHICLE_REG",
        "IND_VEHICLE_REGISTRATION_NUMBER" :"VEHICLE_REG",
        "IN_GSTIN" :"GSTIN",
        "IND_GSTIN" :"GSTIN",
        "IND_UPI_ID" :"UPI",
        "IND_IFSC" :"IFSC",
        "IND_DRIVING_LICENSE" :"DRIVING_LICENSE",
        "IN_DRIVING_LICENSE" :"DRIVING_LICENSE",
        "EMAIL_ADDRESS" :"EMAIL",
        "PHONE_NUMBER" :"PHONE",
        "IP_ADDRESS" :"IP_ADDRESS",
        "PERSON" :"PERSON",
        "CREDIT_CARD" :"CREDIT_CARD",
        "NRP" :"UNKNOWN",
        "LOCATION" :"LOCATION",
        "ORGANIZATION" :"UNKNOWN"
    }
    for i in validated_checked_data['entities']:
        if i['raw_entity_type'] in entity_dicts:
            i['entity_type'] = entity_dicts[i['raw_entity_type']]
        else:
            i['entity_type'] = "UNKNOWN"

    return validated_checked_data


# load file
file_content = file_upload('sample_doc.txt')

detected_data = detector(file_content)

boundary_checked_data = boundary_checkor(file_content, detected_data)

validated_checked_data = valid_check(boundary_checked_data)

normalized_data = normalizer(validated_checked_data)

pprint(normalized_data)