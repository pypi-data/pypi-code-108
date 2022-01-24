import os
import subprocess
import time


def pytest_addoption(parser):
    parser.addini(
        "background-cmd",
        help="Path to command to run at background. Default: None",
        type="string",
        default=None,
    )
    parser.addini(
        "background-cmd-env",
        help="Environmental variable to path to command to run at background. Has higher priority than background-cmd. Default: None",
        type="string",
        default=None,
    )
    parser.addini(
        "background-pid",
        help="Path to save PID data of the background process. Default: background.pid",
        type="string",
        default="background.pid",
    )
    parser.addini(
        "background-log",
        help="Path to save log data of the background process. Default: background.log",
        type="string",
        default="background.log",
    )


class BackgroundRunner(object):
    def __init__(
        self,
        background_cmd=None,
        background_env=None,
        pid_path="background.pid",
        log_path="background.log",
    ):
        self._background_cmd = background_cmd
        if background_env and os.getenv(background_env):
            self._background_cmd = os.getenv(background_env)

        self._pid_path = pid_path
        self._log_path = log_path
        self._proc = None

    def start(self):
        if self._background_cmd:
            print(f"Starting {self._background_cmd}...")
            assert not os.path.exists(
                self._pid_path
            ), f'{self._pid_path} exists. Please check if another "{self._background_cmd}" is running.'

            with open(self._log_path, "w") as f:
                self._proc = subprocess.Popen(
                    self._background_cmd.split(), stdout=f, stderr=f
                )

            with open(self._pid_path, "w") as f:
                f.write(str(self._proc.pid))

            time.sleep(0.1)

    def end(self):
        if self._background_cmd and self._proc:
            print(f"Terminating {self._background_cmd}...")
            self._proc.terminate()
            self._proc.wait()
            if os.path.exists(self._pid_path):
                os.remove(self._pid_path)


bg_runner = None


def pytest_configure(config) -> None:
    global bg_runner

    bg_runner = BackgroundRunner(
        background_cmd=config.getini("background-cmd"),
        background_env=config.getini("background-cmd-env"),
        pid_path=config.getini("background-pid"),
        log_path=config.getini("background-log"),
    )
    bg_runner.start()


def pytest_unconfigure(config) -> None:
    global bg_runner
    if bg_runner:
        bg_runner.end()
