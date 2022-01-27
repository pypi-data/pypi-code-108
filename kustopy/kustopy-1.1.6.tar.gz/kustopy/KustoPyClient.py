from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties
from azure.kusto.data.data_format import DataFormat
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data.exceptions import KustoServiceError
import logging


class Client:

    def __init__(self, cluster, database, client_id, client_secret, tenant_id):
        # Define self variables
        self.cluster = cluster
        self.database = database
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

        # Add ingest cluster
        ingest_cluster = self.cluster.split('//')
        ingest_cluster.insert(1, '//ingest-')
        self.ingest_cluster = ''.join(ingest_cluster)

        # Create client for queries
        kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster, self.client_id,
                                                                                    self.client_secret, self.tenant_id)
        self.query_client = KustoClient(kcsb)

        # Create client for data ingestion
        kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.ingest_cluster, self.client_id,
                                                                                    self.client_secret, self.tenant_id)
        self.ingestion_client = QueuedIngestClient(kcsb)

    # -----------------------------------------QUERY-----------------------------------------

    # Function to construct a database query from user input (string)
    def get_response(self, user_input):
        # If truncation is set to True the user input can be passed right trough
        try:
            response = self.query_client.execute(self.database, user_input)
            return response
        except KustoServiceError as e:
            raise Exception(e)

    # Post a query
    def query(self, user_input, dataframe=True):
        if dataframe:
            response = self.get_response(user_input)
            return dataframe_from_result_table(response.primary_results[0])
        else:
            return self.get_response(user_input)

    # Get a dataframe of all tables in database
    def get_table_names(self):
        get_tables_command = '.show tables'
        response = self.query_client.execute_mgmt(self.database, get_tables_command)
        return dataframe_from_result_table(response.primary_results[0])

    # -----------------------------------------INGESTION-----------------------------------------

    # Create strings for the "creat table" and "create table ingestion csv mapping" commands
    def ingestion_properties(self, dataframe):
        columns_list = []
        csv_mapping_list = []
        # Translate pandas datatypes to kusto datatypes
        type_map = {'float64': 'real',
                    'float32': 'real',
                    'float': 'real',
                    'geometry': 'string',
                    'object': 'string',
                    'int64': 'int',
                    'int32': 'int'}
        # Loop through each column and create respective stings
        for i, col in enumerate(dataframe.columns):
            kusto_type = type_map.get(str(dataframe[col].dtype))
            columns_list.append(f'{col}: {kusto_type}')
            csv_mapping_list.append(f'{{"Name": "{col}", "datatype": "{kusto_type}", "Ordinal": {i}}}')
            # Merge them to one string
        columns_string = ', '.join(columns_list)
        csv_mapping_string = ', '.join(csv_mapping_list)
        return columns_string, csv_mapping_string

    def check_if_exists(self, tablename):
        response = self.query_client.execute_mgmt(self.database, '.show tables')
        table_exists = any(dataframe_from_result_table(response.primary_results[0])['TableName'] == tablename)
        return table_exists, response

    def get_table_folder(self, tablename):
        table_exists, response = self.check_if_exists(tablename)
        if table_exists:
            return self.query(f'.show table {tablename} details | project Folder', dataframe=True)['Folder'][0]
        else:
            raise Exception(f"Table '{tablename}' does not exist in database '{self.database}'.")

    # Function to drop tables from database
    def drop_table(self, tablename):
        self.query(f'.drop table {tablename}_CSV_Mapping ifexists')
        self.query(f'.drop table {tablename} ifexists')

    # Function to drop duplicates from table
    def drop_duplicates(self, tablename):
        folder = self.get_table_folder(tablename)
        if folder == '':
            appendix = folder
        else:
            appendix = f'with (folder={folder})'
        self.query(f'.set TempTable {appendix} <| {tablename} | project-away iris_* | distinct *')
        self.query(f'.rename tables TempTable={tablename} ifexists, {tablename}=TempTable')
        self.query('.drop table TempTable ifexists')

    # Function to write tables to database
    def write_table(self, dataframe, tablename, folder='KustoPyTables'):
        # Get the table creation commands
        columns_string, csv_mapping_string = self.ingestion_properties(dataframe)
        create_table_command = f'.create table {tablename} ({columns_string}) with (folder={folder})'
        create_mapping_command = f'.create table {tablename} ingestion csv mapping \'{tablename}_CSV_Mapping\' \'[{csv_mapping_string}]\' with (folder={folder})'
        # Check if table already exists
        table_exists, response = self.check_if_exists(tablename)
        if table_exists:
            raise Exception(
                f"Table '{tablename}' already exists in database '{self.database}'. If you want to replace the table use write_replace_table().")
        else:
            try:
                # Create the table
                response = self.query_client.execute_mgmt(self.database, create_table_command)
                response_df_table = dataframe_from_result_table(response.primary_results[0])
                # Create the mapping table
                response = self.query_client.execute_mgmt(self.database, create_mapping_command)
                response_df_mapping = dataframe_from_result_table(response.primary_results[0])
                # Add the data
                ingestion_properties = IngestionProperties(database=self.database, table=tablename,
                                                           data_format=DataFormat.CSV)
                self.ingestion_client.ingest_from_dataframe(dataframe, ingestion_properties=ingestion_properties)
                return logging.info(
                    f"Table '{tablename}' successfully created by the following command: {create_table_command}")
            except KustoServiceError as e:
                raise e

    # Function to write and replace tables to database
    def write_replace_table(self, dataframe, tablename, folder='KustoPyTables'):
        # First drop the table (and the mapping table)
        try:
            self.drop_table(tablename)
            self.write_table(dataframe, tablename, folder)
            logging.info(f"Table '{tablename}' replaced in '{self.database}'.")
        except FileNotFoundError:
            self.write_table(dataframe, tablename, folder)
            logging.info(f"Table '{tablename}' newly ingested into '{self.database}'.")