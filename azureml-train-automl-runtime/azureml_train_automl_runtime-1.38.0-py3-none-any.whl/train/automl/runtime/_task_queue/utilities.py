# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""utilities for pipeline task queue"""
import base64
import zlib


def compress(text: str) -> str:
    """Compress a string and return base64 encoded string."""
    compressor = zlib.compressobj(wbits=zlib.MAX_WBITS | 16)
    compressed = compressor.compress(bytearray(text, "utf-8")) + compressor.flush()
    return base64.b64encode(compressed).decode("utf-8")


def decompress(b64_text: str) -> str:
    """Decompress a string generated from b64compress() and return the original one."""
    b64_decoded = base64.b64decode(b64_text)
    return zlib.decompress(b64_decoded, zlib.MAX_WBITS | 16).decode("utf-8")
