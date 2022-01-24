import base64
import inspect
import json
from json import JSONDecodeError
from typing import List, Tuple, Dict

import zlib


# @lru_cache(15)  # Caching actually makes this slower, so don't.
def inflate(compressed_byte_string):
    if isinstance(compressed_byte_string, dict) or \
            isinstance(compressed_byte_string, Dict) or \
            isinstance(compressed_byte_string, int) or \
            isinstance(compressed_byte_string, float) or \
            isinstance(compressed_byte_string, complex) or \
            isinstance(compressed_byte_string, list) or \
            isinstance(compressed_byte_string, List) or \
            isinstance(compressed_byte_string, tuple) or \
            isinstance(compressed_byte_string, Tuple) or \
            isinstance(compressed_byte_string, range) or \
            isinstance(compressed_byte_string, bytes) or \
            isinstance(compressed_byte_string, bytearray) or \
            isinstance(compressed_byte_string, memoryview) or \
            isinstance(compressed_byte_string, set) or \
            isinstance(compressed_byte_string, frozenset) or \
            isinstance(compressed_byte_string, bool):

        # The assumed-json byte string is actually an object already.
        dict_object = compressed_byte_string

        # So just return it as is.
        return dict_object

    compressed_byte_string = base64.b64decode(compressed_byte_string)

    json_string = zlib.decompress(compressed_byte_string)

    try:
        dict_object = json.loads(json_string)
    except (JSONDecodeError, TypeError) as malformed_json_error:
        print(
            'Error: '
            'A function encountered an error where the '
            'data being deserialized is not a valid JSON document. '
            'The function:', inspect.stack()[0][3],
            'The document:', json_string
        )
        raise malformed_json_error

    return dict_object


def inflate_data(data: dict) -> dict:
    """
    Decompress the values of a data dictionary, if they were compressed.

    :param data: The data dictionary whose values shall be decompressed.

    :return: The data dictionary with its values decompressed.
    """
    data: dict = {
        sink: {
            source: inflate(value)
            for source, value in data[sink].items()
        } for sink in data
    }

    return data
