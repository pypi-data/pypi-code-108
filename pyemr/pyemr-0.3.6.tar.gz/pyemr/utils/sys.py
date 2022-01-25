""" """
import glob
import os
import shutil
import socket
import sys
import time

import pexpect


def get_site_package_paths():
    """Returns the paths of the site packages.

    Example:

    Args:

    Returns:

    >>> site_package = get_site_package_paths()
        >>> assert len(site_package) > 0
        >>> assert min([path.endswith("site-packages") for path in site_package])
    """

    spks = []
    for path in sys.path:
        if path.endswith("site-packages"):
            if path not in spks:
                spks.append(path)

    return ",".join(spks)


def copy_and_overwrite(from_path, to_path):
    """

    Args:
      from_path:
      to_path:

    Returns:

    """
    if os.path.exists(to_path):
        shutil.rmtree(to_path)

    # os.makedirs(to_path, exist_ok=True)
    shutil.copytree(from_path, to_path)


def os_cmd(*args, **kwargs):
    """

    Args:
      *args:
      **kwargs:

    Returns:

    """

    args = " ".join(args)
    kwargs = " ".join(["-{k} {v}" for k, v in kwargs.items()])
    cmd = []
    if args:
        cmd.append(args)
    if kwargs:
        cmd.append(kwargs)

    cmd = " ".join(cmd)
    os.system(cmd)


def pexpect_terminate(process):
    """

    Args:
      p:
      process:

    Returns:

    """
    for _ in range(5):
        if process.isalive():
            process.sendeof()

    time.sleep(1)
    if process.isalive():
        process.terminate()

    return True


def pipe_cmd(cmd, cwd=None):
    """

    Args:
      cmd:
      cwd: (Default value = None)

    Returns:

    """

    if type(cmd) == list:
        cmd = " ".join(cmd)

    print("")
    print(f"% {cmd}")
    print("...")
    print("")
    try:

        if cwd:
            process = pexpect.spawn(cmd, cwd=cwd)
        else:
            process = pexpect.spawn(cmd)

        process.interact()

    except KeyboardInterrupt:
        pexpect_terminate(process)
        raise

    pexpect_terminate(process)


def is_port_in_use(port: int):
    """

    Args:
      port: int:
      port: int:
      port: int:
      port: int:
      port: int:
      port: int:
      port: int:
      port: int:
      port: int:
      port: int:
      port: int:

    Returns:

    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        return soc.connect_ex(("localhost", port)) == 0


def get_all_files(depth=10):
    """Get all the file paths at some depth.

    Args:
      depth: (Default value = 10)

    Returns:

    """
    pattern = "*"
    for _ in range(depth):
        yield from glob.glob(pattern)

        pattern += "/*"


def search_pwd(pattern):
    """

    Args:
      pattern:

    Returns:

    """
    res = []
    for path in get_all_files():
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as file:
                    if pattern in file.read():
                        res.append(path)
            except:
                pass
    return res


def argskwargs_to_argv(args: list, kwargs: dict):
    """convert args list and kwargs dict to a list of string.

    Args:
      args: list:
      kwargs: dict:
      args: list:
      kwargs: dict:
      args: list:
      kwargs: dict:
      args: list:
      kwargs: dict:
      args: list:
      kwargs: dict:
      args: list:
      kwargs: dict:
      args: list:
      kwargs: dict:
      args: list:
      kwargs: dict:

    Returns:

    """

    argv = []

    if args and (len(args) > 0):
        for arg in args:
            argv.append(f"{arg}")

    if kwargs and len(kwargs) > 0:
        for key, value in kwargs.items():
            argv.append(f"--{key}")
            argv.append(f"{value}")

    return argv


def validate_py_script(script_path):
    """

    Args:
      script_path:

    Returns:

    """
    if not script_path.endswith(".py"):
        raise ValueError(f"The script '{script_path}' does not end with '.py'")
