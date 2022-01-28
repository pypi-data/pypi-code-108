import fnmatch
import re
import click
import textwrap
from ..env import INDENT
from .util import KatState

# Match fnmatch wildcards.
WILDCARDS_PATTERN = re.compile(r"[\*\?]|\[.*\]")


@click.command()
@click.argument("query", required=False, nargs=-1)
@click.option(
    "--elements/--no-elements",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show elements.",
)
@click.option(
    "--commands/--no-commands",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show commands.",
)
@click.option(
    "--analyses/--no-analyses",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show analyses.",
)
@click.option(
    "--keyword/--positional",
    "keyword_arguments",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show keyword arguments where supported.",
)
@click.option(
    "--exact",
    is_flag=True,
    default=False,
    show_default=True,
    help=(
        "Interpret wildcard characters literally, and do not add an implicit '*' "
        "wildcard to the end of each QUERY term."
    ),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show extended documentation for each directive.",
)
@click.pass_context
def syntax(ctx, query, elements, commands, analyses, keyword_arguments, exact, verbose):
    """Query the KatScript syntax documentation.

    \b
    Simple wildcards are supported (as long as --exact is not specified):
      - ``*`` matches 0 or more characters
      - ``?`` matches any single character
      - ``[abc]`` matches any characters in abc
      - ``[!abc]`` matches any characters not in abc

    A ``*`` is added to the end of each query term if no wildcards are present and
    --exact is not specified.

    Specify zero or more QUERY terms. By default, all syntax is shown.
    """
    from ..script import syntax
    from ..script.spec import KatSpec

    state = ctx.ensure_object(KatState)
    spec = KatSpec()

    directives = {}

    if elements:
        directives.update(spec.elements)
    if commands:
        directives.update(spec.commands)
    if analyses:
        directives.update(spec.analyses)

    adapters = set()
    for directive, adapter in directives.items():
        if query:
            if exact:
                matches = any(directive == q for q in query)
            else:
                # Add trailing '*' wildcard if no other wildcards are present.
                query = [f"{q}*" for q in query if not WILDCARDS_PATTERN.match(q)]
                matches = any(fnmatch.fnmatch(directive, q) for q in query)

            if not matches:
                continue

        adapters.add(adapter)

    if not adapters:
        state.print_error("No directives found.")

    # Sort the directives in order they appear in the spec. This is better than
    # alphabetic sort, which puts `x2axis` ahead of `xaxis`.
    order = list(directives)
    for adapter in sorted(adapters, key=lambda adapter: order.index(adapter.full_name)):
        syntax_form = click.style(
            syntax(
                adapter.full_name,
                verbose=verbose,
                optional_as_positional=not keyword_arguments,
            )
        )

        directive = " / ".join(sorted(adapter.aliases, key=lambda alias: len(alias)))
        if directive in spec.elements:
            fg = "green"
        elif directive in spec.commands:
            fg = "yellow"
        else:
            fg = "red"
        fmt_directive = click.style(directive, fg=fg)

        if verbose:
            state.print(f"{fmt_directive}:\n{textwrap.indent(syntax_form, INDENT)}")
        else:
            state.print(f"{fmt_directive}: {syntax_form}")


if __name__ == "__main__":
    syntax()
