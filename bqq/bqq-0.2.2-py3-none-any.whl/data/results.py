import csv
import glob
import os
import shutil
from pathlib import Path
from typing import Optional

from bqq import const
from bqq.types import JobInfo, Result
from google.cloud.bigquery.table import RowIterator
from rich.console import Console


class Results:
    def __init__(self, console: Console):
        self.path = const.BQQ_RESULTS
        self.console = console

    def clear(self):
        dirs = glob.glob(f"{self.path}/*")
        for dir in dirs:
            shutil.rmtree(dir)

    def write(self, project: str, id: str, rows: RowIterator):
        path = f"{self.path}/{project}"
        Path(path).mkdir(exist_ok=True)
        filename = f"{self.path}/{project}/{id}.csv"
        with open(filename, "w") as f:
            writer = csv.writer(f)
            header = [field.name for field in rows.schema]
            writer.writerow(header)
            for row in rows:
                writer.writerow(row)

    def read(self, job_info: JobInfo) -> Optional[Result]:
        filename = f"{self.path}/{job_info.project}/{job_info.job_id}.csv"
        result = None
        if os.path.isfile(filename):
            with open(filename) as f:
                reader = csv.reader(f, delimiter=",")
                header = reader.__next__()
                result = Result(header, list(reader))
        return result
