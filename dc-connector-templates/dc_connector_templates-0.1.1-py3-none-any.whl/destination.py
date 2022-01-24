import boto3
from .connector import Connector
from io import BytesIO
import pandas as pd

BUCKET_NAME = 'dataconnector-temp-uploads'
SUB_FOLDER = 'etlJobHistory'

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
ecs_resource = boto3.client('ecs')

class DestinationConnector(Connector):
    """Holds the functions specific to destination connectors

    This class is a template class for destination connectors in DataConnector.
    """

    def __init__(self, connector_id):
        self.type = "destination"
        super().__init__(connector_id)
        self._history_finished()

    def _get_all_keys(self):
        keys = []
        for key in s3_client.list_objects(Bucket=BUCKET_NAME, Prefix=f"etlJobHistory/e{self._history_id}")['Contents']:
            keys.append(key['Key'])
        return keys
    
    def batch(self, df):
        self._exit_unsafe("Please overide the batch function with connector's specific code.")
        
    def run_batches(self):
        keys = self._get_all_keys()

        for key in keys:
            obj = s3_resource.Object(BUCKET_NAME, key)
            with BytesIO(obj.get()['Body'].read()) as bio:
                df = pd.read_json(bio)
                self.batch(df)