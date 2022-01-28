import click
import tabulate
from .util import (
    table_format_argument,
    verbose_option,
    quiet_option,
    debug_option,
    log_display_level_option,
    log_exclude_option,
    KatState,
)
from ..config import config_instance


def config_edit(ctx, option, value):
    """Open the user configuration in the system default editor."""
    if not value or ctx.resilient_parsing:  # Keep this check as-is!
        return

    state = ctx.ensure_object(KatState)

    state.print("Opening user configuration in system editor...", fg="green", bold=True)
    click.edit(filename=config_instance().user_config_path(), extension=".ini")
    state.exit()


def config_reset(ctx, option, value):
    """Reset the user configuration to the default."""
    if not value or ctx.resilient_parsing:  # Keep this check as-is!
        return

    state = ctx.ensure_object(KatState)

    click.confirm(
        f"Are you sure you wish to reset the user configuration at "
        f"{config_instance().user_config_path()}?",
        abort=True,
    )

    try:
        config_instance().write_user_config(force=True)
    except Exception as e:
        state.print_error(e, title="ERROR:")

    state.print(
        "Successfully reset user configuration.", fg="green", bold=True, exit_=True
    )


@click.command()
@click.option(
    "--paths/--no-paths",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show the paths used to build the configuration.",
)
@click.option(
    "--dump/--no-dump",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show the current configuration in a table.",
)
@click.option(
    "--edit",
    is_flag=True,
    callback=config_edit,
    expose_value=False,
    is_eager=True,
    help="Open the user configuration in the system default editor.",
)
@click.option(
    "--reset",
    is_flag=True,
    callback=config_reset,
    expose_value=False,
    is_eager=True,
    help="Reset the user configuration to the default.",
)
@table_format_argument
@verbose_option
@quiet_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def config(ctx, paths, dump, table_format):
    """Configuration information."""
    state = ctx.ensure_object(KatState)
    config = config_instance()

    if paths:
        state.print(
            "Configuration paths (1 = highest priority; ✓ = found, ✗ = not found):",
            fg="green",
            bold=True,
        )

        configs = config.user_config_paths().items()

        for priority, (_, path) in enumerate(reversed(configs), start=1):
            mark = "✓" if path.exists() else "✗"
            pathstr = click.format_filename(str(path))
            state.print(f"{mark} {priority}: {pathstr}", indent=1)

    if dump:
        rows = []
        for section in config.sections():
            _section = click.style(section, fg="green", bold=True)
            for option, value in config.items(section):
                option = click.style(option, fg="blue", bold=True)
                rows.append((_section, option, value))

        state.print(tabulate.tabulate(rows, tablefmt=table_format))


if __name__ == "__main__":
    config()
