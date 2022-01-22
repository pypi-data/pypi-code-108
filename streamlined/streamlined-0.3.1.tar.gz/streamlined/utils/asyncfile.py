import hashlib
from os import linesep
from subprocess import DEVNULL

from aiofile import async_open
from aiofiles import os as aio

from ..common import run

DEFAULT_BUFFER_SIZE = 100 * 1024 * 1024


async def _getsize(filepath: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> int:
    """
    Similar as `os.path.getsize`, get the filesize in bytes.
    """
    filesize = 0
    async with async_open(filepath, "rb") as reader:
        async for chunk in reader.iter_chunked(chunk_size):
            filesize += len(chunk)

    return filesize


async def getsize(filepath: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> int:
    try:
        return await aio.path.getsize(filepath)
    except Exception:
        return await _getsize(filepath, chunk_size)


async def _md5(filepath: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> str:
    """
    Compute md5 of a filepath.
    """
    file_hash = hashlib.md5()
    async with async_open(filepath, "rb") as reader:
        async for chunk in reader.iter_chunked(chunk_size):
            file_hash.update(chunk)

    return file_hash.hexdigest()


async def md5(filepath: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> str:
    try:
        result = await run(["md5sum", filepath])
        if result.returncode == 0:
            return result.stdout.split()[0].decode("utf-8")
    except Exception:
        pass
    return await _md5(filepath, chunk_size)


async def _copy(
    source: str, dest: str, chunk_size: int = DEFAULT_BUFFER_SIZE, write_mode: str = "wb"
) -> bool:
    source_bytes_count = 0
    written_bytes_count = 0
    async with async_open(source, "rb") as reader, async_open(dest, write_mode) as writer:
        async for chunk in reader.iter_chunked(chunk_size):
            source_bytes_count += len(chunk)
            written_bytes_count += await writer.write(chunk)
    return written_bytes_count == source_bytes_count


async def copy(source: str, dest: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> bool:
    try:
        result = await run(["cp", source, dest])
        if result.returncode == 0:
            return True
    except Exception:
        pass
    return await _copy(source, dest, chunk_size, write_mode="wb")


async def append(source: str, dest: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> bool:
    return await _copy(source, dest, chunk_size, write_mode="ab")


async def _linecount(filepath: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> int:
    count = 0
    async with async_open(filepath, "rb") as reader:
        async for chunk in reader.iter_chunked(chunk_size):
            count += chunk.count(bytes(linesep, "utf-8"))
    return count


async def linecount(filepath: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> int:
    try:
        result = await run(["wc", "-l", filepath])
        if result.returncode == 0:
            return int(result.stdout.split()[0])
    except Exception:
        pass
    return await _linecount(filepath, chunk_size)


async def _samecontent(source: str, target: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> bool:
    if await getsize(source, chunk_size) != await getsize(target, chunk_size):
        return False

    async with async_open(source, "rb") as source_reader:
        async with async_open(target, "rb") as target_reader:
            source_generator = source_reader.iter_chunked(chunk_size)
            target_generator = target_reader.iter_chunked(chunk_size)

            source_chunk = await source_generator.__anext__()
            target_chunk = await target_generator.__anext__()

            if source_chunk != target_chunk:
                return False

    return True


async def samecontent(source: str, target: str, chunk_size: int = DEFAULT_BUFFER_SIZE) -> bool:
    try:
        result = await run(["cmp", "--silent", source, target], stdout=DEVNULL, stderr=DEVNULL)
        return result.returncode == 0
    except Exception:
        pass
    return await _samecontent(source, target, chunk_size)
