from pathlib import Path
from typing import Final

import aiofiles

from beni import crc_bytes, make_dirs, md5_bytes
from beni.async_func import set_async_limit, wrapper_async_limit

LIMIT_TAG_FILE: Final = 'file'

set_async_limit(LIMIT_TAG_FILE, 50)


@wrapper_async_limit(LIMIT_TAG_FILE)
async def async_writefile_text(file: Path, content: str, encoding: str = 'utf8', newline: str = '\n'):
    make_dirs(file.parent)
    async with aiofiles.open(file, 'w', encoding=encoding, newline=newline) as f:
        return await f.write(content)


@wrapper_async_limit(LIMIT_TAG_FILE)
async def async_writefile_bytes(file: Path, data: bytes):
    make_dirs(file.parent)
    async with aiofiles.open(file, 'wb') as f:
        return await f.write(data)


@wrapper_async_limit(LIMIT_TAG_FILE)
async def async_readfile(file: Path, encoding: str = 'utf8', newline: str = '\n'):
    async with aiofiles.open(file, 'r', encoding=encoding, newline=newline) as f:
        return await f.read()


@wrapper_async_limit(LIMIT_TAG_FILE)
async def async_readfile_bytes(file: Path):
    async with aiofiles.open(file, 'rb') as f:
        return await f.read()


async def async_md5file(file: Path):
    return md5_bytes(
        await async_readfile_bytes(file)
    )


async def async_crcfile(file: Path):
    return crc_bytes(
        await async_readfile_bytes(file)
    )
