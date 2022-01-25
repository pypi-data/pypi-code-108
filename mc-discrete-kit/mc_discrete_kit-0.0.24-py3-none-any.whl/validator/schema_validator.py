import json
import logging
from jsonschema import *

_log = logging.getLogger('discrete_kit.validator.schema_validator')


#
# def validate_json_types(received_json=None):
#     _log.info("Starting validate Shape JSON")
#     if received_json:
#         if type(json.loads(received_json)) is dict:
#             dir_name = os.path.dirname(__file__)
#             full_path = os.path.join(dir_name, discrete_kit.configuration.config.SCHEMA_FOLDER,
#                                      discrete_kit.configuration.config.JSON_NAME)
#             try:
#                 with open(full_path, 'r') as fp:
#                     schema = json.load(fp)
#                     try:
#                         validate(instance=json.loads(received_json), schema=schema)
#                         _log.info("End validate Shape JSON")
#                     except ValidationError as e:
#                         _log.error(e.schema['error_msg'])
#                         raise Exception(e.schema['error_msg'])
#
#             except IOError:
#                 _log.error("Cannot open schema")
#                 raise Exception("Cannot open schema")
#         else:
#             _log.error("not a dictionary")
#             raise Exception("not a dictionary")
#     else:
#         _log.error("received None")
#         raise Exception("received None")


def validate_json_types(schema_to_validate, received_json=None):
    try:
        validate(instance=json.loads(received_json), schema=schema_to_validate)
    except ValidationError as e:

        raise Exception(".".join(e.relative_schema_path) + ' , (The Value is: ' + e.message + ')')
