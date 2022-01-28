# argv[1] is the '.' delimited python path to a (schema) module.
# argv[2] is the filepath to dump to.
from sys import argv
import json
import importlib

module, schema = argv[1].rsplit('.', 1)
module = importlib.import_module(module)
schema = getattr(module, schema)

with open(argv[2], 'w') as f:
    json.dump(schema, f)
