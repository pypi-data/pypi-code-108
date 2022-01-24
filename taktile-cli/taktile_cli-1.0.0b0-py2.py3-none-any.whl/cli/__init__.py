import click
import colorama  # type: ignore
from click._compat import get_text_stderr  # type: ignore

import tktl.cli.login  # noqa: F401


def show(self, file=None):
    if file is None:
        file = get_text_stderr()
    color = None
    hint = ""
    if self.cmd is not None and self.cmd.get_help_option(self.ctx) is not None:
        hint = 'Try "%s %s" for help.\n' % (
            self.ctx.command_path,
            self.ctx.help_option_names[0],
        )
    if self.ctx is not None:
        color = self.ctx.color
        click.echo(self.ctx.get_usage() + "\n%s" % hint, file=file, color=color)
    msg = (
        colorama.Fore.RED
        + "Error: %s" % self.format_message()
        + colorama.Style.RESET_ALL
    )
    click.echo(msg, file=file, color=color)


# not-very-elegant way to color click's error messages
click.exceptions.UsageError.show = show  # type: ignore
