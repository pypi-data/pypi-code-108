import os
import subprocess
import pathlib
import time
import uuid
from datetime import datetime

import logging

import kabaret.subprocess_manager as ksm

logger = logging.getLogger(__name__)


class Runner(ksm.runner_factory.Runner):
    
    def __init__(self, version=None, label=None, extra_argv=[], extra_env={}):
        super(Runner, self).__init__(
            version=version,
            label=label,
            extra_argv=extra_argv,
            extra_env=extra_env,
        )
        self._last_run_time = None
        self._last_cmd = None

    def run(self):
        cmd = [self.executable()]
        cmd.extend(self.argv())

        env = self.env()

        os_flags = {}

        # Disowning processes in linux/mac
        if hasattr(os, "setsid"):
            os_flags["preexec_fn"] = os.setsid

        # Disowning processes in windows
        if hasattr(subprocess, "STARTUPINFO"):
            # Detach the process
            os_flags["creationflags"] = subprocess.CREATE_NEW_CONSOLE

            # Hide the process console
            startupinfo = subprocess.STARTUPINFO()
            if self.show_terminal():
                flag = "/C"
                if self.keep_terminal():
                    flag = "/K"
                cmd = ["cmd", flag] + cmd
            else:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            os_flags["startupinfo"] = startupinfo

        logger.info("Running Subprocess: %r", cmd)
        
        if not os.path.exists(self._get_log_dir()):
            os.mkdir(self._get_log_dir())
        
        # Store run time used to compute log paths
        self._last_run_time = time.time()
        cmd = [str(arg) for arg in cmd]
        self._last_cmd = ' '.join(cmd)

        with open(self.get_log_path(), 'w+') as log_fd:
            self._popen = subprocess.Popen(
                cmd,
                env=env,
                stdout=log_fd,
                stderr=log_fd,
                **os_flags,
            )
    
    def _get_log_dir(self):
        return str(pathlib.Path.home()) + "/.libreflow/log/"

    def get_log_path(self):
        dt = datetime.fromtimestamp(self._last_run_time)
        dt = dt.astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
        
        path = os.path.join(
            self._get_log_dir(),
            '%s_%s.log' % (self.runner_name(), dt),
        )
        return path
    
    def has_run(self):
        return self._last_run_time is not None
    
    def last_run_time(self):
        return self._last_run_time
    
    def cmd(self):
        return self._last_cmd
    
    def pid(self):
        return self._popen.pid
    
    def last_run_time(self):
        return self._last_run_time
    
    def terminate(self):
        self._popen.terminate()
    
    def kill(self):
        self._popen.kill()

    def is_running(self):
        return self._popen.poll() is None
    
    def return_code(self):
        return self._popen.returncode


class SubprocessManager(object):
    """
    The SubprocessManager manages a list of Runner instances.
    
    From original kabaret.subprocess_manager.runner_factory.SubprocessManager
    """

    def __init__(self):
        super(SubprocessManager, self).__init__()
        self._runners = {}

    @staticmethod
    def _get_runner_info(runner, rid):
        return dict(
            id=rid,
            label=runner.label,
            name=runner.runner_name(),
            icon=runner.runner_icon(),
            version=runner.version,
            is_running=runner.is_running(),
            log_path=runner.get_log_path(),
            command=runner.cmd(),
            last_run_time=runner.last_run_time(),
            pid=runner.pid(),
        )
    
    @staticmethod
    def _get_unknown_runner_info(rid):
        return dict(
            id=rid,
            label='!!!',
            name='!!!',
            icon=('icons.libreflow', 'exclamation-sign-colored'),
            version='!!!',
            is_running=False,
            log_path='!!!',
            command='!!!',
            last_run_time=-1,
            pid=-1,
        )
    
    def get_runner_infos(self):
        """
        Return a list of dict with keys:
            label, name, icon, version, is_running, log_path
        """
        infos = []
        for id, runner in self._runners.items():
            if runner.has_run():
                infos.append(
                    self._get_runner_info(runner, id)
                )
        
        return infos
    
    def get_runner_info(self, rid):
        """
        Returns data of the runner indexed with
        the given id `rid`, as a dict with keys:
            id, label, name, icon, version, is_running, log_path, pid
        """
        try:
            runner = self._runners[rid]
        except KeyError:
            return self._get_unknown_runner_info(rid)
        else:
            return self._get_runner_info(runner, rid)
    
    def get_runner(self, rid):
        return self._runners.get(rid, None)
    
    def delete_runner(self, rid):
        try:
            self._runners.pop(rid)
        except KeyError:
            return False
        else:
            return True

    def run(self, runner):
        rid = self._add_runner(runner)
        runner.run()
        return rid

    def _add_runner(self, runner):
        rid = str(uuid.uuid4())
        max_tries = 10
        i = 0
        while rid in self._runners and i < max_tries:
            rid = str(uuid.uuid4())
            i += 1
        if i == max_tries:
            raise Exception('Could not create a new runner...')

        self._runners[rid] = runner
        return rid
