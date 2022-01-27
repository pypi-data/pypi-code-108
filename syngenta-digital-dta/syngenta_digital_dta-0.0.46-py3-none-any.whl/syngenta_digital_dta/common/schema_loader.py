import simplejson as json
import jsonref
import yaml


def load_schema(schema_file, schema_key):
    with open(schema_file, encoding='UTF-8') as openapi:
        api_doc = yaml.load(openapi, Loader=yaml.FullLoader)
    return jsonref.loads(json.dumps(api_doc))['components']['schemas'][schema_key]
