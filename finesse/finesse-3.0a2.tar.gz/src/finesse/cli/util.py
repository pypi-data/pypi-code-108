import sys
import logging
import datetime
import textwrap
from itertools import chain
import click
import tabulate
from .. import __version__, PROGRAM, session
from ..env import show_tracebacks
from ..utilities import networkx_layouts, graphviz_layouts, add_linenos, ngettext
from ..utilities.logging import FinesseStreamHandler
from ..script.exceptions import KatScriptError

LOGGER = logging.getLogger(PROGRAM)


def set_verbosity(ctx, option, value):
    """Callback to set verbosity for root CLI command."""
    # If neither -v nor -q is set, value is 0.
    if not value:
        return

    if option.name == "verbose":
        setter = session.louder
    elif option.name == "quiet":
        setter = session.quieter
    else:
        raise ValueError("Unsupported option.")

    # If -v or -q was specified N times, we want to get increasingly louder/quieter by
    # N times.
    for _ in range(value):
        setter()


def set_log_display_level(ctx, option, value):
    """Callback to set log verbosity for root CLI command."""
    if not value:
        return

    state = ctx.ensure_object(KatState)
    state.log_display_level = value


def set_fancy_error_formatting(ctx, option, value):
    if value is None:
        return

    state = ctx.ensure_object(KatState)
    state.fancy_errors = value


def set_debug(ctx, option, value):
    if value is None:
        return

    state = ctx.ensure_object(KatState)
    state.debug = value


def set_log_excludes(ctx, option, value):
    if value is None:
        return

    state = ctx.ensure_object(KatState)
    for exclude in value:
        state.exclude(exclude)


def print_banner(ctx, option, value):
    """Show the Finesse banner and exit."""
    if not value or ctx.resilient_parsing:  # Keep this check as-is!
        return

    state = ctx.ensure_object(KatState)
    state.print_banner(exit_=True)


def parse_path(state, path, legacy=False, **error_kwargs):
    from finesse.script import parse_file, parse_legacy_file

    try:
        if legacy:
            return parse_legacy_file(path)
        else:
            return parse_file(path)
    except Exception as error:
        state.print_error(error, "PARSING ERROR:", **error_kwargs)


def plot_graph(state, *args, **kwargs):
    from finesse.plotting.graph import plot_graph as finesse_plot_graph

    finesse_plot_graph(*args, **kwargs)


def list_graph_layouts(ctx, option, value):
    """Callback to list available graph layouts."""
    from ..env import has_pygraphviz

    if not value:
        return

    state = ctx.ensure_object(KatState)

    state.print("Available layouts:", fg="green")

    nx_layouts = networkx_layouts()
    gv_layouts = graphviz_layouts()
    layouts = sorted(chain(nx_layouts, gv_layouts))
    gv_suffix = click.style("*", fg="yellow")

    for layout in layouts:
        suffix = gv_suffix if layout in gv_layouts else ""
        state.print(f"- {layout}{suffix}")

    state.print()
    if has_pygraphviz():
        state.print(
            "*This layout can also be plotted directly in graphviz using the "
            "--graphviz flag",
            fg="yellow",
        )
    else:
        state.print("Install pygraphviz/graphviz for more layouts", fg="yellow")

    sys.exit()


def _fancy_format_kat_error(exception):
    """Format each marked error in red."""
    assert isinstance(exception, KatScriptError)

    error = f"{exception.rubric()}\n"
    errorlines = []
    linenos = []
    errorlinenos = set()
    for lineno, linechunks in exception.chunkify().items():
        line = ""
        for bounds, is_error in linechunks:
            chunktxt = exception.container.script(bounds)

            if is_error:
                errorlinenos.add(lineno)

                if len(chunktxt) == chunktxt.count(" "):
                    # Error chunk is just spaces. Replace with interpunct.
                    chunktxt = click.style("·" * len(chunktxt), fg="red")
                elif chunktxt == "\n":
                    # Error is a newline. Replace with carriage return symbol. Also add
                    # the newline anyway without colouring it red.
                    chunktxt = click.style("↵", fg="red") + chunktxt

                line += click.style(chunktxt, fg="red")
            else:
                line += chunktxt

        # Get rid of trailing newline.
        try:
            line = line.splitlines()[0]
        except IndexError:
            # Line is empty.
            pass

        linenos.append(lineno)
        errorlines.append(line)

    # Add line numbers.
    numberedlines = add_linenos(linenos, errorlines)

    # Add message for missing lines.
    finallines = []
    lastlineno = None
    for lineno, line in zip(linenos, numberedlines):
        if lastlineno:
            diff = lineno - lastlineno
            if diff > 1:
                missingmsg = ngettext(diff - 1, "%d missing line", "%d missing lines")
                finallines.append(f"   *** {missingmsg} ***")
        prefix = "-->" if lineno in errorlinenos else "   "
        finallines.append(prefix + line)
        lastlineno = lineno

    syntax = ""
    if exception.syntax is not None:
        syntax = f"\n\nSyntax: {click.style(exception.syntax, fg='green')}"

    message = error + "\n".join(finallines) + syntax

    return message


input_file_argument = click.argument("input_file", type=click.File("r"))
output_file_argument = click.argument("output_file", type=click.File("w"), default="-")
plot_option = click.option(
    "--plot/--no-plot",
    default=True,
    show_default=True,
    help="Display results as figure (if possible).",
)
trace_option = click.option(
    "--trace/--no-trace",
    default=False,
    show_default=True,
    help="Displays the results of a beam trace of the model.",
)
graphviz_option = click.option(
    "--graphviz",
    is_flag=True,
    default=False,
    show_default=True,
    help="Generate layout and display using Graphviz.",
)
list_graph_layouts_option = click.option(
    "--list-graph-layouts",
    callback=list_graph_layouts,
    is_flag=True,
    default=False,
    expose_value=False,
    is_eager=True,
    help="Show available graph layouts and exit.",
)
graph_layout_argument = click.option(
    "--layout",
    type=str,
    default="neato",
    help="Graph layout algorithm to use.",
)
network_type_argument = click.option(
    "-t",
    "--type",
    "network_type",
    type=click.Choice(("full", "components", "optical")),
    default="full",
    help="Network to plot.",
)
table_format_argument = click.option(
    "--table-format",
    type=click.Choice(tabulate.tabulate_formats),
    default="fancy_grid",
    help="Table format to use.",
)
legacy_option = click.option(
    "--legacy",
    is_flag=True,
    default=False,
    show_default=True,
    help="Specify that the input file uses Finesse 2 syntax.",
)
# The current default verbosity is already maximum, so this currently has no effect.
verbose_option = click.option(
    "-v",
    "--verbose",
    count=True,
    callback=set_verbosity,
    expose_value=False,
    is_eager=True,
    help="Increase verbosity of log output (can be specified multiple times).",
)
quiet_option = click.option(
    "-q",
    "--quiet",
    count=True,
    callback=set_verbosity,
    expose_value=False,
    help="Decrease verbosity of log output (can be specified multiple times).",
)
fancy_error_option = click.option(
    "--fancy-errors/--no-fancy-errors",
    is_flag=True,
    default=True,
    callback=set_fancy_error_formatting,
    expose_value=False,
    show_default=True,
    help=(
        "Highlight script error locations in red rather than marking them on the "
        "following line."
    ),
)
log_display_level_option = click.option(
    "--log-level",
    type=click.Choice(("warning", "info", "debug")),
    default="warning",
    show_default=True,
    callback=set_log_display_level,
    expose_value=False,
    help="Set minimum log severity level to display.",
)
log_exclude_option = click.option(
    "--log-exclude",
    multiple=True,
    callback=set_log_excludes,
    expose_value=False,
    help="Ignore log records from a particular logger (wildcards allowed).",
)
debug_option = click.option(
    "--debug",
    is_flag=True,
    default=False,
    callback=set_debug,
    expose_value=False,
    show_default=True,
    help="Enable debug mode (print tracebacks).",
)


class ClickLogColorFormatter(logging.Formatter):
    """Stdout log formatter with colors."""

    # Log prefix format.
    # NOTE: this is NOT a :py:class:`logging.Formatter` compatible format string, but
    # rather a format specific to this class.
    PREFIX_FORMAT = "{short_name:>16s} [{record.levelname:>8s}]:"

    STYLES = {
        "critical": {"fg": "red"},
        "error": {"fg": "red"},
        "warning": {"fg": "yellow"},
        "info": {"fg": "green"},
        "debug": {"fg": "blue"},
    }

    def format(self, record):
        if record.exc_info:
            # Skip formatting of exception info.
            return super().format(record)

        level = record.levelname.casefold()
        msg = record.getMessage()

        if level in self.STYLES:
            # Remove "finesse." prefix.
            short_name = (
                record.name[8:] if record.name.startswith("finesse.") else record.name
            )

            prefix = click.style(
                self.PREFIX_FORMAT.format(short_name=short_name, record=record),
                **self.STYLES[level],
            )
            msg = "\n".join(f"{prefix} {line}" for line in msg.splitlines())

        return msg


class KatState:
    """Shared state for all CLI subcommands.

    This object gets built by Click when the CLI is called and encapsulates global
    settings for use by individual commands/groups.
    """

    LOG_DISPLAY_DEFAULT_LEVEL = logging.WARNING

    def __init__(self):
        # Fancy error flag. This is NOT the default value for the CLI - it is set on by
        # default via the @fancy_error_option decorators.
        self.fancy_errors = False

        # Set up the Finesse logger.
        self._log_handler = FinesseStreamHandler()
        self._log_handler.setFormatter(ClickLogColorFormatter())
        self._log_handler.setStream(click.get_text_stream("stderr"))
        LOGGER.addHandler(self._log_handler)

        # Set *default* log display level.
        # NOTE: the user's requested log display level is set by
        # :func:`set_log_display_level`.
        self.log_display_level = self.LOG_DISPLAY_DEFAULT_LEVEL

    @property
    def log_display_level(self):
        """Log verbosity on stdout."""
        return LOGGER.getEffectiveLevel()

    @log_display_level.setter
    def log_display_level(self, log_display_level):
        try:
            log_display_level = log_display_level.upper()
        except AttributeError:
            # Probably an int.
            pass
        LOGGER.setLevel(log_display_level)

    @property
    def isverbose(self):
        """Verbose output enabled.

        Returns True if the verbosity is enough for info messages to be displayed.
        """
        return session.verbose_for("info")

    @property
    def debug(self):
        return show_tracebacks()

    @debug.setter
    def debug(self, value):
        show_tracebacks(value)

    def exclude(self, pattern):
        """Exclude records from loggers with names matching the specified pattern."""
        self._log_handler.exclude(pattern)

    def print(self, text="", indent=0, error=False, exit_=False, exit_code=0, **kwargs):
        text = str(text)

        if indent > 0:
            text = textwrap.indent(text, " " * 4)

        click.secho(text, err=error, **kwargs)

        if exit_:
            self.exit(exit_code)

    def print_error(
        self, exception_or_msg, title=None, exit_=True, exit_code=1, **kwargs
    ):
        if title:
            self.print(title, error=True, fg="red", bold=True)

        if self.debug and isinstance(exception_or_msg, BaseException):
            # Print the full traceback.
            from traceback import format_exception

            # Only print the traceback part of the exception, because the message is
            # printed below. FIXME: the `etype` is not used here, and the second
            # parameter set to None results in "NoneType: None" being printed by
            # `TracebackException` after the traceback...
            etype, _, tb = sys.exc_info()
            trace = "".join(format_exception(etype, None, tb))
            self.print(trace, indent=1)

        if self.fancy_errors and isinstance(exception_or_msg, KatScriptError):
            msg = _fancy_format_kat_error(exception_or_msg)
            fg = None
        else:
            # Format the whole error as red.
            msg = str(exception_or_msg)
            fg = "red"

        self.print(msg, error=True, fg=fg, **kwargs)

        if exit_:
            self.exit(exit_code)

    def print_banner(self, kat_file=None, **kwargs):
        """Print the Finesse banner."""
        if not self.isverbose:
            return

        input_file = f"Input file: {kat_file.name}" if kat_file else ""
        timenow = datetime.datetime.now().strftime("%c").strip()
        timestr = f"{timenow:>60}"
        banner = rf"""
            ------------------------------------------------------------------------
                                 FINESSE {__version__}
                    o_.-=.       Frequency domain INterferomEter Simulation SoftwarE
                    (\'".\|                         http://www.gwoptics.org/finesse/
                    .>' (_--.
                _=/d   ,^\       {input_file}
                ~~ \)-'   '
                / |
                '  '    {timestr}
            ------------------------------------------------------------------------
            """

        self.print(textwrap.dedent(banner).strip(), **kwargs)

    def exit(self, code=0):
        """Stop execution."""
        sys.exit(code)
