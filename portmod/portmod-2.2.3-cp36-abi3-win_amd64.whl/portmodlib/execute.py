# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import logging
import shlex
import subprocess
import sys
from typing import List, Optional, Union


def execute(
    command: Union[str, List[str]],
    pipe_output: bool = False,
    pipe_error: bool = False,
    err_on_stderr: bool = False,
    check: bool = True,
) -> Optional[str]:
    """
    Executes the given command

    This function handles any platform-specific behaviour,
    in addition to output redirection and decoding.
    """
    cmd = command
    if isinstance(command, str) and sys.platform != "win32":
        cmd = shlex.split(command)

    output = None
    error = None
    if pipe_output or logging.root.level >= logging.WARN:
        output = subprocess.PIPE
    if err_on_stderr or pipe_error or logging.root.level >= logging.WARN:
        error = subprocess.PIPE
    proc = subprocess.run(cmd, check=check, stdout=output, stderr=error)

    if err_on_stderr and proc.stderr:
        raise subprocess.CalledProcessError(0, cmd, proc.stdout, proc.stderr)

    result = ""
    if pipe_output and proc.stdout:
        result += proc.stdout.decode("utf-8")
    if pipe_error and proc.stderr:
        result += proc.stderr.decode("utf-8")
    if pipe_output or pipe_error:
        return result
    return None
