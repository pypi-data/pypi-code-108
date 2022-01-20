import os
import sys
import time
from datetime import datetime as Datetime
from datetime import timezone
from zoneinfo import ZoneInfo

import typer
from colorama import Fore

from . import (copy, getPath, makeFolder, makeTempWorkspace, readFile, remove,
               writeFile)
from .byte import decode
from .execute import execute
from .print import printColor
from .zip import zipFileExtract

app = typer.Typer()


def main():
    app()


# @app.command(
#     help="help",
#     short_help="short_help",
# )
# def test(
#     par1: str,
#     par2: str = "par2",
#     par3: Optional[str] = typer.Argument("par3", help="这是参数描述", show_default=False),
#     par4: Optional[str] = typer.Argument("par4", help="这是参数描述"),
# ):
#     print(par1, par2, par3, par4)

def exit(errorMsg: str):
    print(errorMsg)
    sys.exit(errorMsg and 1 or 0)

# ------------------------------------------------------------------------


@app.command(
    help="创建 beniutils.task 项目",
)
def taskCreate(
    folder: str = typer.Argument("", help="指定项目路径，默认在当前系统路径", show_default=False),
):
    folder = folder or os.getcwd()
    makeFolder(folder)
    workspaceFolder = makeTempWorkspace()
    try:
        taskCreateZipFile = getPath(os.path.dirname(__file__), "data/task_create.zip")
        zipFileExtract(taskCreateZipFile, workspaceFolder)
        for fileName in os.listdir(workspaceFolder):
            toFile = getPath(folder, fileName)
            if os.path.exists(toFile):
                raise Exception(f"创建失败，指定路径下已存在 {toFile}")
        for fileName in os.listdir(workspaceFolder):
            fromFile = getPath(workspaceFolder, fileName)
            toFile = getPath(folder, fileName)
            copy(fromFile, toFile)
        print("创建项目成功 " + folder)
    finally:
        remove(workspaceFolder)


@app.command(
    help="发布 beniutils.task 项目",
)
def taskBuild(
    folder: str = typer.Argument("", help="指定项目路径，默认在当前系统路径", show_default=False),
):
    currentPath: str = ""
    workspaceFolder: str = ""
    try:
        currentPath = os.getcwd()
        folder = folder or currentPath
        workspaceFolder = makeTempWorkspace()
        ignoreList = ["main.py"]
        mainPyFile = getPath(folder, "project/src/main.py")
        if not os.path.isfile(mainPyFile):
            exit(f"发布失败，主文件不存在 {mainPyFile}")
        hiddenimports = [x[:-3] for x in os.listdir(os.path.dirname(mainPyFile)) if x.endswith(".py") and x not in ignoreList]
        name = "task"
        icon = getPath(workspaceFolder, "task.ico")
        pathex = getPath(folder, "project")
        taskBuildZipFile = getPath(os.path.dirname(__file__), "data/task_build.zip")
        zipFileExtract(taskBuildZipFile, workspaceFolder)
        taskSpecFile = getPath(workspaceFolder, "task.spec")
        taskSpecContent = readFile(taskSpecFile)
        taskSpecContent = taskSpecContent.replace("<<projectSrcPath>>", getPath(folder, "project/src"))
        taskSpecContent = taskSpecContent.replace("<<mainPyFile>>", mainPyFile)
        taskSpecContent = taskSpecContent.replace("<<pathex>>", pathex)
        taskSpecContent = taskSpecContent.replace("<<hiddenimports>>", ",".join([f'"{x}"' for x in hiddenimports]))
        taskSpecContent = taskSpecContent.replace("<<name>>", name)
        taskSpecContent = taskSpecContent.replace("<<icon>>", icon)
        print("------------------------------\n")
        print(taskSpecContent)
        print("------------------------------\n")
        writeFile(taskSpecFile, taskSpecContent)

        # import PyInstaller.__main__
        # sys.argv = ["", taskSpecFile]
        # PyInstaller.__main__.run() # pyinstaller main.py -F

        os.chdir(workspaceFolder)
        _, outBytes, errBytes = execute(f"pyinstaller {taskSpecFile}", ignoreError=True)

        outStr = decode(outBytes).replace("\r\n", "\n")
        errStr = decode(errBytes).replace("\r\n", "\n")
        executeLog = "\n".join([outStr, errStr])
        print(executeLog)

        fromExeFile = getPath(workspaceFolder, f"dist/{name}.exe")
        toExeFile = getPath(folder, "project/bin/" + os.path.basename(fromExeFile))
        if not os.path.exists(fromExeFile):
            exit("生成exe文件失败")
        remove(toExeFile)
        copy(fromExeFile, toExeFile)
    finally:
        if currentPath:
            os.chdir(currentPath)
        if workspaceFolder:
            remove(workspaceFolder)


@app.command("time")
def showtime(
    value: str = typer.Argument("", help="时间戳（支持整形和浮点型）或日期（格式：2021-11-23）", show_default=False, metavar="[Timestamp or Date]"),
    value2: str = typer.Argument("", help="时间（格式：09:20:20），只有第一个参数为日期才有意义", show_default=False, metavar="[Time]")
):
    """
    格式化时间戳

    beni showtime

    beni showtime 1632412740

    beni showtime 1632412740.1234

    beni showtime 2021-9-23

    beni showtime 2021-9-23 09:47:00
    """

    timestamp: float | None = None
    if not value:
        timestamp = time.time()
    else:
        try:
            timestamp = float(value)
        except:
            try:
                if value2:
                    timestamp = Datetime.strptime(f"{value} {value2}", "%Y-%m-%d %H:%M:%S").timestamp()
                else:
                    timestamp = Datetime.strptime(f"{value}", "%Y-%m-%d").timestamp()
            except:
                pass

    if timestamp is None:
        color = typer.colors.BRIGHT_RED
        typer.secho("参数无效", fg=color)
        typer.secho("\n可使用格式：", fg=color)
        msgAry = str(showtime.__doc__).strip().replace("\n\n", "\n").split("\n")[1:]
        msgAry = [x.strip() for x in msgAry]
        typer.secho("\n".join(msgAry), fg=color)
        raise typer.Abort()

    print()
    print(timestamp)
    print()
    localtime = time.localtime(timestamp)
    tzname = time.tzname[(time.daylight and localtime.tm_isdst) and 1 or 0]
    printColor(time.strftime("%Y-%m-%d %H:%M:%S %z", localtime), tzname, colorList=[Fore.LIGHTYELLOW_EX])
    print()

    # pytz版本，留作参考别删除
    # tzNameList = [
    #     "Asia/Tokyo",
    #     "Asia/Kolkata",
    #     "Europe/London",
    #     "America/New_York",
    #     "America/Chicago",
    #     "America/Los_Angeles",
    # ]
    # for tzName in tzNameList:
    #     tz = pytz.timezone(tzName)
    #     print(Datetime.fromtimestamp(timestamp, tz).strftime(fmt), tzName)

    datetime_utc = Datetime.fromtimestamp(timestamp, tz=timezone.utc)
    tzname_list = [
        "Australia/Sydney",
        "Asia/Tokyo",
        "Asia/Kolkata",
        "Africa/Cairo",
        "Europe/London",
        "America/Sao_Paulo",
        "America/New_York",
        "America/Chicago",
        "America/Los_Angeles",
    ]
    for tzname in tzname_list:
        datetime_tz = datetime_utc.astimezone(ZoneInfo(tzname))
        dstStr = ""
        dst = datetime_tz.dst()
        if dst:
            dstStr = f"(DST+{dst})"
        print(f"{datetime_tz} {tzname} {dstStr}")

    print()
