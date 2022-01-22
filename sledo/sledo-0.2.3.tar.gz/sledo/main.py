
from io import TextIOWrapper
import os
import shutil
import click
from .generate import main as generate_main


@click.group()
def cli():  # pragma: no cover
    pass


@click.command()
@click.argument("file", type=click.File("r"))
@click.option("-O", "--outdir", default="out", help="The directory where the generated CSVs will be stored", type=click.Path(file_okay=False, writable=True), show_default=True)
def generate(file: TextIOWrapper, outdir: str):
    # check if the 'out'-directory already exists
    if os.path.isdir(outdir):
        click.confirm(f"The output directory '{outdir}' and ALL ITS CONTENTS will be REMOVED! Continue?",
                      default=False, abort=True, prompt_suffix=": ", show_default=True, err=False)
        # delete the existing directory
        shutil.rmtree(outdir)

    # create the directory
    try:
        os.mkdir(outdir)
    except OSError as e:
        raise click.UsageError(e)

    click.echo(generate_main(file, outdir))


cli.add_command(generate)

if __name__ == '__main__':  # pragma: no cover
    cli()
