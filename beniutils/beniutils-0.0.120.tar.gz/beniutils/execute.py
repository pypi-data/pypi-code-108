import subprocess

from beniutils import getUserPath, remove
from beniutils.byte import decode
from beniutils.log import info


def execute(*pars: str, showCmd: bool = True, showOutput: bool = False, ignoreError: bool = False):
    cmd = ' '.join(pars)
    if showCmd:
        info(cmd)
    p = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    outBytes, errBytes = p.communicate()
    p.kill()
    if showOutput:
        outStr = decode(outBytes).replace("\r\n", "\n")
        errStr = decode(errBytes).replace("\r\n", "\n")
        if outStr:
            info(f"output:\n{outStr}")
        if errStr:
            info(f"error:\n{errStr}")
    if not ignoreError and p.returncode != 0:
        raise Exception("执行命令出错")
    return p.returncode, outBytes, errBytes


def executeWinScp(winscpExe: str, keyFile: str, server: str, commandAry: list[str], showCmd: bool = True):
    logFile = getUserPath("executeWinScp.log")
    remove(logFile)
    ary = [
        'option batch abort',
        'option transfer binary',
        f'open sftp://{server} -privatekey={keyFile} -hostkey=*',
    ]
    ary += commandAry
    ary += [
        'close',
        'exit',
    ]
    # /console
    cmd = f'{winscpExe} /log={logFile} /loglevel=0 /command ' + ' '.join('"%s"' % x for x in ary)
    return execute(cmd, showCmd=showCmd)


def executeTry(*parList: str, output: str = "", error: str = ""):
    _, outputBytes, errorBytes = execute(*parList, showCmd=False, ignoreError=True)
    if output and output not in decode(outputBytes):
        raise Exception(f"命令执行失败：{' '.join(parList)}")
    if error and error not in decode(errorBytes):
        raise Exception(f"命令执行失败：{' '.join(parList)}")
