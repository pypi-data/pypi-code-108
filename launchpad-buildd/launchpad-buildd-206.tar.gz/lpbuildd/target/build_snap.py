# Copyright 2015-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import argparse
import json
import logging
import os.path
import tempfile
from textwrap import dedent

from six.moves.urllib.parse import urlparse

from lpbuildd.target.operation import Operation
from lpbuildd.target.proxy import BuilderProxyOperationMixin
from lpbuildd.target.snapstore import SnapStoreOperationMixin
from lpbuildd.target.vcs import VCSOperationMixin


RETCODE_FAILURE_INSTALL = 200
RETCODE_FAILURE_BUILD = 201


logger = logging.getLogger(__name__)


class SnapChannelsAction(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(SnapChannelsAction, self).__init__(
            option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if "=" not in values:
            raise argparse.ArgumentError(
                self, "'{}' is not of the form 'snap=channel'".format(values))
        snap, channel = values.split("=", 1)
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, {})
        getattr(namespace, self.dest)[snap] = channel


class BuildSnap(BuilderProxyOperationMixin, VCSOperationMixin,
                SnapStoreOperationMixin, Operation):

    description = "Build a snap."

    core_snap_names = ["core", "core16", "core18", "core20", "core22"]

    @classmethod
    def add_arguments(cls, parser):
        super(BuildSnap, cls).add_arguments(parser)
        parser.add_argument(
            "--channel", action=SnapChannelsAction, metavar="SNAP=CHANNEL",
            dest="channels", default={}, help=(
                "install SNAP from CHANNEL "
                "(supported snaps: {}, snapcraft)".format(
                    ", ".join(cls.core_snap_names))))
        parser.add_argument(
            "--build-request-id",
            help="ID of the request triggering this build on Launchpad")
        parser.add_argument(
            "--build-request-timestamp",
            help="RFC3339 timestamp of the Launchpad build request")
        parser.add_argument(
            "--build-url", help="URL of this build on Launchpad")
        parser.add_argument(
            "--build-source-tarball", default=False, action="store_true",
            help=(
                "build a tarball containing all source code, including "
                "external dependencies"))
        parser.add_argument(
            "--private", default=False, action="store_true",
            help="build a private snap")
        parser.add_argument("name", help="name of snap to build")

    def install_svn_servers(self):
        proxy = urlparse(self.args.proxy_url)
        svn_servers = dedent("""\
            [global]
            http-proxy-host = {host}
            http-proxy-port = {port}
            """.format(host=proxy.hostname, port=proxy.port))
        # We should never end up with an authenticated proxy here since
        # lpbuildd.snap deals with it, but it's almost as easy to just
        # handle it as to assert that we don't need to.
        if proxy.username:
            svn_servers += "http-proxy-username = {}\n".format(proxy.username)
        if proxy.password:
            svn_servers += "http-proxy-password = {}\n".format(proxy.password)
        with tempfile.NamedTemporaryFile(mode="w+") as svn_servers_file:
            svn_servers_file.write(svn_servers)
            svn_servers_file.flush()
            os.fchmod(svn_servers_file.fileno(), 0o644)
            self.backend.run(["mkdir", "-p", "/root/.subversion"])
            self.backend.copy_in(
                svn_servers_file.name, "/root/.subversion/servers")

    def install(self):
        logger.info("Running install phase...")
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
        if "snapcraft" in self.args.channels:
            # snapcraft requires sudo in lots of places, but can't depend on
            # it when installed as a snap.
            deps.append("sudo")
        else:
            deps.append("snapcraft")
        self.backend.run(["apt-get", "-y", "install"] + deps)
        if self.backend.supports_snapd:
            self.snap_store_set_proxy()
        for snap_name in self.core_snap_names:
            if snap_name in self.args.channels:
                self.backend.run(
                    ["snap", "install",
                     "--channel=%s" % self.args.channels[snap_name],
                     snap_name])
        if "snapcraft" in self.args.channels:
            self.backend.run(
                ["snap", "install", "--classic",
                 "--channel=%s" % self.args.channels["snapcraft"],
                 "snapcraft"])
        if self.args.proxy_url:
            self.install_svn_servers()

    def repo(self):
        """Collect git or bzr branch."""
        logger.info("Running repo phase...")
        env = self.build_proxy_environment(proxy_url=self.args.proxy_url)
        self.vcs_fetch(self.args.name, cwd="/build", env=env)
        self.vcs_update_status(os.path.join("/build", self.args.name))

    @property
    def image_info(self):
        data = {}
        if self.args.build_request_id is not None:
            data["build-request-id"] = 'lp-{}'.format(
                self.args.build_request_id)
        if self.args.build_request_timestamp is not None:
            data["build-request-timestamp"] = self.args.build_request_timestamp
        if self.args.build_url is not None:
            data["build_url"] = self.args.build_url
        return json.dumps(data, sort_keys=True)

    def pull(self):
        """Run pull phase."""
        logger.info("Running pull phase...")
        env = self.build_proxy_environment(proxy_url=self.args.proxy_url)
        env["SNAPCRAFT_LOCAL_SOURCES"] = "1"
        env["SNAPCRAFT_SETUP_CORE"] = "1"
        if not self.args.private:
            env["SNAPCRAFT_BUILD_INFO"] = "1"
        env["SNAPCRAFT_IMAGE_INFO"] = self.image_info
        env["SNAPCRAFT_BUILD_ENVIRONMENT"] = "host"
        self.run_build_command(
            ["snapcraft", "pull"],
            cwd=os.path.join("/build", self.args.name),
            env=env)
        if self.args.build_source_tarball:
            self.run_build_command(
                ["tar", "-czf", "%s.tar.gz" % self.args.name,
                 "--format=gnu", "--sort=name", "--exclude-vcs",
                 "--numeric-owner", "--owner=0", "--group=0",
                 self.args.name],
                cwd="/build")

    def build(self):
        """Run all build, stage and snap phases."""
        logger.info("Running build phase...")
        env = self.build_proxy_environment(proxy_url=self.args.proxy_url)
        if not self.args.private:
            env["SNAPCRAFT_BUILD_INFO"] = "1"
        env["SNAPCRAFT_IMAGE_INFO"] = self.image_info
        env["SNAPCRAFT_BUILD_ENVIRONMENT"] = "host"
        self.run_build_command(
            ["snapcraft"],
            cwd=os.path.join("/build", self.args.name),
            env=env)

    def run(self):
        try:
            self.install()
        except Exception:
            logger.exception('Install failed')
            return RETCODE_FAILURE_INSTALL
        try:
            self.repo()
            self.pull()
            self.build()
        except Exception:
            logger.exception('Build failed')
            return RETCODE_FAILURE_BUILD
        return 0
