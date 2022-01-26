import argparse
import json
import logging
import logging.config
import os
import sys
from argparse import ArgumentParser, FileType, Namespace
from typing import List

from owl_client import scripts

log = logging.getLogger(__name__)


def get_api_url():
    url = os.environ.get("OWL_API_URL")
    if url is None:
        host = os.environ.get("OWL_API_SERVICE_HOST")
        port = os.environ.get("OWL_API_SERVICE_PORT")
        if host and port:
            url = f"http://{host}:{port}"
    return url


def parse_args(input: List[str]) -> Namespace:
    """Parse command line arguments.

    Parameters
    ----------
    input
        list of command line arguments

    Returns
    -------
    parsed arguments
    """
    OWL_API_URL = get_api_url()

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument("--api", required=False, type=str, default=OWL_API_URL)

    main_parser = ArgumentParser(description="Owl Pipeline Client")
    subparsers = main_parser.add_subparsers(help="commands", dest="command")

    # Auth
    auth = subparsers.add_parser("auth", parents=[parent_parser])
    subparsers_auth = auth.add_subparsers(help="commands", dest="command")

    auth_login = subparsers_auth.add_parser("login")
    auth_login.set_defaults(func=scripts.auth_login)

    auth_logout = subparsers_auth.add_parser("logout")
    auth_logout.set_defaults(func=scripts.auth_logout)

    auth_password = subparsers_auth.add_parser("change_password")
    auth_password.set_defaults(func=scripts.auth_password)

    # PDeF
    pipedef = subparsers.add_parser(
        "pdef", description="Owl Pipeline Client", parents=[parent_parser]
    )
    subparsers_pdef = pipedef.add_subparsers(help="commands", dest="command")

    pdef_list = subparsers_pdef.add_parser("list")
    pdef_list.set_defaults(func=scripts.pdef_list)

    pdef_get = subparsers_pdef.add_parser("get")
    pdef_get.add_argument("name", type=str, help="name of pipeline definition")
    pdef_get.add_argument("--output", "-o", type=FileType("w"))
    pdef_get.set_defaults(func=scripts.pdef_get)

    # Job
    job = subparsers.add_parser("job", parents=[parent_parser])
    subparsers_job = job.add_subparsers(help="commands", dest="command")

    job_submit = subparsers_job.add_parser("submit")
    job_submit.add_argument("conf", type=FileType("r"))
    job_submit.set_defaults(func=scripts.job_submit)

    job_status = subparsers_job.add_parser("status")
    job_status.add_argument("jobid", type=int)
    job_status.add_argument("--json", action="store_true", default=False)
    job_status.set_defaults(func=scripts.job_status)

    job_logs = subparsers_job.add_parser("logs")
    job_logs.add_argument("jobid", type=int)
    job_logs.add_argument("--debug", action="store_true", default=False)
    job_logs.set_defaults(func=scripts.job_logs)

    job_cancel = subparsers_job.add_parser("cancel")
    job_cancel.add_argument("jobid", type=int)
    job_cancel.set_defaults(func=scripts.job_cancel)

    job_rerun = subparsers_job.add_parser("rerun")
    job_rerun.add_argument("jobid", type=int)
    job_rerun.set_defaults(func=scripts.job_rerun)

    job_list = subparsers_job.add_parser("list")
    job_list.add_argument("--status", type=str, default="all")
    job_list.add_argument("--all", action="store_true", default=False)
    job_list.set_defaults(func=scripts.job_list)

    # Admin
    admin = subparsers.add_parser("admin", parents=[parent_parser])
    subparsers_admin = admin.add_subparsers(help="commands", dest="command")

    admin_pdef = subparsers_admin.add_parser("pdef")
    subparsers_admin_pdef = admin_pdef.add_subparsers(help="commands", dest="command")

    admin_pdef_add = subparsers_admin_pdef.add_parser("add")
    admin_pdef_add.add_argument(
        "name", type=FileType("r"), help="pipeline definition file"
    )
    admin_pdef_add.set_defaults(func=scripts.pipedef_add)

    # admin_pdef_del = subparsers_admin_pdef.add_parser("delete")
    # admin_pdef_del.add_argument("name", help="name of pipeline definition")
    # admin_pdef_del.set_defaults(func=scripts.pipedef_delete)

    admin_cmd = subparsers_admin.add_parser("cmd")
    admin_cmd.add_argument("command", type=json.loads)
    admin_cmd.set_defaults(func=scripts.admin_command)

    admin_user = subparsers_admin.add_parser("user")
    subparsers_admin_user = admin_user.add_subparsers(help="commands", dest="command")

    admin_user_add = subparsers_admin_user.add_parser("add")
    admin_user_add.add_argument("username", type=str)
    admin_user_add.add_argument(
        "-p", type=str, required=False, dest="password", default=None
    )
    admin_user_add.add_argument("--admin", required=False, action="store_true")
    admin_user_add.add_argument(
        "--active", required=False, dest="active", action="store_true"
    )
    admin_user_add.add_argument(
        "--no-active", required=False, dest="active", action="store_false"
    )
    admin_user_add.set_defaults(active=True)

    admin_user_add.set_defaults(func=scripts.add_user)

    admin_user_update = subparsers_admin_user.add_parser("update")
    admin_user_update.add_argument("username", type=str)
    admin_user_update.add_argument(
        "-p", type=str, required=False, dest="password", default=None
    )
    admin_user_update.add_argument("--admin", required=False, action="store_true")
    admin_user_update.add_argument(
        "--active", required=False, dest="active", action="store_true"
    )
    admin_user_update.add_argument(
        "--no-active", required=False, dest="active", action="store_false"
    )
    admin_user_update.set_defaults(active=True)
    admin_user_update.set_defaults(func=scripts.update_user)

    admin_user_get = subparsers_admin_user.add_parser("get")
    admin_user_get.add_argument("username", type=str)
    admin_user_get.set_defaults(func=scripts.get_user)

    admin_user_list = subparsers_admin_user.add_parser("list")
    admin_user_list.add_argument(
        "--username", type=str, default=0, help=argparse.SUPPRESS
    )
    admin_user_list.set_defaults(func=scripts.get_user)

    # # Admin users interface
    # admin_user = subparsers_admin.add_parser("user")
    # subparsers_admin_user = admin_user.add_subparsers()

    # # Add user: owl admin user add [--admin] username password
    # admin_user_add = subparsers_admin_user.add_parser("add")
    # admin_user_add.add_argument("username", type=str)
    # admin_user_add.add_argument("password", type=str)
    # admin_user_add.add_argument("--admin", required=False, action="store_true")
    # admin_user_add.set_defaults(func=add_user)

    # # Add user: owl admin user update [--admin] username password
    # admin_user_add = subparsers_admin_user.add_parser("update")
    # admin_user_add.add_argument("username", type=str)
    # admin_user_add.add_argument("password", type=str)
    # admin_user_add.add_argument("--admin", required=False, action="store_true")
    # admin_user_add.set_defaults(func=update_user)

    # # PDeF admin
    # pdef = subparsers_admin.add_parser("pdef")
    # subparsers_pdef = pdef.add_subparsers()

    # # Add PDeF: owl admin pdef add pipeline.yaml
    # pdef_add = subparsers_pdef.add_parser("add")
    # pdef_add.add_argument("name", type=FileType("r"))
    # pdef_add.set_defaults(func=add_pipedef)

    # # List pdefs: owl pdef list
    # pdef = subparsers.add_parser("pdef")
    # subparsers_pdef = pdef.add_subparsers()
    # pdef_list = subparsers_pdef.add_parser("list")
    # pdef_list.set_defaults(func=list_pipedef)

    # # Get pdef of a pipeline: owl pdef get example
    # pdef_get = subparsers_pdef.add_parser("get")
    # pdef_get.add_argument("name")
    # pdef_get.set_defaults(func=get_pipedef)

    # # Execute locally: owl execute [-debug] pipeline.yaml
    execute = subparsers.add_parser("execute")
    execute.add_argument("conf", type=FileType("r"))
    execute.add_argument("--debug", action="store_true")
    execute.add_argument("--api", default="local", help=argparse.SUPPRESS)
    execute.set_defaults(func=scripts.run_standalone)

    args = main_parser.parse_args(input)
    if not hasattr(args, "func"):
        if ("admin" in input) and ("pdef" in input):
            admin_pdef.print_help()
        elif ("admin" in input) and ("user" in input):
            admin_user.print_help()
        elif "pdef" in input:
            pipedef.print_help()
        elif "auth" in input:
            auth.print_help()
        elif "job" in input:
            job.print_help()
        elif "admin" in input:
            admin.print_help()
        else:
            main_parser.print_help()
        sys.exit(0)

    if args.api is None:
        raise SystemExit(
            "OWL_API_URL not found. Please set it to the address of the API server."
        )
    return args


def main():
    """Main entry point for owl.

    Invoke the command line help with::

        $ owl --help

    """
    args = parse_args(sys.argv[1:])

    if hasattr(args, "func"):
        args.func(args)
