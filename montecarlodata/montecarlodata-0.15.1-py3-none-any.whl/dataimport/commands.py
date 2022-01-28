import click
from pycarlo.features.dbt import DbtImporter, DbtCloudImporter

from montecarlodata.common.common import create_mc_client


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
@click.option('--default-resource', required=False, type=click.STRING,
              help='The warehouse friendly name or UUID where dbt objects will be associated with.')
@click.pass_obj
def dbt_manifest(ctx, manifest_file, project_name, batch_size, default_resource):
    DbtImporter(mc_client=create_mc_client(ctx), print_func=click.echo).import_dbt_manifest(
        dbt_manifest=manifest_file,
        project_name=project_name,
        batch_size=batch_size,
        default_resource=default_resource
    )


@import_subcommand.command(help='Import DBT run results.')
@click.argument('RUN_RESULTS_FILE', required=True, type=click.Path(exists=True))
@click.option('--project-name', required=False, type=click.STRING,
              help='Name that uniquely identifies dbt project.')
@click.pass_obj
def dbt_run_results(ctx, run_results_file, project_name):
    DbtImporter(mc_client=create_mc_client(ctx), print_func=click.echo).import_run_results(
        dbt_run_results=run_results_file,
        project_name=project_name
    )


@import_subcommand.command(help='Import manifest and run results from DBT cloud. This command is experimental.')
@click.option('--project-id', required=False, type=click.STRING,
              help='dbt cloud project ID to import. If not specified, all projects will be imported.')
@click.option('--job-id', required=False, type=click.STRING,
              help='dbt cloud job ID to import. If not specified, all jobs will be imported.')
@click.option('--manifest-only', required=False, type=click.BOOL, is_flag=True,
              help='If used, will only import manifest (not run results)')
@click.option('--default-resource', required=False, type=click.STRING,
              help='The warehouse friendly name or UUID where dbt objects will be associated with.')
@click.pass_obj
def dbt_cloud(ctx, project_id, job_id, manifest_only, default_resource):
    DbtCloudImporter(client=create_mc_client(ctx), print_func=click.echo).import_dbt_cloud(
        project_id=project_id,
        job_id=job_id,
        manifest_only=manifest_only,
        default_resource=default_resource
    )

