# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
import time

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, BearerTokenAuthenticator, CloudPakForDataAuthenticator
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_watson_openscale import APIClient

logger = FastpathLogger(__name__)


class OpenScale:

    DEFAULT_DATAMART_SCHEMA_NAME = 'wosfastpath'

    def __init__(self, args, credentials, database_credentials, ml_engine_credentials):
        self._args = args
        self._credentials = credentials
        self._keep_schema = self._args.keep_schema
        self._verify = False if self._args.is_icp else True
        self.timers = dict()
        self._database_credentials = database_credentials
        self._ml_engine_credentials = ml_engine_credentials
        self._database = self._get_database()
        start = time.time()
        wos_instance_id = args.datamart_id if args.datamart_id else None
        if not self._args.is_icp:
            if self._args.apikey:
                self._client = APIClient(
                    authenticator=IAMAuthenticator(apikey=credentials['apikey'], url=self._args.env_dict['iam_url']),
                    service_url=credentials['url'],
                    service_instance_id=wos_instance_id
                )
            elif self._args.iam_token:
                self._client = APIClient(
                    authenticator=BearerTokenAuthenticator(bearer_token=self._args.iam_token),
                    service_url=credentials['url'],
                    service_instance_id=wos_instance_id
                )
        else:
            if self._args.username:
                self._client = APIClient(
                    authenticator=CloudPakForDataAuthenticator(
                        username=self._args.username,
                        password=self._args.password,
                        url=self._args.url,
                        disable_ssl_verification=True,
                    ),
                    service_url=credentials['url'],
                    service_instance_id=wos_instance_id,
                    bedrock_url=self._args.bedrock_url
                )
            elif self._args.iam_token:
                self._client = APIClient(
                    authenticator=BearerTokenAuthenticator(
                        bearer_token=self._args.iam_token
                    ),
                    service_url=credentials['url'],
                    service_instance_id=wos_instance_id
                )
        elapsed = time.time() - start
        self._datamart_name = self._get_datamart_name()
        logger.log_info('Using {} Python Client version: {}'.format(self._args.service_name, self._client.version))
        self.timer('connect to APIClient', elapsed)

    def get_datamart_id(self):
        if 'data_mart_id' in self._credentials:
            return self._credentials['data_mart_id']

    def _get_datamart_name(self):
        datamart_name = self._args.datamart_name
        if datamart_name is None:
            if self._database_credentials: # use the datamart database connection user id
                if self._database_credentials['db_type'] == 'postgresql':
                    if 'connection' in self._database_credentials and 'postgres' in self._database_credentials['connection']: # icd
                        datamart_name = self._database_credentials['connection']['postgres']['authentication']['username']
                    else: # compose
                        datamart_name = self._database_credentials['uri'].split('@')[0].split('//')[1].split(':')[0]
                elif self._database_credentials['db_type'] == 'db2':
                    datamart_name = self._database_credentials['username']
                else:
                    raise Exception('Invalid database type specified. Only "postgresql" and "db2" are supported.')
            else:
                datamart_name = OpenScale.DEFAULT_DATAMART_SCHEMA_NAME # for internal database
        self._args.datamart_name = datamart_name
        return datamart_name

    def _get_database(self):
        if not self._database_credentials:
            return None
        if self._database_credentials['db_type'] == 'postgresql':
            if 'connection' in self._database_credentials and 'postgres' in self._database_credentials['connection']: # icd
                from ibm_ai_openscale_cli.database_classes.postgres_icd import PostgresICD
                return PostgresICD(self._database_credentials)
            else: # compose
                from ibm_ai_openscale_cli.database_classes.postgres_compose import PostgresCompose
                return PostgresCompose(self._database_credentials)
        elif self._database_credentials['db_type'] == 'db2':
            from ibm_ai_openscale_cli.database_classes.db2 import DB2, validate_db2_credentials
            self._database_credentials = validate_db2_credentials(self._database_credentials)
            return DB2(self._database_credentials)
        else:
            raise Exception('Invalid database type specified. Only "postgresql" and "db2" are supported.')

    def timer(self, tag, seconds, count=1):
        if tag not in list(self.timers):
            self.timers[tag] = { 'count': 0, 'seconds': 0 }
        self.timers[tag]['count'] += count
        self.timers[tag]['seconds'] += seconds
        logger.log_timer('{} in {:.3f} seconds'.format(tag, seconds))
