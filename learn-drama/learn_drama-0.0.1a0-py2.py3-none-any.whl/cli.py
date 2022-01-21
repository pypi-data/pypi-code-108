"""Console script for learn_drama."""
import sys
import click
from learn_drama import DramaLearner
from learn_drama.text_helper import check_line_break_string


@click.command()
@click.option("--text_input", help="Type in some text.", default="No text")
@click.option("--print_input/--no-print_input",
              help="Prints text input on console.", default=False)
@click.option("--print_drama/--no-print_drama",
              help="Prints formated drama text on console.",
              default=False)
@click.option("-f", help="Get drama text from file.", default="")
def main(text_input, print_input, print_drama, f):
    """Console script for learn_drama:
        Checks input, can print to console: help, raw input, and
        prints input in a format with verse numbers if specified.

    Args:
      text_input (str): Text as input for processing e.g. for formatted output.
      print_input (bool): Bool, print raw input to console. Default: False
      print_drama (bool): Bool, print formattet input to console.
      f (str): Filename as string.

    Returns:
      None
        """
    text_input = check_line_break_string(text_input)
    teacher = DramaLearner(text_input, f)
    if print_input:
        click.echo("-- Raw text: --")
        click.echo(teacher.raw_text)
        if teacher.raw_text == "":
            click.echo("No input given")
    if print_drama:
        click.echo("-- Formatted text --")
        click.echo(teacher.formatted_text())
    return 0


if __name__ == '__main__':
    sys.exit(main())
