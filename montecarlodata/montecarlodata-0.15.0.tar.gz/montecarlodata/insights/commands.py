import click

from montecarlodata.insights.data_insights import InsightsService
from montecarlodata.insights.fields import KEY_ASSETS_INSIGHT_NAME, FILE_SCHEME, S3_SCHEME, SCHEME_DELIM, \
    COVERAGE_OVERVIEW_INSIGHT_NAME, CLEANUP_SUGGESTIONS_INSIGHT_NAME, EVENTS_INSIGHT_NAME, READ_WRITE_INSIGHT_NAME, \
    INCIDENT_QUERY_INSIGHT_NAME, DETERIORATING_QUERY_INSIGHT_NAME, RULES_AND_SLIS_INSIGHT_NAME
from montecarlodata.tools import add_common_options

# Shared command verbiage
GET_VERBIAGE = f"""
\b\n
DESTINATION is the path where the insight will be written to.

Supported schemes:\n
    '{FILE_SCHEME}{SCHEME_DELIM}' - save insight locally.\n
    '{S3_SCHEME}{SCHEME_DELIM}' - save insight to S3.

Notice - Will overwrite a file if it exists in the path and create any missing directories or prefixes.
"""

# Options shared across commands
GET_OPTIONS = [
    click.argument('destination', required=True),
    click.option('--aws-profile', required=False, help=f'AWS profile. If not specified, the one in the Monte Carlo '
                                                       f'CLI profile is used when uploading to S3.'),
    click.option('--dry', required=False, is_flag=True, help='Echo temporary presigned URL for the insight and quit.')
]


@click.group(help='Aggregated insights on your tables.')
def insights():
    """
    Group for any insight related subcommands
    """
    pass


@insights.command(help='List insights details and availability.', name='list')
@click.pass_obj
def list_insights(ctx):
    InsightsService(config=ctx['config']).echo_insights()


@insights.command(help=f'Get key assets insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_key_assets(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=KEY_ASSETS_INSIGHT_NAME, **kwargs)


@insights.command(help=f'Get coverage overview (monitors) insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_coverage_overview(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=COVERAGE_OVERVIEW_INSIGHT_NAME, **kwargs)


@insights.command(help=f'Get cleanup suggestions insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_cleanup_suggestions(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=CLEANUP_SUGGESTIONS_INSIGHT_NAME, **kwargs)


@insights.command(help=f'Get events insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_events(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=EVENTS_INSIGHT_NAME, **kwargs)


@insights.command(help=f'Get table read/write activity insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_table_activity(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=READ_WRITE_INSIGHT_NAME, **kwargs)


@insights.command(help=f'Get incident query changes insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_incident_queries(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=INCIDENT_QUERY_INSIGHT_NAME, **kwargs)


@insights.command(help=f'Get deteriorating queries insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_deteriorating_queries(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=DETERIORATING_QUERY_INSIGHT_NAME, **kwargs)


@insights.command(help=f'Get rule and SLI results insight. {GET_VERBIAGE}')
@add_common_options(GET_OPTIONS)
@click.pass_obj
def get_rule_results(ctx, **kwargs):
    InsightsService(config=ctx['config']).get_insight(insight=RULES_AND_SLIS_INSIGHT_NAME, **kwargs)
