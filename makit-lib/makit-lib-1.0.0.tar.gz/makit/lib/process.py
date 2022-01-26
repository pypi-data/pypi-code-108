# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Created: 2021/11/10
@Desc: 
"""
import subprocess

from makit.lib._time import Timeout


def is_running(pid=None, name=None):
    if name:
        output = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {name}"')
        return name in str(output)
    elif pid:
        output = subprocess.check_output(f'tasklist /FI "PID eq {pid}"')
        return str(pid) in str(output)


def kill_by_pid(pid, ensure_stop=False):
    """
    杀死指定PID的进程
    :param pid: 进程ID
    :param ensure_stop: 是否确保进程停止，默认False
    :return:
    """
    subprocess.check_output(f'taskkill /f /pid {pid}')
    if ensure_stop:
        Timeout(interval=0.2).until(lambda: not is_running(pid=pid))


def kill_by_name(name, ensure_stop=False):
    """
    杀死指定名称的进程
    :param name: 进程名
    :param ensure_stop: 是否确保进程停止，默认False
    :return:
    """
    try:
        subprocess.check_output(f'taskkill /im {name} /f 2>nul >nul')
        if ensure_stop:
            Timeout(interval=0.2).until(lambda: not is_running(name=name))
    except:
        pass


def wait(name, timeout=None):
    return Timeout(timeout).until(is_running, name=name)


def wait_stop(pid=None, name=None, timeout=None):
    return Timeout(timeout).until(lambda: not is_running(pid=pid, name=name))
