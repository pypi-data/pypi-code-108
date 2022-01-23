# -*- coding: utf-8 -*-
"""Module for the version plugin
"""
# import basic stuff

# import own stuff
import tlsmate.plugin as plg
import tlsmate.version as version

# import other stuff


class VersionWorker(plg.Worker):
    """Worker to print the version of tlsmate.
    """

    name = "version"

    def run(self):
        print(version.__version__)


@plg.BaseCommand.extend
class SubcommandVersion(plg.Plugin):
    """CLI plugin to print the version of ``tlsmate``.
    """

    subcommand = plg.Args("version", help="prints the version of tlsmate")
    workers = [VersionWorker]
