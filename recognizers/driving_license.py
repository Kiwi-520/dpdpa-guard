from presidio_analyzer import PatternRecognizer, Pattern

ind_driving_licence_recognizer = PatternRecognizer(
    supported_entity="IND_DRIVING_LICENSE",
    name = "driving_license",
    patterns=[
        Pattern(
            name = "driving_license",
            regex = r"\b[A-Z]{2}[- ]?[0-9]{2}[- ]?[0-9]{4}[- ]?[0-9]{7}\b",
            score = 0.8
        )
    ]
)