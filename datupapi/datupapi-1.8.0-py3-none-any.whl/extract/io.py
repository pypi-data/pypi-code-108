import base64
import boto3
import json
import os
import pandas as pd
import requests
#import snowflake.connector
import time

from boto3.dynamodb.conditions import Key, Attr
from boto3.session import Session
from botocore.exceptions import ClientError
from datetime import datetime
from decimal import Decimal
from hashlib import md5
from datupapi.configure.config import Config
#from snowflake.connector.pandas_tools import write_pandas, pd_writer
#from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy import Integer, Float, String, DECIMAL
from sqlalchemy import insert, delete, exists, schema

class IO(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def get_secret(self, secret_name=None):
        """
        Return the credentials mapped to the entered secret name

        :param secret_name: Name identifying the credentials in AWS.
        :return response: Credential to authenticate against AWS resource

        >>> creds = get_secret()
        >>> creds = ...
        """
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager',
                                region_name=self.region,
                                aws_access_key_id=self.access_key,
                                aws_secret_access_key=self.secret_key)
        try:
            get_secret_value_response = client.get_secret_value(SecretId=self.sql_database + 'secret')
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return json.loads(get_secret_value_response['SecretString'])


    def populate_snowflake_table(self, df, dwh_account=None, dwh_name=None, dwh_user=None, dwh_passwd=None, dwh_dbname=None, dwh_schema=None, table_name=None, replace=True):
        """
         Create a table in Snowflake DWH and insert the records from a dataframe

        :param df: Dataframe storing the records to insert into the database table
        :param dwh_account: Snowflake account identifier
        :param dwh_name: Snowflake datawarehouse name
        :param dwh_user: Snowflake account username
        :param dwh_passwd: Snowflake account password
        :param db_name: Snowflake database name
        :param dwh_schema: Snowflake database schema
        :param table_name: Snowflake table name
        :param replace: If True replace table records whether exists. Otherwise append records. Default True.
        :return inserted_records: Number of records inserted

        >>> records = populate_snowflake_table(df, dwh_account='xx12345.us-east-1', dwh_name='myDwh', dwh_user='myuser', dwh_passwd='12345', dwh_dbname='mydbname', dwh_schema='myschema', table_name='mytable')
        >>> records = 1000

        """
        if self.tenant_id != '':
            tenant_table_name = (self.tenant_id + table_name)
        else:
            tenant_table_name = table_name

        url = URL(account=dwh_account, user=dwh_user, password=dwh_passwd, warehouse=dwh_name, database=dwh_dbname, schema=dwh_schema)
        try:
            engine = create_engine(url)
            conn = engine.connect()
            if replace:
                df.to_sql(tenant_table_name, con=engine, if_exists='replace', index=False, chunksize=16000)
            else:
                df.to_sql(tenant_table_name, con=engine, if_exists='append', index=False, chunksize=16000)
            inserted_records = conn.execute('select count(*) from ' + '"' + tenant_table_name + '"').fetchone()[0]
        finally:
            conn.close()
            engine.dispose()
        return inserted_records


    def populate_dbtable(self, df, hostname=None, db_user=None, db_passwd=None, db_name=None, port='3306', table_name=None, db_type='mysql', replace=True):
        """
        Create a table in a MySQL database and insert the records from a dataframe

        :param df: Dataframe storing the records to insert into the database table
        :param hostname: Public IP address or hostname of the remote database server
        :param db_user: Username of the database
        :param db_passwd: Password of the database
        :param db_name: Name of the target database
        :param port: TCP port number of the database (usually 3306)
        :param table_name: Name of target table
        :param db_type: Name of database type. Choose from mysql, mssql. Default mysql.
        :param replace: If True replace table records whether exists. Otherwise append records. Default True.
        :return inserted_records: Number of records inserted

        >>> records = populate_dbtable(df, hostname='202.10.0.1', db_user='johndoe', db_passwd='123456', db_name='dbo.TheDataBase')
        >>> records = 1000
        """
        if db_type == 'mysql':
            db_api = 'mysql+mysqlconnector://'
        elif db_type == 'mysql_legacy':
            db_api = 'mysql+pymysql://'
        elif db_type == 'mssql':
            db_api = 'mssql+pymssql://'
        else:
            self.logger.exception(f'No valid database type. Please check valid types: mysql, mssql')

        if self.tenant_id != '':
            tenant_table_name = self.tenant_id + table_name
        else:
            tenant_table_name = table_name

        try:
            engine = create_engine(db_api + db_user + ':' + db_passwd + '@' + hostname + ':' + str(port) + '/' + db_name)
            if replace:
                df.to_sql(tenant_table_name, con=engine, if_exists='replace', index=False)
            else:
                df.to_sql(tenant_table_name, con=engine, if_exists='append', index=False)
            inserted_records = engine.execute('SELECT COUNT(*) FROM ' + tenant_table_name).fetchall()[0][0]
        except ConnectionRefusedError as err:
            logger.exception(f'Refused connection to the database. Please check parameters: {err}')
            raise
        return inserted_records


    def download_dbtable(self, hostname=None, db_user=None, db_passwd=None, db_name=None, port='3306', table_name=None, db_type='mysql', query=None):
        """Return a dataframe containing the data extracted from MSSQL database's table supporting PyODBC connector

        :param hostname: Public IP address or hostname of the remote database server
        :param db_user: Username of the database
        :param db_passwd: Password of the database
        :param db_name: Name of the target database
        :param port: TCP port number of the database. Default 3306
        :param table_name: Name of target table
        :param db_type: Name of database type. Choose from mysql, mssql, postgres, mysql_legacy. Default mysql.
        :param query: SQL statement to use as query.
        :return df: Dataframe containing the data from database's table

        >>> df = download_dbtable(hostname='202.10.0.1', db_user='johndoe', db_passwd='123456', db_name='dbo.TheDataBase', query='SELECT * FROM table')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        if db_type == 'mysql':
            db_api = 'mysql+mysqlconnector://'
        elif db_type == 'mysql_legacy':
            db_api = 'mysql+pymysql://'
        elif db_type == 'mssql':
            db_api = 'mssql+pymssql://'
        elif db_type == 'postgres':
            db_api = 'postgresql://'
        else:
            self.logger.exception(f'No valid database type. Please check valid types: mysql, mssql')

        try:
            if db_type == 'postgres':
                engine = create_engine(db_api + db_user + ':' + db_passwd + '@' + hostname + ':' + port + '/' + db_name,
                                       client_encoding='utf8', encoding='utf-8')
            else:
                engine = create_engine(db_api + db_user + ':' + db_passwd + '@' + hostname + ':' + port + '/' + db_name)
            connection = engine.connect()
            stmt = query
            df = pd.read_sql_query(stmt,connection)
            #results = connection.execute(stmt).fetchall()
            #df = pd.DataFrame(results)
        except ConnectionRefusedError as err:
            logger.exception(f'Refused connection to the database. Please check parameters: {err}')
            raise
        return df


    def download_rdstable(self, rds_arn=None, secret_arn=None, database_name=None, sql_query=None, query_params=None):
        """
        Return query results to RDS database

        :param rds_arn: Database instance or clusrter's ARN
        :param secret_arn: Secret Manager resource ARN
        :param database_name: Database name to query on instance or cluster
        :param sql_query: Query string on SQL syntax
        :param query_params: List of dictionary values to put into the query string
        :return response: Records queried from the RDS database

        >>> response = download_rdstable(rds_arn='arn:rds:mycluster', \
                                         secret_arn='arn:secret:mysecret', \
                                         database_name='mydb', \
                                         sql_query=[{'name': 'paramId', 'value': {'stringValue': 'myvalue'}}], \
                                         query_params=None)
        >>> response = [{'date': '2021-06-07'}, {'name': 'John Doe'}, {'salary': 1000}]
        """
        client = boto3.client('rds-data',
                              region_name='us-east-1',
                              aws_access_key_id='AKIAI7NE5TOJSHSOLTQQ',
                              aws_secret_access_key='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')
        try:
            # Query project table
            response = client.execute_statement(
                parameters=query_params,
                resourceArn=rds_arn,
                secretArn=secret_arn,
                database=database_name,
                sql=sql_query
            )
        except client.exceptions.BadRequestException as err:
            print(f'Incorrect request. Please check query syntax and parameters: {err}')
            return False
        return response['records']


    def download_csv(self, q_name, datalake_path=None, sep=',', index_col=None, usecols=None, squeeze=False, num_records=None,
                     dayfirst=False, compression='infer', encoding='utf-8', date_cols=None, types=None, thousands=None, decimal='.', low_memory=True):
        """Return a dataframe from a csv file stored in the datalake

        :param q_name: Plain file (.csv) to download and stored in a dataframe
        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :param sep: Field delimiter of the downloaded file. Default ','
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param squeeze: If the parsed data only contains one column then return a Series. Default False
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator
        :param decimal: Decimal separator. Default '.'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_csv(q_name='Q', datalake_path='as-is/folder')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.csv')
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, q_name + '.csv', file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, q_name, q_name + '.csv'), file_path)
            df = pd.read_csv(file_path,
                             sep=sep,
                             index_col=index_col,
                             usecols=usecols,
                             squeeze=squeeze,
                             nrows=num_records,
                             dayfirst=dayfirst,
                             compression=compression,
                             encoding=encoding,
                             low_memory=low_memory,
                             parse_dates=date_cols,
                             thousands=thousands,
                             decimal=decimal,
                             dtype=types)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No csv file found. Please check paths: {err}')
            raise
        return df


    def download_json_file(self, json_name=None, datalake_path=None):
        """
        Return a JSON file downloaded from the datalake

        :param json_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :return response: JSON file contents

        >>>
        >>>
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, json_name + '.json')
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, json_name + '.csv', file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, json_name + '.json'), file_path)
            with open(file_path, 'r') as json_file:
                response = json.load(json_file)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return response


    def download_object_csv(self, datalake_path=None, sep=',', index_col=None, usecols=None, squeeze=False, num_records=None,
                            dayfirst=False, compression='infer', encoding='utf-8', date_cols=None, types=None, thousands=None, decimal='.', low_memory=True):
        """Return a dataframe from a file stored in the datalake

        :param datalake_path: Path to download the file from the S3 datalake. Do not include datalake name. Default None.
        :param sep: Field delimiter of the downloaded file. Default ','
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param squeeze: If the parsed data only contains one column then return a Series. Default False
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator
        :param decimal: Decimal separator. Default '.'
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_object_csv(datalake_path='as-is/folder/file.txt')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3',
                                 region_name=self.region,
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, 'object.dat')
        try:
            s3_client.download_file(self.datalake, os.path.join(datalake_path), file_path)
            df = pd.read_csv(file_path,
                             sep=sep,
                             index_col=index_col,
                             usecols=usecols,
                             squeeze=squeeze,
                             nrows=num_records,
                             dayfirst=dayfirst,
                             compression=compression,
                             encoding=encoding,
                             low_memory=low_memory,
                             thousands=thousands,
                             parse_dates=date_cols,
                             decimal=decimal,
                             dtype=types)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return df


    def download_all_objects_csv(self, datalake_path=None, sep=',', index_col=None, squeeze=False, num_records=None, dayfirst=False, compression='infer',
                                 encoding='utf-8', low_memory=True, date_cols=None, types=None, thousands=None, decimal='.'):
        """Return a dataframe from a file stored in the datalake

        :param datalake_path: Path to download the file from the S3 datalake. Do not include datalake name. Default None.
        :param sep: Field delimiter of the downloaded file. Default ','
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param squeeze: If the parsed data only contains one column then return a Series. Default False
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator
        :param decimal: Decimal separator. Default '.'
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_all_objects_csv(datalake_path='as-is/folder/file')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_resource = boto3.resource('s3',
                                     region_name=self.region,
                                     aws_access_key_id=self.access_key,
                                     aws_secret_access_key=self.secret_key)

        try:
            df = pd.DataFrame()
            datalake = s3_resource.Bucket(self.datalake)
            objects = datalake.objects.filter(Prefix=datalake_path)
            for obj in objects:
                path, filename = os.path.split(obj.key)
                if filename != '_SUCCESS' and filename != '_CHECK':
                    datalake.download_file(obj.key, os.path.join('/tmp', filename))
                    df_tmp = pd.read_csv(os.path.join('/tmp', filename),
                                         sep=sep,
                                         index_col=index_col,
                                         squeeze=squeeze,
                                         nrows=num_records,
                                         dayfirst=dayfirst,
                                         compression=compression,
                                         encoding=encoding,
                                         low_memory=low_memory,
                                         parse_dates=date_cols,
                                         thousands=thousands,
                                         decimal=decimal,
                                         dtype=types)
                    df = pd.concat([df, df_tmp], axis='rows').drop_duplicates()
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return df


    def download_dynamodb(self, table_name, tenant_id):
        """
        Return a dataframe with the data fetch from DynamoDB

        :param table_name: Table name in DynamoDB table
        :param tenant_id: Partition column mapping tenant's ID to whom belongs the records
        :return df: Dataframe to store records fetched from DynamoDB
        >>> df = download_dynamodb(table_name='sampleTbl', tenant_id='1234')
        >>> df =
                tenantId    Date         Attr
        idx0    A121        2020-12-01   3
        """
        dydb_client = boto3.client('dynamodb', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        dynamodb_session = Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=self.region)
        dydb = dynamodb_session.resource('dynamodb')
        try:
            dynamo_tbl = dydb.Table(table_name)
            response = dynamo_tbl.query(
                KeyConditionExpression=Key('tenantId').eq(md5(tenant_id.encode('utf-8')).hexdigest()) &\
                                       Key('Fecha').between('2010-01-01', '2025-12-31')
            )
            items = response['Items']
        except dydb_client.exceptions.ResourceNotFoundException as err:
            print(f'Table not found. Please check names :{err}')
            return False
            raise
        return items


    def download_excel(self, q_name, sheet_name, datalake_path=None, index_col=None, usecols=None, squeeze=False, num_records=None, date_cols=None, types=None, header_=0, skiprows_=None):
        """Return a dataframe from a csv file stored in the datalake

        :param q_name: Excel file to download and stored in a dataframe. Include extension xls, xlsx, ods, etc.
        :param sheet_name: Excel sheet to download and stored in a dataframe
        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param squeeze: If the parsed data only contains one column then return a Series. Default False
        :param num_records: Number of records to fetch from the source. Default None
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_excel(q_name='Q', sheet_name='sheet1', datalake_path='as-is/folder')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name)
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, q_name, file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, q_name), file_path)
            df = pd.read_excel(file_path,
                               sheet_name=sheet_name,
                               index_col=index_col,
                               usecols=usecols,
                               squeeze=squeeze,
                               engine='openpyxl',
                               nrows=num_records,
                               parse_dates=date_cols,
                               dtype=types,
                               header=header_,
                               skiprows=skiprows_)
            df = df.dropna(how='all')
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            raise
        return df


    def download_xml(self, url_=None, header_=None, body_=None):
        """Return a response in XML format from a SOAP web service

        :param url_: URL endpoint to access SOAP web service
        :param header_: Header in rest api configuration parameters
        :param body_: Body input parameters
        :return response: Plain  text with data xml

        address = 'http://200.200.200.200:81/service.asmx'
        headers = {'Content-Type':'text/xml;charset=UTF-8'}
        body = ""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
                     <soapenv:Header/>
                            <soapenv:Body>
                                <tem:EjecutarConsultaXML>
                                    <!--Optional:-->
                                    <tem:pvstrxmlParametros>
                                        <![CDATA[
                                        <Consulta>
                                            <NombreConexion>Datup_Real</NombreConexion>
                                            <IdCia>2</IdCia>
                                            <IdProveedor>Analytics</IdProveedor>
                                            <IdConsulta>CONSULTA_VENTAS</IdConsulta>
                                            <Usuario>myuser</Usuario>
                                            <Clave>mypassword</Clave>
                                            <Parametros>
                                                <p_periodo_ini>202105</p_periodo_ini>
                                                <p_periodo_fin>202105</p_periodo_fin>
                                            </Parametros>
                                        </Consulta>]]>
                                    </tem:pvstrxmlParametros>
                                </tem:EjecutarConsultaXML>
                            </soapenv:Body>
                        </soapenv:Envelope>""

        >>> response = download_xml(url_=address, header_=headers, body_=body)
        >>> response =
                        '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><EjecutarConsultaXMLResponse xmlns="http://tempuri.org/"><EjecutarConsultaXMLResult><xs:schema id="NewDataSet"
                        xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"><xs:element name="NewDataSet" msdata:IsDataSet="true"
                        msdata:UseCurrentLocale="true"><xs:complexType><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="Resultado"><xs:complexType><xs:sequence><xs:element
                        name="Compañia" type="xs:short" minOccurs="0" /><xs:element name="Llave_x0020_Documento" type="xs:int" minOccurs="0"'
        """
        try:
            r = requests.post(url_, headers=header_, data=body_, allow_redirects=True)
            response = r.text
        except requests.exceptions.HTTPError as err:
            self.logger.exception(f'Http error: {err}')
            raise
        except requests.exceptions.ConnectionError as err:
            self.logger.exception(f'Error connecting: {err}')
            raise
        except requests.exceptions.Timeout as err:
            self.logger.exception(f'Timeout error: {err}')
            raise
        except requests.exceptions.RequestException as err:
            self.logger.exception(f'Oops: Something else: {err}')
            raise
        return response


    def download_models(self, datalake_path=None):
        """Returns True as successful download of the n_backtests models trained by attup model

        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :return: True if success, else False.

        >>> models = download_models(datalake_path='path/to/data')
        >>> True
        """

        s3_client = boto3.client('s3',
                                 region_name=self.region,
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)
        for i in range(self.backtests + 1):
            q_name = "model" + str(i)
            file_path = os.path.join(Config.LOCAL_PATH, q_name + '.h5')
            print(file_path)
            try:
                if datalake_path is None:
                    s3_client.download_file(self.datalake, q_name + '.h5', file_path)
                else:
                    s3_client.download_file(self.datalake, os.path.join(datalake_path, "models", q_name + '.h5'),
                                            file_path)
            except ClientError as err:
                self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            except FileNotFoundError as err:
                self.logger.exception(f'No csv file found. Please check paths: {err}')
                raise
            return True

    def download_models_tft(self, datalake_path=None):
        """Returns True as successful download of the n_backtests models trained by attup model

        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :return: True if success, else False.

        >>> models = download_models(datalake_path='path/to/data')
        >>> True
        """

        s3_client = boto3.client('s3',
                                 region_name=self.region,
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)
        for i in range(self.backtests + 1):
            q_name = "model" + str(i)
            file_path = os.path.join(Config.LOCAL_PATH, q_name + '.ckpt')
            print(file_path)
            try:
                if datalake_path is None:
                    s3_client.download_file(self.datalake, q_name + '.ckpt', file_path)
                else:
                    s3_client.download_file(self.datalake, os.path.join(datalake_path, "models", q_name + '.ckpt'),
                                            file_path)
            except ClientError as err:
                self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            except FileNotFoundError as err:
                self.logger.exception(f'No csv file found. Please check paths: {err}')
                raise
            return True


    def upload_csv(self, df, q_name, datalake_path, sep=',', encoding='utf-8', date_format='%Y-%m-%d'):
        """Return a success or failure boolean attempting to upload a local file to the datalake

        :param df: Dataframe to upload
        :param q_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :param sep: Field delimiter for the output file. Default ','
        :param date_format: Format string for datetime objects of output file. Default '%Y-%m-%d'
        :param encoding: A string representing the encoding to use in the output file. Default 'utf-8'
        :return: True if success, else False.

        >>> upload_csv(df=df, q_name='Q', datalake_path='as-is/folder')
        >>> True
        """
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.csv')
        df.to_csv(file_path, sep=sep, encoding=encoding, date_format=date_format, index=False)
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        try:
            response = s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, q_name, q_name + '.csv'))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True


    def upload_dynamodb(self, df, table_name, tenant_id, sort_col):
        """
        Return a success or failure boolean attempting to upload timeseries data to DynamoDB

        :param df: Dataframe to upload to DynamoDB table
        :param table_name: Table name in DynamoDB table
        :param tenant_id: Partition column mapping tenant's ID to whom belongs the records
        :param sort_col: Sorting column mapping usually to date column
        :return response: HTTP status code response. If 400 success, failure otherwise

        >>> upload_dynamodb(df=df, table_name=sampleTbl, tenant_id='acme', sort_col='Date')
        >>> True
        """
        dydb_client = boto3.client('dynamodb', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        dynamodb_session = Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=self.region)
        dydb = dynamodb_session.resource('dynamodb')
        try:
            dynamo_tbl = dydb.Table(table_name)
            with dynamo_tbl.batch_writer() as batch:
                for row in df.itertuples(index=False):
                    record = {}
                    record.update({'tenantId': md5(tenant_id.encode('utf-8')).hexdigest()})
                    record.update({sort_col: row[0].strftime('%Y-%m-%d')})
                    for ix, rec in enumerate(row[1:]):
                        record.update({df.columns[ix + 1]: Decimal(str(rec))})
                    batch.put_item(Item=record)
        except dydb_client.exceptions.ResourceNotFoundException as err:
            print(f'Table not found. Please check names :{err}')
            return False
            raise
        return True


    def upload_json(self, df, q_name=None, datalake_path=None, orient_=None, date_format_=None, date_unit_='s', compression_=None, indent_=4):
        """
        Return a success or failure response after attempting to upload a dataframe in JSON format

        :param df: Dataframe to upload in JSON format
        :param q_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :param orient_: Expected JSON string format. Possible values split, records, index, table, columns, values
        :param date_format_: Type of date conversion. epoch = epoch milliseconds, iso = ISO8601.
        :param date_unit_: The time unit to encode to, governs timestamp and ISO8601 precisione, e.g. s, ms, us, ns.
        :param compression_: A string representing the compression to use in the output file, e.g. gzip, bz2, zip, xz.
        :param indent_: Length of whitespace used to indent each record. Default 4.
        :return response: Success or failure uploading the dataframe

        >>> upload_json(df, q_name='Qtest', orient_='columns')
        >>> True
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.json')
        try:
            df.to_json(file_path, orient=orient_, date_format=date_format_, date_unit=date_unit_, compression=compression_, indent=indent_)
            response = s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, q_name + '.json'))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True


    def upload_json_file(self, message=None, json_name=None, datalake_path=None, indent_=4):
        """
        Return a success or failure response after attempting to upload a JSON file


        :param message: Dict type to convert to JSON and upload to datalake
        :param json_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :param indent_: Length of whitespace used to indent each record. Default 4.
        :return : Success or failure uploading the dataframe

        >>> upload_json_file(message=resp_dict, json_name='myjson', datalake_path='/path/to/data')
        >>> True
        """

        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, json_name + '.json')
        try:
            with open(file_path, 'w') as json_file:
                json.dump(message, json_file, indent=indent_)
            s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, json_name + '.json'))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True


    def upload_timestream(self, df, db_name, table_name):
        """
        Return a success or failure boolean attempting to upload timeseries data to timestream database

        :param df: Dataframe to upload to Timestream table
        :param db_name: Database name in Timestream service
        :param table_name: Table name in Timestream service
        :return response: HTTP status code response. If 400 success, failure otherwise

        >>> upload_timestream(df=df, db_name=dbSample, table_name=tbSample)
        >>> True
        """
        ts_client = boto3.client('timestream-write', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        dimensions = [
            {'Name': 'tenantId', 'Value': '1000', 'DimensionValueType': 'VARCHAR'}
        ]
        records = []
        for row in df.itertuples(index=False):
            for ix, rec in enumerate(row[1:]):
                records.append({
                    'Dimensions': dimensions,
                    'MeasureName': df.columns[ix + 1],
                    'MeasureValue': str(rec),
                    'MeasureValueType': 'DOUBLE',
                    'Time': str(int(pd.to_datetime(row[0]).timestamp())),
                    'TimeUnit': 'SECONDS',
                    'Version': 3
                })
        try:
            response = ts_client.write_records(DatabaseName=db_name,
                                               TableName=table_name,
                                               Records=records)
            status = response['ResponseMetadata']['HTTPStatusCode']
            print(f'Processed records: {len(records)}. WriteRecords status: {status}')
            self.logger.exception(f'Processed records: {len(records)}. WriteRecords status: {status}')
        except ts_client.exceptions.RejectedRecordsException as err:
            print(f'{err}')
            self.logger.exception(f'{err}')
            for e in err.response["RejectedRecords"]:
                print("Rejected Index " + str(e["RecordIndex"]) + ": " + e["Reason"])
                self.logger.exception("Rejected Index " + str(e["RecordIndex"]) + ": " + e["Reason"])
            return False
        except ts_client.exceptions.ValidationException as err:
            print(f"{err.response['Error']['Message']}")
            self.logger.exception(f"{err.response['Error']['Message']}")
            return False
        return status


    def upload_models(self, datalake_path):
        """Return a success or failure boolean attempting to upload a tensorflow models to the datalake.

        :param datalake_path: Path to upload the attup trained models to S3 datalake
        :return: True if success, else False.

        >>> upload_models(datalake_path='as-is/folder')
        >>> True
        """
        s3_client = boto3.client('s3',
                                 region_name=self.region,
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)

        for i in range(self.backtests + 1):
            q_name = "model" + str(i)
            print(q_name)
            file_path = os.path.join(Config.LOCAL_PATH, q_name + '.h5')
            try:
                response = s3_client.upload_file(file_path, self.datalake,
                                                 os.path.join(datalake_path, "models", q_name + '.h5'))
            except ClientError as err:
                self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
                return False
            except FileNotFoundError as err:
                self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
                return False
        return True

    def upload_models_tft(self, q_name, datalake_path):
            """Return a success or failure boolean attempting to upload a tensorflow models to the datalake.

            :param datalake_path: Path to upload the attup trained models to S3 datalake
            :return: True if success, else False.

            >>> upload_models(datalake_path='as-is/folder')
            >>> True
            """
            s3_client = boto3.client('s3',
                                 region_name=self.region,
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)
            print(q_name)
            file_path = os.path.join(Config.LOCAL_PATH, q_name + '.ckpt')
            try:
                response = s3_client.upload_file(file_path, self.datalake,
                                                 os.path.join(datalake_path, "models", q_name + '.ckpt'))
            except ClientError as err:
                self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
                return False
            except FileNotFoundError as err:
                self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
                return False
            return True


    def upload_object(self, datalake_name=None, datalake_path='', object_name=None):
        """Return a success or failure boolean attempting to upload a local file to the datalake

        :param datalake_name: S3 bucket name (datalake) to upload the object
        :param datalake_path: Path to upload the Q to S3 datalake
        :param object_name: Object name to upload to the S3 bucket (datalake)
        :return: True if success, else False.

        >>> upload_object(datalake_name='datup-datalake-datup', datalake_path='path/to/data', object_name='datup.dat')
        >>> True
        """
        file_path = os.path.join(Config.LOCAL_PATH, object_name)
        s3_client = boto3.client('s3', region_name='us-east-1',
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)
        try:
            response = s3_client.upload_file(file_path, datalake_name, os.path.join(datalake_path, object_name))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True


    def upload_log(self):
        """Return a success or failure boolean attempting to upload a local file to the datalake

        :param datalake_path: Path to upload the Q to S3 datalake
        :return: True if success, else False.

        >>> upload_log()
        >>> True
        """
        file_path = os.path.join(Config.LOCAL_PATH, self.logfile)
        s3_client = boto3.client('s3', region_name='us-east-1',
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)
        try:
            response = s3_client.upload_file(file_path, self.datalake, os.path.join(self.log_path, self.logfile))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True


    def copy_between_datalakes(self, q_name=None, src_datalake=None, src_path=None, dst_datalake=None, dst_path=None):
        """
        Return True whether successful copy between datalake buckets occurs

        :param q_name: File or dataset name including the type or extension
        :param src_datalake: Source datalake's bucket name
        :param src_path: Source datalake's key path, excluding dataset name
        :param dst_datalake: Destination datalake's bucket name
        :param dst_path: Destination datalake's key path, excluding dataset name
        :return : True if success, else False.

        >>> copy_between_datalakes(q_name='mycube', src_datalake='bucket-a', src_path='path/to/file', dst_datalake='bucket-b', dst_path='path/to/file')
        >>> True
        """

        s3_client = boto3.resource('s3', region_name='us-east-1',
                                   aws_access_key_id='AKIAI7NE5TOJSHSOLTQQ',
                                   aws_secret_access_key='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'
                                  )
        try:
            copy_source = {
                'Bucket': src_datalake,
                'Key': os.path.join(src_path, q_name)
            }
            filename, filetype = q_name.split('.')
            if filetype == 'csv':
                s3_client.meta.client.copy(copy_source, dst_datalake, os.path.join(dst_path, filename, filename + '.' + filetype))
            elif filetype == 'xls' or filetype == 'xlsx' or filetype == 'XLS' or filetype == 'XLSX':
                s3_client.meta.client.copy(copy_source, dst_datalake, os.path.join(dst_path, filename + '.' + filetype))
            else:
                self.logger.debug(f'No valid dataset type. Please check database or datalake to debug.')
        except FileNotFoundError as err:
            self.logger.exception(f'No file or datalake found. Please check paths: {err}')
            return False
        return True
    
    def download_txt(self, q_name, datalake_path=None, sep='\t', index_col=None, usecols=None, squeeze=False, num_records=None,
                     dayfirst=False, compression='infer', encoding='utf-8', date_cols=None, types=None, thousands=None, low_memory=True, decimal='.'):
        """Return a dataframe from a csv file stored in the datalake

        :param q_name: Plain file (.txt) to download and stored in a dataframe
        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :param sep: Field delimiter of the downloaded file. Default '\t'
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param squeeze: If the parsed data only contains one column then return a Series. Default False
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator.
        :param decimal: Decimal separator. Default '.'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_txt(q_name='Q', datalake_path='as-is/folder')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.txt')
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, q_name + '.txt', file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, q_name + '.txt'), file_path)

            df = pd.read_csv(file_path,
                             sep=sep,
                             index_col=index_col,
                             usecols=usecols,
                             squeeze=squeeze,
                             nrows=num_records,
                             dayfirst=dayfirst,
                             compression=compression,
                             encoding=encoding,
                             low_memory=low_memory,
                             parse_dates=date_cols,
                             thousands=thousands,
                             decimal=decimal,
                             dtype=types)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No csv file found. Please check paths: {err}')
            raise
        return df