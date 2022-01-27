from typing import Dict, Optional, List

import click
import click_config_file

from montecarlodata import settings
from montecarlodata.common.commands import DISAMBIGUATE_DC_OPTIONS
from montecarlodata.common.resources import CloudResourceService
from montecarlodata.discovery.networking import NetworkDiscoveryService
from montecarlodata.tools import add_common_options

# Shared command verbiage
PROFILE_VERBIAGE = 'If not specified, the one in the Monte Carlo CLI profile is used'
RESOURCE_VERBIAGE = 'This can be helpful if the resource and collector are in different accounts'


@click.group(help='Display information about resources.')
def discovery():
    """
    Group for any discovery related subcommands
    """
    pass


@discovery.command(help='List details about EMR clusters in a region.')
@click.option('--aws-profile', help=f'AWS profile. {PROFILE_VERBIAGE}', required=False)
@click.option('--aws-region', help=f'AWS region. {PROFILE_VERBIAGE}', required=False)
@click.option('--only-log-locations', help='Display only unique log locations', is_flag=True, default=False)
@click.option('--created-after', help='Display clusters created after date (e.g. 2017-07-04T00:01:30)', required=False)
@click.option('--state', help='Cluster states', required=False, type=click.Choice(['active', 'terminated', 'failed']),
              multiple=True)
@click.option('--no-grid',
              help='Do not display as grid and print as results are available, useful when the cluster list is large',
              is_flag=True, default=False)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
@click.pass_obj
def list_emr_clusters(ctx: Dict, aws_profile: Optional[str] = None, aws_region: Optional[str] = None,
                      only_log_locations: Optional[bool] = False, created_after: Optional[str] = None,
                      state: Optional[List] = None, no_grid: Optional[bool] = False) -> None:
    CloudResourceService(config=ctx['config'], aws_profile_override=aws_profile, aws_region_override=aws_region) \
        .list_emr_clusters(only_log_locations=only_log_locations, created_after=created_after, states=state,
                           no_grid=no_grid)


@discovery.command(help='Alpha network recommender. Attempts to analyze and makes recommendations on how to connect a '
                        'resource with the Data Collector.')
@click.pass_obj
@click.option('--resource-identifier', required=True,
              help='Identifier for the AWS resource you want to connect the Collector with (e.g. Redshift cluster ID).')
@click.option('--resource-type', required=True, help='Type of AWS resource.',
              type=click.Choice(NetworkDiscoveryService.MCD_NETWORK_REC_RESOURCE_TYPE_MAP.keys()))
@click.option('--resource-aws-region', required=False,
              help='Override the AWS region where the resource is located. Defaults to the region where the collector is hosted.')
@click.option('--resource-aws-profile', required=False,
              help=f'Override the AWS profile use by the CLI for the resource. {RESOURCE_VERBIAGE}.')
@click.option('--collector-aws-profile', required=False,
              help=f'Override the AWS profile use by the CLI for the Collector. {RESOURCE_VERBIAGE}.')
@add_common_options(DISAMBIGUATE_DC_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def network_recommender(ctx, **kwargs):
    NetworkDiscoveryService(config=ctx['config'], aws_wrapper=None).recommend_network_dispatcher(**kwargs)
