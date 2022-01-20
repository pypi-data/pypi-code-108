import asyncio

import pytest
from beniutils.aio import asyncTimeout

'''

settings.json 配置（vscode会自动配置）
"python.testing.pytestArgs": [
    "test",  // 指定单元测试查找的目录
    "-s"     // 支持print输出
],
"python.testing.unittestEnabled": false,
"python.testing.pytestEnabled": true,


快捷键（默认）
CTRL+; A        执行全部单元测试
CTRL+; E        只执行上次出错的用例
CTRL+; C        清除结果
CTRL+; CTRL+A   调试全部单元测试
CTRL+; CTRL+E   只调试上次出错的用例

'''

# 基础用法 -----------------------------------------------------------------------


@pytest.fixture(scope="function")
def prefun_1():
    # 这里相当于执行 setup
    yield "prefun_1_return"  # 可以带返回值
    # 这里相当于执行 teardown


@pytest.fixture  # scope默认值就是function，所以这里不写scope都可以
def prefun_2():
    yield "prefun_2_return"


@pytest.fixture(scope="module", autouse=True)   # 每个模块文件只会执行一次，autouse相当于每个测试函数都有调用
def premodule_1():
    yield "premodule_1_return"


def test_1(prefun_1: str, prefun_2: str):  # 参数顺序决定了函数执行顺序，变量为函数的返回值
    pass


# 测试类用法 -----------------------------------------------------------------------


@pytest.fixture(scope="class")  # 每个类最多只会执行一次
def preclass_1():
    yield "preclass_1_return"


class Test_ClassA():  # 测试类开头必须Test开头，否则里面的方法不检查

    def test_classa_fun1(self, prefun_1: str, preclass_1: str):  # 如果scope=class，只会在这个类成员方法第一次调用执行，后面执行的成员发发都不会触发执行，返回值就是第一次调用的返回值
        pass


# 异步用法 -----------------------------------------------------------------------
'''
注意：除了 pytest 以外，还要安装 pytest-asyncio
'''


@pytest.fixture
async def prefun_async_1():
    await asyncio.sleep(0.1)
    yield "prefun_async_1_return"


@pytest.mark.asyncio  # 异步测试用例记得要加上这个
@asyncTimeout(1)         # 自己写的一个wrapper
async def test_async_2(prefun_async_1: str):  # 记得要加上async
    await asyncio.sleep(0.1)
