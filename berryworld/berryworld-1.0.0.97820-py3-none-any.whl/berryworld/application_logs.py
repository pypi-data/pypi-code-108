from berryworld.sql_connection import *
import datetime


class ApplicationLogs:

    def __init__(self, sql_con, schema_name, table_name):
        self.started_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.finalised_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.processed = 0
        self.sql_con = sql_con
        self.schema_name = schema_name
        self.table_name = table_name
        self.url = ''
        self.job_name = ''

    def start_log(self, job_name='', url=''):
        self.started_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.job_name = job_name
        self.url = url
        df = pd.DataFrame({'JobName': [self.job_name], 'URL': [self.url],
                           'Started': [self.started_datetime], 'Processed': [self.processed]})
        self.sql_con.insert(df, self.schema_name, self.table_name)
        print("Process: " + self.job_name + ". Started at " + self.started_datetime)

    def finalise_log(self, error=''):
        self.finalised_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.processed = 1
        df = pd.DataFrame({'JobName': [self.job_name], 'URL': [self.url],
                           'Started': [self.started_datetime], 'Finalised': [self.finalised_datetime],
                           'Processed': [self.processed], 'Error': [error]})
        self.sql_con.merge_into(df, self.schema_name, self.table_name, ['JobName', 'URL', 'Started'],
                                ['Finalised', 'Processed', 'Error'])
        print("Process: " + self.job_name + ". Finished at " + self.started_datetime)
