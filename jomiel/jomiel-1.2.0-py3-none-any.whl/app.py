#
# jomiel
#
# Copyright
#  2019-2020 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""
from jomiel_kore.app import App as KoreApp


class App(KoreApp):
    """Implements the application."""

    __slots__ = []

    def version_long_packages(self):
        """Return the required package (list) for --version-long."""
        return [
            "jomiel-messages",
            "configargparse",
            "jomiel-comm",
            "jomiel-kore",
            "ruamel.yaml",
            "validators",
            "protobuf",
            "requests",
            "pyzmq",
            "ujson",
        ]

    def run(self):
        """Application entry point; executes the app."""
        from configargparse import get_parser

        parser = get_parser()

        parser.add(
            "-p",
            "--plugin-list",
            help="Display the found plugins and exit",
            action="store_true",
        )

        def debug_group():
            """Add the debug options group."""
            grp = parser.add_argument_group("debug")

            grp.add(
                "-m",
                "--debug-minify-json",
                help="Minify JSON messages in the logger",
                action="store_true",
            )

            grp.add(
                "--debug-sensitive",
                help="""Log sensitive data, e.g. input URIs,
                    serialized messages""",
                action="store_true",
            )

        debug_group()

        def http_group():
            """Add the http option group."""
            grp = parser.add_argument_group("http")

            grp.add(
                "-F",
                "--http-allow-redirects",
                help="Follow HTTP redirections",
                action="store_true",
            )

            grp.add(
                "--http-user-agent",
                help="Identify as STRING to the HTTP server",
                metavar="STRING",
                default="Mozilla/5.0",
            )

            from jomiel_kore.opts import check_if_positive_integer

            grp.add(
                "--http-timeout",
                help="""Time in seconds allowed for the connection to
                  the HTTP server to take""",
                metavar="TIME",
                type=check_if_positive_integer,
                default=5,
            )

            grp.add(
                "--http-debug",
                help="Enable verbose HTTP output",
                action="store_true",
            )

        http_group()

        def broker_group():
            """Add the broker option group."""
            grp = parser.add_argument_group("broker")

            grp.add(
                "-I",
                "--broker-input-allow-any",
                help="Disable input URI validation",
                action="store_true",
            )

            grp.add(
                "-r",
                "--broker-router-endpoint",
                help="""Bind the frontend (router) socket to the
                    local endpoint""",
                default="tcp://*:5514",
                metavar="ADDR",
                env_var="BROKER_ROUTER_ENDPOINT",
            )

            grp.add(
                "-d",
                "--broker-dealer-endpoint",
                help="""Bind the backend (dealer) socket to the
                    local endpoint""",
                default="inproc://workers",
                metavar="ADDR",
                env_var="BROKER_DEALER_ENDPOINT",
            )

            def check_worker_thread_range(argval):
                """Checks that the worker thread value is within the
                range.

                """
                value = int(argval)
                if value < 1 or value > 64:
                    from argparse import ArgumentTypeError

                    raise ArgumentTypeError(
                        "%s is not within the range (1-64)" % argval,
                    )
                return value

            grp.add(
                "-w",
                "--broker-worker-threads",
                help="""Number of worker threads in the pool waiting
                    for client connections""",
                default="5",
                type=check_worker_thread_range,
                metavar="[1-64]",
            )

        broker_group()

        def curve_group():
            """Add the curve option group."""
            grp = parser.add_argument_group("curve")

            grp.add(
                "--curve-enable",
                help="Enable CURVE support",
                action="store_true",
                default=False,
            )

            grp.add(
                "--curve-public-key-dir",
                help="Directory that holds all public client key files",
                default=".curve/",
                metavar="DIR",
            )

            grp.add(
                "--curve-server-key-file",
                help="Secret CURVE key file for the server",
                default=".curve/server.key_secret",
                metavar="FILE",
            )

            grp.add(
                "--curve-domain",
                help="Configure CURVE authentication for a given domain",
                default="*",
                metavar="DOMAIN",
            )

            grp.add(
                "--curve-allow",
                help="Allow (whitelist IP addresses)",
                default="127.0.0.1",
                metavar="ADDR",
            )

        curve_group()
        super().parse_opts(parser)

        from jomiel.subsys import init

        init()


# vim: set ts=4 sw=4 tw=72 expandtab:
