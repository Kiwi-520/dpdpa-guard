from presidio_analyzer import PatternRecognizer, Pattern

ind_ifsc_recognizer = PatternRecognizer(
    supported_entity="IND_IFSC",
    name = "IFSC_recognizer",
    patterns=[
        Pattern(
            name = "ifsc",
            regex = r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
            score = 0.8
        )
    ]
)