# Copyright 2015-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import os

from six.moves.configparser import (
    NoOptionError,
    NoSectionError,
    )

from lpbuildd.debian import (
    DebianBuildManager,
    DebianBuildState,
    )
from lpbuildd.proxy import BuildManagerProxyMixin


RETCODE_SUCCESS = 0
RETCODE_FAILURE_INSTALL = 200
RETCODE_FAILURE_BUILD = 201


class SnapBuildState(DebianBuildState):
    BUILD_SNAP = "BUILD_SNAP"


class SnapBuildManager(BuildManagerProxyMixin, DebianBuildManager):
    """Build a snap."""

    backend_name = "lxd"
    initial_build_state = SnapBuildState.BUILD_SNAP

    @property
    def needs_sanitized_logs(self):
        return True

    def initiate(self, files, chroot, extra_args):
        """Initiate a build with a given set of files and chroot."""
        self.name = extra_args["name"]
        self.channels = extra_args.get("channels", {})
        self.build_request_id = extra_args.get("build_request_id")
        self.build_request_timestamp = extra_args.get(
            "build_request_timestamp")
        self.build_url = extra_args.get("build_url")
        self.branch = extra_args.get("branch")
        self.git_repository = extra_args.get("git_repository")
        self.git_path = extra_args.get("git_path")
        self.proxy_url = extra_args.get("proxy_url")
        self.revocation_endpoint = extra_args.get("revocation_endpoint")
        self.build_source_tarball = extra_args.get(
            "build_source_tarball", False)
        self.private = extra_args.get("private", False)
        self.proxy_service = None

        super(SnapBuildManager, self).initiate(files, chroot, extra_args)

    def doRunBuild(self):
        """Run the process to build the snap."""
        args = []
        for snap, channel in sorted(self.channels.items()):
            args.extend(["--channel", "%s=%s" % (snap, channel)])
        if self.build_request_id:
            args.extend(["--build-request-id", str(self.build_request_id)])
        if self.build_request_timestamp:
            args.extend(
                ["--build-request-timestamp", self.build_request_timestamp])
        if self.build_url:
            args.extend(["--build-url", self.build_url])
        args.extend(self.startProxy())
        if self.revocation_endpoint:
            args.extend(["--revocation-endpoint", self.revocation_endpoint])
        if self.branch is not None:
            args.extend(["--branch", self.branch])
        if self.git_repository is not None:
            args.extend(["--git-repository", self.git_repository])
        if self.git_path is not None:
            args.extend(["--git-path", self.git_path])
        if self.build_source_tarball:
            args.append("--build-source-tarball")
        if self.private:
            args.append("--private")
        try:
            snap_store_proxy_url = self._builder._config.get(
                "proxy", "snapstore")
            args.extend(["--snap-store-proxy-url", snap_store_proxy_url])
        except (NoSectionError, NoOptionError):
            pass
        args.append(self.name)
        self.runTargetSubProcess("buildsnap", *args)

    def iterate_BUILD_SNAP(self, retcode):
        """Finished building the snap."""
        self.stopProxy()
        self.revokeProxyToken()
        if retcode == RETCODE_SUCCESS:
            print("Returning build status: OK")
            return self.deferGatherResults()
        elif (retcode >= RETCODE_FAILURE_INSTALL and
              retcode <= RETCODE_FAILURE_BUILD):
            if not self.alreadyfailed:
                self._builder.buildFail()
                print("Returning build status: Build failed.")
            self.alreadyfailed = True
        else:
            if not self.alreadyfailed:
                self._builder.builderFail()
                print("Returning build status: Builder failed.")
            self.alreadyfailed = True
        self.doReapProcesses(self._state)

    def iterateReap_BUILD_SNAP(self, retcode):
        """Finished reaping after building the snap."""
        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()

    def gatherResults(self):
        """Gather the results of the build and add them to the file cache."""
        output_path = os.path.join("/build", self.name)
        if self.backend.path_exists(output_path):
            for entry in sorted(self.backend.listdir(output_path)):
                path = os.path.join(output_path, entry)
                if self.backend.islink(path):
                    continue
                if (entry.endswith(".snap") or entry.endswith(".manifest")
                        or entry.endswith(".dpkg.yaml")):
                    self.addWaitingFileFromBackend(path)
        if self.build_source_tarball:
            source_tarball_path = os.path.join(
                "/build", "%s.tar.gz" % self.name)
            if self.backend.path_exists(source_tarball_path):
                self.addWaitingFileFromBackend(source_tarball_path)
