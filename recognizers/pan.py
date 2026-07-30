from presidio_analyzer import PatternRecognizer, Pattern

ind_pan_recognizer = PatternRecognizer(
    supported_entity= "IND_PAN",
    name = "PAN_recognizer",
    patterns = [
        Pattern(
            name="pan",
            regex = r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
            score = 0.9
            )
        ]
)