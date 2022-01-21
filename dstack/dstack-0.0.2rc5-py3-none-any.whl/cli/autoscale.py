import sys
from argparse import Namespace

import colorama
from tabulate import tabulate

from dstack.cli.common import do_post, do_get, sensitive
from dstack.config import ConfigurationError


def enable_func(_: Namespace):
    try:
        data = {
            "paused": False
        }
        response = do_post("autoscale/config", data)
        if response.status_code == 200:
            print(f"{colorama.Fore.LIGHTBLACK_EX}OK{colorama.Fore.RESET}")
        else:
            response.raise_for_status()
    except ConfigurationError:
        sys.exit(f"Call 'dstack config' first")


def disable_func(_: Namespace):
    try:
        data = {
            "paused": True
        }
        response = do_post("autoscale/config", data)
        if response.status_code == 200:
            print(f"{colorama.Fore.LIGHTBLACK_EX}OK{colorama.Fore.RESET}")
        else:
            response.raise_for_status()
    except ConfigurationError:
        sys.exit(f"Call 'dstack config' first")


def allow_func(args: Namespace):
    if not args.spot and not args.on_demand:
        sys.exit("Either --spot or --on-demand argument is required")
    elif args.spot and args.on_demand:
        sys.exit("Both --spot and --on-demand arguments are not allowed")
    else:
        try:
            data = {
                "instance_type": args.instance_type,
                "maximum": args.max,
                "purchase_type": "spot" if args.spot else "on-demand"
            }
            response = do_post("autoscale/rules/set", data)
            if response.status_code == 200:
                print(f"{colorama.Fore.LIGHTBLACK_EX}OK{colorama.Fore.RESET}")
            if response.status_code == 400 and response.json().get("message") == "aws is not configured":
                sys.exit(f"Call 'dstack aws config' first")
            if response.status_code == 404 and response.json().get("message") == "instance type not found":
                sys.exit(f"Instance type is not supported")
            else:
                response.raise_for_status()
        except ConfigurationError:
            sys.exit(f"Call 'dstack config' first")


def remove_rules_func(args: Namespace):
    if not args.instance_type and not args.all:
        sys.exit("Either INSTANCE_TYPE or --all argument is required")
    elif args.instance_type and args.all:
        sys.exit("Both INSTANCE_TYPE and --all arguments are not allowed")
    else:
        if args.all:
            try:
                response = do_post("autoscale/rules/clear")
                if response.status_code == 200:
                    print(f"{colorama.Fore.LIGHTBLACK_EX}OK{colorama.Fore.RESET}")
                else:
                    response.raise_for_status()
            except ConfigurationError:
                sys.exit(f"Call 'dstack config' first")
        else:
            try:
                data = {
                    "instance_type": args.instance_type,
                    "maximum": 0,
                    "purchase_type": "spot"
                }
                response = do_post("autoscale/rules/set", data)
                if response.status_code == 200:
                    print(f"{colorama.Fore.LIGHTBLACK_EX}OK{colorama.Fore.RESET}")
                if response.status_code == 400 and response.json().get("message") == "aws is not configured":
                    sys.exit(f"Call 'dstack aws config' first")
                if response.status_code == 404 and response.json().get("message") == "instance type not found":
                    sys.exit(f"Instance type is not supported")
                else:
                    response.raise_for_status()
            except ConfigurationError:
                sys.exit(f"Call 'dstack config' first")


def info_func(_: Namespace):
    try:
        response = do_post("autoscale/info")
        if response.status_code == 200:
            response_json = response.json()
            print(f"{colorama.Fore.LIGHTMAGENTA_EX}Status{colorama.Fore.RESET}: " + (
                f"{colorama.Fore.LIGHTRED_EX}Disabled{colorama.Fore.RESET}" if response_json.get(
                    "paused") is True else f"{colorama.Fore.LIGHTGREEN_EX}Enabled{colorama.Fore.RESET}"))
        else:
            response.raise_for_status()
        response = do_get("autoscale/rules/list")
        if response.status_code == 200:
            table_headers = [
                f"{colorama.Fore.LIGHTMAGENTA_EX}INSTANCE TYPE{colorama.Fore.RESET}",
                f"{colorama.Fore.LIGHTMAGENTA_EX}PURCHASE TYPE{colorama.Fore.RESET}",
                f"{colorama.Fore.LIGHTMAGENTA_EX}MAXIMUM{colorama.Fore.RESET}"
            ]
            table_rows = []
            for rule in response.json()["rules"]:
                table_rows.append([
                    rule["instance_type"],
                    rule["purchase_type"].upper(),
                    rule["maximum"],
                ])
            print(tabulate(table_rows, headers=table_headers, tablefmt="plain"))
        else:
            response.raise_for_status()
    except ConfigurationError:
        sys.exit(f"Call 'dstack config' first")


def register_parsers(main_subparsers):
    parser = main_subparsers.add_parser("autoscale", help="Manage autoscale settings")

    subparsers = parser.add_subparsers()

    info_parser = subparsers.add_parser("info",
                                        help="Show if autoscaling is enabled, and list the allowed instance types")
    info_parser.set_defaults(func=info_func)

    disable_parser = subparsers.add_parser("disable", help="Disable autoscaling")
    disable_parser.set_defaults(func=disable_func)

    enable_parser = subparsers.add_parser("enable", help="Enable autoscaling")
    enable_parser.set_defaults(func=enable_func)

    allow_parser = subparsers.add_parser("allow", help="Allow using the given instance type for autoscaling")
    allow_parser.add_argument('instance_type', metavar='INSTANCE_TYPE', type=str)
    allow_parser.add_argument("--max", "-m", type=str, help="The maximum number of instances", required=True)
    allow_parser.add_argument("--spot", "-s", action="store_true", help="Spot instances",
                              default=False, required=False)
    allow_parser.add_argument("--on-demand", "-d", action="store_true", help="On-demand instances",
                              default=False, required=False)
    allow_parser.set_defaults(func=allow_func)

    remove_rules_parser = subparsers.add_parser("remove", help="Disallow using instances for autoscaling")
    remove_rules_parser.add_argument('instance_type', metavar='INSTANCE_TYPE', type=str, nargs='?')
    remove_rules_parser.add_argument("--all", "-a", action="store_true", help="Disallow all instances",
                                     default=False, required=False)
    remove_rules_parser.set_defaults(func=remove_rules_func)
