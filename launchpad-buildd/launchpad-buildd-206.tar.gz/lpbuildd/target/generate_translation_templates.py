# Copyright 2010-2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import logging
import os.path

from lpbuildd.pottery import intltool
from lpbuildd.target.operation import Operation
from lpbuildd.target.vcs import VCSOperationMixin


logger = logging.getLogger(__name__)


RETCODE_FAILURE_INSTALL = 200
RETCODE_FAILURE_BUILD = 201


class GenerateTranslationTemplates(VCSOperationMixin, Operation):
    """Script to generate translation templates from a branch."""

    description = "Generate templates for a branch."

    @classmethod
    def add_arguments(cls, parser):
        super(GenerateTranslationTemplates, cls).add_arguments(parser)
        parser.add_argument(
            "result_name",
            help="the name of the result tarball; should end in '.tar.gz'")

    def __init__(self, args, parser):
        super(GenerateTranslationTemplates, self).__init__(args, parser)
        self.work_dir = os.environ["HOME"]
        self.branch_dir = os.path.join(self.work_dir, "source-tree")

    def install(self):
        logger.info("Installing dependencies...")
        deps = ["intltool"]
        deps.extend(self.vcs_deps)
        self.backend.run(["apt-get", "-y", "install"] + deps)

    def fetch(self, quiet=False):
        logger.info("Fetching %s...", self.vcs_description)
        self.vcs_fetch(
            os.path.basename(self.branch_dir), cwd=self.work_dir, quiet=quiet)

    def _makeTarball(self, files):
        """Put the given files into a tarball in the working directory."""
        tarname = os.path.join(self.work_dir, self.args.result_name)
        logger.info("Making tarball with templates in %s..." % tarname)
        cmd = ["tar", "-C", self.branch_dir, "-czf", tarname]
        files = [name for name in files if not name.endswith('/')]
        for path in files:
            full_path = os.path.join(self.branch_dir, path)
            logger.info("Adding template %s..." % full_path)
            cmd.append(path)
        self.backend.run(cmd)
        logger.info("Tarball generated.")

    def generate(self):
        logger.info("Generating templates...")
        pots = intltool.generate_pots(self.backend, self.branch_dir)
        logger.info("Generated %d templates." % len(pots))
        if len(pots) > 0:
            self._makeTarball(pots)

    def run(self):
        """Do It.  Generate templates."""
        try:
            self.install()
        except Exception:
            logger.exception("Install failed")
            return RETCODE_FAILURE_INSTALL
        try:
            self.fetch()
            self.generate()
        except Exception:
            logger.exception("Build failed")
            return RETCODE_FAILURE_BUILD
        return 0
