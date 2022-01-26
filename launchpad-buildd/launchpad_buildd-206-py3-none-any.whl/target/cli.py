# Copyright 2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

from argparse import ArgumentParser
import logging
import sys

from lpbuildd.target.apt import (
    AddTrustedKeys,
    OverrideSourcesList,
    Update,
    )
from lpbuildd.target.build_charm import BuildCharm
from lpbuildd.target.build_oci import BuildOCI
from lpbuildd.target.build_livefs import BuildLiveFS
from lpbuildd.target.build_snap import BuildSnap
from lpbuildd.target.generate_translation_templates import (
    GenerateTranslationTemplates,
    )
from lpbuildd.target.lifecycle import (
    Create,
    KillProcesses,
    Remove,
    Start,
    Stop,
    )
from lpbuildd.target.run_ci import (
    RunCI,
    RunCIPrepare,
    )


def configure_logging():
    class StdoutFilter(logging.Filter):
        def filter(self, record):
            return record.levelno < logging.ERROR

    class StderrFilter(logging.Filter):
        def filter(self, record):
            return record.levelno >= logging.ERROR

    logger = logging.getLogger()
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.addFilter(StdoutFilter())
    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.addFilter(StderrFilter())
    for handler in (stdout_handler, stderr_handler):
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


operations = {
    "add-trusted-keys": AddTrustedKeys,
    "build-oci": BuildOCI,
    "build-charm": BuildCharm,
    "buildlivefs": BuildLiveFS,
    "buildsnap": BuildSnap,
    "generate-translation-templates": GenerateTranslationTemplates,
    "override-sources-list": OverrideSourcesList,
    "mount-chroot": Start,
    "remove-build": Remove,
    "run-ci": RunCI,
    "run-ci-prepare": RunCIPrepare,
    "scan-for-processes": KillProcesses,
    "umount-chroot": Stop,
    "unpack-chroot": Create,
    "update-debian-chroot": Update,
    }


def parse_args(args=None):
    parser = ArgumentParser(description="Run an operation in the target.")
    subparsers = parser.add_subparsers(metavar="OPERATION")
    for name, factory in sorted(operations.items()):
        subparser = subparsers.add_parser(
            name, description=factory.description, help=factory.description)
        factory.add_arguments(subparser)
        subparser.set_defaults(operation_factory=factory)
    args = parser.parse_args(args=args)
    args.operation = args.operation_factory(args, parser)
    return args
