# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import csv
from datetime import datetime
from pathlib import Path
import re

from azure.storage.blob import BlobServiceClient


def _get_rows_from_csv(file_path, column_type_dict=None):
    """Parse a csv file to a list of dicts."""
    if not column_type_dict:
        column_type_dict = {}
    rows = []
    with open(file_path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            for key, value in row.items():
                if value == "N/A":
                    row[key] = None
                elif key in column_type_dict:
                    if column_type_dict[key] == datetime:
                        # No datetime.fromisoformat API in Python 3.6
                        row[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        row[key] = column_type_dict[key](value)
            rows.append(row)
    return rows


class _DataDownloader(object):
    """Pull metric data from blob."""

    def __init__(self, data_store, run_id):
        """Init blob client."""
        connection_string = "DefaultEndpointsProtocol={};AccountName={};AccountKey={};EndpointSuffix={}".format(
            data_store.protocol,
            data_store.account_name,
            data_store.account_key,
            data_store.endpoint,
        )
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = blob_service_client.get_container_client("azureml")
        self.run_id = run_id
        self.metric_blob_prefix = "ExperimentRun/dcid.{}/logs/sys/metrics/".format(self.run_id)
        self.processed_mini_batches_blob_name = (
            "ExperimentRun/dcid.{}/logs/sys/job_report/processed_mini-batches.csv".format(self.run_id)
        )

    def get_latest_progress(self):
        """Get latest progress data. Return None if can't get data."""
        latest_blob_name = None
        for blob in self.container_client.list_blobs(self.metric_blob_prefix):
            m = re.match("^{}([^/]+)/progress.csv$".format(self.metric_blob_prefix), blob.name)
            if m:
                if not latest_blob_name:
                    latest_blob_name = blob.name
                elif blob.name > latest_blob_name:
                    latest_blob_name = blob.name

        if latest_blob_name:
            column_type_dict = {
                "Datetime": datetime,
                "Total Tasks": int,
                "Scheduled Tasks": int,
                "Completed Tasks": int,
                "Failed Tasks": int,
            }
            rows = self._get_rows_from_blob_csv(latest_blob_name, column_type_dict, re_download=True)
            if rows:
                return rows[-1]

        return None

    def get_final_progress(self):
        """Get the final progress data. Retrieved from processed_mini-batch.csv after job terminates."""
        blob_client = self.container_client.get_blob_client(blob=self.processed_mini_batches_blob_name)
        if not blob_client.exists():
            return None

        rows = self._get_rows_from_blob_csv(self.processed_mini_batches_blob_name)
        processed_task_ids = set()
        succeeded_task_ids = set()
        for row in rows:
            if row["Mini-batch Id"]:
                task_id = row["Mini-batch Id"]
                processed_task_ids.add(task_id)
                if row["Status"] == "RUN_DONE":
                    succeeded_task_ids.add(task_id)

        progress_dict = {
            "Total Tasks": None,
            "Completed Tasks": len(processed_task_ids),
            "Failed Tasks": len(processed_task_ids) - len(succeeded_task_ids),
            "Scheduled Tasks": None,
            "Elapsed Time": None,
            "Estimated Remaining Time": "0:00:00",
        }
        return progress_dict

    def _get_rows_from_blob_csv(self, blob_name, column_type_dict=None, re_download=True):
        """Parse a csv file in blob to a list of dicts."""
        local_path = self._download(blob_name, re_download)
        return _get_rows_from_csv(local_path, column_type_dict)

    def _download(self, blob_name, re_download=True):
        """Download a file in blob."""
        path_components = blob_name.split("/")
        local_path = Path("..", *path_components)
        if re_download or not local_path.exists():
            local_path.parent.mkdir(parents=True, exist_ok=True)
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            with open(local_path, "wb") as fp:
                fp.write(blob_client.download_blob().readall())
        return local_path
