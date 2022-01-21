import subprocess


def run_subprocess(command, **kwargs):
    """
    subprocess.run was added in Python 3.5 as a simplification over subprocess.
    Popen when you just want to execute a command and wait until it finishes,
     but you don't want to do anything else meanwhile.
      For other cases, you still need to use subprocess.Popen.
    """
    stdout = kwargs.pop("stdout", subprocess.PIPE)
    stderr = kwargs.pop("stderr", subprocess.PIPE)
    # cmd = subprocess.run(command, shell=shell, capture_output=True)
    cmd = subprocess.Popen(command, stdout=stdout, stderr=stderr, **kwargs)
    cmd.wait()
    return cmd


def exec_command(command, shell=True, **kwargs):
    cmd = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd.wait()
    result = cmd.stdout
    try:
        result = result.read()
    except Exception as e:
        print("[stdout]", result, e)
    if cmd.returncode == 0:
        return True, result, ""
    else:
        error = cmd.stderr
        try:
            error = error.read()
        except Exception as e:
            print("[stderr]", error, e)
        return False, result, error
