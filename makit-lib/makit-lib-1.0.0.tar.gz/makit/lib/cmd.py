#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：kevinleong1011@hotmail.com
@desc: 
"""
import os
import subprocess
import sys
from typing import Union


def run_command(command: Union[str, list, tuple], *args, **kwargs):
    """执行ADB命令"""
    timeout = kwargs.pop('timeout', None)
    if isinstance(command, (list, tuple)):
        command = ' '.join(command)
    command = command.format(command, *args, **kwargs)
    try:
        if 'linux' in sys.platform:
            output = bytes(os.popen(command).read(), encoding='utf8')
        elif 'stdout' not in kwargs.keys():
            output = subprocess.check_output(command, timeout=timeout)
        else:
            output = subprocess.run(command, *args, timeout=timeout, **kwargs)
    except subprocess.CalledProcessError as e:
        if not e.output and not e.stderr and not e.stdout:
            return ''
        raise Exception(e.stdout)
    else:
        result = output
    return result.decode().strip()
