# Copyright 2021 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import logging
import os

from lpbuildd.target.backend import check_path_escape
from lpbuildd.target.build_snap import SnapChannelsAction
from lpbuildd.target.operation import Operation
from lpbuildd.target.proxy import BuilderProxyOperationMixin
from lpbuildd.target.snapstore import SnapStoreOperationMixin
from lpbuildd.target.vcs import VCSOperationMixin


RETCODE_FAILURE_INSTALL = 200
RETCODE_FAILURE_BUILD = 201


logger = logging.getLogger(__name__)


class BuildCharm(BuilderProxyOperationMixin, VCSOperationMixin,
                 SnapStoreOperationMixin, Operation):

    description = "Build a charm."

    core_snap_names = ["core", "core16", "core18", "core20", "core22"]

    @classmethod
    def add_arguments(cls, parser):
        super(BuildCharm, cls).add_arguments(parser)
        parser.add_argument(
            "--channel", action=SnapChannelsAction, metavar="SNAP=CHANNEL",
            dest="channels", default={}, help=(
                "install SNAP from CHANNEL "
                "(supported snaps: {}, charmcraft)".format(
                    ", ".join(cls.core_snap_names))))
        parser.add_argument(
            "--build-path", default=".",
            help="location of charm to build.")
        parser.add_argument("name", help="name of charm to build")

    def __init__(self, args, parser):
        super(BuildCharm, self).__init__(args, parser)
        self.buildd_path = os.path.join("/home/buildd", self.args.name)

    def install(self):
        logger.info("Running install phase")
        deps = []
        if self.args.proxy_url:
            deps.extend(self.proxy_deps)
            self.install_git_proxy()
        if self.backend.supports_snapd:
            # udev is installed explicitly to work around
            # https://bugs.launchpad.net/snapd/+bug/1731519.
            for dep in "snapd", "fuse", "squashfuse", "udev":
                if self.backend.is_package_available(dep):
                    deps.append(dep)
        deps.extend(self.vcs_deps)
        # See charmcraft.provider.CharmcraftBuilddBaseConfiguration.setup.
        deps.extend([
            "python3-pip",
            "python3-setuptools",
            ])
        self.backend.run(["apt-get", "-y", "install"] + deps)
        if self.backend.supports_snapd:
            self.snap_store_set_proxy()
        for snap_name in self.core_snap_names:
            if snap_name in self.args.channels:
                self.backend.run(
                    ["snap", "install",
                     "--channel=%s" % self.args.channels[snap_name],
                     snap_name])
        if "charmcraft" in self.args.channels:
            self.backend.run(
                ["snap", "install", "--classic",
                 "--channel=%s" % self.args.channels["charmcraft"],
                 "charmcraft"])
        else:
            self.backend.run(["snap", "install", "--classic", "charmcraft"])
        # The charmcraft snap can't see /build, so we have to do our work under
        # /home/buildd instead.  Make sure it exists.
        self.backend.run(["mkdir", "-p", "/home/buildd"])

    def repo(self):
        """Collect git or bzr branch."""
        logger.info("Running repo phase...")
        env = self.build_proxy_environment(proxy_url=self.args.proxy_url)
        self.vcs_fetch(self.args.name, cwd="/home/buildd", env=env)
        self.vcs_update_status(self.buildd_path)

    def build(self):
        logger.info("Running build phase...")
        build_context_path = os.path.join(
            "/home/buildd",
            self.args.name,
            self.args.build_path)
        check_path_escape(self.buildd_path, build_context_path)
        env = self.build_proxy_environment(proxy_url=self.args.proxy_url)
        args = ["charmcraft", "pack", "-v", "--destructive-mode"]
        self.run_build_command(args, env=env, cwd=build_context_path)

    def run(self):
        try:
            self.install()
        except Exception:
            logger.exception('Install failed')
            return RETCODE_FAILURE_INSTALL
        try:
            self.repo()
            self.build()
        except Exception:
            logger.exception('Build failed')
            return RETCODE_FAILURE_BUILD
        return 0
