import math
from threading import Thread
import pandas as pd
import datetime
import time


class EmailLogging:
    """ Manage Error Logs in ApplicationLogs """

    def __init__(self, project_name, pipeline, ip_address, request_url, sql_con=None, timeout=30*60):
        """ Initialize the class
        :param project_name: Name of the project being run. it must be already declared in PythonEmailProjectSeverity
        :param pipeline: Pipeline name being run. It must identify the process being executed uniquely
        :param ip_address: IP Address
        :param request_url: URL requested by the client
        :param sql_con: Connection to the Database to upload the Logs
        :param timeout: Time in seconds after which an unsuccessful log will be sent
        """
        self.log_df = pd.DataFrame({'ProjectName': [project_name], 'Pipeline': [pipeline],
                                    'Successful': [0], 'IPAddress': [ip_address],
                                    'RequestUrl': [request_url], 'Sent': [0],
                                    'StartedDate': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]})
        self.id_list = list()
        self.sql_con = sql_con
        self.timeout = timeout
        self.exit_event = False
        Thread(target=self.start_threading).start()

    def start_threading(self):
        """ Start a threading to update on failure if the script breaks or the pipeline gets blocked
        """
        time_range = math.ceil(self.timeout / 10)
        for times in range(time_range):
            time.sleep(10)
            if self.exit_event:
                break

        if len(self.id_list) == 0:
            self.on_failure(error_message=f'The pipeline failed to succeed after running '
                                          f'for {self.timeout/60:.2f} minutes')

    def on_successful(self):
        """ Update log on success
        """
        if len(self.id_list) == 0:
            successful_columns = {'Successful': 1,
                                  'FinishedDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}
            self.log_df = self.log_df.assign(**successful_columns)
            self.id_list.append(self.sql_con.insert(self.log_df, 'ETL', 'PythonEmailLogs', output=['Id']))
            self.exit_event = True

    def on_failure(self, error_message, section=None):
        """ Update log on failure
        :param error_message: Error message to be sent in the Log
        :param section: Indicate the script section. Useful to locate the error
        """
        unsuccessful_columns = {'Successful': 0,
                                'FinishedDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                'Section': section,
                                'ErrorMessage': str(error_message).replace("'", "''")}
        self.log_df = self.log_df.assign(**unsuccessful_columns)
        self.id_list.append(self.sql_con.insert(self.log_df, 'ETL', 'PythonEmailLogs', output=['Id']))
        self.exit_event = True
