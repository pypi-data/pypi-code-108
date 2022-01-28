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
        return ["pyzmq"]

    def run(self):
        """Application entry point; executes the app."""
        from configargparse import get_parser

        parser = get_parser()

        parser.add(
            "filename",
            help="""Name for the authentication key-pair files for use
                    with jomiel""",
            nargs="*",
        )

        opts = super().parse_opts(parser)

        if len(opts.filename) == 0:
            from sys import stderr
            from jomiel_kore.app import exit_error

            print(
                "error: the following arguments are required: filename",
                file=stderr,
            )

            exit_error()

        def generate_keypair(filename):
            """Generate a new key-pair."""

            from os.path import abspath, dirname, basename

            fpath = abspath(filename)
            basedir = dirname(fpath)

            from zmq.auth import create_certificates

            try:
                name = basename(fpath)
                (
                    public_key_file,
                    secret_key_file,
                ) = create_certificates(basedir, name)
            except OSError as message:
                print("error: %s" % message)
                from jomiel_kore.app import exit_error

                exit_error()

            from os import chmod

            chmod(public_key_file, 0o644)
            chmod(secret_key_file, 0o400)

            print(
                "Created:\n  %s\n  %s"
                % (public_key_file, secret_key_file),
            )

        for filename in opts.filename:
            generate_keypair(filename)


# vim: set ts=4 sw=4 tw=72 expandtab:
