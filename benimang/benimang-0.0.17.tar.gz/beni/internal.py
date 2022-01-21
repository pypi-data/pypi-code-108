
from typing import Any, Final

from beni import getpath, getpath_workspace

_httpHeaders = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}


def makeHttpHeaders(headers: dict[str, Any] | None = None):
    if headers:
        return _httpHeaders | headers
    else:
        return dict(_httpHeaders)

# ------------------------------------------------------------------


storagePath: Final = getpath_workspace('.storage')


def getStorageFile(key: str):
    return getpath(storagePath, f'{key}.yaml')


# ------------------------------------------------------------------
