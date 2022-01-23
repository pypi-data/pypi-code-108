from pathlib import Path
from ehelply_bootstrapper.utils.docs import export_code_docs as lib_export_code_docs
import typer

cli = typer.Typer()
dev_cli = typer.Typer()

cli.add_typer(dev_cli, name="dev")


@dev_cli.command()
def export_code_docs():
    lib_export_code_docs(root_path=Path(__file__).parents[2], modules=["ehelply_microservice_library"])


def cli_main():
    cli()


if __name__ == '__main__':
    cli()
