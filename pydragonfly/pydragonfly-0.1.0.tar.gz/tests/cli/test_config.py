# system imports
from unittest import TestCase
from click.testing import CliRunner

# lib imports
import click_creds
from pydragonfly.cli import cli


class TestConfig(TestCase):
    def setUp(self):
        self.runner: CliRunner = CliRunner()

    def test_config_help(self):
        result = self.runner.invoke(cli, ["config", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage", result.output)

    def test_config_get(self):
        result = self.runner.invoke(cli, ["config", "get"])
        self.assertEqual(result.exit_code, 0)

    def test_config_set_and_get(self):
        # step 1
        mapp = {
            "certificate": __file__,
            "api_key": "hax0r",
            "instance_url": "http://localhost",
        }
        result = self.runner.invoke(
            cli,
            [
                "config",
                "set",
                "-c",
                mapp["certificate"],
                "-k",
                mapp["api_key"],
                "-u",
                mapp["instance_url"],
                "-v",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "Successfully saved config variables!",
            result.output.strip("\n"),
        )
        # step 2
        obj = click_creds.NetrcStore("pydragonfly")
        self.assertDictEqual(mapp, obj.host_with_mapping)
