# system imports
from unittest import TestCase
from click.testing import CliRunner

# lib imports
from pydragonfly.cli import cli


class TestBasic(TestCase):
    def setUp(self):
        self.runner: CliRunner = CliRunner()

    def test__cli_invoke(self):
        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage", result.output)
