import click
from _pytask.config import hookimpl
from _pytask.shared import convert_truthy_or_falsy_to_bool
from _pytask.shared import get_first_non_none_value


@hookimpl
def pytask_extend_command_line_interface(cli):
    """Extend the cli."""
    cli.commands["build"].params.append(
        click.Option(
            ["--update-environment"],
            is_flag=True,
            default=None,
            help="Update the information on the environment stored in the database.",
        )
    )


@hookimpl
def pytask_parse_config(config, config_from_file, config_from_cli):
    """Parse the configuration."""
    config["check_python_version"] = get_first_non_none_value(
        config_from_file,
        key="check_python_version",
        default=True,
        callback=convert_truthy_or_falsy_to_bool,
    )

    config["check_environment"] = get_first_non_none_value(
        config_from_file,
        key="check_environment",
        default=True,
        callback=convert_truthy_or_falsy_to_bool,
    )

    config["update_environment"] = get_first_non_none_value(
        config_from_cli,
        key="update_environment",
        default=False,
        callback=convert_truthy_or_falsy_to_bool,
    )
