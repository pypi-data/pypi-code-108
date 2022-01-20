from base64 import b64decode
import json


def get_user(context):
    metadata = dict(context.invocation_metadata())
    user64 = metadata['x-delphai-user']
    user = b64decode(user64)
    return json.loads(user)
