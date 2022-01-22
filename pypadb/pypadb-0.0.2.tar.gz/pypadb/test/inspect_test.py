from test.select_test import User
from utils import inspect_util


def sth(a: int) -> User:
    return User(id=123, account=a)


if __name__ == '__main__':
    print(inspect_util.arg_list(sth))
    print(inspect_util.returns_type(sth))
