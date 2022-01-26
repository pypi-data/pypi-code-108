#!/usr/bin/env python3

"""
CLI script to unzip truncated or corrupt zip files
"""

import mmap
import struct
import os
import sys
import zlib
import logging
import click
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)


@dataclass
class ZipLocalFileHeader:
    version: int
    bitflag: int
    compression_method: int
    modification_time: int
    modification_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    filename_length: int
    extra_field_length: int


HEADER_SIZE = 2 + 2 + 2 + 2 + 2 + 4 + 4 + 4 + 2 + 2


def decompress(archive_filename, dry_run):
    """
    Decompress `filename` into current directory.
    """
    with open(archive_filename, "rb") as f, mmap.mmap(
        f.fileno(), 0, access=mmap.ACCESS_READ
    ) as mm:

        pos = 0

        print(f"Archive: {archive_filename}")

        if dry_run:
            print(f"{'Length':10s} Name")
            print(f"{'-'*10} {'-'*4}")

        while (pos := mm.find(b"PK\x03\x04", pos)) != -1:
            logging.debug(f"found header @ 0x{pos:x}")

            pos += 4

            chunk = mm[pos : pos + HEADER_SIZE]
            pos += HEADER_SIZE

            header = ZipLocalFileHeader(*struct.unpack("<hhhHHLllhh", chunk))

            # zip file encodings are a mess with multiple non-conformant implementations
            filename = mm[pos : pos + header.filename_length]
            try:
                filename = filename.decode("utf8")
            except:
                filename = filename.decode("latin1")

            pos += header.filename_length

            if header.extra_field_length > 0:
                pos += header.extra_field_length

            if dry_run:
                print(f"{header.uncompressed_size:10d} {filename:s}")
                continue

            dirname = os.path.dirname(filename)
            if len(dirname) > 0:
                os.makedirs(dirname, exist_ok=True)

            if header.compressed_size == 0:
                next_header = mm.find(b"PK\x03\x04", pos)
                if next_header == -1:
                    header.compressed_size = len(mm) - pos
                    logging.warn(
                        f"{filename} lacks a following header, and might be truncated"
                    )
                else:
                    header.compressed_size = next_header - pos

            contents = mm[pos : pos + header.compressed_size]
            pos += header.compressed_size

            if header.compression_method == 8:
                decompress_obj = zlib.decompressobj(wbits=-zlib.MAX_WBITS)
                contents = decompress_obj.decompress(contents)
            elif header.compression_method != 0:
                logging.error(f"unknown compression method for {filename}")

            if len(contents) < header.uncompressed_size:
                logging.warn(f"{filename} is truncated {len(contents)}")

            if os.path.dirname(filename) == filename:
                continue

            print(f"creating: {filename:s}")
            with open(filename, "wb") as new_file:
                new_file.write(contents)


@click.command()
@click.option("-l", "--dry_run", is_flag=True, default=False)
@click.argument("filenames", nargs=-1, required=True)
def main(filenames, dry_run):
    for filename in filenames:
        try:
            decompress(filename, dry_run)
        except Exception as ex:
            logging.exception(f"Error with file: '{filename}'")
