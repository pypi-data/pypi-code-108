import sys
import time
from datetime import datetime as Datetime
from datetime import timezone
from pathlib import Path
from typing import Final
from zoneinfo import ZoneInfo

import typer
from colorama import Fore

from beni import clear_dirs, copy, getpath, getpath_user, hold
from beni.print import print_color
from beni.storage import get_storage, set_storage

_app = typer.Typer()


def main():
    _app()


def exit(errorMsg: str):
    print(errorMsg)
    sys.exit(errorMsg and 1 or 0)


# ------------------------------------------------------------------------


@_app.command('time')
def showtime(
    value: str = typer.Argument('', help='时间戳（支持整形和浮点型）或日期（格式: 2021-11-23）', show_default=False, metavar='[Timestamp or Date]'),
    value2: str = typer.Argument('', help='时间（格式: 09:20:20），只有第一个参数为日期才有意义', show_default=False, metavar='[Time]')
):
    '''
    格式化时间戳

    beni showtime

    beni showtime 1632412740

    beni showtime 1632412740.1234

    beni showtime 2021-9-23

    beni showtime 2021-9-23 09:47:00
    '''

    timestamp: float | None = None
    if not value:
        timestamp = time.time()
    else:
        try:
            timestamp = float(value)
        except:
            try:
                if value2:
                    timestamp = Datetime.strptime(f'{value} {value2}', '%Y-%m-%d %H:%M:%S').timestamp()
                else:
                    timestamp = Datetime.strptime(f'{value}', '%Y-%m-%d').timestamp()
            except:
                pass

    if timestamp is None:
        color = typer.colors.BRIGHT_RED
        typer.secho('参数无效', fg=color)
        typer.secho('\n可使用格式: ', fg=color)
        msgAry = str(showtime.__doc__).strip().replace('\n\n', '\n').split('\n')[1:]
        msgAry = [x.strip() for x in msgAry]
        typer.secho('\n'.join(msgAry), fg=color)
        raise typer.Abort()

    print()
    print(timestamp)
    print()
    localtime = time.localtime(timestamp)
    tzname = time.tzname[(time.daylight and localtime.tm_isdst) and 1 or 0]
    print_color(time.strftime('%Y-%m-%d %H:%M:%S %z', localtime), tzname, colorList=[Fore.LIGHTYELLOW_EX])
    print()

    # pytz版本，留作参考别删除
    # tzNameList = [
    #     'Asia/Tokyo',
    #     'Asia/Kolkata',
    #     'Europe/London',
    #     'America/New_York',
    #     'America/Chicago',
    #     'America/Los_Angeles',
    # ]
    # for tzName in tzNameList:
    #     tz = pytz.timezone(tzName)
    #     print(Datetime.fromtimestamp(timestamp, tz).strftime(fmt), tzName)

    datetime_utc = Datetime.fromtimestamp(timestamp, tz=timezone.utc)
    tzname_list = [
        'Australia/Sydney',
        'Asia/Tokyo',
        'Asia/Kolkata',
        'Africa/Cairo',
        'Europe/London',
        'America/Sao_Paulo',
        'America/New_York',
        'America/Chicago',
        'America/Los_Angeles',
    ]
    for tzname in tzname_list:
        datetime_tz = datetime_utc.astimezone(ZoneInfo(tzname))
        dstStr = ''
        dst = datetime_tz.dst()
        if dst:
            dstStr = f'(DST+{dst})'
        print(f'{datetime_tz} {tzname} {dstStr}')

    print()


# ------------------------------------------------------------------------

@_app.command()
def synclib():
    '''
    src -> lib
    '''
    _sync_path(
        _getpath_src(),
        _getpath_lib(),
    )


@_app.command()
def syncsrc():
    '''
    lib -> src
    '''
    _sync_path(
        _getpath_lib(),
        _getpath_src(),
    )


def _getpath_lib():
    return getpath_user(r'AppData\Local\Programs\Python\Python310\Lib\site-packages\beni')


def _getpath_src():
    KEY_SRC: Final = 'beni_src'
    path_src = get_storage(KEY_SRC, '')
    is_update_storage = False
    while True:
        print()
        print('-' * 50)
        print()
        print(f'lib: {_getpath_lib()}')
        print(f'src: {path_src}')
        print()
        print('确认输入[ok]')
        print('退出输入[exit]')
        print('修改src路径直接输入路径')
        print()
        value = hold('输入', False, '*')
        match(value):
            case 'ok':
                break
            case 'exit':
                exit('主动退出')
            case _:
                print('go here')
                if value != path_src:
                    is_update_storage = True
                path_src = value
    if is_update_storage:
        print('go save')
        set_storage(KEY_SRC, str(path_src))
    return getpath(path_src)


def _sync_path(path_from: Path, path_to: Path):

    print()
    print('-' * 50)
    print()
    print('确认当前操作')
    print(path_from)
    print('->')
    print(path_to)
    print()

    match(hold('确认输入[ok] 退出输入[exit]', False, 'exit', 'ok')):
        case 'ok':
            pass
        case 'exit':
            exit('主动退出')

    clear_dirs(path_to)
    for file_from in path_from.glob('**/*'):
        if file_from.is_file():
            file_to = path_to / file_from.relative_to(path_from)
            copy(file_from, file_to)


# ------------------------------------------------------------------------
