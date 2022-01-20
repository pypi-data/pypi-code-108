import base64
from ast import literal_eval


def decodeResponse(encoded) -> dict:
    return base64.b64decode(encoded).decode('utf-8')
