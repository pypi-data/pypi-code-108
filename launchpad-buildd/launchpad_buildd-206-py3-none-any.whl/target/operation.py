# Copyright 2017-2021 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

from collections import OrderedDict

from lpbuildd.target.backend import make_backend


class Operation:
    """An operation to perform on the target environment."""

    description = "An unidentified operation."
    buildd_path = "/build"

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument(
            "--backend", choices=["chroot", "lxd", "fake", "uncontained"],
            help="use this type of backend")
        parser.add_argument(
            "--series", metavar="SERIES", help="operate on series SERIES")
        parser.add_argument(
            "--arch", metavar="ARCH", help="operate on architecture ARCH")
        parser.add_argument(
            "build_id", metavar="ID", help="operate on build ID")

    def __init__(self, args, parser):
        self.args = args
        self.backend = make_backend(
            self.args.backend, self.args.build_id,
            series=self.args.series, arch=self.args.arch)

    def run_build_command(self, args, env=None, **kwargs):
        """Run a build command in the target.

        :param args: the command and arguments to run.
        :param env: dictionary of additional environment variables to set.
        :param kwargs: any other keyword arguments to pass to Backend.run.
        """
        full_env = OrderedDict()
        full_env["LANG"] = "C.UTF-8"
        full_env["SHELL"] = "/bin/sh"
        if env:
            full_env.update(env)
        cwd = kwargs.pop("cwd", self.buildd_path)
        return self.backend.run(args, cwd=cwd, env=full_env, **kwargs)

    def run(self):
        raise NotImplementedError
