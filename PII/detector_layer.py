import logging
logging.getLogger("presidio analyzer").setLevel(logging.ERROR)


from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerRegistry, Pattern
import regex as re

# custom recognitzer
acadeimc_title_recognizer = PatternRecognizer(
    supported_entity="ACADEMIC TITLE",
    deny_list=["Dr.", "Dr", "Professor", "Prof."]
)

# adhaar card

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

ind_driving_licence_recognizer = PatternRecognizer(
    supported_entity="IND_DRIVING_LICENSE",
    name = "driving_license",
    patterns=[
        Pattern(
            name = "driving_license",
            regex = r"\b[A-Z]{2}[- ]?[0-9]{2}[  ]?[0-9]{4}[- ]?[0-9]{7}\b",
            score = 0.8
        )
    ]
)

ind_ifsc_recognizer = PatternRecognizer(
    supported_entity="IND_IFSC",
    name = "IFSC_recognizer",
    patterns=[
        Pattern(
            name = "ifsc",
            regex = r"\b[A-Z]{4}0[A-Z0-9]{7}\b",
            score = 0.8
        )
    ]
)

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
ALL_RECOGNIZERS = [
    ind_adhaar_recognizer,
    ind_pan_recognizer,
    ind_passport_number_recognizer,
    ind_voter_id_recognizer,
    ind_driving_licence_recognizer,
    ind_ifsc_recognizer,
    ind_upi_recognizer,
    ind_vehicle_registration_number_recognizer
]


# add it to registry
registry = RecognizerRegistry()
registry.load_predefined_recognizers()
registry.add_recognizer(acadeimc_title_recognizer)
for i in ALL_RECOGNIZERS:
    registry.add_recognizer(i)

analyzer = AnalyzerEngine(registry=registry)

text = "Dr. John Smith is a Professor at ABC Technologies. His Aadhaar number is 2345-6789-1234 and his PAN card number is ABCDE1234F. His passport number is A1234567 and voter ID is ABC1234567. His driving license number is MH-12-20210012345. The bank IFSC code is SBIN0001234. You can send money to his UPI ID john.smith@oksbi. His registered vehicle number is MH 12 AB 1234. Contact him at john.smith@gmail.com or call him at +91 9876543210. His office IP address is 192.168.1.100."

results = analyzer.analyze(text=text, language="en")
print(results)

