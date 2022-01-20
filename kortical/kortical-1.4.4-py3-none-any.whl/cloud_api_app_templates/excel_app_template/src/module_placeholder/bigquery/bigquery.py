import os
import logging

from google.oauth2 import service_account
from google.cloud import bigquery
from google.cloud import bigquery_storage


logger = logging.getLogger(__name__)
current_dir = os.path.dirname(os.path.abspath(__file__))

credentials = service_account.Credentials.from_service_account_file(
    f"{current_dir}/service_account_key.json", scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Make clients.
bqclient = bigquery.Client(credentials=credentials, project=credentials.project_id,)
bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)


def create_dataframe_from_bigquery():
    # Creating dataframe from bigquery data
    logger.info('Creating dataframe from bigquery')

    # Download a table.
    table = bigquery.TableReference.from_string(
        "speedy-mcgee.titanic.titanic"
    )
    rows = bqclient.list_rows(
        table,
        selected_fields=[
            bigquery.SchemaField("PassengerId", "INTEGER"),
            bigquery.SchemaField("Pclass", "INTEGER"),
            bigquery.SchemaField("Name", "STRING"),
            bigquery.SchemaField("Sex", "STRING"),
            bigquery.SchemaField("Age", "FLOAT"),
            bigquery.SchemaField("SibSp", "INTEGER"),
            bigquery.SchemaField("Parch", "INTEGER"),
            bigquery.SchemaField("Ticket", "STRING"),
            bigquery.SchemaField("Fare", "FLOAT"),
            bigquery.SchemaField("Cabin", "STRING"),
            bigquery.SchemaField("Embarked", "STRING"),
        ],
    )
    dataframe = rows.to_dataframe(bqstorage_client=bqstorageclient)
    return dataframe
