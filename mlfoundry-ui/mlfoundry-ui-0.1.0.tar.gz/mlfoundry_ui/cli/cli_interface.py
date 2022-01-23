import os

import click

from mlfoundry_ui.constants import MLF_FOLDER_NAME, MLRUNS_FOLDER_NAME


def create_mlfoundry_ui_cli():
    """Generates CLI by combining all subcommands into a main CLI and returns in
    Returns:
        function: main CLI functions will all added sub-commands
    """
    _cli = mlfoundry_ui_cli()
    _cli.add_command(start_dashboard)
    return _cli


@click.group()
@click.version_option("1.0.0")
def mlfoundry_ui_cli():
    """MlFoundry UI CLI"""


@mlfoundry_ui_cli.command(
    help="Generate MLFoundry Dashboard",
    short_help="Generate MLFoundry Dashboard",
)
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    default=os.path.abspath("."),
)
def start_dashboard(path: str):
    abs_path = os.path.abspath(path)
    if not os.path.exists(os.path.join(abs_path, MLF_FOLDER_NAME)):
        raise Exception(
            f"Please provide a valid path of directory containing {MLF_FOLDER_NAME} directory. "
            f"{abs_path} does not contain {MLF_FOLDER_NAME}."
        )
    mlruns_path = os.path.join(abs_path, MLRUNS_FOLDER_NAME)

    import mlfoundry_ui as mlf_ui

    mlf_ui_main_file_path = os.path.join(
        os.path.dirname(mlf_ui.__file__), "webapp", "main_app.py"
    )
    os.system(f"streamlit run {mlf_ui_main_file_path} -- {mlruns_path}")
