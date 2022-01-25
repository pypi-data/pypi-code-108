"""
Package management - interactions with pip, virtual environments.
"""
import re
import subprocess
import sys
import tempfile

PTN_EXPR = re.compile(r'^\s*([A-Za-z0-9\-._]+)(\[[A-Za-z0-9.\-_]+])?(\s*(=|==|>|>=|<|<=)\s*([0-9.\-a-zA-Z]+)\s*,?)*(\s+-[^\s]+)*\s*?$')


def current_packages():
    """
    Get the list of currently installed packages.
    """
    stdout = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
    out = {}
    for line in stdout.decode("utf-8").split("\n"):
        if "==" not in line:
            continue
        package, version = line.split("==", maxsplit=1)
        out[package] = version
    return out


def parse_package_expr(line: str):
    """
    Verify the format of a package expression is correct.
    """
    if not line or not line.strip() or line.strip().startswith("#"):
        return
    m = PTN_EXPR.match(line)
    if not m:
        raise ValueError(f"Invalid package specification: {line}")
    package = m.group(1)
    options = m.group(2)
    versions = m.group(3)
    flags = m.group(6)
    # TODO compiled callable method that tests whether a package version matches
    # TODO work out the ideal version to install (latest or something else), or rather the whole set of options
    return line


def install_packages(packages: list, verbose: bool=False):
    """
    Install packages.
    """
    for line in packages:
        parse_package_expr(line)
    with tempfile.NamedTemporaryFile(suffix=".requirements.txt", mode='w') as f_tmp:
        f_tmp.write("\n".join(packages))
        f_tmp.flush()
        subprocess.check_call([sys.executable, "-m", "pip", "install", *([] if verbose else ["-q"]), "--disable-pip-version-check", "-r", f_tmp.name])
