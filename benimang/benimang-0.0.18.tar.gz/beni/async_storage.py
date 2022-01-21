from typing import Any

import yaml

from beni.async_file import async_readfile, async_writefile_text
from beni.internal import getStorageFile


async def async_get_storage(key: str, default: Any = None):
    storageFile = getStorageFile(key)
    if storageFile.is_file():
        content = await async_readfile(storageFile)
        return yaml.safe_load(content)
    else:
        return default


async def async_set_storage(key: str, value: Any):
    storageFile = getStorageFile(key)
    content = yaml.safe_dump(value)
    return await async_writefile_text(storageFile, content)
