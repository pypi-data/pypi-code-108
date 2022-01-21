from __future__ import print_function  # Only Python 2.x
import subprocess


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def test():
    """
    Run all unittests.
    """
    cmd = ["poetry", "run", "python", "-u", "-m", "unittest", "discover", "tests", "-v"]
    for stdout_line in execute(cmd):
        print(stdout_line, end="")
