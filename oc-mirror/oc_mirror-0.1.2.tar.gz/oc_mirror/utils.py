#!/usr/bin/env python

"""Utility classes."""

import tarfile

from io import BytesIO
from docker_sign_verify.utils import chunk_file


async def read_from_tar(tar_file, tarinfo: tarfile.TarInfo) -> bytes:
    """Reads an entry from a tar file into memory."""
    bytesio = BytesIO()
    await chunk_file(
        tar_file.extractfile(tarinfo),
        bytesio,
        file_in_is_async=False,
        file_out_is_async=False,
    )
    return bytesio.getvalue()
