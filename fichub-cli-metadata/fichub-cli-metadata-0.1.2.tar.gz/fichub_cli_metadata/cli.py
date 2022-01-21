import typer
import sys
from loguru import logger
from datetime import datetime
from colorama import init, Fore, Style

from .utils.fetch_data import FetchData

init(autoreset=True)  # colorama init
timestamp = datetime.now().strftime("%Y-%m-%d T%H%M%S")

app = typer.Typer(add_completion=False)


# @logger.catch  # for internal debugging
@app.callback(no_args_is_help=True,
              invoke_without_command=True)
def metadata(
    input: str = typer.Option(
        "", "-i", "--input", help="Input: Either an URL or path to a file"),

    out_dir: str = typer.Option(
        "", "-o", " --out-dir", help="Path to the Output directory for files (default: Current Directory)"),

    debug: bool = typer.Option(
        False, "-d", " --debug", help="Show the log in the console for debugging", is_flag=True),

    log: bool = typer.Option(
        False, help="Save the logfile for debugging", is_flag=True),

    automated: bool = typer.Option(
        False, "-a", "--automated", help="For internal testing only", is_flag=True, hidden=True),

    version: bool = typer.Option(
        False, help="Display version & quit", is_flag=True)


):
    """
    A metadata plugin for fetching Metadata from the Fichub API for fichub-cli

    To report issues upstream for the supported sites, visit https://fichub.net/#contact

    To report issues for the plugin, open an issue at https://github.com/fichub-cli-contrib/fichub-cli-metadata/issues

    To report issues for the CLI, open an issue at https://github.com/FicHub/fichub-cli/issues

    Failed downloads will be saved in the `err.log` file in the current directory
    """
    if log:
        # debug = True
        typer.echo(
            Fore.GREEN + "Creating " + Style.RESET_ALL + Fore.YELLOW +
            f"fichub_cli - {timestamp}.log" + Style.RESET_ALL +
            Fore.GREEN + " in the current directory!" + Style.RESET_ALL)
        logger.add(f"fichub_cli - {timestamp}.log")

    if input:
        fic = FetchData(debug=debug, automated=automated,
                        out_dir=out_dir)
        fic.get_metadata(input)

    if version:
        typer.echo("fichub-cli-metadata: v0.1.2")

    try:
        if fic.exit_status == 1:
            typer.echo(
                Fore.RED +
                "\nMetadata fetch failed  for one or more URLs! Check " + Style.RESET_ALL +
                Fore.YELLOW + "err.log" + Style.RESET_ALL + Fore.RED +
                " in the current directory!" + Style.RESET_ALL)
        sys.exit(fic.exit_status)
    except UnboundLocalError:
        sys.exit(0)
