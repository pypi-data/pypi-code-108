import os
import logging
import urllib
import time
import requests
from datetime import datetime
from itertools import islice
from abc import ABC, abstractmethod

UNINSTALLED_CONNECTORS = []

# common dependencies to snowflake and bigquery connectors
try:
    from google.cloud import storage
    from google.oauth2 import service_account
except ImportError:
    UNINSTALLED_CONNECTORS += ['bigquery', 'snowflake']

try:
    from google.cloud import bigquery
except ImportError:
    UNINSTALLED_CONNECTORS += ['bigquery']

try:
    import googleapiclient.discovery
    from google.api_core.exceptions import PreconditionFailed
    import snowflake.connector
except ImportError:
    UNINSTALLED_CONNECTORS += ['snowflake']

UNINSTALLED_CONNECTORS = list(set(UNINSTALLED_CONNECTORS))

logger = logging.getLogger('tinybird-connect')


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(text):
    logger.info(f"{_now()} - {text}")


class GCS():
    MAX_COMPOSE = 31
    READ_TIMEOUT = 3

    def __init__(self, options):
        self.options = options
        filename = options['service_account']
        if not filename:
            filename = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.credentials = service_account.Credentials.from_service_account_file(
            filename=filename,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.storage_client = storage.Client(project=options['project_id'], credentials=self.credentials)

    def gcs_url(self):
        return f'gcs://{self.bucket_name()}/'

    def gs_url(self):
        return f'gs://{self.bucket_name()}/'

    def bucket_name(self):
        return self.options['bucket_name']

    def sign(self, blob_name):
        bucket = self.storage_client.get_bucket(self.bucket_name())
        blob = bucket.get_blob(blob_name)
        if not blob:
            raise Exception('Warning: File not found. This probably just means there is no new data to load')
        return blob.generate_signed_url(expiration=86400, version='v4', scheme='https')

    def grant_access(self, member_name):
        role_name = self.get_role_name()
        service = googleapiclient.discovery.build(
            "iam", "v1", credentials=self.credentials
        )
        result = service.roles().list(parent='projects/' + self.options['project_id']).execute()
        exists = False if 'roles' not in result else any(role['title'] == role_name for role in result['roles'])
        if not exists:
            role_name = self.create_custom_role(service)
        self.add_member_to_bucket(member_name, role_name, self.bucket_name())

    def get_role_name(self):
        return f"{self.bucket_name().replace('-', '')}_5".lower()

    def create_custom_role(self, service):
        service.projects().roles().create(
            parent=f"projects/{self.options['project_id']}",
            body={
                'roleId': self.get_role_name(),
                'role': {
                    'title': self.get_role_name(),
                    'description': self.get_role_name(),
                    'includedPermissions': ['storage.objects.create', 'storage.buckets.get', 'storage.objects.delete', 'storage.objects.get', 'storage.objects.list'],
                    'stage': 'GA'
                }
            }).execute()
        return self.get_role_name()

    def add_member_to_bucket(self, member_name, iam_role, bucket_name, retry=True):
        try:
            project_id = self.options['project_id']
            role = f'projects/{project_id}/roles/{iam_role}'
            member = f'serviceAccount:{member_name}'

            bucket = self.storage_client.bucket(bucket_name)
            policy = bucket.get_iam_policy(requested_policy_version=3)
            policy.bindings.append({"role": role, "members": {member}})
            bucket.set_iam_policy(policy)
        except PreconditionFailed as e:
            _log(str(e))
            if retry:
                _log('retrying...')
                self.add_member_to_bucket(member_name, iam_role, bucket_name, retry=False)

    def compose(self, source_prefix, destination_blob_name):
        bucket = self.storage_client.bucket(self.bucket_name())
        retries = 0
        sources = None
        # for some reason when this list_blobs run in GH actions takes forever and fails
        # so retry many times with a lower timeout
        while not sources and retries < 5:
            try:
                sources = list(self.storage_client.list_blobs(
                    self.bucket_name(), prefix=source_prefix, timeout=self.READ_TIMEOUT, fields='items(name)'
                ))
            except requests.exceptions.ReadTimeout:
                _log("exception fetching blob list from GCS")
            retries += 1

        if sources is None:
            raise Exception("couldn't load list of blobs from GCS")

        _log(f'Exported {len(sources)} CSV files')
        if len(sources) == 0:
            raise Exception('Warning: Nothing to load. Aborting next steps')

        sources_iter = iter(sources)
        chunks = [list(islice(sources_iter, self.MAX_COMPOSE)) for i in range(0, 1 + int(len(sources) / self.MAX_COMPOSE))]
        blobs_to_delete = []
        if len(chunks) == 1:
            _log(f"Composing {destination_blob_name} from {','.join([c.name for c in chunks[0]])}")
            destination = bucket.blob(destination_blob_name)
            destination.content_type = "text/csv"
            destination.compose(chunks[0])
            blobs_to_delete += chunks[0]
        else:
            count = 0
            for chunk in chunks:
                destination_name = f'{destination_blob_name}_part{count}'
                if count > 0:
                    blob = bucket.get_blob(f'{destination_blob_name}_part{count - 1}')
                    chunk.append(blob)
                if count == len(chunks) - 1:
                    destination_name = destination_blob_name
                _log(f"[{count}] - Composing {destination_name} from {','.join([c.name for c in chunk])}")
                destination = bucket.blob(destination_name)
                destination.content_type = "text/csv"
                destination.compose(chunk)
                count = count + 1
                blobs_to_delete += chunk

        try:
            _log('Removing temp blobs')
            for blob in blobs_to_delete:
                blob.delete()
        except Exception:
            pass

        _log('Done composing!')

    def delete(self, blob_name):
        bucket = self.storage_client.bucket(self.bucket_name())
        bucket.delete_blob(blob_name)


class Connector(ABC):

    def __init__(self, options):
        self.options = options
        self.options['gcs'] = {
            'project_id': options['project_id'],
            'service_account': options['service_account'],
            'sign_service_account': options['service_account'],
            'bucket_name': options['bucket_name'],
        }
        self.gcs = GCS(self.options['gcs'])

    @abstractmethod
    def export_to_gcs(self, sql, destination):
        pass

    @abstractmethod
    def clean(self, blob_name):
        pass


class BigQuery(Connector):
    def __init__(self, options):
        super().__init__(options)
        self.configure()

    def configure(self):
        pass

    def datasource_analyze(self, resource):
        raise Exception("BigQuery does not support data source analyze")

    def export_to_gcs(self, sql, destination):
        mm = str(int(round(time.time() * 1000)))
        destination = f"{destination}_{mm}"
        with_headers: bool = self.options.get('with_headers')
        sql = f"""
                EXPORT DATA OPTIONS(
                    uri='{self.gcs.gs_url()}{destination}*.csv',
                    format='CSV',
                    overwrite=true,
                    header={ "true" if with_headers else "false" },
                    field_delimiter=',') AS
                    {sql}
                """
        self.execute(sql)
        final_destination = f'{destination}_final.csv'
        self.gcs.compose(f'{destination}', final_destination)
        return urllib.parse.unquote(self.gcs.sign(final_destination))

    def execute(self, sql, result=False):
        client = self.connector()
        job_config = bigquery.QueryJobConfig()

        query_job = client.query(
            sql,
            job_config=job_config,
        )

        return query_job.result()  # Waits for the query to finish

    def connector(self):
        credentials = service_account.Credentials.from_service_account_file(
            filename=self.options['service_account'],
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.credentials = credentials

        return bigquery.Client(credentials=credentials, project=credentials.project_id)

    def clean(self, blob_name):
        self.gcs.delete(blob_name)


class Snowflake(Connector):
    DEFAULT_STORAGE_INTEGRATION = 'tb__gcs_int'
    DEFAULT_STAGE = 'tb__gcs_stage'

    def __init__(self, options):
        super().__init__(options)
        self.configure()

    def configure(self):
        self.create_storage_integration()
        self.create_stage()
        self.gcs.grant_access(self.get_sf_member_name())

    def create_storage_integration(self):
        sql = f"""
                    create storage integration {self.storage_integration()}
                        type = external_stage
                        storage_provider = gcs
                        enabled = true
                        storage_allowed_locations = ('{self.gcs.gcs_url()}');
                """
        try:
            self.execute(sql)
        except Exception as e:
            if 'already exists' in str(e):
                pass
            else:
                raise e

    def get_sf_member_name(self):
        try:
            sql = F'DESC STORAGE INTEGRATION {self.storage_integration()};'
            result = self.execute(sql, result=True)
            for row in result:
                if row['property'] == 'STORAGE_GCP_SERVICE_ACCOUNT':
                    return row['property_value']
        except Exception:
            return None

    def create_stage(self):
        sql = f"""
                    create stage "{self.options['schema']}".{self.stage()}
                        url='{self.gcs.gcs_url()}'
                        storage_integration = {self.storage_integration()};
                """
        try:
            self.execute(sql)
        except Exception as e:
            if 'already exists' in str(e):
                pass

    def export_to_gcs(self, sql, destination):
        mm = str(int(round(time.time() * 1000)))
        destination = f"{destination}_{mm}"
        with_headers: bool = self.options.get('with_headers')
        sql = f"""copy into '@{self.stage()}/{destination}'
                    from ({sql})
                    overwrite = true
                    file_format = (TYPE=CSV COMPRESSION=NONE ESCAPE_UNENCLOSED_FIELD=NONE FIELD_DELIMITER='|' FIELD_OPTIONALLY_ENCLOSED_BY='"' null_if=())
                    header = {"true" if with_headers else "false" }
                    max_file_size = 5000000000;
                """
        self.execute(sql)
        final_destination = f'{destination}_final.csv'
        self.gcs.compose(destination, final_destination)
        return urllib.parse.unquote(self.gcs.sign(final_destination))

    def execute(self, sql, result=False):
        ctx = self.connector()
        cs = ctx.cursor(snowflake.connector.DictCursor)
        try:
            cs.execute(f"use role {self.options['role']};")
            cs.execute(f"use warehouse {self.options['warehouse']};")
            cs.execute(sql)
            if result:
                result = cs.fetchall()
        finally:
            cs.close()
        ctx.close()
        return result

    def datasource_analyze(self, resource):
        """returns .datasource file for resource"""
        # TODO: deal with the right precisions for Integers
        YES = 'Y'
        NO = 'N'

        def from_snowflake_type(t, nullable=NO):
            """transforms snowflake types to CH ones"""
            the_type = 'String'
            if t.startswith('NUMBER'):
                the_type = 'Int32'
            if t.startswith('FLOAT') or t.startswith('DOUBLE') or t.startswith('REAL') or t.startswith('NUMERIC') or t.startswith('DECIMAL'):
                the_type = 'Float32'
            if t == 'DATE':
                the_type = 'Date'
            if t == 'DATETIME' or t.startswith('TIMESTAMP'):
                the_type = 'DateTime'
            if nullable == YES:
                the_type = f'Nullable({the_type})'
            return the_type

        result = self.execute(f"DESCRIBE TABLE {resource};", result=True)
        sql = []
        columns = []
        for row in result:
            if row['kind'] == 'COLUMN':
                sql.append(f"{row['name']} {from_snowflake_type(row['type'], row['null?'])}")
                columns.append({
                    'path': row['name'],
                    'name': row['name'],
                    'present_pct': 1 if row['null?'] != YES else None,
                    'recommended_type': from_snowflake_type(row['type'])
                })
        return {
            'analysis': {
                'columns': columns,
                'schema': ', '.join(sql)
            }
        }

    def connector(self):
        auth = {key: self.options[key] for key in self.options.keys() & {'user', 'password', 'account', 'warehouse', 'database', 'schema'}}
        return snowflake.connector.connect(**auth)

    def stage(self):
        return self.options.get('stage') or self.DEFAULT_STAGE

    def storage_integration(self):
        return self.options.get('storage_integration') or self.DEFAULT_STORAGE_INTEGRATION

    def clean(self, blob_name):
        self.gcs.delete(blob_name)


connectors = {
    'snowflake': Snowflake,
    'bigquery': BigQuery,
}


def create_connector(source, params):
    return connectors[source](params)


class DataSensitiveSettings:
    kafka = [
        'kafka_sasl_plain_password'
    ]


class DataConnectorSettings:
    kafka = [
        'cli_version',
        'tb_endpoint',
        'kafka_bootstrap_servers',
        'kafka_sasl_plain_username',
        'kafka_sasl_plain_password',
        'kafka_security_protocol',
        'kafka_sasl_mechanism',
        'kafka_schema_registry_url',
    ]


class DataLinkerSettings:
    kafka = [
        'tb_datasource',
        'tb_token',
        'kafka_topic',
        'kafka_group_id',
        'kafka_auto_offset_reset',
        'kafka_store_raw_value'
    ]
