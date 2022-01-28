import click

import montecarlodata.settings as settings
from montecarlodata.insights.commands import insights
from montecarlodata.collector.commands import collectors
from montecarlodata.dataimport.commands import import_subcommand
from montecarlodata.common.user import UserService
from montecarlodata.config import ConfigManager
from montecarlodata.discovery.commands import discovery
from montecarlodata.iac.commands import monitors
from montecarlodata.integrations.commands import integrations


@click.group(help='Monte Carlo\'s CLI.')
@click.option('--profile', default=settings.DEFAULT_PROFILE_NAME,
              help='Specify an MCD profile name. Uses default otherwise.')
@click.option('--config-path', default=settings.DEFAULT_CONFIG_PATH, type=click.Path(dir_okay=True),
              help=f'Specify path where to look for config file. Uses {settings.DEFAULT_CONFIG_PATH} otherwise.')
@click.version_option()
@click.pass_context
def entry_point(ctx, profile, config_path):
    """
    Entry point for all subcommands and options. Reads configuration and sets as context, except when configuring
    or getting help.
    """
    if ctx.invoked_subcommand != settings.CONFIG_SUB_COMMAND and settings.HELP_FLAG not in click.get_os_args():
        config = ConfigManager(profile_name=profile, base_path=config_path).read()
        if not config:
            ctx.abort()
        ctx.obj = {'config': config}


@click.command(help='Configure the CLI.')
@click.option('--profile-name', required=False, help='Specify a profile name for configuration.',
              default=settings.DEFAULT_PROFILE_NAME)
@click.option('--config-path', required=False, help='Specify path where to look for config file.',
              default=settings.DEFAULT_CONFIG_PATH, type=click.Path(dir_okay=True))
@click.option('--mcd-id', prompt='Key ID', help='Monte Carlo token user ID.')
@click.option('--mcd-token', prompt='Secret', help='Monte Carlo token value.', hide_input=True)
@click.option('--aws-profile', prompt='AWS profile name',
              help='AWS named profile with access to the DC stack and resources (e.g. CloudFormation and S3).',
              default='')
@click.option('--aws-region', prompt='AWS region', help='AWS region where DC is deployed.',
              default=settings.DEFAULT_AWS_REGION)
def configure(profile_name, config_path, mcd_id, mcd_token, aws_profile, aws_region):
    """
    Special subcommand for configuring the CLI
    """
    ConfigManager(profile_name=profile_name, base_path=config_path).write(mcd_id=mcd_id,
                                                                          mcd_token=mcd_token,
                                                                          aws_profile=aws_profile,
                                                                          aws_region=aws_region)


@click.command(help='Validate that the CLI can Connect to Monte Carlo.')
@click.pass_obj
def validate(ctx):
    """
    Special subcommand for validating the CLI was correctly configured
    """
    click.echo(f"Hi, {UserService(config=ctx['config']).user.first_name}! All is well.")


entry_point.add_command(integrations)
entry_point.add_command(configure)
entry_point.add_command(validate)
entry_point.add_command(collectors)
entry_point.add_command(discovery)
entry_point.add_command(monitors)
entry_point.add_command(import_subcommand)
entry_point.add_command(insights)


# to allow this to be run as a script within an IDE (for debugging)
if __name__ == '__main__':
    entry_point()