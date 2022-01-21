import click

from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    cmd_confirm_or_abort,
    option_force,
    check_config,
    cmd_error,
    cmd_info,
    cmd_success,
    cmd_warning,
    get_cmd_command,
)


@click.group("rm")
def commands():
    """
    Remove of local algorithm or dataset from local Anylearn project.
    """
    pass


@commands.command()
@click.argument('name')
@option_force
@check_config()
@get_cmd_command()
def algorithm(name: str, force: bool=False):
    config = AnylearnCliConfig.load()
    try:
        algo = config.algorithms[name]
        dir = config.path['algorithm'][name]
    except KeyError:
        cmd_error(msg=(
            "Algorithm {name} or its path config does not exist.\n"
        ))
        raise click.Abort
    cmd_warning(msg=(
        "Algorithm to remove:"
        "\n(\n"
        f"  ID={algo.id},\n"
        f"  NAME={algo.name},\n"
        f"  DESCRIPTION={algo.description},\n"
        f"  LOCAL_DIR={dir},\n"
        "\n)\n"
        "Note: this action only removes the reference in current project. "
        "Local files and remote entries are kept as is."
    ))
    if not force:
        cmd_confirm_or_abort()
    del(config.algorithms[name])
    del(config.path['algorithm'][name])
    AnylearnCliConfig.update(config)
    cmd_success(msg="REMOVED")


@commands.command()
@click.argument('name')
@option_force
@check_config()
@get_cmd_command()
def dataset(name: str, force: bool=False):
    config = AnylearnCliConfig.load()
    try:
        dset = config.datasets[name]
        dir = config.path['dataset'][name]
    except KeyError:
        cmd_error(msg=(
            "Dataset {name} or its path config does not exist.\n"
        ))
        raise click.Abort
    cmd_warning(msg=(
        "Dataset to remove:"
        "\n(\n"
        f"  ID={dset.id},\n"
        f"  NAME={dset.name},\n"
        f"  DESCRIPTION={dset.description},\n"
        f"  LOCAL_DIR={dir},\n"
        "\n)\n"
        "Note: this action only removes the reference in current project. "
        "Local files and remote entries are kept as is."
    ))
    if not force:
        cmd_confirm_or_abort()
    del(config.datasets[name])
    del(config.path['dataset'][name])
    AnylearnCliConfig.update(config)
    cmd_success(msg="REMOVED")
