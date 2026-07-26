from presidio_analyzer import AnalyzerEngine

import logging

logging.getLogger("presidio analyzer").setLevel(logging.ERROR)

analyzer = AnalyzerEngine()

results = analyzer.analyze(text="My phone number is 212-334-5555",
                           entities = ['PHONE_NUMBER'],
                           language='en')

print(results)

