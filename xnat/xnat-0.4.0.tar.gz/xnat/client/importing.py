import click
import xnat

from xnat import exceptions
from .utils import unpack_context

@click.group(name="import")
@click.pass_context
def importing(ctx):
    """
    Commands to import data from your machine into XNAT
    """



@importing.command()
@click.argument('folder')
@click.option('--destination', help="The destination to upload the scan to.")
@click.option('--project', help="The project in the archive to assign the session to (only accepts project ID, not a label).")
@click.option('--subject', help="The subject in the archive to assign the session to.")
@click.option('--experiment', help="The experiment in the archive to assign the session content to.")
@click.option('--import_handler')
@click.option('--quarantine', is_flag=True, help="Flag to indicate session should be quarantined.")
@click.option('--trigger_pipelines', is_flag=True, help="Indicate that importing should trigger pipelines.")
@click.pass_context
def experiment(ctx,
               folder,
               destination,
               project,
               subject,
               experiment,
               import_handler,
               quarantine,
               trigger_pipelines):
    """Import experiment from the target folder to XNAT"""
    try:
        ctx = unpack_context(ctx)
        with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
            session.services.import_dir(folder, quarantine=quarantine, destination=destination,
                                          trigger_pipelines=trigger_pipelines, project=project, subject=subject,
                                          experiment=experiment, import_handler=import_handler)
            session.logger.info("Import complete!")
    except exceptions.XNATLoginFailedError:
        print(f"ERROR Failed to login")
