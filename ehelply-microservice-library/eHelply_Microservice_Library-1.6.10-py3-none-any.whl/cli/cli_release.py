import typer
from pathlib import Path
from typing import Optional
from ehelply_bootstrapper.utils.releases import ReleasesConfig, ReleaseDetails, Releaser
import os

cli = typer.Typer()


@cli.command()
def create(
        version: str = typer.Option(..., prompt=True, help="The version of the new release. This MUST always be greater than the previous version. Use semantic versioning"),
        name: str = typer.Option(..., prompt=True, help="Name of the release"),
        changelog: str = typer.Option(..., prompt=True, help="Brief, comma separated changelog"),
        dirty: Optional[bool] = typer.Option(False, help="When false, a release cannot be made if a repository is dirty"),
        releases: Optional[Path] = typer.Option(None, help="Path to the directory where releases.json can be found. By default it is the current working directory")
):
    """
    Create a new microservice release
    """

    base_path: Path = releases
    if not base_path:
        base_path = Path(os.getcwd())

    repo_path: Path = base_path  # Path(Path(__file__).resolve().parents[3])  # TODO: Change back to 3 (4 when testing in template)

    releases_path: Path = base_path.joinpath("releases.json")

    config: ReleasesConfig = ReleasesConfig(
        repo_path=repo_path,
        releases_path=releases_path
    )

    releaser: Releaser = Releaser(config, allow_dirty=dirty)
    releaser.make(ReleaseDetails(name=name, version=version, changelog=changelog))


if __name__ == '__main__':
    cli()
