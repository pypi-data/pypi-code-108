# Copyright 2017-2021 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

from argparse import ArgumentParser

from testtools import TestCase
from testtools.matchers import MatchesListwise

from lpbuildd.target.operation import Operation
from lpbuildd.target.tests.matchers import RanBuildCommand


class TestOperation(TestCase):

    def test_run_build_command_no_env(self):
        parser = ArgumentParser()
        Operation.add_arguments(parser)
        args = ["--backend=fake", "--series=xenial", "--arch=amd64", "1"]
        operation = Operation(parser.parse_args(args=args), parser)
        operation.run_build_command(["echo", "hello world"])
        self.assertThat(operation.backend.run.calls, MatchesListwise([
            RanBuildCommand(["echo", "hello world"]),
            ]))

    def test_run_build_command_env(self):
        parser = ArgumentParser()
        Operation.add_arguments(parser)
        args = ["--backend=fake", "--series=xenial", "--arch=amd64", "1"]
        operation = Operation(parser.parse_args(args=args), parser)
        operation.run_build_command(
            ["echo", "hello world"], env={"FOO": "bar baz"})
        self.assertThat(operation.backend.run.calls, MatchesListwise([
            RanBuildCommand(["echo", "hello world"], FOO="bar baz"),
            ]))
