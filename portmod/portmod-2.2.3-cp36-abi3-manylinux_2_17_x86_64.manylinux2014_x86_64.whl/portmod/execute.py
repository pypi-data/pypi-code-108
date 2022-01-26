# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import subprocess
import sys
from pathlib import Path
from shutil import which
from typing import AbstractSet, Iterable, List, Set, Tuple, Union

from portmodlib.fs import is_parent
from portmodlib.l10n import l10n

from .config import get_config, get_config_value
from .globals import env
from .perms import Permissions
from .win32 import get_personal


def _required_exe(name: str) -> str:
    path = which(name)

    if not path:
        raise FileNotFoundError(l10n("missing-executable", file=name))
    return path


def resolve_paths(path: str) -> List[str]:
    """
    Returns all paths related to the symlink chain at paths
    If no symlinks exist, just returns path
    """
    paths = []
    prefix = ""
    for part in Path(path).parts:
        if os.path.islink(os.path.join(prefix, part)):
            last = os.path.join(prefix, part)
            paths.append(last)
            while os.path.islink(last):
                linkpath = os.readlink(last)
                if os.path.isabs(linkpath):
                    last = linkpath
                else:
                    last = os.path.normpath(
                        os.path.join(os.path.dirname(last), linkpath)
                    )
                paths.append(last)
        prefix = os.path.realpath(os.path.join(prefix, part))

    return paths


def parents(paths: Set[str]) -> Set[str]:
    results = set()
    for path in paths:
        for ppath in Path(path).parents:
            results.add(str(ppath))
    return results


def _dedup_subpaths(paths: Iterable[str]) -> List[str]:
    used: List[str] = []
    for path in sorted(paths):
        abspath = os.path.abspath(path)
        if os.path.exists(abspath):
            if any(is_parent(abspath, usedpath) for usedpath in used):
                continue
            used.append(abspath)

    return used


def get_paths(
    ro_paths: AbstractSet[str], rw_paths: AbstractSet[str]
) -> Tuple[Set[str], Set[str], Set[str]]:
    result_ro: Set[str] = set()
    result_rw: Set[str] = set()
    symlinks = set()

    def resolve_chain(path: str, path_set: Set[str]):
        chain = resolve_paths(path)
        if chain:
            # Elements are symlinks
            # the last is the end of the symlink chain.
            if os.path.islink(path):
                symlinks.add(path)
            else:
                path_set.add(path)
            path_set.add(os.path.realpath(path))
            for link in chain[:-1]:
                symlinks.add(link)
            # Ignore last element in chain, since it is
            # part of the resolved path (but not necessarily identical to the resolved
            # path if it's a directory symlink, but the original path pointed to either
            # a subdirectory of the symlink, or a file)
        else:
            path_set.add(path)

    for path in _dedup_subpaths(rw_paths):
        resolve_chain(path, result_rw)

    for path in _dedup_subpaths(ro_paths | rw_paths):
        if path not in result_rw:
            resolve_chain(path, result_ro)

    filtered_symlinks: Set[str] = set()
    for path in _dedup_subpaths(result_ro | result_rw | symlinks):
        if path in symlinks:
            filtered_symlinks.add(path)
    return result_ro, result_rw, filtered_symlinks


def sandbox_execute(
    command: List[str],
    permissions: Permissions,
    *,
    pipe_output: bool = False,
    err_on_stderr: bool = False,
    check: bool = True,
    pipe_error: bool = False,
) -> Union[str, None, bool]:
    """
    Executes command

    This is designed to be assigned to the FullPybuild.execute field prior to phase function
    execution. It is not set by default as it is not permitted outside of phase functions
    (e.g. in __init__)"""

    def cleanup():
        pass

    rw_paths = set(permissions.rw_paths)
    ro_paths = set(permissions.ro_paths)
    if env.TESTING:
        # Add source directory to whitelist so that we can get coverage from subprocesses
        rw_paths.add(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    environ = os.environ.copy()

    # Set profile variables as environment variables in the sandbox
    for key, value in get_config().items():
        if isinstance(value, str):
            environ[key] = value
        elif isinstance(value, bool):
            if value:
                environ[key] = str(value)

    if permissions.tmp:
        environ["TMP"] = permissions.tmp
        os.makedirs(permissions.tmp, exist_ok=True)

    # ensure paths added at runtime are available
    if "PYTHONPATH" not in environ:
        environ["PYTHONPATH"] = ""
    if sys.platform == "win32":
        environ["PYTHONPATH"] += ";" + ";".join(sys.path)
    else:
        environ["PYTHONPATH"] += ":" + ":".join(sys.path)

    if sys.platform == "linux":
        if permissions.global_read:
            ro_paths.add("/")
        else:
            ro_paths |= {
                "/bin",
                "/etc",
                "/gnu",
                "/lib",
                "/lib32",
                "/lib64",
                "/run",
                "/nix",
                "/opt",
                "/usr",
                "/var",
            }

        ro_paths, rw_paths, syms = get_paths(ro_paths, rw_paths)

        ro_bind: List[str] = sum([["--ro-bind", path, path] for path in ro_paths], [])
        bind: List[str] = sum([["--bind", path, path] for path in rw_paths], [])

        sym_dests = []
        for path in syms:
            linkpath = os.readlink(path)
            if os.path.isabs(linkpath):
                sym_dests.append(linkpath)
            else:
                sym_dests.append(os.path.join(os.path.dirname(path), linkpath))

        symlink: List[str] = sum(
            [["--ro-bind", dpath, path] for dpath, path in zip(sym_dests, syms)], []
        )

        # Needs to be a list of command arguments
        # I.e. NOT a string
        user = get_config_value("_SANDBOX_PERMISSIONS", [])
        if not isinstance(user, list):
            raise TypeError("_SANDBOX_PERMISSIONS must be a list of arguments to bwrap")

        sandbox_command = (
            [_required_exe("bwrap")]
            + ro_bind
            + bind
            + symlink
            + [
                "--dev",
                "/dev",
                "--proc",
                "/proc",
                "--unshare-all",
                "--chdir",
                os.getcwd(),
                "--die-with-parent",
            ]
            + user
        )
        if permissions.network:
            sandbox_command.append("--share-net")
        if permissions.tmp:
            sandbox_command.extend(["--bind", permissions.tmp, permissions.tmp])
        else:
            os.makedirs(env.PYBUILD_TMP_DIR, exist_ok=True)
            sandbox_command.extend(["--bind", env.PYBUILD_TMP_DIR, env.PYBUILD_TMP_DIR])

    elif sys.platform == "win32":
        SINI = _required_exe("sbieini.exe")
        start_exe = _required_exe("start.exe")

        BOXNAME = "Portmod"
        delete_commands = []

        def win32_cleanup():
            olddir = os.getcwd()
            os.chdir(os.path.dirname(start_exe))
            try:
                subprocess.check_call(
                    f'"{start_exe}" /box:Portmod /silent /nosbiectrl delete_sandbox'
                )
            except subprocess.CalledProcessError:
                pass
            finally:
                for command in delete_commands:
                    subprocess.check_call(command)
                os.chdir(olddir)

        cleanup = win32_cleanup  # noqa

        def add_command(command: str, typ: str, value: str):
            nonlocal delete_commands
            subprocess.check_call(f'"{SINI}" {command} {BOXNAME} {typ} "{value}"')
            delete_commands.append(f'"{SINI}" delete {BOXNAME} {typ} "{value}"')

        if not permissions.network:
            add_command("append", "ClosedFilePath", "InternetAccessDevices")

        # Create a temporary directory that can be used without affecting the user's system
        if not permissions.tmp:
            environ["TMP"] = env.PYBUILD_TMP_DIR
        add_command("append", "WriteFilePath", environ["TMP"])

        ro_paths.add(os.path.normpath(os.environ["programfiles(x86)"]))
        ro_paths.add(os.path.normpath(os.environ["programfiles"]))

        ro_paths, rw_paths, symlinks = get_paths(ro_paths, rw_paths)

        if not permissions.global_read:
            add_command("append", "ClosedFilePath", get_personal())

        for path in rw_paths:
            add_command("append", "OpenPipePath", path)
        add_command("set", "Enabled", "y")

        # A wrapper command is used, combined with ForceProcess, as starting the process
        # using sandboxie's start.exe would not give us any stdout or stderr.
        add_command("set", "ForceFolder", os.getcwd())

        # Needs to be a list of command argument tuples
        user = get_config_value("_SANDBOX_PERMISSIONS", [])
        if not isinstance(user, list):
            raise TypeError(
                "_SANDBOX_PERMISSIONS must be a list with sbieini commands in the order of $command $type $value. "
                'E.g. ["append", "ClosedFilePath", "filename.txt"]'
            )
        for user_command, typ, value in user:
            add_command(user_command, typ, value)

        sandbox_command = []
    elif sys.platform == "darwin":
        sandbox_command = [_required_exe("sandbox-exec"), "-p"]

        sandbox_profile = """
            (version 1)
            (deny default)
            (allow process-exec*)
            (allow signal (target self))
            (allow process-fork)
            (allow sysctl-read)
            (allow file-read*
                file-write-data
                (literal "/dev/null")
                (literal "/dev/zero")
            )
            (allow file-read*
                file-write-data
                file-ioctl
                (literal "/dev/dtracehelper")
            )
            (allow ipc-posix-shm)
        """

        if permissions.global_read:
            sandbox_profile += """
                (allow file-read*)
            """
        else:
            sandbox_profile += """
                (allow file-read-data file-read-metadata
                  (regex "^/dev/autofs.*")
                  (regex "^/Users/[^/]*/.gitconfig")
                  (literal "/var")
                  (literal "/dev/fd")
                  (literal "/dev/random")
                  (literal "/dev/urandom")
                  (literal "/var/db")
                  (literal "/var/db/xcode_select_link")
                  (literal "/")
                )
            """

            ro_paths |= {
                "/usr",
                "/System/Library",
                "/Applications",
                "/etc",
                "/private/etc",
                "/Library",
                "/opt",
            }

        if not permissions.tmp:
            environ["TMPDIR"] = env.PYBUILD_TMP_DIR
            os.makedirs(environ["TMPDIR"], exist_ok=True)
        rw_paths.add(environ["TMPDIR"])
        ro_paths.add("/private/var/select/sh")
        ro_paths, rw_paths, symlinks = get_paths(ro_paths, rw_paths)

        if not permissions.global_read:
            sandbox_profile += """
                (allow file-read*"""
            for path in ro_paths:
                sandbox_profile += f"""
                    (subpath "{path}")"""
            for path in parents(ro_paths | rw_paths):
                sandbox_profile += f"""
                    (literal "{path}")"""
            for path in symlinks:
                sandbox_profile += f"""
                    (literal "{path}")"""
            sandbox_profile += """
                )"""

        if permissions.network:
            sandbox_profile += "\n(allow network*)"

        sandbox_profile += """
            (allow file-write* file-read*"""
        for path in rw_paths:
            sandbox_profile += f"""
                (subpath "{path}")"""
        sandbox_profile += """
            )"""

        # Must be a string
        user = get_config_value("_SANDBOX_PERMISSIONS", "")
        if not isinstance(user, str):
            raise TypeError(
                "_SANDBOX_PERMISSIONS must be a string with sandbox-exec profile contents"
            )
        sandbox_profile += user

        sandbox_command.append(sandbox_profile)
    else:
        raise Exception("Unsupported Platform")

    output = None
    error = None
    if pipe_output:
        output = subprocess.PIPE
    if err_on_stderr or pipe_error:
        error = subprocess.PIPE

    try:
        proc = subprocess.run(
            sandbox_command + command,
            check=check,
            stdout=output,
            stderr=error,
            env=environ,
        )
    except subprocess.CalledProcessError as err:
        # Mostly arbitrary number used to indicate boolean true
        # Used by can-update-live
        if err.returncode == 142:
            return True
        raise err
    finally:
        cleanup()

    if err_on_stderr and proc.stderr:
        raise subprocess.CalledProcessError(
            0, sandbox_command + command, proc.stdout, proc.stderr
        )

    result = ""
    if pipe_output and proc.stdout:
        result += proc.stdout.decode("utf-8")
    if pipe_error and proc.stderr:
        result += proc.stderr.decode("utf-8")
    if pipe_output or pipe_error:
        return result

    # Mostly arbitrary number used to indicate boolean true
    if proc.returncode == 142:
        return True

    return None
