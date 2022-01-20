import pytest


@pytest.fixture(scope="session", autouse=True)  # 每次会话只会执行一次，autouse相当于每个测试函数都有调用
def presession_1():
    yield "presession_1_return"
