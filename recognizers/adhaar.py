from presidio_analyzer import PatternRecognizer, Pattern

ind_adhaar_recognizer = PatternRecognizer(
    supported_entity="IND_ADHAAR",
    name = "Adhaar_recognizer",
    patterns = [
        Pattern(
            name="adhaar_recognizer",
            regex = r"\b[2-9]{1}\d{3}[- ]?\d{4}[- ]?\d{4}\b",
            score = 0.8
            )
        ]
)