from presidio_analyzer import PatternRecognizer, Pattern

ind_upi_recognizer = PatternRecognizer(
    supported_entity="IND_UPI_ID",
    name = "upi_recognizer" ,
    patterns=[
        Pattern(
            name = "upi_id",
            regex = r"^[a-zA-Z0-9-._]{2,256}@[a-zA-Z][a-zA-Z0-9.-]{2,65}$",
            score = 0.8
        )
    ]
)
