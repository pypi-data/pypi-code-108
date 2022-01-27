import subprocess
from threading import Timer
from types import SimpleNamespace
import shlex

class TimeoutError(Exception):
    pass
class ExitCodeError(Exception):
    def __init__(self, command, code, stderr):
        message = f"Command {command} exited with return code: {code}\n{stderr}"
        super().__init__(message)

        self.command = command
        self.code = code
        self.stderr = stderr

def run_process(command, stdin="", timeout=None):
    process = subprocess.Popen(
            shlex.split(command),
            stdin=subprocess.PIPE if stdin else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
    )
    # Timeout timer
    # timer = Timer(timeout, process.kill) if timeout else None

    try:
        # if timer:
        #     timer.start()

        # out, err = process.communicate(input=stdin.encode('utf-8'))
        # stdout = out.decode('utf-8')
        # stderr = err.decode('utf-8')
        stdout, stderr = map(lambda x: x.decode("utf-8"),
                process.communicate(
                    input=stdin.encode('utf-8'),
                    timeout=timeout
                ))

        return_code = process.returncode
    except subprocess.TimeoutExpired as e:
        raise TimeoutError()

    finally:
        pass
        # if timer:
        #     timer.cancel()

    if return_code != 0:
        raise ExitCodeError(command, return_code, stderr)

    return SimpleNamespace(stdout = stdout, stderr = stderr)

def run_process_interactive(command):
    try:
        process = subprocess.Popen(command.split())
        process.communicate()
    except KeyboardInterrupt:
        print("\rProgram stopped.")
