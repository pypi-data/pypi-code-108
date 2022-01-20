import sys
import uuid
import argparse
import logging
from colorama import Fore, Style
from sumatra.config import CONFIG
from sumatra.auth import CognitoAuth
from sumatra.client import Client
from sumatra.admin import AdminClient

logger = logging.getLogger("sumatra.cli")


def _tmp_branch_name() -> str:
    return "tmp_" + str(uuid.uuid4()).replace("-", "")


def _quantify(format: str, n: int) -> str:
    if n == 0:
        return ""
    plural = "" if n == 1 else "s"
    return format.format(n=n, plural=plural)


def _print_diff(diff, no_color=False) -> None:
    for warning in diff["warnings"]:
        logger.warning(warning)
    events_added = diff["eventsAdded"]
    events_deleted = diff["eventsDeleted"]
    events_modified = []
    tdiffs = {}
    total_added, total_deleted, total_modified = 0, 0, 0
    for tdiff in diff["topologyDiffs"]:
        event_type = tdiff["eventType"]
        if event_type not in events_added + events_deleted:
            events_modified.append(event_type)
        added = [(f, "+") for f in tdiff["featuresAdded"]]
        total_added += len(added)
        deleted = [(f, "-") for f in tdiff["featuresDeleted"]]
        total_deleted += len(deleted)
        modified = [(f, "~") for f in tdiff["featuresRedefined"]]
        total_modified += len(modified)
        tdiffs[event_type] = added + deleted + modified

    color = {"+": Fore.GREEN, "-": Fore.RED, "~": Fore.YELLOW}
    for event in sorted(events_added + events_deleted + events_modified):
        op = "+" if event in events_added else "-" if event in events_deleted else "~"
        if no_color:
            print(f"{op} event {event}")
        else:
            print(
                f"{Style.BRIGHT + color[op] + op} event {event + Fore.RESET + Style.NORMAL}"
            )

        for f, op in sorted(tdiffs.get(event, [])):
            if no_color:
                print(f"  {op + ' ' + f}")
            else:
                print(f"  {color[op] + op + ' ' + f + Fore.RESET}")
        print()
    plan = ", ".join(
        s
        for s in [
            _quantify("add {n} event{plural}", len(events_added)),
            _quantify("delete {n} event{plural}", len(events_deleted)),
            _quantify("add {n} feature{plural}", total_added),
            _quantify("delete {n} feature{plural}", total_deleted),
            _quantify("modify {n} feature{plural}", total_modified),
        ]
        if s
    )

    if any(diff.values()):
        if no_color:
            print(f"Plan: {plan}.")
        else:
            print(f"{Style.BRIGHT}Plan:{Style.NORMAL} {plan}.")
    else:
        print("No changes. LIVE is up-to-date.")


def login(args) -> None:
    instance = args.instance
    try:
        curr_instance = CONFIG.instance
    except:
        curr_instance = None
    while not instance:
        prompt = "Sumatra Instance URL [%s]: " % (
            curr_instance or "e.g.: yourco.sumatra.ai"
        )
        instance = input(prompt).strip()
        if not instance:
            instance = curr_instance
    CONFIG.instance = instance

    auth = CognitoAuth()
    auth.fetch_new_tokens()
    CONFIG.save()
    print("Authentication successful.")


def plan(args) -> None:
    scowl_dir = args.scowl_dir or CONFIG.scowl_dir
    client = Client(args.instance)
    print(f"Comparing '{scowl_dir}' to LIVE on {CONFIG.instance} ({client.tenant})\n")
    branch = _tmp_branch_name()
    client.create_branch_from_dir(scowl_dir, branch)
    try:
        diff = client.diff_branch_with_live(branch)
        _print_diff(diff, args.no_color)
        if not any(diff.values()):
            sys.exit(0)
    finally:
        client.delete_branch(branch)


def apply(args):
    plan(args)
    if not args.auto_approve:
        if args.no_color:
            print(
                f"""\nDo you want to perform the above actions?
      Only 'yes' will be accepted to approve.\n"""
            )
        else:
            print(
                f"""\nDo you want to perform the above actions?
      Only {Fore.GREEN}'yes'{Fore.RESET} will be accepted to approve.\n"""
            )
        reply = ""
        try:
            prompt = "Enter a value: "
            reply = input(prompt).strip()
        except KeyboardInterrupt:
            pass
        if reply.lower() != "yes":
            print("Aborting.")
            sys.exit(1)

    Client(args.instance).publish_dir(args.scowl_dir)
    print("Successfully published to LIVE.")


def push(args):
    branch = Client(args.instance).create_branch_from_dir(args.scowl_dir, args.branch)
    print(f"Successfully pushed to branch '{branch}'.")


def timeline_list(args):
    timelines = Client(args.instance).get_timelines().sort_index()
    if args.show:
        print(timelines)
    else:
        print("\n".join(timelines.index.to_list()))


def timeline_delete(args):
    deleted = Client(args.instance).delete_timeline(args.timeline)
    print(f"Successfully deleted timeline '{deleted}'.")


def timeline_schema(args):
    scowl = Client(args.instance).infer_schema_from_timeline(args.timeline)
    print(scowl)


def timeline_show(args):
    print(Client(args.instance).get_timeline(args.timeline))


def timeline_upload(args):
    with open(args.jsonl, "r") as f:
        jsonl = f.read()
        Client(args.instance).create_timeline_from_jsonl(jsonl, args.timeline)
    print(f"Successfully uploaded to timeline '{args.timeline}'.")


def branch_list(args):
    branches = Client(args.instance).get_branches().sort_index()
    if args.show:
        print(branches)
    else:
        print("\n".join(branches.index.to_list()))


def branch_delete(args):
    deleted = Client(args.instance).delete_branch(args.branch)
    print(f"Successfully deleted branch '{deleted}'.")


def branch_show(args):
    print(Client(args.instance).get_branch(args.branch))


def branch_select(args):
    CONFIG.default_branch = args.branch
    CONFIG.save(update_default_instance=False)


def version(args):
    print(Client(args.instance).version())


def tenant(args):
    print(Client(args.instance).tenant)


def admin_list_tenants(args):
    tenants = AdminClient(args.aws_profile).list_tenants()
    print("\n".join(tenants))


def admin_current_tenant(args):
    print(AdminClient(args.aws_profile).current_tenant(args.user))


def admin_assign_tenant(args):
    AdminClient(args.aws_profile).assign_tenant(args.user, args.tenant)
    print(f"Successfully assigned '{args.user}' to '{args.tenant}'.")


def admin_list_users(args):
    users = AdminClient(args.aws_profile).list_users()
    print("\n".join(users))


ADMIN_COMMANDS = [
    {
        "name": "list-tenants",
        "help": "list all tenants",
        "handler": admin_list_tenants,
    },
    {
        "name": "current-tenant",
        "help": "show user's current tenant",
        "handler": admin_current_tenant,
    },
    {
        "name": "assign-tenant",
        "help": "assign user to tenant",
        "handler": admin_assign_tenant,
    },
    {
        "name": "list-users",
        "help": "list all users",
        "handler": admin_list_users,
    },
]

TIMELINE_COMMANDS = [
    {
        "name": "list",
        "help": "list all remote timelines",
        "handler": timeline_list,
    },
    {
        "name": "delete",
        "help": "delete remote timeline",
        "handler": timeline_delete,
    },
    {
        "name": "schema",
        "help": "display timeline schema as scowl",
        "handler": timeline_schema,
    },
    {
        "name": "show",
        "help": "display timeline metadata",
        "handler": timeline_show,
    },
    {
        "name": "upload",
        "help": "upload event data as timeline",
        "handler": timeline_upload,
    },
]

BRANCH_COMMANDS = [
    {
        "name": "list",
        "help": "list all remote branches",
        "handler": branch_list,
    },
    {
        "name": "delete",
        "help": "delete remote branch",
        "handler": branch_delete,
    },
    {
        "name": "show",
        "help": "display branch metadata",
        "handler": branch_show,
    },
    {
        "name": "select",
        "help": "update default_branch in local config",
        "handler": branch_select,
    },
]

COMMANDS = [
    {
        "name": "login",
        "help": "authenticate sumatra cli",
        "handler": login,
    },
    {
        "name": "plan",
        "help": "compare local changes to LIVE",
        "handler": plan,
    },
    {
        "name": "apply",
        "help": "publish local changes to LIVE",
        "handler": apply,
    },
    {
        "name": "push",
        "help": "save local scowl to named remote branch",
        "handler": push,
    },
    {
        "name": "branch",
        "help": "run `sumatra branch -h` for subcommands",
        "subcommands": BRANCH_COMMANDS,
    },
    {
        "name": "timeline",
        "help": "run `sumatra timeline -h` for subcommands",
        "subcommands": TIMELINE_COMMANDS,
    },
    {
        "name": "admin",
        "help": "run `sumatra admin -h` for subcommands",
        "subcommands": ADMIN_COMMANDS,
    },
    {"name": "version", "help": "show remote sumatra version", "handler": version},
    {"name": "tenant", "help": "show tenant name", "handler": tenant},
]


def main():
    parser = argparse.ArgumentParser(
        description="Sumatra command line interface.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="run in verbose mode"
    )

    parser.add_argument("--debug", action="store_true", help="run in debug mode")

    parser.add_argument("--instance", metavar="URL", help="sumatra instance url")

    cmd_parsers = parser.add_subparsers(
        title="commands", metavar="CMD", help="run `sumatra CMD -h` for command help"
    )

    for cmd in sorted(COMMANDS, key=lambda c: c["name"]):
        p = cmd_parsers.add_parser(
            cmd["name"],
            help=cmd["help"],
            description=None if cmd.get("subcommands") else cmd["help"],
        )
        if "handler" in cmd:
            p.set_defaults(handler=cmd["handler"])

        if cmd["name"] in ["plan", "apply", "push"]:
            p.add_argument("--scowl-dir", metavar="DIR", help="path to scowl files")

        if cmd["name"] in ["plan", "apply"]:
            p.add_argument(
                "--no-color", action="store_true", help="disable color in output"
            )

        if cmd["name"] == "apply":
            p.add_argument(
                "--auto-approve",
                action="store_true",
                help="automatically agree to all prompts",
            )

        if cmd["name"] == "push":
            p.add_argument("--branch", metavar="NAME", help="remote branch name")

        if cmd["name"] == "admin":
            p.add_argument(
                "--aws-profile",
                metavar="NAME",
                help="name of profile stored in aws credentials file",
            )

        if "subcommands" in cmd:
            subcmd_parsers = p.add_subparsers(
                title="commands",
                metavar="CMD",
                help=f"run `sumatra {cmd['name']} CMD -h for subcommand help",
            )
            for subcmd in sorted(cmd["subcommands"], key=lambda c: c["name"]):
                p = subcmd_parsers.add_parser(
                    subcmd["name"], help=subcmd["help"], description=subcmd["help"]
                )
                p.set_defaults(handler=subcmd["handler"])

                if cmd["name"] == "branch":
                    if subcmd["name"] in ["delete", "select", "show"]:
                        p.add_argument("branch", nargs="?", help="remote branch name")
                    if subcmd["name"] == "list":
                        p.add_argument(
                            "--show", action="store_true", help="display metadata"
                        )
                if cmd["name"] == "timeline":
                    if subcmd["name"] in ["delete", "show", "upload", "schema"]:
                        p.add_argument("timeline", help="remote timeline name")
                    if subcmd["name"] == "list":
                        p.add_argument(
                            "--show", action="store_true", help="display metadata"
                        )
                    if subcmd["name"] == "upload":
                        p.add_argument(
                            "--jsonl",
                            metavar="FILE",
                            help="file with event data in JSON Lines format",
                            required=True,
                        )
                if cmd["name"] == "admin":
                    if subcmd["name"] in ["current-tenant", "assign-tenant"]:
                        p.add_argument("user", help="cognito login name of user")
                    if subcmd["name"] == "assign-tenant":
                        p.add_argument("tenant", help="tenant name")

    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO

    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        stream=sys.stderr,
        format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
    )

    if hasattr(args, "handler"):
        try:
            args.handler(args)
        except Exception as e:
            if args.debug:
                raise e
            print(e)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
