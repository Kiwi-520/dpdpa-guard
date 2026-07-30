from presidio_analyzer import PatternRecognizer, Pattern

ind_voter_id_recognizer = PatternRecognizer(
    supported_entity="IND_VOTER_ID",
    name = "voter_id_recognizer",
    patterns = [
        Pattern(
            name="voter_id",
            regex = r"\b[A-Z]{3}[0-9]{7}\b",
            score = 0.8
        )
    ]
)
