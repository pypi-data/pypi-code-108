import os
from codefast.logger import Logger
import uuid
from pydub.utils import mediainfo
from typing import List, Union, Tuple
import inspect
from shutil import copy2
import subprocess
from termcolor import colored
import pprint
import subprocess


class FormatPrint:
    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    @staticmethod
    def magenta(text: str, attrs: List[str] = None) -> str:
        return colored(text, 'magenta', attrs=attrs)

    @classmethod
    def red(cls, text: str, attrs: List[str] = None) -> str:
        return colored(text, 'red', attrs=attrs)

    @classmethod
    def green(cls, text: str, attrs: List[str] = None) -> str:
        return colored(text, 'green', attrs=attrs)

    @classmethod
    def cyan(cls, text: str, attrs: List[str] = None) -> str:
        return colored(text, 'cyan', attrs=attrs)


# Pretty print dict/list type of data structure.
def pretty_print(js: Tuple[list, dict],
                 indent: int = 0,
                 prev: str = '') -> None:
    _margin = ' ' * indent
    nxt_margin = _margin + ' ' * 3
    if isinstance(js, dict):
        print('{' if prev == ':' else _margin + '{')
        for k, v in js.items():
            print(nxt_margin + FormatPrint.cyan(k), end=': ')
            if isinstance(v, dict) or isinstance(v, list):
                pretty_print(v, indent + 3, prev=':')
            else:
                print(v)
        print(_margin + '}')
    elif isinstance(js, list):
        print('[')
        for v in js:
            pretty_print(v, indent + 3)
        print(_margin + ']')
    elif isinstance(js, str):
        print(_margin + js)
    else:
        raise Exception("Unexpected type of input.")


class FileIO:
    def __call__(self, filename: str = '', delimiter: str = '\n') -> list:
        if filename:
            return FileIO.read(filename, delimiter)

    @classmethod
    def tmpfile(cls, prefix: str, suffix: str) -> str:
        '''return file name'''
        suffix = suffix.lstrip('.')
        opf = '/tmp/{}_{}.{}'.format(prefix, str(uuid.uuid4()), suffix)
        Logger().info(f'creating file {opf}')
        return opf

    @classmethod
    def readable_size(cls, size: int) -> str:
        '''Convert file size into human readable string'''
        units = ['KB', 'MB', 'GB', 'TB', 'PB'][::-1]
        res, copy_size = [], size
        size //= 1024
        while size > 0:
            res.append("{}{}".format(size % 1024, units.pop()))
            size //= 1024
        return str(copy_size) + ' ({})'.format(' '.join(reversed(res)))

    @classmethod
    def readable_duration(cls, duration: float) -> str:
        '''Convert duration into human readable string'''
        units = ['s', 'm', 'h', 'd', 'w'][::-1]
        res, duration = [], duration
        while duration > 0:
            res.append("{}{}".format(int(duration % 60), units.pop()))
            duration //= 60
        return ' '.join(reversed(res))

    @classmethod
    def info(cls, file_path: str) -> dict:
        mi = mediainfo(file_path.strip())
        if 'size' in mi:
            mi['size'] = FormatPrint.sizeof_fmt(int(mi['size']))

        if 'duration' in mi:
            mi['duration'] = float(mi['duration'])
        return mi

    @staticmethod
    def read(file_name: str, delimiter: str = '\n') -> Union[str, list]:
        texts = open(file_name, 'r').read().__str__()
        if delimiter:
            return texts.strip().split(delimiter)
        return texts

    @staticmethod
    def reads(file_name: str) -> str:
        '''Different with read method, this method will return string only'''
        return open(file_name, 'r').read().__str__()

    @staticmethod
    def rd(file_name: str, delimiter: str = '\n'):
        return FileIO.read(file_name, delimiter)

    @staticmethod
    def iter(filename: str) -> None:
        with open(filename, 'r') as f:
            for line in f.readlines():
                yield line.strip()

    @staticmethod
    def dumps(file_path: str, content: str) -> None:
        with open(file_path, 'w') as f:
            f.write(content)

    @staticmethod
    def write(cons: Union[str, List, set],
              file_name: str,
              mode='w',
              overwrite: bool = True) -> None:
        if not overwrite and FileIO.exists(file_name):
            print(f'{file_name} exists')
            return

        with open(file_name, mode) as f:
            if isinstance(cons, str):
                cons = [cons]
            text = '\n'.join(map(str, list(cons)))
            f.write(text)

    @staticmethod
    def wt(cons, file_name, mode='w', overwrite: bool = True):
        FileIO.write(cons, file_name, mode, overwrite)

    @staticmethod
    def say(*contents):
        for e in contents:
            if isinstance(e, dict) or isinstance(e, list):
                pretty_print(e)
            else:
                pprint.pprint(e)

    @classmethod
    def walk(cls, path, depth: int = 1, suffix=None):
        if depth <= 0:
            return []

        for f in os.listdir(path):
            abs_path = os.path.join(path, f)
            if os.path.isfile(abs_path):
                if not suffix or (suffix and abs_path.endswith(suffix)):
                    yield abs_path

            else:
                for sf in cls.walk(abs_path, depth - 1, suffix):
                    yield sf

    @staticmethod
    def exists(file_name: str) -> bool:
        return os.path.exists(file_name)

    @staticmethod
    def dirname() -> str:
        previous_frame = inspect.currentframe().f_back
        # (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
        filename, *_ = inspect.getframeinfo(previous_frame)
        return os.path.dirname(os.path.realpath(filename))

    @staticmethod
    def pwd() -> str:
        return subprocess.check_output(['pwd']).decode('utf-8').strip()

    @staticmethod
    def basename(file_path: str) -> str:
        return os.path.basename(file_path)

    @staticmethod
    def stem(file_path: str) -> str:
        ''' Get file name stem only. E.g., /tmp/gone-with-wind.json -> gone-with-wind '''
        return os.path.splitext(os.path.basename(file_path))[0]

    @staticmethod
    def path(file_path: str) -> str:
        return os.path.dirname(file_path)

    @staticmethod
    def rm(file_path: str) -> None:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    @staticmethod
    def rename(old_name: str, new_name: str) -> None:
        os.rename(old_name, new_name)

    @staticmethod
    def copy(old_name: str, new_name: str) -> None:
        copy2(old_name, new_name)

    @staticmethod
    def home() -> str:
        from pathlib import Path
        return str(Path.home())
