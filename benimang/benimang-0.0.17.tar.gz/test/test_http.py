'''

settings.json 配置（vscode会自动配置）
'python.testing.pytestArgs': [
    'test',  // 指定单元测试查找的目录
    '-s'     // 支持print输出
],
'python.testing.unittestEnabled': false,
'python.testing.pytestEnabled': true,


快捷键（默认）
CTRL+; A        执行全部单元测试
CTRL+; E        只执行上次出错的用例
CTRL+; C        清除结果
CTRL+; CTRL+A   调试全部单元测试
CTRL+; CTRL+E   只调试上次出错的用例

'''

# 基础用法 -----------------------------------------------------------------------

import pytest
from beni.async_http import async_http_get
from beni.http import http_get


def test_http_get():
    result, _ = http_get('https://www.baidu.com')
    assert '<title>百度一下，你就知道</title>' in result.decode()


@pytest.mark.asyncio
async def test_async_http_get():
    result, _ = await async_http_get('https://www.baidu.com')
    assert '<title>百度一下，你就知道</title>' in result.decode()
