import traceback
from datetime import datetime as Datetime
from functools import wraps
from pathlib import Path
from typing import Any, Final, cast
from uuid import uuid4

import typer
from colorama import Back, Fore

from beni import WrappedFunc, getpath
from beni.logging import (error, getcount_critical, getcount_error,
                      getcount_warning, info, init_logger, warning)
from beni.print import reset_print_color, set_print_color

_startTime: Datetime | None = None
_logFile: Path | None = None

app: Final = typer.Typer()


def _main(func: WrappedFunc) -> WrappedFunc:
    @wraps(func)
    def wraper(*args: Any, **kwargs: Any):
        global _startTime
        _startTime = Datetime.now()
        try:
            init_logger(logFile=_logFile)
            return func(*args, **kwargs)
        except BaseException:
            set_print_color(Fore.LIGHTRED_EX)
            traceback.print_exc()
            error('执行失败')
            reset_print_color()
        finally:

            if getcount_critical():
                color = Fore.LIGHTWHITE_EX + Back.LIGHTMAGENTA_EX
            elif getcount_error():
                color = Fore.LIGHTWHITE_EX + Back.LIGHTRED_EX
            elif getcount_warning():
                color = Fore.BLACK + Back.LIGHTYELLOW_EX
            else:
                color = Fore.BLACK + Back.LIGHTGREEN_EX

            set_print_color(color)
            info('-' * 75)

            msgAry = ['任务结束']
            if getcount_critical():
                msgAry.append(f'critical({getcount_critical()})')
            if getcount_error():
                msgAry.append(f'error({getcount_error()})')
            if getcount_warning():
                msgAry.append(f'warning({getcount_warning()})')

            set_print_color(color)
            info(' '.join(msgAry))

            passTime = str(Datetime.now() - _startTime)
            if passTime.startswith('0:'):
                passTime = '0' + passTime
            info(f'用时: {passTime}')

    return cast(WrappedFunc, wraper)


def set_log_path(log_path: Path):
    if _startTime:
        warning('task.setLogDir 必须在任务启动前调用，本次忽略执行')
    else:
        global _logFile
        _logFile = getpath(log_path, f'{uuid4()}.log')


@_main
def run():
    app()


@_main
def debug(*args: str):
    from typer.testing import CliRunner
    CliRunner().invoke(app, args)
