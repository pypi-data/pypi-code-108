# Query responses
EXPECTED_ADD_CONNECTION_RESPONSE_FIELD = 'addConnection'
EXPECTED_GENERIC_DB_GQL_RESPONSE_FIELD = 'testDatabaseCredentials'
EXPECTED_HIVE_S3_GQL_RESPONSE_FIELD = 'testS3Credentials'
EXPECTED_HIVE_SQL_GQL_RESPONSE_FIELD = 'testHiveCredentials'
EXPECTED_PRESTO_SQL_GQL_RESPONSE_FIELD = 'testPrestoCredentials'
EXPECTED_PRESTO_S3_GQL_RESPONSE_FIELD = 'testS3Credentials'
EXPECTED_GLUE_GQL_RESPONSE_FIELD = 'testGlueCredentials'
EXPECTED_ATHENA_GQL_RESPONSE_FIELD = 'testAthenaCredentials'
EXPECTED_SPARK_GQL_RESPONSE_FIELD = 'testSparkCredentials'
EXPECTED_SNOWFLAKE_GQL_RESPONSE_FIELD = 'testSnowflakeCredentials'
EXPECTED_BQ_GQL_RESPONSE_FIELD = 'testBqCredentials'
EXPECTED_SELF_HOSTED_GQL_RESPONSE_FIELD = 'testSelfHostedCredentials'
EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD = 'toggleEventConfig'
EXPECTED_UPDATE_CREDENTIALS_RESPONSE_FIELD = 'updateCredentials'
EXPECTED_REMOVE_CONNECTION_RESPONSE_FIELD = 'removeConnection'
EXPECTED_TEST_EXISTING_RESPONSE_FIELD = 'testExistingConnection'
EXPECTED_TEST_TABLEAU_RESPONSE_FIELD = 'testTableauCredentials'
EXPECTED_ADD_TABLEAU_RESPONSE_FIELD = 'addTableauAccount'
EXPECTED_LOOKER_METADATA_RESPONSE_FIELD = 'testLookerCredentials'
EXPECTED_LOOKER_GIT_SSH_RESPONSE_FILED = 'testLookerGitSshCredentials'
EXPECTED_LOOKER_GIT_CLONE_RESPONSE_FIELD = 'testLookerGitCloneCredentials'
EXPECTED_ADD_BI_RESPONSE_FIELD = 'addBiConnection'

# Available connections types
HIVE_MYSQL_CONNECTION_TYPE = 'hive-mysql'
HIVE_S3_CONNECTION_TYPE = 'hive-s3'
HIVE_SQL_CONNECTION_TYPE = 'hive'
PRESTO_SQL_CONNECTION_TYPE = 'presto'
PRESTO_S3_CONNECTION_TYPE = 'presto-s3'
GLUE_CONNECTION_TYPE = 'glue'
ATHENA_CONNECTION_TYPE = 'athena'
SPARK_CONNECTION_TYPE = 'spark'
REDSHIFT_CONNECTION_TYPE = 'redshift'
SNOWFLAKE_CONNECTION_TYPE = 'snowflake'
BQ_CONNECTION_TYPE = 'bigquery'
LOOKER_MD_CONNECTION_TYPE = 'looker'
LOOKER_GIT_SSH_CONNECTION_TYPE = 'looker-git-ssh'
LOOKER_GIT_CLONE_CONNECTION_TYPE = 'looker-git-clone'

# Available warehouse types
DATA_LAKE_WAREHOUSE_TYPE = 'data-lake'
REDSHIFT_WAREHOUSE_TYPE = REDSHIFT_CONNECTION_TYPE
SNOWFLAKE_WAREHOUSE_TYPE = SNOWFLAKE_CONNECTION_TYPE
BQ_WAREHOUSE_TYPE = BQ_CONNECTION_TYPE

CONNECTION_TO_WAREHOUSE_TYPE_MAP = {
    BQ_CONNECTION_TYPE: BQ_WAREHOUSE_TYPE,
    REDSHIFT_CONNECTION_TYPE: REDSHIFT_WAREHOUSE_TYPE,
    SNOWFLAKE_CONNECTION_TYPE: SNOWFLAKE_WAREHOUSE_TYPE,
}

# Available credential self-hosting mechanisms
SECRETS_MANAGER_CREDENTIAL_MECHANISM = 'secretsmanager'
SELF_HOSTING_MECHANISMS = [SECRETS_MANAGER_CREDENTIAL_MECHANISM]

# S3 event types
S3_METADATA_EVENT_TYPE = 's3_metadata_events'
S3_QL_EVENT_TYPE = 's3_ql_events'

# Job types
QL_JOB_TYPE = ['query_logs']

# Job limits
PRESTO_CATALOG_KEY = 'catalog_name'
HIVE_GET_PARTS_KEY = 'get_partition_locations'
HIVE_MAX_PARTS_KEY = 'max_partition_locations'
HIVE_MAX_PARTS_DEFAULT_VALUE = 50

# Certificate details
S3_CERT_MECHANISM = 'dc-s3'
PRESTO_CERT_PREFIX = 'certificates/presto/'
AWS_RDS_CA_CERT = 'https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem'

# Connections to friendly name (i.e. human presentable) map
GQL_TO_FRIENDLY_CONNECTION_MAP = {
    HIVE_MYSQL_CONNECTION_TYPE: 'Hive (metastore)',
    HIVE_S3_CONNECTION_TYPE: 'Hive (EMR logs)',
    HIVE_SQL_CONNECTION_TYPE: 'Hive (SQL)',
    PRESTO_SQL_CONNECTION_TYPE: PRESTO_SQL_CONNECTION_TYPE.capitalize(),
    PRESTO_S3_CONNECTION_TYPE: 'Presto (logs)',
    GLUE_CONNECTION_TYPE: GLUE_CONNECTION_TYPE.capitalize(),
    ATHENA_CONNECTION_TYPE: 'Athena',
    SPARK_CONNECTION_TYPE: 'Spark (SQL)',
    REDSHIFT_CONNECTION_TYPE: REDSHIFT_CONNECTION_TYPE.capitalize(),
    SNOWFLAKE_CONNECTION_TYPE: SNOWFLAKE_CONNECTION_TYPE.capitalize(),
    BQ_CONNECTION_TYPE: 'BigQuery',
    LOOKER_MD_CONNECTION_TYPE: 'Looker (metadata)',
    LOOKER_GIT_SSH_CONNECTION_TYPE: 'Looker ML (git)',
    LOOKER_GIT_CLONE_CONNECTION_TYPE: 'Looker ML (git)',
}

# Verbiage
CONNECTION_TEST_SUCCESS_VERBIAGE = 'Connection test was successful!'
CONNECTION_TEST_FAILED_VERBIAGE = 'Connection test failed!'
ADD_CONNECTION_SUCCESS_VERBIAGE = 'Success! Added connection for '
ADD_CONNECTION_FAILED_VERBIAGE = 'Failed to add connection!'
VALIDATIONS_FAILED_VERBIAGE = 'Some validations failed. Would you like to create the connection anyway?'
OPERATION_ERROR_VERBIAGE = 'Operation failed - This might not be a valid connection for your account. ' \
                           'Please contact Monte Carlo.'
CONFIRM_CONNECTION_VERBIAGE = 'Please confirm you want to add this connection'
SKIP_ADD_CONNECTION_VERBIAGE = 'Skipping adding the connection.'
