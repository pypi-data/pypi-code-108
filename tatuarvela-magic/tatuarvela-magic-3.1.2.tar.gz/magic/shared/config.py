from os import path

SPELLBOOK_SCHEMA_PATH = path.join(path.dirname(__file__), "spellbook.schema.json")
SPELLBOOK_PATH = path.join(path.expanduser("~"), ".spellbook.json")
SPELLBOOK_INDENTATION = 2
SPELLBOOK_EDITOR = "code"
