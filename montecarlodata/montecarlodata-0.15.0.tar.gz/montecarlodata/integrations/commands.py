import click
import click_config_file

import montecarlodata.settings as settings
from montecarlodata.integrations.onboarding.bi.reports import ReportsOnboardingService
from montecarlodata.common.commands import DISAMBIGUATE_DC_OPTIONS
from montecarlodata.common.resources import CloudResourceService
from montecarlodata.integrations.info.status import OnboardingStatusService
from montecarlodata.integrations.onboarding.data_lake.events import EventsOnboardingService
from montecarlodata.integrations.onboarding.data_lake.glue_athena import GlueAthenaOnboardingService
from montecarlodata.integrations.onboarding.data_lake.hive import HiveOnboardingService
from montecarlodata.integrations.onboarding.data_lake.presto import PrestoOnboardingService
from montecarlodata.integrations.onboarding.data_lake.spark import SparkOnboardingService, \
    SPARK_HTTP_MODE_CONFIG_TYPE, SPARK_DATABRICKS_CONFIG_TYPE, SPARK_BINARY_MODE_CONFIG_TYPE
from montecarlodata.integrations.onboarding.fields import (
    CONNECTION_TO_WAREHOUSE_TYPE_MAP,
    GLUE_CONNECTION_TYPE,
    GQL_TO_FRIENDLY_CONNECTION_MAP,
    HIVE_MYSQL_CONNECTION_TYPE,
    HIVE_S3_CONNECTION_TYPE,
    PRESTO_S3_CONNECTION_TYPE,
    S3_METADATA_EVENT_TYPE,
    S3_QL_EVENT_TYPE,
    SECRETS_MANAGER_CREDENTIAL_MECHANISM,
    SELF_HOSTING_MECHANISMS,
)
from montecarlodata.integrations.onboarding.operations.connection_ops import ConnectionOperationsService
from montecarlodata.integrations.onboarding.self_hosted_credentials import SelfHostedCredentialOnboardingService
from montecarlodata.integrations.onboarding.warehouse.warehouses import WarehouseOnboardingService
from montecarlodata.integrations.keys import IntegrationKeyScope, IntegrationKeyService
from montecarlodata.tools import add_common_options, validate_json_callback, AdvancedOptions, \
    convert_uuid_callback, convert_empty_str_callback

# Shared command verbiage
METADATA_VERBIAGE = 'For metadata'
QL_VERBIAGE = 'For query logs'
SQL_VERBIAGE = 'For health queries'
EVENT_VERBIAGE = 'For tracking data freshness and volume at scale. Requires s3 notifications to be configured first'
REGION_VERBIAGE = 'If not specified the region the collector is deployed in is used'
WAREHOUSE_VERBIAGE = 'For metadata, query logs and metrics'
BI_VERBIAGE = 'For reports'
PASSWORD_VERBIAGE = f'If you prefer a prompt (with hidden input) enter {settings.SHOW_PROMPT_VALUE}'
RESOURCE_VERBIAGE = 'This can be helpful if the resources are in different accounts'

# Options shared across commands
ROLE_OPTIONS = [
    click.option('--role', help='Assumable role ARN to use for accessing AWS resources.', required=False),
    click.option('--external-id', help='An external id, per assumable role conditions.', required=False),
]
S3_OPTIONS = [
    click.option('--bucket', help='S3 Bucket where query logs are contained.', required=True),
    click.option('--prefix', help='Path to query logs.', required=True),
    *ROLE_OPTIONS
]
EVENT_OPTIONS = [
    click.option('--enable/--disable', 'toggle', help='Enable or disable events. Enables if not specified.',
                 default=True)
]
DATABASE_OPTIONS = [
    click.option('--host', help='Hostname.', required=True),
    click.option('--user', help='Username with access to the database.', required=True),
    click.option('--database', help='Name of database.', required=True),
    click.option('--password', help=f'User\'s password. {PASSWORD_VERBIAGE}.', required=True, cls=AdvancedOptions, prompt_if_requested=True)
]

CONNECTION_OPTIONS = [
    click.option('--connection-id', help='ID for the connection.', required=True, type=click.UUID, callback=convert_uuid_callback)
]

ONBOARDING_CONFIGURATION_OPTIONS = [
    *DISAMBIGUATE_DC_OPTIONS,
    click.option('--skip-validation', is_flag=True, help='Skip all connection tests.',
                 cls=AdvancedOptions, mutually_exclusive_options=['validate_only']),
    click.option('--validate-only', is_flag=True, help='Run connection tests without adding.',
                 cls=AdvancedOptions, mutually_exclusive_options=['skip_validation']),
    click.option('--auto-yes', is_flag=True, help='Skip any interactive approval.', default=False, show_default=True)
]

NETWORK_OPTIONS = [
    click.option('--test-network-only', 'skip_permission_tests', is_flag=True, default=False, show_default=True,
                 cls=AdvancedOptions, mutually_exclusive_options=['skip_validation'],
                 help='Skip any permission tests. Only validates network connection between the collector and resource can be established.')
]

BI_OPTIONS = [
    click.option('--verify-ssl/--no-verify-ssl', 'verify_ssl', required=False, default=True, show_default=True,
                 help='Whether to verify the SSL connection (uncheck for self-signed certs).')
]


@click.group(help='Manage or integrate an asset with Monte Carlo.')
def integrations():
    """
    Group for any integration related subcommands
    """
    pass


@integrations.command(help=f'Setup a Hive metastore integration (MySQL). {METADATA_VERBIAGE}.')
@click.pass_obj
@click.option('--port', help='HTTP port.', default=3306, type=click.INT, show_default=True)
@click.option('--use-ssl', help='Use SSL to connect (using AWS RDS certificates).', required=False, is_flag=True,
              default=False, show_default=True)
@click.option('--catalog', help='Presto catalog name. For using multiple hive clusters with Presto. '
                                'Uses \'hive\' if not specified.', required=False)
@add_common_options(DATABASE_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_hive_metastore(ctx, database, **kwargs):
    """
    Onboard a hive metastore connection (MySQL)
    """
    HiveOnboardingService(config=ctx['config']).onboard_hive_mysql(dbName=database, **kwargs)


@integrations.command(help=f'Setup a Presto SQL integration. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--host', help='Hostname.', required=True)
@click.option('--port', help='HTTP port.', default=8889, type=click.INT, show_default=True)
@click.option('--user', help='Username with access to catalog/schema.', required=False)
@click.option('--password', help=f'User\'s password. {PASSWORD_VERBIAGE}', required=False, cls=AdvancedOptions, prompt_if_requested=True)
@click.option('--catalog', help='Mount point to access data source.', required=False)
@click.option('--schema', help='Schema to access.', required=False)
@click.option('--http-scheme', help='Scheme for authentication.',
              type=click.Choice(['http', 'https'], case_sensitive=True), required=True)
@click.option('--cert-file', help='Local SSL certificate file to upload to collector.', required=False,
              type=click.Path(dir_okay=False, exists=True), cls=AdvancedOptions, mutually_exclusive_options=['cert_s3'])
@click.option('--cert-s3', help='Object path (key) to a certificate already uploaded to the collector.',
              required=False, cls=AdvancedOptions, mutually_exclusive_options=['cert_file'])
@click.option('--skip-cert-verification', help='Skip SSL certificate verification.', required=False, is_flag=True)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_presto(ctx, password, **kwargs):
    """
    Onboard a presto sql connection
    """
    if not password:
        password = None  # make explicitly null if not set. Prompts can't be None
    PrestoOnboardingService(config=ctx['config']).onboard_presto_sql(password=password, **kwargs)


@integrations.command(help=f'Setup a Hive SQL integration. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--host', help='Hostname.', required=True)
@click.option('--database', help='Name of database.', required=False)
@click.option('--port', help='HTTP port.', default=10000, type=click.INT, show_default=True)
@click.option('--user', help='Username with access to hive.', required=True)
@click.option('--auth-mode', help='Hive authentication mode.', required=False, default='SASL',
              type=click.Choice(['SASL', 'NOSASL']), show_default=True)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_hive(ctx, user, **kwargs):
    HiveOnboardingService(config=ctx['config']).onboard_hive_sql(username=user, **kwargs)


@integrations.command(help=f'Setup a Presto logs integration (S3). {QL_VERBIAGE}.')
@click.pass_obj
@add_common_options(S3_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_presto_logs(ctx, role, **kwargs):
    """
    Onboard a presto logs (s3) connection
    """
    PrestoOnboardingService(config=ctx['config']).onboard_presto_s3(assumable_role=role, **kwargs)


@integrations.command(help=f'Setup a Hive EMR logs integration (S3). {QL_VERBIAGE}.')
@click.pass_obj
@add_common_options(S3_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_hive_logs(ctx, role, **kwargs):
    """
    Onboard a hive emr (s3) connection
    """
    HiveOnboardingService(config=ctx['config']).onboard_hive_s3(assumable_role=role, **kwargs)


@integrations.command(help=f'Setup a Glue integration. {METADATA_VERBIAGE}.')
@click.pass_obj
@click.option('--region', help=f'Glue catalog region. {REGION_VERBIAGE}.', required=False)
@add_common_options(ROLE_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_glue(ctx, role, region, **kwargs):
    """
    Onboard a glue connection
    """
    GlueAthenaOnboardingService(config=ctx['config']).onboard_glue(assumable_role=role, aws_region=region, **kwargs)


@integrations.command(help='Setup an Athena integration. For query logs and health queries.')
@click.pass_obj
@click.option('--catalog', help='Glue data catalog. If not specified the AwsDataCatalog is used.', required=False)
@click.option('--workgroup',
              help='Workbook for running queries and retrieving logs. If not specified the primary is used.',
              required=False)
@click.option('--region', help=f'Athena cluster region. {REGION_VERBIAGE}.', required=False)
@add_common_options(ROLE_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_athena(ctx, role, region, **kwargs):
    """
    Onboard an athena connection
    """
    GlueAthenaOnboardingService(config=ctx['config']).onboard_athena(assumable_role=role, aws_region=region, **kwargs)


@integrations.command(help=f'Setup a thrift binary Spark integration. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--host', help='Hostname.', required=True)
@click.option('--database', help='Name of database.', required=True)
@click.option('--port', help='Port.', default=10000, type=click.INT, show_default=True)
@click.option('--user', help='Username with access to spark.', required=True)
@click.option('--password', help=f'User\'s password. {PASSWORD_VERBIAGE}.', required=True,
              cls=AdvancedOptions, prompt_if_requested=True)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_spark_binary_mode(ctx, user, **kwargs):
    """
    Onboard a spark connection, thrift binary mode
    """
    SparkOnboardingService(config=ctx['config']).onboard_spark(SPARK_BINARY_MODE_CONFIG_TYPE, username=user, **kwargs)


@integrations.command(help=f'Setup a thrift HTTP Spark integration. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--url', help='HTTP URL.', required=True)
@click.option('--user', help='Username with access to spark.', required=True)
@click.option('--password', help=f'User\'s password. {PASSWORD_VERBIAGE}.', required=True,
              cls=AdvancedOptions, prompt_if_requested=True)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_spark_http_mode(ctx, user, **kwargs):
    """
    Onboard a spark connection, thrift http mode
    """
    SparkOnboardingService(config=ctx['config']).onboard_spark(SPARK_HTTP_MODE_CONFIG_TYPE, username=user, **kwargs)


@integrations.command(help=f'Setup a Spark integration for Databricks. {SQL_VERBIAGE}.')
@click.pass_obj
@click.option('--workspace-url', help='Databricks workspace URL.', required=True)
@click.option('--workspace-id', help='Databricks workspace ID.', required=True)
@click.option('--cluster-id', help='Databricks cluster ID.', required=True)
@click.option('--token', help=f'Databricks access token. {PASSWORD_VERBIAGE}.', required=True,
              cls=AdvancedOptions, prompt_if_requested=True)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_spark_databricks(ctx, **kwargs):
    """
    Onboard a spark connection, databricks
    """
    SparkOnboardingService(config=ctx['config']).onboard_spark(SPARK_DATABRICKS_CONFIG_TYPE, **kwargs)


@integrations.command(help=f'Setup a Redshift integration. {WAREHOUSE_VERBIAGE}.')
@click.pass_obj
@click.option('--port', help='HTTP port.', default=5439, type=click.INT, show_default=True)
@click.option('--name', help='Friendly name for the warehouse.', required=True)
@add_common_options(DATABASE_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@add_common_options(NETWORK_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_redshift(ctx, database, name, **kwargs):
    """
    Onboard a redshift connection
    """
    WarehouseOnboardingService(config=ctx['config']).onboard_redshift(dbName=database, warehouseName=name, **kwargs)


@integrations.command(help=f'Setup a Snowflake integration. {WAREHOUSE_VERBIAGE}.')
@click.pass_obj
@click.option('--user', help='User with access to snowflake.', required=True)
@click.option('--account', help='Snowflake account name.', required=True)
@click.option('--warehouse', help='Name of the warehouse for the user.', required=True)
@click.option('--password', help=f'User\'s password. {PASSWORD_VERBIAGE}.', required=True,
              cls=AdvancedOptions, prompt_if_requested=True)
@click.option('--name', help='Friendly name for the warehouse.', required=True)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_snowflake(ctx, name, **kwargs):
    """
    Onboard a snowflake connection
    """
    WarehouseOnboardingService(config=ctx['config']).onboard_snowflake(warehouseName=name, **kwargs)


@integrations.command(help=f'Setup a BigQuery integration. {WAREHOUSE_VERBIAGE}.')
@click.pass_obj
@click.option('--key-file', help='JSON Key file.', type=click.Path(exists=True), required=True)
@click.option('--name', help='Friendly name for the warehouse.', required=True)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_bigquery(ctx, key_file, name, **kwargs):
    """
    Onboard a BigQuery connection
    """
    WarehouseOnboardingService(config=ctx['config']).onboard_bq(ServiceFile=key_file, warehouseName=name, **kwargs)


@integrations.command(help='Setup an integration that uses self-hosted credentials.')
@click.pass_obj
@click.option(
    '--connection-type',
    help='Type of connection.',
    required=True,
    type=click.Choice(GQL_TO_FRIENDLY_CONNECTION_MAP.keys(), case_sensitive=False),
    cls=AdvancedOptions,
    values_with_required_options=CONNECTION_TO_WAREHOUSE_TYPE_MAP.keys(),
    required_options_for_values=['name'],
)
@click.option(
    '--mechanism',
    help='Credential self-hosting mechanism.',
    required=True,
    type=click.Choice(SELF_HOSTING_MECHANISMS, case_sensitive=False),
    default=SECRETS_MANAGER_CREDENTIAL_MECHANISM,
)
@click.option('--key', help='Identifier for credentials within self-hosting mechanism.', required=True)
@click.option('--name', help='Friendly name for the warehouse. Required for warehouses.', required=False)
@add_common_options(ROLE_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_self_hosted_credentials(ctx, mechanism, key, role, name, **kwargs):
    """
    Onboard a connection with self-hosted credentials
    """
    SelfHostedCredentialOnboardingService(config=ctx['config']).onboard_connection(
        self_hosting_mechanism=mechanism,
        self_hosting_key=key,
        assumable_role=role,
        warehouseName=name,
        **kwargs
    )


@integrations.command(help=f'Toggle S3 metadata events for Hive/Presto. {EVENT_VERBIAGE}.')
@click.pass_obj
@add_common_options(EVENT_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def toggle_hive_metadata_events(ctx, toggle):
    """
    Toggle s3 metadata events for a hive lake
    """
    EventsOnboardingService(config=ctx['config']).toggle_event_configuration(enable=toggle,
                                                                             connection_type=HIVE_MYSQL_CONNECTION_TYPE,
                                                                             event_type=S3_METADATA_EVENT_TYPE)


@integrations.command(help=f'Toggle S3 metadata events for Glue/Athena. {EVENT_VERBIAGE}.')
@click.pass_obj
@add_common_options(EVENT_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def toggle_glue_metadata_events(ctx, toggle):
    """
    Toggle s3 metadata events for a glue lake
    """
    EventsOnboardingService(config=ctx['config']).toggle_event_configuration(enable=toggle,
                                                                             connection_type=GLUE_CONNECTION_TYPE,
                                                                             event_type=S3_METADATA_EVENT_TYPE)


@integrations.command(help=f'Toggle S3 query log events. {EVENT_VERBIAGE}.')
@click.pass_obj
@add_common_options(EVENT_OPTIONS)
@add_common_options(ROLE_OPTIONS)
@click.option('--connection-type', help='Type of the integration.',
              type=click.Choice([HIVE_S3_CONNECTION_TYPE, PRESTO_S3_CONNECTION_TYPE], case_sensitive=True),
              required=False)
@click.option('--format-type', help='Query log format.',
              type=click.Choice(['hive-emr', 'custom'], case_sensitive=True),
              required=False)
@click.option('--source-format', help='Query log file format. Only required when "custom" is used.',
              type=click.Choice(['json', 'jsonl'], case_sensitive=True),
              required=False)
@click.option('--mapping-file',
              help='Mapping of expected to existing query log fields. Only required if "custom" is used.',
              type=click.Path(exists=True),
              required=False)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def toggle_ql_events(ctx, toggle, role, **kwargs):
    """
    Toggle s3 query log events for a lake
    """
    EventsOnboardingService(config=ctx['config']).toggle_event_configuration(enable=toggle,
                                                                             event_type=S3_QL_EVENT_TYPE,
                                                                             assumable_role=role,
                                                                             **kwargs)


@integrations.command(help=f'Setup a Tableau integration. {BI_VERBIAGE}.')
@click.pass_obj
@click.option('--token-name', help='Name for the personal access token.', cls=AdvancedOptions,
              mutually_exclusive_options=['password', 'username'], required_with_options=['token_value'],
              at_least_one_set=['password', 'username', 'token_name', 'token_value'])
@click.option('--token-value', help=f'Value for the personal access token. {PASSWORD_VERBIAGE}.', cls=AdvancedOptions,
              mutually_exclusive_options=['password', 'username'], required_with_options=['token_name'],
              prompt_if_requested=True)
@click.option('--password', help=f'Password for the service account. {PASSWORD_VERBIAGE}.', cls=AdvancedOptions,
              mutually_exclusive_options=['token_name', 'token_value'], required_with_options=['user'],
              prompt_if_requested=True)
@click.option('--user', help='Username for the service account.', cls=AdvancedOptions,
              mutually_exclusive_options=['token_name', 'token_value'], required_with_options=['password'])
@click.option('--site-name', help='The Tableau site name.', required=True)
@click.option('--server-name', help='The Tableau server name.', required=True)
@add_common_options(BI_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_tableau(ctx, user, **kwargs):
    """
    Onboard a tableau connection
    """
    ReportsOnboardingService(config=ctx['config']).onboard_tableau(username=user, **kwargs)


@integrations.command(help=f'Setup a Looker metadata integration. {BI_VERBIAGE}.')
@click.pass_obj
@click.option('--host-url', 'base_url', help='Looker host url.', required=True)
@click.option('--client-id', help='Looker client id.', required=True)
@click.option('--client-secret', help=f'Looker client secret (API key). {PASSWORD_VERBIAGE}.',
              required=True, cls=AdvancedOptions, prompt_if_requested=True)
@add_common_options(BI_OPTIONS)
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
def add_looker(ctx, **kwargs):
    """
    Onboard a looker metadata connection
    """
    ReportsOnboardingService(config=ctx['config']).onboard_looker_metadata(**kwargs)


@integrations.command(help=f'Setup a Looker ML (git) integration. {BI_VERBIAGE}.')
@click.pass_obj
@click.option('--ssh-key', help='The ssh key for git ssh integrations.', required=False,
              type=click.Path(dir_okay=False, exists=True),
              cls=AdvancedOptions, mutually_exclusive_options=['token', 'username'])
@click.option('--repo-url', help='Repository URL as ssh://[user@]server/project.git or the shorter '
                                 'form [user@]server:project.git for ssh. For https, use https://server/project.git.',
              required=True)
@click.option('--token', help='Git Access Token to be used for Https instead of ssh key.', required=False,
              cls=AdvancedOptions, mutually_exclusive_options=['ssh-key'])
@click.option('--username', help='Git username to be used in conjunction with the access token. This is only '
                                 'required for BitBucket integrations.',
              cls=AdvancedOptions, required=False, mutually_exclusive_options=['ssh-key'])
@add_common_options(ONBOARDING_CONFIGURATION_OPTIONS)
def add_looker_git(ctx, **kwargs):
    """
    Onboard a looker metadata connection
    """
    ReportsOnboardingService(config=ctx['config']).onboard_looker_git(**kwargs)


@integrations.command(help='List all active connections.', name='list')
@click.pass_obj
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def display_integrations(ctx):
    """
    Display active integrations
    """
    OnboardingStatusService(config=ctx['config']).display_integrations()


@integrations.command(help='Create an IAM role from a policy FILE. '
                           'The returned role ARN and external id should be used for adding lake assets.')
@click.pass_obj
@click.argument('file', type=click.Path(dir_okay=False, exists=True))
@click.option('--aws-profile', required=False,
              help='Override the AWS profile used by the CLI, which determines where the role is created. '
                   'This can be helpful when the account that manages the asset is not the same as the collector.')
def create_role(ctx, file, aws_profile):
    """
    Create a collector compatible role from the provided policy
    """
    CloudResourceService(config=ctx['config'], aws_profile_override=aws_profile).create_role(path_to_policy_doc=file)


@integrations.command(help='Update credentials for a connection. Only replaces/inserts the keys in changes by default.', name='update')
@click.pass_obj
@add_common_options(CONNECTION_OPTIONS)
@click.option('--changes', help="""
              Credential key,value pairs as JSON.
              \b
              \n
              E.g. --changes '{"user":"Apollo"}'
              """, required=True, callback=validate_json_callback)
@click.option('--skip-validation', help='Skip validating credentials.', default=False, show_default=True, is_flag=True)
@click.option('--replace-all', help='Replace all credentials rather than just inserting/updating the keys in changes.', default=False, show_default=True, is_flag=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def update_credentials(ctx, connection_id, changes, skip_validation, replace_all):
    """
    Update credentials for a connection
    """
    ConnectionOperationsService(config=ctx['config']).update_credentials(
        connection_id=connection_id,
        changes=changes,
        should_validate=not skip_validation,
        should_replace=replace_all
    )


@integrations.command(help='Remove an existing connection. Deletes any associated jobs, monitors, etc.', name='remove')
@click.pass_obj
@add_common_options(CONNECTION_OPTIONS)
@click.option('--no-prompt', help='Don\'t ask for confirmation.', default=False, show_default=True, is_flag=True)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def remove_connection(ctx, **kwargs):
    """
    Remove connection by ID
    """
    ConnectionOperationsService(config=ctx['config']).remove_connection(**kwargs)


@integrations.command(help='Retest an existing connection.', name='test')
@click.pass_obj
@add_common_options(CONNECTION_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def echo_test_existing(ctx, **kwargs):
    """
    Tests an existing connection and echos results in pretty JSON.
    """
    ConnectionOperationsService(config=ctx['config']).echo_test_existing(**kwargs)


@integrations.command(help='Setup S3 event notifications for a lake.')
@click.pass_obj
@click.option('--bucket', 'bucket_name', required=True, help='Name of bucket to enable events for.')
@click.option('--prefix', default=None, callback=convert_empty_str_callback, required=False,
              help='Limit the notifications to objects starting with a prefix (e.g. \'data/\').')
@click.option('--suffix', default=None, callback=convert_empty_str_callback, required=False,
              help='Limit notifications to objects ending with a suffix (e.g. \'.csv\').')
@click.option('--topic-arn', default=None, callback=convert_empty_str_callback, required=False,
              help='Use an existing SNS topic (same region as the bucket). Creates a topic if one is not specified or '
                   'if an MCD topic does not already exist in the region.')
@click.option('--collector-aws-profile', required=False,
              help=f'Override the AWS profile use by the CLI for operations on SQS/Collector. {RESOURCE_VERBIAGE}.')
@click.option('--resource-aws-profile', 'bucket_aws_profile', required=False,
              help=f'Override the AWS profile use by the CLI for operations on S3/SNS. {RESOURCE_VERBIAGE}.')
@click.option('--event-type', required=True, default=CloudResourceService.MCD_EVENT_TYPE_MD, show_default=True,
              help='Type of event to setup.',
              type=click.Choice(CloudResourceService.MCD_EVENT_TYPE_FRIENDLY_TO_COLLECTOR_OUTPUT_MAP.keys(), case_sensitive=True))
@click.option('--auto-yes', is_flag=True, help='Skip any interactive approval.', default=False, show_default=True)
@add_common_options(DISAMBIGUATE_DC_OPTIONS)
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def add_events(ctx, **kwargs):
    CloudResourceService(config=ctx['config'], aws_wrapper=None).add_events(**kwargs)


@integrations.command(help='Create an integration key. The resulting key id and secret will be printed to the console.')
@click.pass_obj
@click.option('--description',
              required=True,
              help='Key description.')
@click.option('--scope',
              required=True,
              type=click.Choice(IntegrationKeyScope.values(), case_sensitive=False),
              help='Key scope (integration the key can be used for).')
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def create_key(ctx, **kwargs):
    IntegrationKeyService(config=ctx['config']).create(**kwargs)


@integrations.command(help='Delete an integration key.')
@click.pass_obj
@click.option('--key-id', required=True, help='Integration key id.')
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def delete_key(ctx, **kwargs):
    IntegrationKeyService(config=ctx['config']).delete(**kwargs)


@integrations.command(help='List all integration keys.')
@click.pass_obj
@click_config_file.configuration_option(settings.OPTION_FILE_FLAG)
def list_keys(ctx):
    IntegrationKeyService(config=ctx['config']).get_all()
