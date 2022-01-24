# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import subprocess
import sys
import threading

from typing import Dict, List


class DaskProcessController:
    """Controller for native Dask processes."""

    def __init__(self):
        self._process = None

    def start_process(self, dask_process_name: str, process_args: List[str], process_kwargs: Dict[str, str]) -> None:
        cmd = self._build_popen_command_line(dask_process_name, process_args, process_kwargs)
        self._process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
            env={**os.environ,
                 'DASK_DISTRIBUTED__COMM__TIMEOUTS__CONNECT': '120s',
                 'DASK_DISTRIBUTED__COMM__TIMEOUTS__TCP': '120s'})

        threading.Thread(target=self._flush_process_stdout).start()

    def kill(self) -> None:
        """Kill the process."""
        if self._process is not None:
            self._process.kill()

    def wait(self) -> None:
        """Wait for the process to terminate."""
        if self._process is not None:
            self._process.wait()

    @classmethod
    def _build_popen_command_line(
            cls,
            dask_process_name: str,
            process_args: List[str],
            process_kwargs: Dict[str, str]) -> List[str]:
        """Build the command line for executing the process."""
        # Start the command line as the Python executable plus the full process path
        cmd = [sys.executable, cls._get_dask_process_path(dask_process_name)]

        # Add the positional arguments
        cmd += process_args

        # Add the named arguments
        for arg_name, arg_value in process_kwargs.items():
            cmd.append('--{}'.format(arg_name))
            cmd.append(arg_value)

        return cmd

    @classmethod
    def _get_dask_process_path(cls, dask_process_name: str) -> str:
        """Get the full path of the Dask process."""
        # Note: all Dask processes live in the same directory as the current Python executable
        return os.path.join(os.path.dirname(sys.executable), dask_process_name)

    def _flush_process_stdout(self) -> None:
        """Flush stdout of the subprocess to stdout of the current process."""
        if self._process is None:
            return
        while True:
            proc_out = self._process.stdout.readline()
            if proc_out == '' and self._process.poll() is not None:
                break
            sys.stdout.write(proc_out)
