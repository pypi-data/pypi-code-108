from os import environ
import boto3
from .connector import Connector
import io
import pandas as pd
from pandas.core.frame import DataFrame
import sys

BUCKET_NAME = 'dataconnector-temp-uploads'
SUB_FOLDER = 'etlJobHistory'

s3_resource = boto3.resource('s3')
ecs_resource = boto3.client('ecs')

class SourceConnector(Connector):
    """Holds the functions specific to source connectors

    This class is a template class for source connectors in DataConnector. Many of the functions will need to be
    overwritten in its inherited classes.
    """

    def __init__(self, connector_id):
        self.type = "source"
        super().__init__(connector_id)
        print(environ['APP_ENV'])
        if environ['APP_ENV'] == 'production' or environ['APP_ENV'] == 'staging':
            self._invoke_next()

    def _get_history_id(self):
        history = None
        try:
        # Check if its stored in the environment
            history = environ['HISTORY_ID']
        except KeyError as e:
            # History is not in the environment so create a new one.
            history = self._create_history()
        
        if history is None:
            self.log_unhandled("Error trying to create new history.")
        return history
    
    def _create_history(self) -> str:
        self._cursor.execute("""
            INSERT INTO [ETLJobHistory]
                ([ETLJobID]
                ,[StartDTS]
                ,[StatusCD]
                ,[StatusDSC])
            VALUES
                (?
                ,?
                ,1
                ,'Running')
        """, (self._job_id, self._get_datetime_offset(),))
        self._cursor.commit()

        self._cursor.execute("""
            SELECT TOP 1 ETLJobHistoryID FROM [ETLJobHistory] WHERE ETLJobID = ? ORDER BY ETLJobHistoryID DESC
        """, (self._job_id,))

        row = self._cursor.fetchone()
        if row:
            self._history_id = row.ETLJobHistoryID
            return self._history_id
        else:
            self.exit_fail("Failed to create ETL History.")

    def apply_df_filters(self, df):
        if self.job.FilteredColumnNM and self.job.FilteredColumnNM != "":
            self.log_info(f"Filters applied to {self.job.FilteredColumnNM}")
        else:
            self.log_info("No filters applied.")

        return df

    def upload_batch_records(self, df: DataFrame, batch):
        """
        
        """
        if df is None or len(df) == 0:
            self.end_no_rows()

        json = df.to_json(orient="records")

        self.bytes += sys.getsizeof(json)

        json_buffer = io.StringIO(json)

        s3_resource.Object(BUCKET_NAME, f"{SUB_FOLDER}/e{self._history_id}-b{batch}.json").put(Body=json_buffer.getvalue())

    def upload_records(self, df: DataFrame, batch=None):
        """
        Uploads all records retrieved to S3. Call this function optionally passing in df parameter. If no parameter is given or
        the passed in dataframe is empty the connector will end calling end_no_rows function.

        :param df - Pandas Dataframe needing to be uploaded.
        """
        if df is None or len(df) == 0:
            self.end_no_rows()

        json = df.to_json(orient="records")

        self.bytes += sys.getsizeof(json)

        batch_holder = []
        batches = []
        max_file_size = 5242880
        if sys.getsizeof(json) < max_file_size:
            json_buffer = io.StringIO(json)
            s3_resource.Object(BUCKET_NAME, f"{SUB_FOLDER}/e{self._history_id}-b0.json").put(Body=json_buffer.getvalue())
        else:
            for x in range(0, len(json)):
                if sys.getsizeof(batch_holder) < max_file_size:
                    batch_holder.append(json[x])
                    if x == len(json) - 1:
                        batches.append(batch_holder)
                        batch_holder = []
                else:
                    batches.append(batch_holder)
                    batch_holder = []
                    batch_holder.append(json[x])
            for batch in range(0, len(batches)):
                json_buffer = io.StringIO(str(batches[batch]))
                s3_resource.Object(BUCKET_NAME, f"{SUB_FOLDER}/e{self._history_id}-b{batch}.json").put(Body=json_buffer.getvalue())


    def _invoke_next(self):
        self._history_bytes()

        response = ecs_resource.run_task(
            cluster='dc-3',
            count=1,
            enableECSManagedTags=False,
            enableExecuteCommand=False,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        'subnet-095c3230c890e0841',
                    ],
                    'securityGroups': [
                        'sg-00678e3bdcef56894',
                    ],
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides={
                'containerOverrides': [
                    {
                        'name': self.job.ContainerNM,
                        'environment': [
                            {
                                'name': 'JOB_ID',
                                'value': str(self._job_id)
                            },
                            {
                                'name': 'HISTORY_ID',
                                'value': str(self._history_id)
                            }
                        ],
                    }
                ],
            },
            platformVersion='LATEST',
            taskDefinition=f"{self.job.ContainerNM}:{self.job.VersionNBR}"
        )

        if len(response['tasks']) == 0:
            self.log_unhandled("Problem invoking next connector.")


    def end_no_rows(self):
        self._history_finished()
        self.exit_no_fail("No rows were returned from source. Finished job.")
