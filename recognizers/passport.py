from presidio_analyzer import PatternRecognizer, Pattern

ind_passport_number_recognizer = PatternRecognizer(
    supported_entity="IND_PASSPORT",
    name = "IND_PASSPORT",
    patterns= [
        Pattern(
            name = "passport_number",
            regex = r"\b[A-Z]{1}[0-9]{7}\b",
            score = 0.8
        )
    ]
)
