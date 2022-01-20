import base64
import json
import timeit
from functools import lru_cache
import zlib


def deflate_logged(dict_object):
    start = timeit.default_timer()

    compressed_byte_string = deflate(dict_object)

    end = timeit.default_timer()

    input_length = len(json.dumps(dict_object).encode('utf-8'))
    output_length = len(compressed_byte_string)
    print(
        f'Deflated {input_length} to {output_length} bytes '
        f'or to {round(output_length / input_length * 100, 0)} % '
        f'in {round(end - start, 6)} seconds'
    )

    return compressed_byte_string


def deflate(dict_object) -> bytes:
    json_string = json.dumps(dict_object).encode(encoding='utf-8')

    compressed_byte_string: bytes = \
        compress_string_to_bytes(string=json_string)

    return compressed_byte_string


@lru_cache(15)  # Caching is quicker than compressing, so use it.
def compress_string_to_bytes(string):
    compressed_json_string = \
        zlib.compress(string, level=1)
    encoded_compressed_byte_string = \
        base64.b64encode(s=compressed_json_string)
    compressed_byte_string: bytes = \
        encoded_compressed_byte_string.decode(encoding='ascii')

    return compressed_byte_string


def deflate_data_logged(data: dict) -> dict:
    """
    Compress the values of a data dictionary.

    This method logs what its actions to stdout.

    :param data: The data dictionary whose values shall be compressed.

    :return: The data dictionary with its values compressed.
    """
    data: dict = {
        key: deflate_logged(dict_object=value)
        for key, value in data.items()
    }

    return data


def deflate_data(data: dict) -> dict:
    """
    Compress the values of a data dictionary.

    :param data: The data dictionary whose values shall be compressed.

    :return: The data dictionary with its values compressed.
    """
    data: dict = {
        key: deflate(dict_object=value)
        for key, value in data.items()
    }

    return data
