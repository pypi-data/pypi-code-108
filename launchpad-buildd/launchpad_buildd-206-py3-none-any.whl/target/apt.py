# Copyright 2009-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import logging
import os
import subprocess
import sys
import tempfile
from textwrap import dedent
import time

from lpbuildd.target.operation import Operation


logger = logging.getLogger(__name__)


class OverrideSourcesList(Operation):

    description = "Override sources.list in the target environment."

    @classmethod
    def add_arguments(cls, parser):
        super(OverrideSourcesList, cls).add_arguments(parser)
        parser.add_argument(
            "--apt-proxy-url", metavar="URL", help="APT proxy URL")
        parser.add_argument(
            "archives", metavar="ARCHIVE", nargs="+",
            help="sources.list lines")

    def run(self):
        logger.info("Overriding sources.list in build-%s", self.args.build_id)
        with tempfile.NamedTemporaryFile(mode="w+") as sources_list:
            for archive in self.args.archives:
                print(archive, file=sources_list)
            sources_list.flush()
            os.fchmod(sources_list.fileno(), 0o644)
            self.backend.copy_in(sources_list.name, "/etc/apt/sources.list")
        with tempfile.NamedTemporaryFile(mode="w+") as apt_retries_conf:
            print('Acquire::Retries "3";', file=apt_retries_conf)
            apt_retries_conf.flush()
            os.fchmod(apt_retries_conf.fileno(), 0o644)
            self.backend.copy_in(
                apt_retries_conf.name, "/etc/apt/apt.conf.d/99retries")
        # Versions of APT that support phased updates do this automatically
        # if running in a chroot, but builds may be running in a LXD
        # container instead.
        with tempfile.NamedTemporaryFile(mode="w+") as apt_phasing_conf:
            print('APT::Get::Always-Include-Phased-Updates "true";',
                  file=apt_phasing_conf)
            apt_phasing_conf.flush()
            os.fchmod(apt_phasing_conf.fileno(), 0o644)
            self.backend.copy_in(
                apt_phasing_conf.name, "/etc/apt/apt.conf.d/99phasing")
        if self.args.apt_proxy_url is not None:
            with tempfile.NamedTemporaryFile(mode="w+") as apt_proxy_conf:
                print(
                    'Acquire::http::Proxy "{}";'.format(
                        self.args.apt_proxy_url),
                    file=apt_proxy_conf)
                apt_proxy_conf.flush()
                os.fchmod(apt_proxy_conf.fileno(), 0o644)
                self.backend.copy_in(
                    apt_proxy_conf.name, "/etc/apt/apt.conf.d/99proxy")
        for pocket in ("proposed", "backports"):
            with tempfile.NamedTemporaryFile(mode="w+") as preferences:
                print(dedent("""\
                    Package: *
                    Pin: release a=*-{}
                    Pin-Priority: 500
                    """).format(pocket), file=preferences, end="")
                preferences.flush()
                os.fchmod(preferences.fileno(), 0o644)
                self.backend.copy_in(
                    preferences.name,
                    "/etc/apt/preferences.d/{}.pref".format(pocket))
        return 0


class AddTrustedKeys(Operation):

    description = "Write out new trusted keys."

    def __init__(self, args, parser):
        super(AddTrustedKeys, self).__init__(args, parser)
        self.input_file = sys.stdin

    def run(self):
        """Add trusted keys from an input file."""
        logger.info("Adding trusted keys to build-%s", self.args.build_id)
        self.backend.run(["apt-key", "add", "-"], stdin=self.input_file)
        self.backend.run(["apt-key", "list"])
        return 0


class Update(Operation):

    description = "Update the target environment."

    def run(self):
        logger.info("Updating target for build %s", self.args.build_id)
        with open("/dev/null", "r") as devnull:
            env = {
                "LANG": "C",
                "DEBIAN_FRONTEND": "noninteractive",
                "TTY": "unknown",
                }
            apt_get = "/usr/bin/apt-get"
            update_args = [apt_get, "-uy", "update"]
            try:
                self.backend.run(update_args, env=env, stdin=devnull)
            except subprocess.CalledProcessError:
                logger.warning("Waiting 15 seconds and trying again ...")
                time.sleep(15)
                self.backend.run(update_args, env=env, stdin=devnull)
            upgrade_args = [
                apt_get, "-o", "DPkg::Options::=--force-confold", "-uy",
                "--purge", "dist-upgrade",
                ]
            self.backend.run(upgrade_args, env=env, stdin=devnull)
        return 0
