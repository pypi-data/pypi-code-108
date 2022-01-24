import base64
import os
import pty
import subprocess
from functools import wraps
from indico_install.config import D_PATH

import click



def options_wrapper():
    def opt_wrapper_outer(f):
        @wraps(f)
        @click.option(
            "--yes/--no",
            "-y/-n",
            default=False,
            show_default=True,
            help="Accept changes",
        )
        def wrapped(
            *args,
            yes=False,
            **kwargs,
        ):
            # Backend
            return f(
                *args,
                yes=yes,
                **kwargs,
            )

        return wrapped

    return opt_wrapper_outer


def _read(fd):
    return os.read(fd, 10240)


def with_pty(cmd: list):
    pty.spawn(cmd, master_read=_read, stdin_read=_read)


def run_cmd(mycmd, envvars: dict = None, silent=False, tty=False):
    if envvars is None:
        envvars = dict(os.environ)
    if tty and not isinstance(mycmd, list):
        raise AssertionError("Command must be passed in as a list for TTY")
    if not silent:
        click.secho(f"Running command: {mycmd}", fg="blue")

    popen_kwargs = dict(env=envvars, shell=True, stdout=subprocess.PIPE)
    if tty:
        return with_pty(mycmd)
    else:
        output = subprocess.Popen(mycmd, **popen_kwargs)
        stdout, _ = output.communicate()
        if stdout is not None:
            stdout = stdout.decode("utf-8").strip()
            if not silent:
                print(stdout, "\n")
        return stdout


def region_to_gmt(region):
    offset = "+0:00"
    if region.upper().startswith("us-east"):
        offset = "-5:00"
    return f"GMT{offset}"


def get_value(value_dict, keys):
    if not keys:
        return value_dict
    elif len(keys) == 1:
        return value_dict.get(keys[0], None)
    else:
        return get_value(value_dict[keys[0]], keys[1:])


def find_values(value_dict, target_value, base_key=None):
    if base_key is None:
        base_key = []
    for key, value in value_dict.items():
        if isinstance(value, dict):
            yield from find_values(value, target_value, base_key=base_key + [key])
        elif isinstance(value, str) and value.strip().lower() == target_value:
            yield value_dict, key, base_key


def base64file(filename):
    with open(filename, "r") as f:
        return convertb64(f.read())


def convertb64(mystring):
    return base64.b64encode(mystring.encode("utf-8")).decode("utf-8")


def decodeb64(mystring):
    return base64.b64decode(mystring.encode("utf-8")).decode("utf-8")


def determine_resource(deployment):
    for resource in ("deployment", "statefulset"):
        result = run_cmd(
            f"kubectl get {resource} | tail -n +2 | awk '{{print $1}}'", silent=True
        )
        if deployment in result.split():
            return resource


def current_user(clean=False):
    try:
        user = next(
            (
                s
                for s in run_cmd(
                    "gcloud auth list 2>/dev/null", silent=True
                ).splitlines()
                if s.startswith("*")
            ),
            "- unknown",
        ).split()[1]
        if user == "unknown":
            user = "service_acct" if os.getenv("GOOGLE_SERVICE_ACCOUNT") else None
        elif clean:
            user = user.split("@", 1)[0].replace("gcr-", "", 1)
        return user
    except Exception:
        return None


def current_tag():
    branch = run_cmd(
        f"git -C {D_PATH} rev-parse --abbrev-ref HEAD 2>&1", silent=True
    )
    if branch.startswith("fatal:"):
        return "unknown"
    commit = run_cmd(f"git -C {D_PATH} rev-parse 2>&1", silent=True)
    return string_to_tag(f"{branch}_{commit}")


def find_gcs_key(quiet=False):
    # TODO: improve the gcr key finder
    key_file = run_cmd(
        f"ls {D_PATH}" + r" | grep -e '^gcr-.*\.json$'", silent=True
    )
    err = None
    if not key_file:
        err = f"No GCR key file found in {D_PATH}! A GCR key file looks like 'gcr-<name>.json'"
    elif len(key_file.split("/n")) > 1:
        err = "Too many GCR key files found. Please only have 1"

    if err:
        if not quiet:
            click.secho(err, fg="red")
        return None
    return key_file


def string_to_tag(string):
    """Clean string to be used as folder path"""
    return "".join(
        [c if c.isalnum() or c in ("-", "_") else "_" for c in (string or "")]
    )


def pretty_diff(diff: list, show_all=False):
    for k, status, old_val, new_val in diff:
        if status == "+":
            click.secho(f"{k}: {new_val}", fg="green")
        elif status == "-":
            click.secho(f"{k}: {old_val}", fg="red")
        elif status == "*":
            click.secho(f"{k}: {old_val} -> {new_val}", fg="yellow")
        elif show_all:
            click.echo(f"{k}: {new_val}")


def diff_dicts(old: dict, new: dict):
    """
    Diff a dictionary
    + : added
    - : removed
    * : changed

    Return a list of tuples (key, status, old, new)
    """
    results = []
    for k in sorted(set(old).union(set(new))):
        old_val = old.get(k)
        new_val = new.get(k)
        status = None
        if old_val == new_val:
            pass
        elif old_val is None and new_val:
            status = "+"
        elif new_val is None and old_val:
            status = "-"
        elif new_val != old_val:
            status = "*"
        results.append((k, status, old_val, new_val))
    return results


def diff_files(f1, f2):
    diff_out = run_cmd(f"diff {f1} {f2}", silent=True)
    for line in diff_out.splitlines():
        if line.startswith("+"):
            click.secho(line, fg="green")
        elif line.startswith("-"):
            click.secho(line, fg="red")
        else:
            click.echo(line)
