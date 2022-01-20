import os
import sys
import time
import traceback
from datetime import datetime as Datetime
from typing import Final

import typer
from colorama import Back, Fore

from beniutils import getAllFileList, getPath, makeFolder, remove, writeFile
from beniutils.log import (error, getCountCritical, getCountError,
                           getCountWarning, info, initLogger)
from beniutils.print import resetPrintColor, setPrintColor

ISDEV: Final = getPath(sys.executable) != getPath(sys.argv[0]) or not sys.executable.endswith(".exe")
if ISDEV:
    _workspace = getPath(sys.argv[0], "./../../workspace")
else:
    _workspace = getPath(sys.executable, "./../../workspace")


_startTime: Datetime
_lockfile: str


def _onStart(ctx: typer.Context):
    print(f"callback ctx.invoked_subcommand={ctx.invoked_subcommand}")
    global _startTime, _lockfile

    _lockfile = get_workspace("task.lock")
    if os.path.isfile(_lockfile):
        typer.echo(f"不支持重复执行 {_lockfile}")
        value: str = ""
        while value != "unlock":
            value = typer.prompt("如果确认上次执行是意外退出，输入unlock可继续")
    writeFile(_lockfile, "\n".join([
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        ctx.invoked_subcommand or "",
        # todo: 加入参数
    ]))
    _startTime = Datetime.now()

    # 始初始化日志（前面有可能时参数对不上进不来）
    logdirectory = get_workspace("log")
    makeFolder(logdirectory)
    # 删除100条以前的日志
    for logfile in sorted(getAllFileList(logdirectory), reverse=True)[100:]:
        remove(logfile)
    logfile = getPath(logdirectory, f"{time.strftime('%Y%m%d_%H%M%S')}_{ctx.invoked_subcommand}.log")
    initLogger(logFile=logfile)


def _onEnd():
    if getCountCritical():
        color = Fore.LIGHTWHITE_EX + Back.LIGHTMAGENTA_EX
    elif getCountError():
        color = Fore.LIGHTWHITE_EX + Back.LIGHTRED_EX
    elif getCountWarning():
        color = Fore.BLACK + Back.LIGHTYELLOW_EX
    else:
        color = Fore.BLACK + Back.LIGHTGREEN_EX

    setPrintColor(color)
    info("---------------------------------------------------------------------------")

    msgAry = ["任务结束"]
    if getCountCritical():
        msgAry.append(f"critical({getCountCritical()})")
    if getCountError():
        msgAry.append(f"error({getCountError()})")
    if getCountWarning():
        msgAry.append(f"warning({getCountWarning()})")

    setPrintColor(color)
    info(" ".join(msgAry))

    passTime = str(Datetime.now() - _startTime)
    if passTime.startswith("0:"):
        passTime = "0" + passTime
    info(f"用时：{passTime}")

    resetPrintColor()
    if _lockfile:
        remove(_lockfile)

    if not ISDEV:
        while True:
            time.sleep(1)


def run(exe_workspace: str | None, dev_workspace: str | None, dev_parlist: list[str]):
    global _workspace

    if ISDEV and dev_workspace:
        _workspace = dev_workspace
    elif not ISDEV and exe_workspace:
        _workspace = exe_workspace

    try:
        if ISDEV:
            from typer.testing import CliRunner
            CliRunner().invoke(app, dev_parlist)
        else:
            app()
    except Exception:
        setPrintColor(Fore.LIGHTRED_EX)
        traceback.print_exc()
        error("执行失败")
        resetPrintColor()
    finally:
        _onEnd()


def get_workspace(*parList: str):
    return getPath(_workspace, *parList)


app: Final = typer.Typer(callback=_onStart)
