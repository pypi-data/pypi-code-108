from importlib.util import find_spec
from io import StringIO
from pathlib import Path
from typing import Any

from nv.utils.decorators import requires


if find_spec('charset_normalizer'):
    import charset_normalizer
else:
    charset_normalizer = None


__ALL__ = ["detect_file_encoding", "decode_file", "detect_bytes_encoding", "decode_bytes",
           "EncodingDetectionException", ]


class EncodingDetectionException(Exception):
    pass


def _decode_with(decoder, obj, **decoding_kwargs) -> charset_normalizer.CharsetMatches:
    results = decoder(obj, **decoding_kwargs)
    if not results:
        raise EncodingDetectionException(f"{decoder} unable to detect encoding from {obj!r}")
    return results


@requires('charset_normalizer')
def detect_file_encoding(fp: Path | str, **decoding_kwargs: Any) -> str:
    """
    Detects the file type and returns a file-like object with the contents of the file.
    :param fp: path to the file or file-like object.
    :return: file-like object with the contents of the file.
    """
    results = _decode_with(charset_normalizer.from_path, Path(fp), **decoding_kwargs)
    return results.best().encoding


@requires('charset_normalizer')
def decode_file(fp: Path | str, **decoding_kwargs: Any) -> StringIO:
    """
    Detects the file type and returns a file-like object with the contents of the file.
    :param fp: path to the file or file-like object.
    :return: file-like object with the contents of the file.
    """
    results = _decode_with(charset_normalizer.from_path, Path(fp), **decoding_kwargs)
    return StringIO(str(results.best()))


@requires('charset_normalizer')
def decode_bytes(b: bytes | bytearray, **decoding_kwargs: Any) -> str:
    results = charset_normalizer.from_bytes(b, **decoding_kwargs)
    return str(results.best())


@requires('charset_normalizer')
def detect_bytes_encoding(b: bytes | bytearray, **decoding_kwargs: Any) -> str:
    results = charset_normalizer.from_bytes(b, **decoding_kwargs)
    return results.best().encoding
