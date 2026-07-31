import logging
logging.getLogger("presidio analyzer").setLevel(logging.ERROR)


from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerRegistry, Pattern
import regex as re

from recognizers import ALL_RECOGNIZERS

# add it to registry
registry = RecognizerRegistry()
registry.load_predefined_recognizers()

for i in ALL_RECOGNIZERS:
    registry.add_recognizer(i)

analyzer = AnalyzerEngine(registry=registry)

def detector(input_text):
    results = analyzer.analyze(text = input_text, language='en')
    return results

text = "Dr. John Smith is a Professor at ABC Technologies. His Aadhaar number is 2345-6789-1234 and his PAN card number is ABCDE1234F. His passport number is A1234567 and voter ID is ABC1234567. His driving license number is MH-12-20210012345. The bank IFSC code is SBIN0001234. You can send money to his UPI ID john.smith@oksbi. His registered vehicle number is MH 12 AB 1234. Contact him at john.smith@gmail.com or call him at +91 9876543210. His office IP address is 192.168.1.100."

# results = analyzer.analyze(text=text, language="en")
results = detector(text)
# print(results)
print(type(results))
