import argparse
import logging

from shyft.dashboard.base.app import start_bokeh_apps
from shyft.dashboard.entry_points.entry_points import parse_entry_points_for_apps
from shyft.dashboard.util.find_free_port import find_free_port


def main(input_args=None):
    """Entry point to run all apps defined under `shyft.dashboard_apps` entry-point"""
    all_apps = parse_entry_points_for_apps()

    entry_points = [a[0] for a in all_apps]
    double_defined_entry_points = [e for e in entry_points if entry_points.count(e) > 1]
    max_len = max([len(i) for i in entry_points])
    if double_defined_entry_points:
        max_len += 16
    app_names = []

    available_apps = {}
    for entry_point, app in all_apps:
        entry_point_name = entry_point
        app_key = entry_point
        if entry_point in double_defined_entry_points:
            entry_point_name = f'{entry_point_name} (use module name)'
            app_key = app.__module__
        app_names.append(f'{entry_point_name:<{max_len}}: {app.__module__}')
        available_apps[app_key] = app

    app_names = '\n        '.join(app_names)
    h = f"""Select bokeh-app defined under `shyft.dashboard_apps` entry-points

    All available apps are:\n\n
        {app_names}
"""

    # add user name as in old bat scripts from sih
    default_port = find_free_port()

    parser = argparse.ArgumentParser(prog="Start Bokeh Apps",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=h, add_help=True)
    parser.add_argument("--no-show", action="store_false", default=True,
                        help="Don't show bokeh apps in default browser")
    parser.add_argument("-a", "--apps", nargs="+",
                        dest='apps', help=f"Run one or more specific app(s)")
    parser.add_argument("-p", "--port", type=int, default=default_port,
                        help="Port to run bokeh server [will crash if it is not free]")
    parser.add_argument('-d', '--debug', help="Print lots of debugging statements",
                        action="store_const", dest="log_level", const=logging.DEBUG,
                        default=logging.ERROR)
    parser.add_argument('-v', '--verbose', help="Be verbose",
                        action="store_const", dest="log_level", const=logging.INFO)
    parser.add_argument("-l", "--logger_box", action="store_true", default=False,
                        help="Enable logger box in application")
    parser.add_argument("--async_off", action="store_true", default=False,
                        help="Disable async data loading")
    parser.add_argument("--async-max-worker", type=int, default=12,
                        help="Number of worker for async data loading")

    args = parser.parse_args(input_args)

    if not args.apps or args.apps is None:
        parser.print_help()
        print(f"No apps defined, use -a to define apps listed above!")
        return

    apps = [available_apps[k] for k in args.apps if k in available_apps]
    if not apps:
        parser.print_help()
        print(f"'-a : {', '.join(args.apps)}' unknown apps defined! use apps listed above!")
        return

    start_bokeh_apps(apps=apps,
                     show=args.no_show,
                     port=args.port,
                     log_level=args.log_level,
                     show_logger_box=args.logger_box,
                     async_on=not args.async_off,
                     async_max_worker=args.async_max_worker)
