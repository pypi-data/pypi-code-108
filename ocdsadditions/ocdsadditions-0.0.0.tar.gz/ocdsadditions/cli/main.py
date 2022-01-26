from os import getcwd

import click

from ocdsadditions.library import Repository


@click.group()
def cli():
    pass


@click.command("addocid")
@click.argument("ocid")
def addocid_command(ocid: str):
    click.echo("Adding OCID")

    repo = Repository(getcwd())
    repo.add_ocid(ocid)


@click.command("addexternalreleasepackage")
@click.argument("url")
def addexternalreleasepackage_command(url: str):
    click.echo("Adding external release package")
    repo = Repository(getcwd())
    repo.add_external_release_package(url)


@click.command("addemptyrelease")
@click.argument("ocid")
@click.argument("releaseid")
def addemptyrelease_command(ocid: str, releaseid: str):
    click.echo("Adding Empty release")
    repo = Repository(getcwd())
    cp = repo.get_contracting_process(ocid)
    cp.add_empty_release(releaseid)


@click.command("buildsite")
@click.argument("output_directory")
def buildsite_command(output_directory: str):
    click.echo("Building site")
    repo = Repository(getcwd())
    repo.build_site(output_directory)


cli.add_command(addocid_command)
cli.add_command(addexternalreleasepackage_command)
cli.add_command(addemptyrelease_command)
cli.add_command(buildsite_command)

if __name__ == "__main__":
    cli()
