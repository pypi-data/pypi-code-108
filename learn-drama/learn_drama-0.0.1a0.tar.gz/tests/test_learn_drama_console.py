
"""Tests for `learn_drama` package."""

import pytest
import os

from click.testing import CliRunner
from main import main
from learn_drama import cli


class TestCommandLineInput:
    """Test the CLI."""
    def test_naked_command_line_interface(self):
        # ToDo: Understand why the SystemExit raised here, not down below.
        runner = CliRunner()
        with pytest.raises(SystemExit):
            result = runner.invoke(main())
            assert result.exit_code == 0
            assert 'learn_drama.main' in result.output

    def test_command_line_interface_help(self):
        runner = CliRunner()
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--text_input TEXT' in help_result.output
        assert 'Type in some text.' in help_result.output
        assert '--print_input' in help_result.output
        assert 'Prints text input on console.' in help_result.output
        assert '--print_drama' in help_result.output
        assert 'Prints formated drama text on console.' in help_result.output
        assert '--help' in help_result.output
        assert 'Show this message and exit.' in help_result.output

    def test_command_line_interface_text_input_not_printed(self):
        runner = CliRunner()
        string = 'command line input parameter test'
        text_input_result = runner.invoke(cli.main, ['--text_input', string])
        assert text_input_result.exit_code == 0
        assert string not in text_input_result.output

    def test_command_line_interface_text_input(self):
        runner = CliRunner()
        string = 'command line input parameter test'
        options = ['--text_input', string, '--print_input']
        result = runner.invoke(cli.main, options)
        assert result.exit_code == 0
        assert string in result.output

    def test_print_out_with_verse_numbers(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, [
            '--text_input',
            'verse1\nThis is verse2.',
            '--print_drama'
            ])
        assert result.exit_code == 0
        assert "     1 verse1" in result.output
        assert "     2 Tis is verse2. This should not be found"\
               not in result.output
        assert "     2 This is verse2." in result.output

    def test_print_out_with_verse_numbers_one_line_check(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, [
            '--text_input',
            'verse1\nThis is verse2.',
            '--print_drama'
            ])
        assert result.exit_code == 0
        assert "     1 verse1\n     2 This is verse2." in result.output

    def test_print_drama_longer_verse(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, [
            '--text_input',
            'verse1\nThis is verse2.\nThis is verse3$',
            '--print_drama'
            ])
        assert result.exit_code == 0
        string = "     1 verse1\n"
        string += "     2 This is verse2.\n"
        string += "     3 This is verse3$"
        assert string in result.output

    def test_formatted_text(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, [
            '--text_input',
            'verse1\nverse2\nverse3',
            '--print_drama'
            ])
        assert result.exit_code == 0
        assert "     1 verse1\n     2 verse2\n     3 verse3" in result.output


class TestConsoleTextFromFile:
    def test_print_formatted_text_from_file(self):
        runner = CliRunner()
        file_path = os.path.join(
                os.path.dirname(__file__),
                "res/dramatesttext.txt"
                )
        result = runner.invoke(cli.main, ['-f', file_path, '--print_drama'])
        assert result.exit_code == 0
        string = "     1 Wieder sehe ich schwankende Gestalten,\n"
        string += "     2 oder auch nicht."
        assert string in result.output
