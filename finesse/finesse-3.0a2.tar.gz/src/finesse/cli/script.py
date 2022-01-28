import click
from .util import (
    input_file_argument,
    output_file_argument,
    legacy_option,
    verbose_option,
    quiet_option,
    fancy_error_option,
    debug_option,
    log_display_level_option,
    log_exclude_option,
    parse_path,
    KatState,
)


@click.command()
@input_file_argument
@output_file_argument
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def convert(ctx, input_file, output_file, legacy):
    """Convert and normalize kat script to canonical form.

    This can be used to convert Finesse 2 or Finesse 3 scripts to canonical Finesse 3 form. Note
    that some Finesse 2 instructions are not supported. The resulting script is arranged in standard
    order and with standard spacing.

    If OUTPUT_FILE is not specified, it defaults to stdout.
    """
    # Get state object to set verbosity, etc.
    state = ctx.ensure_object(KatState)

    model = parse_path(state, input_file, legacy=legacy)
    model.unparse_file(output_file)


if __name__ == "__main__":
    convert()
