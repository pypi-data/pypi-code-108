import os
import glob
import errno
import shlex
import shutil
import pathlib
import subprocess


def run(cmd, stdin="", directory=".", shell=False):
    opt = {}
    opt["stdin"] = subprocess.PIPE
    opt["stdout"] = subprocess.PIPE
    opt["stderr"] = subprocess.PIPE
    opt["shell"] = shell
    current = pathlib.Path.cwd()
    working = pathlib.Path(directory)
    os.chdir(working)
    if shell:
        p = subprocess.Popen(cmd, **opt)
    else:
        p = subprocess.Popen(shlex.split(cmd, posix=False), **opt)
    stdout, stderr = p.communicate(input=stdin.encode())
    os.chdir(current)
    return [stdout.decode(), stderr.decode()]


def call_latex(tex, directory="."):
    run(f"pdflatex -interaction=batchmode {tex}", directory=directory)
    current = pathlib.Path.cwd()
    working = pathlib.Path(directory)
    os.chdir(working)
    for e in [".aux", ".log"]:
        os.remove(os.path.splitext(tex)[0] + e)
    os.chdir(current)


def mkdir(directory, mode=0o755):
    p = pathlib.Path(directory)
    p.mkdir(mode=mode, parents=True, exist_ok=True)
    os.chmod(directory, mode)


def cp(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy2(src, dst)


def rm(obj):
    for iobj in glob.glob(str(obj)):
        if os.path.isfile(iobj):
            os.remove(iobj)
        if os.path.isdir(iobj):
            shutil.rmtree(iobj)


def keep(obj):
    for iobj in glob.glob("*"):
        if iobj not in obj:
            rm(iobj)


def exist(obj):
    return os.path.isfile(obj)
