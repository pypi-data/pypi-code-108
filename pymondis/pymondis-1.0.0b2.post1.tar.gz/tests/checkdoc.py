from asyncio import gather, run

from aiofiles import open as aopen
from httpx import AsyncClient


async def get_scheme():
    content: bytes = b''
    async with AsyncClient() as client:
        async with client.stream("GET", "https://quatromondisapi.azurewebsites.net/swagger/docs/v1") as response:
            async for chunk in response.aiter_raw(1024):
                content += chunk
    return content


async def get_cache():
    content: bytes = b''
    try:
        async with aopen("checkdoc-cache.gz", "rb") as file:
            while chunk := await file.read(1024):
                content += chunk
    except FileNotFoundError:
        return
    return content


async def main():
    scheme, cache = await gather(get_scheme(), get_cache())
    if scheme == cache:
        print("Brak zmian w schemacie")
        return
    if cache is None:
        print("Initializowanie pliku...")
    elif scheme != cache:
        print("WYKRYTO ZMIANY W SCHEMACIE!")
    async with aopen("checkdoc-cache.gz", "wb") as file:
        await file.write(scheme)
        await file.flush()


if __name__ == "__main__":
    run(main())
