import click
import click_config_file

from montecarlodata import settings
from montecarlodata.iac.mc_config_service import MonteCarloConfigService


@click.group(help='Manage monitors.')
def monitors():
    """
    Group for any collector related subcommands
    """
    pass

@monitors.command(help='Compile monitor configuration.')
@click.option('--project-dir', required=False, help='Base directory of MC project (where montecarlo.yml is located). By default, this is set to the current working directory')
@click.pass_obj
def compile(ctx, project_dir):
    MonteCarloConfigService(config=ctx['config'], project_dir=project_dir).compile()

@monitors.command(help='Compile and apply monitor configuration.')
@click.option('--project-dir', required=False, help='Base directory of MC project (where montecarlo.yml is located). By default, this is set to the current working directory')
@click.option('--namespace', required=True, help='Namespace of monitors configuration.')
@click.option('--dry-run', required=False, default=False, show_default=True, is_flag=True, help='Dry run (just shows planned changes but doesn\'t apply them.')
@click.pass_obj
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def apply(ctx, project_dir, namespace, dry_run):
    MonteCarloConfigService(config=ctx['config'], project_dir=project_dir).apply(namespace, dry_run=dry_run)

@monitors.command(help='Delete monitor configuration.')
@click.option('--project-dir', required=False, help='Base directory of MC project (where montecarlo.yml is located). By default, this is set to the current working directory')
@click.option('--namespace', required=True, help='Namespace of monitors configuration.')
@click.option('--dry-run', required=False, default=False, show_default=True, is_flag=True, help='Dry run (just shows planned changes but doesn\'t apply them.')
@click.pass_obj
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def delete(ctx, project_dir, namespace, dry_run):
    MonteCarloConfigService(config=ctx['config'], project_dir=project_dir).delete(namespace, dry_run=dry_run)