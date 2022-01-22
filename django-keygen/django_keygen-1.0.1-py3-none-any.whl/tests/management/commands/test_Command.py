from argparse import ArgumentParser
from unittest import TestCase

from django_keygen import KeyGen
from django_keygen.management.commands.genkey import Command


class CliDocumentation(TestCase):
    """Test the command line parser help text is set"""

    def runTest(self) -> None:
        self.assertEqual(KeyGen.__doc__, Command.help)


class CliParsing(TestCase):
    """Test for the parsing of command line arguments"""

    def test_for_cli_arguments(self) -> None:
        """Test arguments are added to the command line parser"""

        command = Command()
        test_parser = ArgumentParser()
        command.add_arguments(test_parser)

        # Compare parser defaults against design specs
        parsed_args = test_parser.parse_args([])
        self.assertEqual(50, parsed_args.length)
        self.assertEqual(command.default_chars, parsed_args.chars)
        self.assertEqual(False, parsed_args.force)
