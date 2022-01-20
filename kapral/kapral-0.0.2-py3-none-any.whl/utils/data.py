import bz2
import gzip
import json
import lzma
import os


def detect_archive_format_and_open(path):
    if path.endswith(".xz"):
        return lzma.open(path, mode="rt", encoding="utf-8", errors="replace")
    if path.endswith(".bz2"):
        return bz2.open(path, mode="rt", encoding="utf-8", errors="replace")
    if path.endswith(".gz"):
        return gzip.open(path, mode="rt", encoding="utf-8", errors="replace")
    return open(path, encoding="utf8", errors="replace")


def get_uncompressed_size(path):
    with detect_archive_format_and_open(path) as f:
        size = f.seek(0, 2)
    return size
