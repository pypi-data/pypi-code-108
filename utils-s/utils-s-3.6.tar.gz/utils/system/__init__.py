import os
import sys
import random
import signal
import subprocess
from . import paths


def HomeDirectory():
    return os.path.expanduser('~')


def command(args: list, quite=False, read=False):
    if quite:
        sub = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    elif read:
        sub = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

        response = sub.communicate()[0].decode('utf8')
        sub.wait()
        sub.poll()
        returnCode = int(sub.returncode)

        return response, returnCode, sub
    else:
        sub = subprocess.Popen(args)

    sub.wait()
    sub.kill()
    sub.terminate()


def ip_address(interface='en0'):
    ip = command(['ipconfig', 'getifaddr', interface], read=True)
    try:
        ip = ip[0].removesuffix('\n')
    except AttributeError or Exception:
        if ip[0].endswith('\n'):
            ip = ip[0][:-1]

    return ip


def hostname():
    import socket
    return socket.gethostname()


def remove(file):
    command(['rm', '-rf', file])


def kill_process(pid):
    if not isinstance(pid, int):
        pid = int(pid)
    os.kill(pid, signal.SIGTERM)


class CaptureSTDOUT:
    def __init__(self):
        self.rnSTD = sys.stdout
        self.newStd = '.' + random.random().__str__() + '.std'
        self.newStdFile = open(self.newStd, 'w+')

        self.data = None

    def startCapture(self):
        sys.stdout = self.newStdFile

    def stopCapture(self):
        sys.stdout = self.rnSTD
        self.newStdFile.close()

        file = open(self.newStd, 'rb+')
        content = file.read().decode()
        file.close()
        remove(self.newStd)
        self.data = content

    def readCapture(self):
        return self.data

    def __enter__(self):
        self.startCapture()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stopCapture()


if __name__ == '__main__':
    pass
