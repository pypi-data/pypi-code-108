import getpass
import json
import os
from argparse import Namespace
from pathlib import Path

import requests
import yaml
from owl_client.utils import get_auth, make_request, read_config

from ..schema import schema_pipeline
from ..utils import print_table
from .run_standalone import run_standalone  # noqa: F401


# Auth -----------------------------------------------------------------------
def auth_login(args: Namespace) -> None:
    """Login to the API.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/auth/login"
    print("Using Authentication API: {}{}".format(args.api, route))
    username = input("Username: ")
    password = getpass.getpass("{}'s Password: ".format(username))

    data = {"username": username, "password": password}
    res = make_request(args.api, route, "POST", data=data)

    owlrc = Path("~/.owlrc").expanduser()
    with owlrc.open(mode="w+") as fd:
        config = yaml.safe_load(fd.read())
        if config is None:
            config = {}
        config.update({"username": username, "token": res["token"]})
        config = yaml.dump(config)
        fd.seek(0)
        fd.write(config)

    os.chmod("{}".format(owlrc), 0o600)
    print("Login Successful")


def auth_password(args: Namespace) -> None:
    """Login to the API.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/auth/change_password"
    password = getpass.getpass("New Password: ")
    password2 = getpass.getpass("Repeat Password: ")
    if password != password2:
        raise SystemExit("ERROR: Passwords do not match.")

    data = {"username": "xxx", "password": password}
    make_request(args.api, route, "POST", data=data, auth=True)

    print("Password changed")


def auth_logout(args: Namespace) -> None:
    """Login to the API.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/auth/logout"
    make_request(args.api, route, "POST", auth=True)

    Path("~/.owlrc").unlink(missing_ok=True)
    print("Logout Successful")


# PDeF -----------------------------------------------------------------------
def pdef_list(args: Namespace) -> None:
    """List pipeline definitions in the server.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pdef/list"
    res = make_request(args.api, route, "GET", auth=True)
    table = [["Id", "Name", "Package", "Active"]]
    for r in res:
        table.append([r["id"], r["name"], r["extra_pip_packages"], r["active"]])
    print_table(table)


def pdef_get(args: Namespace) -> None:
    """Get pipeline defition file

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pdef/get"
    res = make_request(args.api, f"{route}/{args.name}", "GET", auth=True)
    pdef = res["pdef"]
    if args.output:
        args.output.write(pdef)
    else:
        print(pdef)


# Job ------------------------------------------------------------------------
def job_submit(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pipeline/add"
    conf = read_config(args.conf, schema_pipeline)

    data = {"config": conf}
    res = make_request(args.api, route, "POST", data=data, auth=True)

    print("JobID {id} submitted".format(**res))


def job_status(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pipeline/status"

    res = make_request(args.api, f"{route}/{args.jobid}", "GET", auth=True)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        msg = "{id:5d} {user:12s} {status}"
        print(msg.format(**res))


def job_logs(args: Namespace) -> None:
    """Get pipeline log
    """
    route = "/api/pipeline/log"
    headers = get_auth()
    level = "debug" if args.debug else "info"
    r = requests.get(
        f"{args.api}{route}/{args.jobid}/{level}", headers=headers, stream=True
    )
    for line in r.iter_lines():
        if line:
            jline = json.loads(line.decode())
            if "detail" in jline:
                print("ERROR:", jline["detail"])
            else:
                print(
                    "\033[92m{timestamp}\033[0m \033[94mPIPELINE({jobid})\033[0m \033[96m{level}\033[0m {func_name} - {message}".format(
                        **jline
                    )
                )


def job_cancel(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pipeline/update"
    data = {"status": "TO_CANCEL"}
    res = make_request(args.api, f"{route}/{args.jobid}", "POST", data=data, auth=True)

    msg = "{id:5d} {user:12s} {status}"
    print(msg.format(**res))


def job_rerun(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pipeline/update"
    data = {"status": "PENDING"}
    res = make_request(args.api, f"{route}/{args.jobid}", "POST", data=data, auth=True)

    msg = "{id:5d} {user:12s} {status}"
    print(msg.format(**res))


def job_list(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pipeline/list"
    data = {"listall": args.all}
    res = make_request(args.api, f"{route}/{args.status}", "GET", data=data, auth=True)
    table = [["Id", "User", "Name", "Status"]]
    for r in res:
        table.append([r["id"], r["user"], r["config"]["name"], r["status"]])
    print_table(table)


# Admin ----------------------------------------------------------------------
def pipedef_add(args: Namespace) -> None:
    """Add or update a pipeline definition signature.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/pdef/add"
    pdef = [line for line in args.name.readlines()]
    config = read_config("".join(pdef))
    name = config["name"]
    data = {
        "name": name,
        "pdef": "".join([line for line in pdef if not line.startswith("sig:")]),
        "extra_pip_packages": config["sig:extra_pip_packages"],
        "active": config["sig:active"],
    }

    res = make_request(args.api, route, "POST", data=data, auth=True)
    print("Pipeline {!r} {}".format(res["name"], res["action"]))


def add_user(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/auth/user/add"

    if args.password is None:
        password = getpass.getpass("Password: ")
        password2 = getpass.getpass("Repeat Password: ")
        if password != password2:
            raise SystemExit("Passwords do not match")
    else:
        password = args.password

    data = {
        "username": args.username,
        "password": password,
        "is_admin": args.admin,
        "active": args.active,
    }

    res = make_request(args.api, route, "POST", data=data, auth=True)
    print("User", res["user"], "added")


def update_user(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/auth/user/update"
    data = {
        "username": args.username,
        "password": args.password,
        "is_admin": args.admin,
        "active": args.active,
    }

    res = make_request(args.api, route, "POST", data=data, auth=True)
    print("User", res["user"], "updated")


def get_user(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/auth/user/get"

    res = make_request(args.api, f"{route}/{args.username}", "GET", auth=True)
    table = [["Id", "User", "Admin", "Active"]]
    for r in res:
        table.append([r["id"], r["username"], r["is_admin"], r["active"]])
    print_table(table, pad=10)


def admin_command(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    route = "/api/admin/command"
    data = {"cmd": args.command}

    res = make_request(args.api, route, "POST", data=data, auth=True)
    print(res)
