import typer
from pathlib import Path
from typing import Optional
from ehelply_bootstrapper.utils.state import State
from ehelply_microservice_library.lightweight_bootstrap import lightweight_bootstrap
from ehelply_microservice_library.utils.secret_names import secret_name_updater_vault
from ehelply_bootstrapper.drivers.aws_utils.aws_asm import ASM
import os

cli = typer.Typer()


@cli.command()
def install(
        root: Optional[Path] = typer.Option(None, help="Path to where the ehelply-package.json file can be found. If blank, default is current working directory")
):
    """
    Install the latest service template updates
    """
    with typer.progressbar(length=4, label="Updating") as progress:
        root_path: Path = root
        if not root_path:
            root_path = Path(os.getcwd())
        # root_path: Path = Path(Path(__file__).resolve().parents[3])

        lightweight_bootstrap(root_path)
        progress.update(1)

        secret = ASM.get_secret(secret_name_updater_vault())
        access_key: str = secret.access
        secret_key: str = secret.secret
        api_base_url: str = State.config.updater.endpoint

        from ehelply_updater.updater import Updater, Config

        config: Config = Config(
            api_base_url=api_base_url + "/templates",
            update_dir=str(root_path),
            package_file=str(root_path.joinpath("ehelply-package.json")),
            access_key=access_key,
            secret_key=secret_key,
        )
        updater: Updater = Updater(config=config)
        progress.update(1)

        update_available: bool = updater.is_update_required()
        progress.update(1)

        if update_available:
            updater.pp_upgrade_info(updater.update())
        else:
            typer.echo("No service template updates available")

        progress.update(1)


@cli.command()
def preview(
        root: Optional[Path] = typer.Option(None, help="Path to where the ehelply-package.json file can be found. If blank, default is current working directory")
):
    """
    Preview the latest service template updates. Won't install, but will show the changelog and changes
    """
    with typer.progressbar(length=4, label="Processing") as progress:
        root_path: Path = root
        if not root_path:
            root_path = Path(os.getcwd())
        #root_path: Path = Path(Path(__file__).resolve().parents[3])

        lightweight_bootstrap(root_path)
        progress.update(1)

        secret = ASM.get_secret(secret_name_updater_vault())
        access_key: str = secret.access
        secret_key: str = secret.secret
        api_base_url: str = State.config.updater.endpoint

        from ehelply_updater.updater import Updater, Config


        config: Config = Config(
            api_base_url=api_base_url + "/templates",
            update_dir=str(root_path),
            package_file=str(root_path.joinpath("ehelply-package.json")),
            access_key=access_key,
            secret_key=secret_key,
        )
        updater: Updater = Updater(config=config)
        progress.update(1)

        update_available: bool = updater.is_update_required()
        progress.update(1)

        if update_available:
            updater.pp_upgrade_info(updater.preview())
        else:
            typer.echo("No service template updates available")

        progress.update(1)


@cli.command()
def review(
        start_version: str = typer.Option(..., prompt=True, help="Start version"),
        end_version: str = typer.Option(..., prompt=True, help="End version"),
        root: Optional[Path] = typer.Option(None, help="Path to where the ehelply-package.json file can be found. If blank, default is current working directory")
):
    """
    Compare the changes and changelog between two versions
    """
    with typer.progressbar(length=4, label="Processing") as progress:
        root_path: Path = root
        if not root_path:
            root_path = Path(os.getcwd())
        #root_path: Path = Path(Path(__file__).resolve().parents[3])

        lightweight_bootstrap(root_path)
        progress.update(1)

        secret = ASM.get_secret(secret_name_updater_vault())
        access_key: str = secret.access
        secret_key: str = secret.secret
        api_base_url: str = State.config.updater.endpoint

        from ehelply_updater.updater import Updater, Config, UpdateInfo

        root_path: Path = Path(Path(__file__).resolve().parents[3])
        config: Config = Config(
            api_base_url=api_base_url + "/templates",
            update_dir=str(root_path),
            package_file=str(root_path.joinpath("ehelply-package.json")),
            access_key=access_key,
            secret_key=secret_key,
        )
        updater: Updater = Updater(config=config)
        progress.update(1)

        import requests

        response = requests.get(
            updater.config.api_base_url + "/versions/" + start_version + "/updates/" + end_version,
            headers=updater.headers)

        if response.status_code == 200:
            updater.pp_upgrade_info(UpdateInfo(**response.json()))
        else:
            raise typer.echo("Unable to get update information")

        progress.update(1)