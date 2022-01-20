import glob
import json
import os
import shutil
from pathlib import Path
from typing import List

from bqq import const
from bqq.types import JobInfo
from google.cloud.bigquery.schema import SchemaField


class Schemas:
    def __init__(self):
        self.path = const.BQQ_SCHEMAS

    def clear(self):
        dirs = glob.glob(f"{self.path}/*")
        for dir in dirs:
            shutil.rmtree(dir)

    def write(self, project: str, id: str, schema: List[SchemaField]):
        path = f"{self.path}/{project}"
        Path(path).mkdir(exist_ok=True)

        filename = f"{self.path}/{project}/{id}.json"
        with open(filename, "w") as f:
            f.write(json.dumps([field.to_api_repr() for field in schema]))

    def read(self, job_info: JobInfo) -> List[SchemaField]:
        filename = f"{self.path}/{job_info.project}/{job_info.job_id}.json"
        schema = []
        if os.path.isfile(filename):
            with open(filename) as f:
                columns = json.load(f)
                for col in columns:
                    field = SchemaField.from_api_repr(col)
                    schema.append(field)

        return schema
