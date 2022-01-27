import click
import xnat

from .utils import unpack_context

@click.group()
@click.pass_context
def download(ctx):
    """
    Commands to download XNAT objects to your machine.
    """


@download.command()
@click.argument('project')
@click.argument('targetdir')
@click.pass_context
def project(ctx, project, targetdir):
    """Download XNAT project to the target directory."""
    ctx = unpack_context(ctx)

    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
        xnat_project = session.projects.get(project)

        if project is None:
            print('[ERROR] Could not find project!'.format(project))

        result = xnat_project.download_dir(targetdir)
        session.logger.info("Download complete!")
