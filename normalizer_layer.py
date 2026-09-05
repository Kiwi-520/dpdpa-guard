from ingestion_layer import file_upload
from detector_layer import detector, boundary_checkor, valid_check
from pprint import pprint

ENTITY_TYPE_MAPPING = {
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

def normalizer(validated_checked_data):
    for i in validated_checked_data['entities']:
        if i['raw_entity_type'] in ENTITY_TYPE_MAPPING:
            i['entity_type'] = ENTITY_TYPE_MAPPING[i['raw_entity_type']]
        else:
            i['entity_type'] = "UNKNOWN"

    return validated_checked_data
