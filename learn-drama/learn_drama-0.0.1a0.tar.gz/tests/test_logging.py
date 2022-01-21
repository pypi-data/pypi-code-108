import os
from click.testing import CliRunner
import warnings

from learn_drama import cli


class TestWarnings:
    def test_newline_in_input_text(self):
        runner = CliRunner()
        with warnings.catch_warnings(record=True) as w:
            path = os.path.join(
                os.path.dirname(__file__),
                "res/dramatesttext.txt"
                )
            options = ['--text_input', 'test', '-f', path, '--print_drama']
            runner.invoke(cli.main, options)
            string = "Text and file input given. "
            string += "Will only use file input."
            assert string in str(w[-1].message)
