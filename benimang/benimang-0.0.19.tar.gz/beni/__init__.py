import os
import shutil
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Coroutine, TypeVar, cast


def getpath(path: str | Path, expand: str = ''):
    if type(path) is not Path:
        path = Path(path)
    return path.joinpath(expand).resolve()


def getpath_user(expand: str = ''):
    return getpath(Path('~').expanduser(), expand)


def getpath_workspace(expand: str = ''):
    return getpath_user(f'beni.workspace/{expand}')


def getpath_desktop(expand: str = ''):
    return getpath_user(f'Desktop/{expand}')


def open_windir(dir: Path):
    os.system(f'start explorer {dir}')


def remove(path: Path):
    if path.is_file():
        path.unlink(True)
    elif path.is_dir():
        shutil.rmtree(path)


def make_dirs(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def clear_dirs(dir: Path):
    for sub in dir.iterdir():
        remove(sub)


def copy(src: Path, dst: Path):
    make_dirs(dst.parent)
    if src.is_file():
        shutil.copyfile(src, dst)
    elif src.is_dir():
        shutil.copytree(src, dst)


def move(src: Path, dst: Path, force: bool = False):
    if dst.exists():
        if force:
            remove(dst)
        else:
            raise Exception(f'move error: dst exists {dst}')
    make_dirs(dst.parent)
    os.rename(src, dst)


def writefile_text(file: Path, content: str):
    make_dirs(file.parent)
    return file.write_text(content, encoding='utf8', newline='\n')


def writefile_bytes(file: Path, data: bytes):
    make_dirs(file.parent)
    return file.write_bytes(data)


def jsondumps(value: Any):
    import json
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def list_path(path: Path, recursive: bool = False):
    '''获取指定路径下文件以及目录列表'''
    if recursive:
        return list(path.glob('**/*'))
    else:
        return list(path.glob("*"))


def list_file(path: Path, recursive: bool = False):
    '''获取指定路径下文件列表'''
    if recursive:
        return list(filter(lambda x: x.is_file(), path.glob('**/*')))
    else:
        return list(filter(lambda x: x.is_file(), path.glob('*')))


def list_dir(path: Path, recursive: bool = False):
    '''获取指定路径下目录列表'''
    if recursive:
        return list(filter(lambda x: x.is_dir(), path.glob('**/*')))
    else:
        return list(filter(lambda x: x.is_dir(), path.glob('*')))


def md5_file(file: Path):
    return md5_bytes(file.read_bytes())


def md5_str(content: str):
    return md5_bytes(content.encode())


def md5_bytes(data: bytes):
    import hashlib
    return hashlib.md5(data).hexdigest()


def crc_file(file: Path):
    return crc_bytes(file.read_bytes())


def crc_str(content: str):
    return crc_bytes(content.encode())


def crc_bytes(data: bytes):
    import binascii
    return hex(binascii.crc32(data))[2:].zfill(8)


WrappedFunc = TypeVar("WrappedFunc", bound=Callable[..., object])
WrappedAsyncFunc = TypeVar("WrappedAsyncFunc", bound=Callable[..., Coroutine[Any, Any, object]])
AnyType = TypeVar("AnyType")


def wrapper_retry(times: int):
    def fun(func: WrappedFunc) -> WrappedFunc:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            current = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except:
                    current += 1
                    if current >= times:
                        raise
        return cast(WrappedFunc, wrapper)
    return fun


_DEFAULT_FMT = '%Y-%m-%d %H:%M:%S'


def timestamp_bystr(value: str, fmt: str = _DEFAULT_FMT):
    return time.mktime(time.strptime(value, fmt))


def timestamp_tostr(timestamp: float | None, fmt: str = _DEFAULT_FMT):
    timestamp = timestamp or time.time()
    ary = time.localtime(timestamp)
    return time.strftime(fmt, ary)


def hold(msg: str | None = None, password: bool = False, *exitvalue_list: str):
    msg = msg or '测试暂停，输入exit可以退出'
    exitvalue_list = exitvalue_list or ('exit',)
    import getpass
    inputFunc = password and getpass.getpass or input
    while True:
        inputValue = inputFunc(f'{msg}: ')
        if (inputValue in exitvalue_list) or ('*' in exitvalue_list):
            return inputValue


IntFloatStr = TypeVar("IntFloatStr", int, float, str)


def tofloat(value: IntFloatStr, default: float = 0):
    result = default
    try:
        result = float(value)
    except:
        pass
    return result


def toint(value: IntFloatStr, default: int = 0):
    result = default
    try:
        result = int(value)
    except:
        pass
    return result


def getvalue_inside(value: IntFloatStr, minValue: IntFloatStr, maxValue: IntFloatStr):
    '包括最小值和最大值'
    value = min(value, maxValue)
    value = max(value, minValue)
    return value


_xPar = '0123456789abcdefghijklmnopqrstuvwxyz'


def xint_tostr(value: int) -> str:
    n = len(_xPar)
    return ((value == 0) and '0') or (xint_tostr(value // n).lstrip('0') + _xPar[value % n])


def xint_fromstr(value: str):
    return int(value, len(_xPar))
