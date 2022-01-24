__version__ = "1.0.1"

from targer_api import api, model

# Re-export functions and types:
analyze_text = api.analyze_text
ArgumentLabel = model.ArgumentLabel
ArgumentTag = model.ArgumentTag
ArgumentSentence = model.ArgumentSentence
ArgumentSentences = model.ArgumentSentences
ArgumentModelSentences = model.ArgumentModelSentences
