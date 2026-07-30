from presidio_analyzer import PatternRecognizer, Pattern

ind_vehicle_registration_number_recognizer = PatternRecognizer(
    supported_entity="IND_VEHICLE_REGISTRATION NUMBER",
    name = "vehicle_registration_number_recognizer",
    patterns=[
        Pattern(
            name = "vehicle_regiatration_number",
            regex = r"^[A-Z]{2}\s?[0-9]{2}\s?[A-Z]{1,3}\s?[0-9]{4}$",
            score=0.8
        )
    ]
)