import click

from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    check_config,
    check_connection,
    cmd_error,
    cmd_success,
    get_cmd_command,
)
from anylearn.interfaces import Dataset


@click.group("dataset")
@check_config()
def commands():
    """
    Add local or remote dataset to local Anylearn project.
    """
    pass


@commands.command()
@get_cmd_command()
@click.argument('name')
@click.option(
    '-d', '--dir',
    prompt=True,
    help="Local dataset folder (absolute path)."
)
def local(name: str, dir: str):
    """
    Add local algorithm to current project.
    """
    dset = Dataset(name=name)
    config = AnylearnCliConfig.load()
    old_dset = config.datasets.get(name, None)
    old_dir = config.path['dataset'].get(name, None)
    if old_dset:
        cmd_error(msg=(
            "A dataset with same name "
            "has already been added to current project"
            "\n(\n"
            f"  ID={old_dset.id},\n"
            f"  NAME={old_dset.name},\n"
            f"  LOCAL_DIR={old_dir},\n"
            "\n)\n"
        ))
        raise click.Abort
    config.datasets[name] = dset
    config.path['dataset'][name] = dir
    AnylearnCliConfig.update(config)
    cmd_success(msg="ADDED")

@commands.command()
@click.argument('id')
@check_connection()
@get_cmd_command()
def remote(id: str):
    """
    Add remote dataset by ID to current project.
    """
    config = AnylearnCliConfig.load()
    try:
        old_dset = next(
            d
            for d in config.datasets.values()
            if d.id == id
        )
        cmd_error(msg=(
            f"Remote dataset (ID={id}, name={old_dset.name}) "
            "has already been added to current project.\n"
            "Aborted!"
        ))
    except:
        try:
            dset = Dataset(id=id, load_detail=True)
            config = AnylearnCliConfig.load()
            old_dset = config.datasets.get(dset.name, None) # type: ignore
            old_dir = config.path['dataset'].get(dset.name, None) # type: ignore
            if old_dset:
                cmd_error(msg=(
                    "A dataset with same name "
                    "has already been added to current project"
                    "\n(\n"
                    f"  ID={old_dset.id},\n"
                    f"  NAME={old_dset.name},\n"
                    f"  LOCAL_DIR={old_dir},\n"
                    "\n)\n"
                ))
                raise click.Abort
            config.datasets[dset.name] = dset # type: ignore
            config.path['dataset'][dset.name] = None # type: ignore
            AnylearnCliConfig.update(config)
            cmd_success(msg="ADDED")
        except:
            cmd_error(msg=(
                f"Remote dataset (ID={id}) does not exist.\n"
                "Aborted!"
            ))
