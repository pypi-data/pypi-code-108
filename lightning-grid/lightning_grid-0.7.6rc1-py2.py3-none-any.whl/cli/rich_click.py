import collections
import contextlib
from enum import Enum
from typing import Mapping, Optional, Type, TypeVar

import click
from rich import box
from rich.console import Console, RenderableType
try:
    from rich.console import RenderGroup
except ImportError:
    # this was renamed to rich.console.Group as of Rich 11.0
    # see https://github.com/Textualize/rich/releases/tag/v11.0.0 for more details
    from rich.console import Group as RenderGroup
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from grid.cli.utilities import is_latest_version
from grid.metadata import __package_name__
import grid.sdk.env as env


class GridColors(str, Enum):
    """These are the grid brand colors made slightly darker so they work with both black and white backgrounds."""

    GREEN = "#47ff6f"  # Original: #78FF96
    PERIWINKLE = "#70a5ff"  # Original: #A4C6FF
    ORANGE = "#e66700"  # Original: #FF7300
    TEAL = "#14857e"  # Original: #18A096
    PURPLE = "#5233ff"  # Original: #6950FF


GRID_THEME = Theme(
    {
        "title": "bold",
        "header": "bold",
        "warning": "bold red",
        "note": f"bold {GridColors.ORANGE}",
        "command_path": f"bold {GridColors.PURPLE}",
        "argument": GridColors.TEAL,
        "option": GridColors.ORANGE,
        "command": GridColors.TEAL,
    },
    inherit=False,
)


def grid_console():
    """Creates a ``rich.console.Console`` equipped with the GRID_THEME."""
    return Console(theme=GRID_THEME, force_terminal=True)


@contextlib.contextmanager
def console_from_formatter(formatter):
    """Context manager which substitutes a formatter for a ``grid_console`` and writes the output back to the
    formatter.
    """
    console = grid_console()
    with console.capture() as capture:
        yield console
    formatter.write(capture.get())


def render(renderable: RenderableType):
    """Renders a ``rich.RenderableType`` to a string and returns it."""
    console = grid_console()
    with console.capture() as capture:
        console.print(renderable)
    return capture.get()


def render_warning(renderable: RenderableType):
    """Utility method to render a ``rich.RenderableType`` alongside a 'Warning' header."""
    return render(RenderGroup(
        '[warning]Warning[/warning]:',
        pad(renderable),
    ))


def render_error(renderable: RenderableType):
    """Utility method to render a ``rich.RenderableType`` alongside an 'Error' header."""
    return render(RenderGroup(
        '[error]Error[/error]:',
        pad(renderable),
    ))


def render_note(renderable: RenderableType):
    """Utility method to render a ``rich.RenderableType`` alongside a 'Note' header."""
    return render(RenderGroup(
        '[note]Note[/note]:',
        pad(renderable),
    ))


def pad(renderable: RenderableType):
    """Pads the given ``rich.RenderableType`` to the standard padding used in the Grid CLI."""
    padding = (0, 4, 1, 4)
    if isinstance(renderable, Table):
        padding = (0, 4, 1, 2)
    return Padding(renderable, padding)


COMMAND_TYPE = TypeVar("COMMAND_TYPE", bound=click.Command)


def make_rich_command(cls: Type[COMMAND_TYPE]) -> Type[COMMAND_TYPE]:
    """Creates and returns a subclass of the given ``click.Command`` type which renders help text with rich.

    Parameters
    ----------
    cls
        The ``click.Command`` subclass to enhance with rich.
    """
    class RichCommand(cls):
        def __init__(self, name, **kwargs):
            context_settings = kwargs.pop("context_settings", {})
            context_settings.update(
                {  # Let rich handle line wrapping
                    'terminal_width': 10000,
                    'max_content_width': 10000,
                }
            )
            super().__init__(name, context_settings=context_settings, **kwargs)

        def get_max_lhs_column_width(self, ctx) -> int:
            all_lens = []
            all_lens += [len(argument) for argument in self.get_arguments(ctx).keys()]
            all_lens += [len(option) for option in self.get_options(ctx).keys()]
            return max(all_lens)

        def format_help(self, ctx, formatter):
            self.format_help_text(ctx, formatter)
            self.format_usage(ctx, formatter)
            self.format_options(ctx, formatter)
            self.format_arguments(ctx, formatter)
            self.format_epilog(ctx, formatter)

        def format_help_text(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                if self.help is not None:
                    console.print(pad(Panel(self.help, style="title", expand=False)))

        def format_usage(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                self.print_header("Usage:", console)

                usage_pieces = []
                for usage_piece in self.collect_usage_pieces(ctx):
                    usage_pieces += list(usage_piece.split(" "))

                usage_pieces = [
                    f"[command_path]{ctx.command_path}[/command_path]", f"[option]{self.options_metavar}[/option]"
                ]
                for param in self.get_params(ctx):
                    if isinstance(param, click.Argument):
                        usage_pieces += [f"[argument]{param.get_usage_pieces(ctx)[0]}[/argument]"]

                subcommand_metavar = getattr(self, "subcommand_metavar", "")
                usage_pieces.append(f"[command]{subcommand_metavar}[/command]")

                console.print(pad(" ".join(usage_pieces)))

        @staticmethod
        def get_arguments(ctx):
            arguments = collections.OrderedDict()
            for p in ctx.command.params:
                if isinstance(p, click.Argument):
                    arguments[p.name.upper()] = getattr(p, 'help', '')
            return arguments

        def get_options(self, ctx):
            options = collections.OrderedDict()
            for param in self.params:
                help_record = param.get_help_record(ctx)
                if help_record is not None:
                    options[help_record[0]] = help_record[1]
            options["--help"] = "Get detailed info."
            return options

        @staticmethod
        def print_header(header, console):
            console.print(header, style="header")

        def get_help_table(self, entries: Mapping[str, str], ctx, style):
            table = Table(show_header=False, box=box.MINIMAL)
            table.add_column(justify="left", style=style, width=self.get_max_lhs_column_width(ctx))
            table.add_column(justify="left")
            for entry, help_text in entries.items():
                table.add_row(escape(entry), help_text)
            return table

        def format_arguments(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                arguments = self.get_arguments(ctx)
                if len(arguments) > 0:
                    self.print_header("Arguments:", console)
                    console.print(pad(self.get_help_table(arguments, ctx, "argument")))

        def format_options(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                options = self.get_options(ctx)
                if len(options) > 0:
                    self.print_header("Options:", console)
                    console.print(pad(self.get_help_table(options, ctx, "option")))

    return RichCommand


GROUP_TYPE = TypeVar("GROUP_TYPE", bound=click.Group)


def make_rich_group(cls: Type[GROUP_TYPE]) -> Type[GROUP_TYPE]:
    """Creates and returns a subclass of the given ``click.Group`` type which renders help text with rich.

    Parameters
    ----------
    cls
        The ``click.Group`` subclass to enhance with rich.
    """
    class RichGroup(make_rich_command(cls)):
        def command(self, *args, **kwargs):
            cls = kwargs.get("cls", click.Command)
            kwargs["cls"] = make_rich_command(cls)
            return super().command(*args, **kwargs)

        def group(self, *args, **kwargs):
            cls = kwargs.get("cls", click.Group)
            kwargs["cls"] = make_rich_group(cls)
            return super().command(*args, **kwargs)

        def get_max_lhs_column_width(self, ctx) -> int:
            all_lens = [super().get_max_lhs_column_width(ctx)]
            all_lens += [len(command) for command in self.get_commands(ctx).keys()]
            return max(all_lens)

        def format_help(self, ctx, formatter):
            self.format_help_text(ctx, formatter)
            self.format_usage(ctx, formatter)
            self.format_options(ctx, formatter)
            self.format_arguments(ctx, formatter)
            self.format_commands(ctx, formatter)
            self.format_learn_more(ctx, formatter)
            self.format_epilog(ctx, formatter)

        def get_commands(self, ctx):
            commands = collections.OrderedDict()
            for command in self.list_commands(ctx):
                command = self.commands.get(command)
                commands[command.name] = command.get_short_help_str(limit=120)
            return commands

        def format_commands(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                self.print_header("Commands:", console)
                console.print(pad(self.get_help_table(self.get_commands(ctx), ctx, "command")))

        def format_learn_more(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                self.print_header("Learn more:", console)
                console.print(
                    pad(
                        f"Use [command_path]{ctx.command_path.strip()}[/command_path] [command]COMMAND[/command] "
                        "[option]--help[/option] for more information about a command."
                    )
                )

    return RichGroup


def make_rich(cls: Type[COMMAND_TYPE]) -> Type[COMMAND_TYPE]:
    """Utility function to enhance a ``click.Command`` or ``click.Group`` type with rich by choosing the correct
    ``make_rich_*`` method.

    Parameters
    ----------
    cls
        The ``click.Command`` subclass to enhance with rich.
    """
    if issubclass(cls, click.Group):
        return make_rich_group(cls)
    return make_rich_command(cls)


def command(name=None, cls=None, **attrs):
    """An override for the ``click.command`` decorator which adds rich help text."""
    if cls is None:
        cls = click.Command
    cls = make_rich(cls)
    return click.command(name=name, cls=cls, **attrs)


def group(name=None, cls=None, **attrs):
    """An override for the ``click.group`` decorator which adds rich help text."""
    if cls is None:
        cls = click.Group
    cls = make_rich(cls)
    return click.group(name=name, cls=cls, **attrs)


def main_group(name=None, cls=None, **attrs):
    if cls is None:
        cls = click.Group
    cls = make_rich(cls)

    class RichMainGroup(cls):
        def format_epilog(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                self.print_header("Examples:", console)
                console.print(
                    pad(
                        RenderGroup(
                            "[command_path]grid[/command_path] [command]login[/command]",
                            "[command_path]grid[/command_path] [command]version[/command]",
                        )
                    )
                )

                self.print_header("Feedback:", console)
                console.print(
                    pad(
                        "For questions or feedback Join our slack! "
                        "[underline][link=https://bit.ly/3fUOeDU]https://bit.ly/3fUOeDU[/link][/underline]"
                    )
                )

        def parse_args(self, ctx, args):
            if not is_latest_version():
                message = render_warning(
                    f"A newer version of [command_path]{__package_name__}[/command_path] is available. To upgrade, "
                    f"please run: pip install [command_path]{__package_name__}[/command_path] --upgrade"
                )
                if not env.IGNORE_WARNINGS:
                    click.echo(message)
            return super().parse_args(ctx, args)

    cls = RichMainGroup
    return click.group(name=name, cls=cls, **attrs)


def argument(*param_decls, **attrs):
    """An override for the ``click.argument`` decorator that adds a ``help`` argument, similar to ``click.Command``."""
    cls = attrs.get("cls", click.Argument)

    class HelpArgument(cls):
        """A ``click.Argument`` which includes a short help message."""
        def __init__(self, *args, **kwargs):
            self.help = kwargs.pop("help", None)
            super().__init__(*args, **kwargs)

    attrs["cls"] = HelpArgument
    return click.argument(*param_decls, **attrs)


def deprecate_grid_options(cls: Optional[Type[click.Command]] = None):
    """Creates a custom ``click.Command`` class that gives a warning if parameters beginning with ``grid_`` or ``g_``
    are used.

    Parameters
    ----------
    cls
        Optionally pass the ``click.Command`` class to extend.
    """
    cls = cls or click.Command

    class DeprecatedCommand(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def format_epilog(self, ctx, formatter):
            with console_from_formatter(formatter) as console:
                if self.epilog:
                    console.print(self.epilog)
                console.print('[note]Note[/note]:')
                console.print(
                    pad(
                        'Parameters prefixed with "grid_" or "g_" are deprecated and will be removed in a later '
                        'release. Use their non-prefixed variants instead.'
                    )
                )

        def parse_args(self, ctx, args):
            new_args = []
            for arg in args:
                if str(arg).startswith('--grid_') or str(arg).startswith('--g_'):
                    preferred = arg.replace('--grid_', '--').replace('--g_', '--')
                    # If the preferred param actually exists (is in the opts for anything in self.params) then we give a
                    # deprecation warning and replace the arg. If not, we do nothing and click will give a 'does not
                    # exist' error message.
                    if any(preferred in param.opts for param in self.params):
                        message = render_warning(
                            f'The [option]{arg}[/option] parameter is deprecated and will be removed in a later '
                            f'release. Use [option]{preferred}[/option] instead.'
                        )
                        if not env.IGNORE_WARNINGS:
                            click.echo(message)
                        arg = preferred
                new_args.append(arg)
            return super().parse_args(ctx, new_args)

    return DeprecatedCommand


def deprecate_and_alias(aliases: Mapping[str, str], cls: Optional[Type[GROUP_TYPE]] = None) -> Type[GROUP_TYPE]:
    """Creates a custom ``click.Group`` class that swaps commands with their aliases and gives a deprecation warning if
    the aliased commands are used.
    Parameters
    ----------
    aliases
        The mapping from old command name to new command name (alias).
    cls
        Optionally pass the ``click.Command`` class to extend.
    """
    cls = cls or click.Group

    # Referencing from: https://stackoverflow.com/questions/46641928/python-click-multiple-command-names
    class AliasedGroup(cls):
        def get_command(self, ctx, cmd_name):
            if cmd_name in aliases:
                preferred = aliases[cmd_name]
                message = render_warning(
                    f'The [option]{cmd_name}[/option] command is deprecated and will be removed in a later release. '
                    f'Use [option]{preferred}[/option] instead.'
                )
                if not env.IGNORE_WARNINGS:
                    click.echo(message)
                cmd_name = preferred
            return super().get_command(ctx, cmd_name)

    return AliasedGroup
