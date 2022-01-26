from os import environ
from dotenv import load_dotenv
import sys
import yaml
import pyodbc
from datetime import datetime
from .crypt import AesEncryption
import json

class Connector:
    def __init__(self, connector_id) -> None:
        self._connector_id = connector_id
        self._job_id = None
        self._credential_objects, self._env = self._load_yml_connector()
        self._load_ev()
        self.row_count = 0
        self.bytes = 0

        # Initialize database
        self._connection = pyodbc.connect(environ['CONNECTION_STRING'])
        self._cursor = self._connection.cursor()
        
        # Setup History ID
        self._history_id = self._get_history_id()

        # Get Job
        self.job = JobDetails(self._get_job())

        self.log_info(f"Starting {self.type} {self.job.ETLJobNM}")

        self.source_columns, self.destination_columns = self._parse_job_data()

        # Parse Credentials
        aes = AesEncryption()

        self.source_credentials = aes.decrypt(self.job.SourceEncryptionTXT)
        self.destination_credentials = aes.decrypt(self.job.DestinationEncryptionTXT)

        # Run Job
        try:
            self.run()
        except Exception as e:
            self.log_unhandled(f"Error with source code: {e}")

        connector_name = self.job.SourceConnectorNM if self._connector_id == self.job.SourceConnectorID else self.job.DestinationConnectorNM

        self.log_info(f"Successfully ran {connector_name} connector.\nColumns affected: {len(self.source_columns)}\nRows affected: {self.row_count}\n")

    def _get_job(self):
        self._cursor.execute("""
            SELECT
                etl.ETLJobNM
                ,scred.EncryptionCredentialTXT as SourceEncryptionTXT
                ,dcred.EncryptionCredentialTXT as DestinationEncryptionTXT
                ,jd.JobDataJSON
                ,jd.SourceObjectID
                ,jd.UpdateMethodCD
                ,jd.DestinationObjectID
                ,scn.ConnectorID as SourceConnectorID
                ,scn.ConnectorNM as SourceConnectorNM
                ,dcn.ConnectorID as DestinationConnectorID
                ,dcn.ConnectorNM as DestinationConnectorNM
                ,dcn.ContainerNM
                ,dcn.VersionNBR
                ,jdr.FilteredColumnNM
                ,jdr.StartSelectionNM
                ,jdr.StartValueTXT
                ,jdr.EndSelectionNM
                ,jdr.EndValueTXT
                ,jdr.TimezoneOffsetNBR
            FROM ETLJobConfiguration as etl
            INNER JOIN JobData jd on jd.JobDataID = etl.SourceJobDataID
            INNER JOIN ConnectorCredential scred on scred.ConnectorCredentialID = etl.SourceCredentialsID
            INNER JOIN ConnectorCredential dcred on dcred.ConnectorCredentialID = etl.DestinationCredentialsID
            INNER JOIN Connector scn on scn.ConnectorID = etl.SourceConnectorID
            INNER JOIN Connector dcn on dcn.ConnectorID = etl.DestinationConnectorID
            LEFT JOIN ETLJobDateRange jdr on jdr.ETLJobDateRangeID = etl.ETLJobDateRangeID
            WHERE ETLJobID = ?
        """, self._job_id)

        row = self._cursor.fetchone()
        if row:
            return row
        else:
            self.log_unhandled(f"Job ID not found: {self._job_id}")
    
    def _get_datetime_offset(self) -> str:
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f %z') # 2017-03-16 10:35:18.5 -06:00

    def log_info(self, message):
        print(message)
        log_cd = 1
        log_dsc = "Info"

        try:
            self._cursor.execute("""
                INSERT INTO [Logging]
                    ([JobID]
                    ,[ETLJobHistoryID]
                    ,[ConnectorID]
                    ,[LogTypeCD]
                    ,[LogTypeDSC]
                    ,[LogTXT]
                    ,[LogDTS]
                    ,[ExternalFacingFLG])
                VALUES (? ,? ,? ,? ,? ,? ,?, ?);
            """, (self._job_id, self._history_id, self._connector_id, log_cd, log_dsc, message, self._get_datetime_offset(), 1))
            self._cursor.commit()

        except Exception as e:
            self._exit_unsafe(f"Failed to log message: {e}")

    def log_internal(self, message):
        print(message)
        log_cd = 1
        log_dsc = "Info"

        try:
            self._cursor.execute("""
                INSERT INTO [Logging]
                    ([JobID]
                    ,[ETLJobHistoryID]
                    ,[ConnectorID]
                    ,[LogTypeCD]
                    ,[LogTypeDSC]
                    ,[LogTXT]
                    ,[LogDTS]
                    ,[ExternalFacingFLG])
                VALUES (? ,? ,? ,? ,? ,? ,?, ?);
            """, (self._job_id, self._history_id, self._connector_id, log_cd, log_dsc, message, self._get_datetime_offset(), 0))
            self._cursor.commit()

        except Exception as e:
            self._exit_unsafe(f"Failed to log message: {e}")
    
    def log_err(self, message):
        print(message)
        log_cd = 2
        log_dsc = "Error"

        try:
            self._cursor.execute("""
                INSERT INTO [Logging]
                    ([JobID]
                    ,[ETLJobHistoryID]
                    ,[ConnectorID]
                    ,[LogTypeCD]
                    ,[LogTypeDSC]
                    ,[LogTXT]
                    ,[LogDTS]
                    ,[ExternalFacingFLG])
                VALUES (? ,? ,? ,? ,? ,? ,?, ?);
            """, (self._job_id, self._history_id, self._connector_id, log_cd, log_dsc, message, self._get_datetime_offset(), 1))
            self._cursor.commit()

        except Exception as e:
            self._exit_unsafe(f"Failed to log message: {e}")

        self.history_fail()

    def log_unhandled(self, message):
        print(message)
        log_cd = 2
        log_dsc = "Error"

        try:
            self._cursor.execute("""
                INSERT INTO [Logging]
                    ([JobID]
                    ,[ETLJobHistoryID]
                    ,[ConnectorID]
                    ,[LogTypeCD]
                    ,[LogTypeDSC]
                    ,[LogTXT]
                    ,[LogDTS]
                    ,[ExternalFacingFLG])
                VALUES (? ,? ,? ,? ,? ,? ,?, ?);
            """, (self._job_id, self._history_id, self._connector_id, log_cd, log_dsc, message, self._get_datetime_offset(), 0))
            self._cursor.commit()
        except Exception as e:
            self._exit_unsafe(f"Failed to log message: {e}")

        self.log_err("A problem internally has occurred. Our team has been notified and will reach out within 24 hours.")

    def _exit_unsafe(self, message):
        print(message)
        sys.exit()

    def exit_no_fail(self, message):
        self.log_info(message)
        sys.exit()

    def run(self):
        self._exit_unsafe("Please overide the run function with connector's specific code.")

    def _parse_job_data(self):
        jobData = json.loads(self.job.JobDataJSON)

        source_columns = []
        destination_columns = []
        for d in jobData:
            column = d['mapped']
            destination_columns.append(d['column'])
            # Filter out any duplicates if any
            if column not in source_columns and column != '':
                source_columns.append(d['mapped'])
            
        return [source_columns, destination_columns]

    def _history_bytes(self):
        try:
            self._cursor.execute("""
                UPDATE ETLJobHistory
                SET 
                    BytesTransferredNBR = ?
                WHERE ETLJobHistoryID = ?
            """, (self.bytes, self._history_id))
            self._cursor.commit()
        except Exception as e:
            self.log_unhandled("Failed updating history: {e}")

    def _history_finished(self):
        try:
            self._cursor.execute("""
                UPDATE ETLJobHistory
                SET 
                    EndDTS = ?
                    ,StatusCD = 2
                    ,StatusDSC = 'Finished'
                WHERE ETLJobHistoryID = ?
            """, (self._get_datetime_offset(), self._history_id))
            self._cursor.commit()
        except Exception as e:
            self.log_unhandled("Failed updating history: {e}")

    def history_fail(self, bytes_transferred=0):
        try:
            self._cursor.execute("""
                UPDATE ETLJobHistory
                SET 
                    EndDTS = ?
                    ,StatusCD = 3
                    ,StatusDSC = 'Failed'
                    ,BytesTransferredNBR = ?
                WHERE ETLJobHistoryID = ?
            """, (self._get_datetime_offset(), bytes_transferred, self._history_id))
            self._cursor.commit()
        except Exception as e:
            self._exit_unsafe(f"Failed on updating history status: {e}")
        sys.exit()

    def _load_ev(self):
            load_dotenv()
            try:
                environ['CONNECTION_STRING']
                environ['MASTER_HASH']
                if self._env:
                    for v in self._env:
                        environ[v]
                self._job_id = environ['JOB_ID']
            except KeyError as e:
                self._exit_unsafe(f"Unable to start job. Environment variable was not provided: {e}")

    def _load_yml_connector(self):
        credentials = None
        env = []
        with open('./connectors.yaml') as file:
            documents = yaml.full_load(file)

            for item, doc in documents.items():
                if doc['connector_id'] == self._connector_id:
                    credentials = doc['credentials']
                    try:
                        env = doc['env']
                    except KeyError:
                        print("No environment variables to load.")
        return [credentials, env]

    def _get_history_id(self):
        history = None
        try:
        # Check if its stored in the environment
            history = environ.get('HISTORY_ID')
        except KeyError as e:
            # History is not in the environment so log problem.
            self.log_unhandled("History was not sent to environment.")
            
        return history

class JobDetails:
    def __init__(self, job):
        self.ETLJobNM = job.ETLJobNM
        self.SourceEncryptionTXT = job.SourceEncryptionTXT
        self.DestinationEncryptionTXT = job.DestinationEncryptionTXT
        self.JobDataJSON = job.JobDataJSON
        self.SourceObjectID = job.SourceObjectID
        self.ContainerNM = job.ContainerNM
        self.VersionNBR = job.VersionNBR
        self.FilteredColumnNM = job.FilteredColumnNM
        self.StartSelectionNM = job.StartSelectionNM
        self.StartValueTXT = job.StartValueTXT
        self.EndSelectionNM = job.EndSelectionNM
        self.EndValueTXT = job.EndValueTXT
        self.TimezoneOffsetNBR = job.TimezoneOffsetNBR
        self.SourceConnectorNM = job.SourceConnectorNM
        self.DestinationConnectorNM = job.DestinationConnectorNM
        self.SourceConnectorID = job.SourceConnectorID
        self.DestinationConnectorID = job.DestinationConnectorID
        self.DestinationObjectID = job.DestinationObjectID
        self.UpdateMethodCD = job.UpdateMethodCD