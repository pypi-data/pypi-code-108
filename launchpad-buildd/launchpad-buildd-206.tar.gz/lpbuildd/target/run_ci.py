# Copyright 2022 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import logging
import os

from lpbuildd.target.build_snap import SnapChannelsAction
from lpbuildd.target.operation import Operation
from lpbuildd.target.proxy import BuilderProxyOperationMixin
from lpbuildd.target.snapstore import SnapStoreOperationMixin
from lpbuildd.target.vcs import VCSOperationMixin
from lpbuildd.util import shell_escape


RETCODE_FAILURE_INSTALL = 200
RETCODE_FAILURE_BUILD = 201


logger = logging.getLogger(__name__)


class RunCIPrepare(BuilderProxyOperationMixin, VCSOperationMixin,
                   SnapStoreOperationMixin, Operation):

    description = "Prepare for running CI jobs."
    buildd_path = "/build/tree"

    @classmethod
    def add_arguments(cls, parser):
        super(RunCIPrepare, cls).add_arguments(parser)
        parser.add_argument(
            "--channel", action=SnapChannelsAction, metavar="SNAP=CHANNEL",
            dest="channels", default={}, help="install SNAP from CHANNEL")

    def install(self):
        logger.info("Running install phase...")
        deps = []
        if self.args.proxy_url:
            deps.extend(self.proxy_deps)
            self.install_git_proxy()
        if self.backend.supports_snapd:
            for dep in "snapd", "fuse", "squashfuse":
                if self.backend.is_package_available(dep):
                    deps.append(dep)
        deps.extend(self.vcs_deps)
        self.backend.run(["apt-get", "-y", "install"] + deps)
        if self.backend.supports_snapd:
            self.snap_store_set_proxy()
        for snap_name, channel in sorted(self.args.channels.items()):
            if snap_name not in ("lxd", "lpcraft"):
                self.backend.run(
                    ["snap", "install", "--channel=%s" % channel, snap_name])
        for snap_name, classic in (("lxd", False), ("lpcraft", True)):
            cmd = ["snap", "install"]
            if classic:
                cmd.append("--classic")
            if snap_name in self.args.channels:
                cmd.append("--channel=%s" % self.args.channels[snap_name])
            cmd.append(snap_name)
            self.backend.run(cmd)
        self.backend.run(["lxd", "init", "--auto"])

    def repo(self):
        """Collect VCS branch."""
        logger.info("Running repo phase...")
        env = self.build_proxy_environment(proxy_url=self.args.proxy_url)
        self.vcs_fetch("tree", cwd="/build", env=env)
        self.vcs_update_status(self.buildd_path)

    def run(self):
        try:
            self.install()
        except Exception:
            logger.exception("Install failed")
            return RETCODE_FAILURE_INSTALL
        try:
            self.repo()
        except Exception:
            logger.exception("VCS setup failed")
            return RETCODE_FAILURE_BUILD
        return 0


class RunCI(BuilderProxyOperationMixin, Operation):

    description = "Run a CI job."
    buildd_path = "/build/tree"

    @classmethod
    def add_arguments(cls, parser):
        super(RunCI, cls).add_arguments(parser)
        parser.add_argument("job_name", help="job name to run")
        parser.add_argument(
            "job_index", type=int, help="index within job name to run")

    def run_job(self):
        logger.info("Running job phase...")
        env = self.build_proxy_environment(proxy_url=self.args.proxy_url)
        job_id = "%s:%s" % (self.args.job_name, self.args.job_index)
        logger.info("Running %s" % job_id)
        output_path = os.path.join("/build", "output", job_id)
        self.backend.run(["mkdir", "-p", output_path])
        lpcraft_args = [
            "lpcraft", "-v", "run-one", "--output", output_path,
            self.args.job_name, str(self.args.job_index),
            ]
        tee_args = ["tee", "%s.log" % output_path]
        args = [
            "/bin/bash", "-o", "pipefail", "-c", "%s 2>&1 | %s" % (
                " ".join(shell_escape(arg) for arg in lpcraft_args),
                " ".join(shell_escape(arg) for arg in tee_args)),
            ]
        self.run_build_command(args, env=env)

    def run(self):
        try:
            self.run_job()
        except Exception:
            logger.exception("Job failed")
            return RETCODE_FAILURE_BUILD
        return 0
