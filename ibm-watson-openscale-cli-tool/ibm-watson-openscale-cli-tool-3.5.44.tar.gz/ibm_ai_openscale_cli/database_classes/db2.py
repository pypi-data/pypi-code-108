# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
import os
import site
import tempfile
import base64
import uuid
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from sys import platform

logger = FastpathLogger(__name__)

def _get_clidriver_location():
    clidriver_location = None
    for location in site.getsitepackages():
        if os.path.exists(location + '/clidriver/lib'):
            clidriver_location = location + '/clidriver/lib'
            break
    return clidriver_location

try:
    import ibm_db
except Exception as e:
    if platform == "darwin" and ('Library not loaded' in str(e) or 'SQL1042C' in str(e)):
        logger.log_error('ERROR: Unable to import module "ibm_db"')
        logger.log_error('Environment variable "DYLD_LIBRARY_PATH" needs to set to use the ibm_db driver. This can be set using:')
        clidriver_location = _get_clidriver_location()
        if clidriver_location is not None:
            logger.log_info('"export DYLD_LIBRARY_PATH={}:{}/icc"'.format(clidriver_location, clidriver_location))
        else:
            clidriver_location = '</path/to>/clidriver/lib'
            logger.log_info('"export DYLD_LIBRARY_PATH={}:{}/icc"'.format(clidriver_location, clidriver_location))
        error_msg = 'Please retry with the above setting.'
        logger.log_error(error_msg)
        raise Exception(error_msg) # retry will not help
    else:
        raise e

USE_UPPERCASE_SCHEMA_NAME = False

DROP_SCHEMA = u'DROP SCHEMA {} RESTRICT'
CREATE_SCHEMA = u'CREATE SCHEMA {}'
DROP_TABLE = u'DROP {} {}."{}"'
DELETE_TABLE_ROWS = u'DELETE FROM {}."{}"'
COUNT_TABLE_ROWS = u'SELECT COUNT(*) AS ROWS FROM {}."{}"'
SELECT_MEASUREMENTFACTS_SUBCOUNTS = u'SELECT "measurement", COUNT(*) AS NUM FROM "{}"."MeasurementFacts" GROUP BY "measurement" ORDER BY "measurement"'
SELECT_EXPLANATIONS_SUBCOUNTS = u'SELECT "status", COUNT(*) AS NUM FROM "{}"."Explanations" GROUP BY "status" ORDER BY "status"'
SELECT_SOURCES_SUBCOUNTS = u'SELECT "type", COUNT(*) AS NUM FROM "{}"."Sources" GROUP BY "type" ORDER BY "type"'
SELECT_DEBIASED_PREDICTION_COLUMN = u"SELECT COUNT(*) AS NUM FROM SYSCAT.COLUMNS WHERE TABSCHEMA='{}' AND TABNAME='{}' AND COLNAME='debiased_prediction'"
SELECT_NULL_DEBIASED_PREDICTION_SUBCOUNT = u'SELECT COUNT(*) AS NUM FROM "{}"."{}" WHERE "debiased_prediction" IS NULL'
PROC_NAME = u'AIOSFASTPATHPROC."DROPSCHEMA{}{}"'
CALL_PROC = u'CALL {}'
DROP_SCHEMA_PROC = u'''CREATE OR REPLACE PROCEDURE {} BEGIN
    DECLARE varErrSchema varchar(128) default {};
    DECLARE varErrTable varchar(128) default {};
    CALL SYSPROC.ADMIN_DROP_SCHEMA('{}', NULL, varErrSchema, varErrTable);
END'''
DSN_STRING='DATABASE={};HOSTNAME={};PORT={};PROTOCOL=TCPIP;UID={};PWD={};' #pragma: allowlist secret

def validate_db2_credentials(credentials):
    if 'db2' in credentials: # PrimaryStorageCredentialsShort format
        logger.log_warning('This format of db2 credentials has been deprecated and will not be supported in future releases.')
        hostname = credentials['db2'].split(':')[2].split('@')[1]
        port = credentials['db2'].split(':')[3].split('/')[0]
        db = credentials['db2'].split(':')[3].split('/')[1]
        username = credentials['db2'].split(':')[1].split('//')[1]
        password = credentials['db2'].split(':')[2].split('@')[0] #pragma: allowlist secret
        uri = 'db2://{}:{}@{}:{}/{}'.format(username, password, hostname, port, db) #pragma: allowlist secret
        dsn = DSN_STRING.format(db, hostname, port, username, password)
        credentials = {
            "db_type": "db2",
            "hostname": hostname,
            "port": port,
            "db": db,
            "username": username,
            "password": password, #pragma: allowlist secret
            "uri": uri,
            "dsn": dsn
        }
    elif 'username' not in credentials or 'password' not in credentials or 'hostname' not in credentials or 'db' not in credentials:
        error_msg = 'Invalid DB2 credentials supplied: values for username, password, hostname, and db are all required'
        logger.log_error(error_msg)
        raise Exception(error_msg)
    else: # PrimaryStorageCredentialsLong format or DB2 Warehouse on Cloud format
        if 'port' not in credentials:
            credentials['port'] = 50000
    return credentials

class DB2():

    def __init__(self, credentials):
        self.credentials = credentials
        conn_string = None
        if 'ssldsn' in credentials and credentials['ssldsn'] is not None:
            conn_string = credentials['ssldsn']
        else:
            if 'dsn' in credentials and credentials['dsn'] is not None:
                conn_string = credentials['dsn']
            else:
                conn_string = DSN_STRING.format(credentials['db'], credentials['hostname'], credentials['port'], credentials['username'], credentials['password'])

            if 'ssl' in credentials and credentials['ssl'] is not None:
                if credentials['ssl']:
                    conn_string += 'Security=ssl;'

                    cert_file = None
                    if 'certificate_base64' in credentials and credentials['certificate_base64'] is not None:
                        cert_file = self.create_certificate_file(credentials['hostname'],
                                                                 credentials['port'],
                                                                 credentials['certificate_base64'])

                    if cert_file is not None:
                        conn_string += 'SSLServerCertificate={};'.format(cert_file)
        self._connection = ibm_db.connect(conn_string, '', '')

    def create_certificate_file(self, hostname, port, certificate, is_base64=True):
        cert_content = None
        if is_base64:
            cert_content = base64.b64decode(certificate.strip()).decode()
        else:
            cert_content = certificate
        with tempfile.NamedTemporaryFile(mode='w', prefix='db2ssl_', suffix='_cert.arm', delete=False) as f:
            f.write(cert_content)
            return f.name
        return None

    def _execute(self, statement_str):
        return ibm_db.exec_immediate(self._connection, statement_str)

    def _fetch_results(self, command):
        results = []
        result = ibm_db.fetch_assoc(command)
        while result:
            results.append(result)
            result = ibm_db.fetch_assoc(command)
        return results

    def _get_tables_in_schema(self, schema_name):
        schema_name = self._process_schema_name(schema_name)
        results = self._fetch_results(ibm_db.tables(self._connection, None, schema_name))
        return results

    def _drop_tables_in_schema(self, schema_name):
        schema_name = self._process_schema_name(schema_name)
        tables = self._get_tables_in_schema(schema_name)
        for table in tables:
            self._execute(DROP_TABLE.format(table['TABLE_TYPE'], table['TABLE_SCHEM'], table['TABLE_NAME']))

    def _restrict_drop_existing_schema(self, schema_name):
        schema_name = self._process_schema_name(schema_name)
        self._execute(DROP_SCHEMA.format(schema_name))

    def _admin_drop_existing_schema(self, schema_name):
        uuid_string = uuid.uuid4().hex
        # drop existing error table
        # error_schema_name = "'{}ERRORSCHEMA'".format(schema_name)
        error_schema_name = "'AIOSFASTPATHPROCERROR'"
        self._drop_tables_in_schema(error_schema_name)
        error_table_name = "'{}{}ERRORTAB'".format(schema_name, uuid_string)
        # drop schema
        proc_name = PROC_NAME.format(schema_name, uuid_string)
        self._execute(DROP_SCHEMA_PROC.format(proc_name, error_schema_name, error_table_name, schema_name))
        self._execute(CALL_PROC.format(proc_name))

    def drop_existing_schema(self, schema_name, keep_schema):
        schema_name_with_quotes = self._process_schema_name(schema_name)
        logger.log_debug('Dropping tables from schema {}'.format(schema_name_with_quotes))
        self._drop_tables_in_schema(schema_name)
        if keep_schema:
            return
        logger.log_debug('Dropping schema {}'.format(schema_name))
        self._admin_drop_existing_schema(schema_name)

    def create_new_schema(self, schema_name, keep_schema):
        if keep_schema:
            return
        schema_name = self._process_schema_name(schema_name)
        logger.log_debug('Creating schema {}'.format(schema_name))
        self._execute(CREATE_SCHEMA.format(schema_name))

    def reset_metrics_tables(self, schema_name):
        schema_name = self._process_schema_name(schema_name)
        tables = self._get_tables_in_schema(schema_name)
        for table in tables:
            if table['TABLE_NAME'] == 'MeasurementFacts' or table['TABLE_NAME'] == 'Explanations' or table['TABLE_NAME'] == 'Monitor_quality' or table['TABLE_NAME'].startswith('Payload_') or table['TABLE_NAME'].startswith('Feedback_') or table['TABLE_NAME'].startswith('Manual_Labeling_'):
                self._execute(DELETE_TABLE_ROWS.format(table['TABLE_SCHEM'], table['TABLE_NAME']))

    def drop_metrics_tables(self, schema_name):
        schema_name = self._process_schema_name(schema_name)
        tables = self._get_tables_in_schema(schema_name)
        for table in tables:
            if table['TABLE_NAME'].startswith('Payload_') or table['TABLE_NAME'].startswith('Feedback_') or table['TABLE_NAME'].startswith('Manual_Labeling_'):
                self._execute(DROP_TABLE.format(table['TABLE_TYPE'], table['TABLE_SCHEM'], table['TABLE_NAME']))

    # function needed for sorting list of tables by table name
    def _get_key(self, table):
        return table['TABLE_NAME']

    def _process_schema_name(self, schema_name):
        if USE_UPPERCASE_SCHEMA_NAME:
            schema_name = schema_name.upper()
        schema_name = schema_name.replace('"', '')
        schema_name = '"{}"'.format(schema_name)
        return schema_name

    def count_datamart_rows(self, schema_name, context=None):
        if context:
            context = ', {}'.format(context)
        else:
            context = ''
        logger.log_debug('Counting rows in all tables from schema {}{}'.format(schema_name, context))
        schema_name = self._process_schema_name(schema_name)
        tables = self._get_tables_in_schema(schema_name)
        tables.sort(key=self._get_key)
        results = []
        for table in tables:
            table_name = table['TABLE_NAME']
            count = self._execute(COUNT_TABLE_ROWS.format(schema_name, table_name))
            rows = self._fetch_results(count)
            rowcount = int(rows[0]['ROWS'])
            results.append([table_name, rowcount])
            if rowcount == 0:
                continue
            if table_name == 'MeasurementFacts':
                subcount = self._execute(SELECT_MEASUREMENTFACTS_SUBCOUNTS.format(schema_name))
                subcount_rows = self._fetch_results(subcount)
                for subcount_row in subcount_rows:
                    measurement = '> {}'.format(subcount_row['measurement'])
                    num = subcount_row['NUM']
                    results.append([measurement, num])
            elif table_name == 'Explanations':
                subcount = self._execute(SELECT_EXPLANATIONS_SUBCOUNTS.format(schema_name))
                subcount_rows = self._fetch_results(subcount)
                for subcount_row in subcount_rows:
                    status = '> {}'.format(subcount_row['status'])
                    num = subcount_row['NUM']
                    results.append([status, num])
            elif table_name == 'Sources':
                subcount = self._execute(SELECT_SOURCES_SUBCOUNTS.format(schema_name))
                subcount_rows = self._fetch_results(subcount)
                for subcount_row in subcount_rows:
                    type = '> {}'.format(subcount_row['type'])
                    num = subcount_row['NUM']
                    results.append([type, num])
            elif table_name.startswith('Payload_') and len(table_name.split('_')) == 2: # base Payload table
                debias_prediction_column = self._execute(SELECT_DEBIASED_PREDICTION_COLUMN.format(schema_name, table_name))
                col_rows = self._fetch_results(debias_prediction_column)
                if int(col_rows[0]['NUM']) == 1:
                    subcount = self._execute(SELECT_NULL_DEBIASED_PREDICTION_SUBCOUNT.format(schema_name, table_name))
                    subcount_rows = self._fetch_results(subcount)
                    results.append(['> debiased_prediction is NULL', subcount_rows[0]['NUM']])
        return results

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._connection:
                if ibm_db.close(self._connection):
                    logger.log_debug('Successfully closed the DB2 connection')
                else:
                    logger.log_debug('Unable to close the DB2 connection')
        except Exception as e:
            logger.log_debug('Unable to close the DB2 connection.')
