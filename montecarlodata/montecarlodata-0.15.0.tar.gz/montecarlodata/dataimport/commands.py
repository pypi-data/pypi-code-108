import click

from montecarlodata.dataimport.dbt import DbtImportService
from montecarlodata.dataimport.dbt_cloud import DbtCloudImportService
from montecarlodata.dataimport.dbt_run_results import DbtRunResultsImportService


@click.group(help='Import data.', name='import')
def import_subcommand():
    """
    Group for any import related subcommands
    """
    pass


@import_subcommand.command(help='Import DBT manifest.')
@click.argument('MANIFEST_FILE', required=True, type=click.Path(exists=True))
@click.option('--project-name', required=False, type=click.STRING,
              help='Name that uniquely identifies dbt project.')
@click.option('--batch-size', required=False, default=10, type=click.INT,
              help='Number of DBT manifest nodes to send in each batch.'
                   'Use smaller number if requests are timing out.'
                   'Use larger number for higher throughput.')
@click.pass_obj
def dbt_manifest(ctx, manifest_file, project_name, batch_size):
    DbtImportService(config=ctx['config'], dbt_manifest=manifest_file).import_dbt_manifest(
        project_name=project_name,
        batch_size=batch_size
    )


@import_subcommand.command(help='Import DBT run results.')
@click.argument('RUN_RESULTS_FILE', required=True, type=click.Path(exists=True))
@click.option('--project-name', required=False, type=click.STRING,
              help='Name that uniquely identifies dbt project.')
@click.pass_obj
def dbt_run_results(ctx, run_results_file, project_name):
    DbtRunResultsImportService(config=ctx['config'], dbt_run_results=run_results_file).import_run_results(
        project_name=project_name
    )


@import_subcommand.command(help='Import manifest and run results from DBT cloud. This command is experimental.')
@click.option('--project-id', required=False, type=click.STRING,
              help='dbt cloud project ID to import. If not specified, all projects will be imported.')
@click.option('--job-id', required=False, type=click.STRING,
              help='dbt cloud job ID to import. If not specified, all jobs will be imported.')
@click.option('--manifest-only', required=False, type=click.BOOL, is_flag=True,
              help='If used, will only import manifest (not run results)')
@click.pass_obj
def dbt_cloud(ctx, project_id, job_id, manifest_only):
    DbtCloudImportService(config=ctx['config']).import_dbt_cloud(project_id=project_id, job_id=job_id, manifest_only=manifest_only)
