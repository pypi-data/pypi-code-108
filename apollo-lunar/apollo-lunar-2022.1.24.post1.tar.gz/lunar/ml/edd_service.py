from typing import Any, Dict

import os
import requests
import time

from lunar.config import Config
from lunar.data import BatchClient
from lunar.lunar_client import LunarError

BATCH_JOB_CHECK_STATUS_LIST = ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"]


class EDDService:
    def __init__(self, config: Config):
        if config.RUNTIME_ENV != "EDD":
            raise LunarError(code=400, msg="EDDService is only available on EDD runtime")

        self.config = config
        self.batch_client = BatchClient(config=config)

    def copy_model_to_s3(self, model_path: str, model_name: str, model_version: str) -> Dict[str, Any]:
        """
        Copy model binaries and meta files from EDD to Lunar model registry.

        ## Args

        - model_path: (str) Relative path of model binaries and meta (Caution: Must not start with slash and must end with slash)
        - model_name: (str) Name of a model
        - model_version: (str) Version of a model

        ## Returns
        dict

        ## Example

        ```python
        response = copy_model_to_s3(model_path="myfiles/models/test_model/v1/", model_name="test_model", version="v1")

        ```
        """
        if model_path.startswith("/"):
            model_path = model_path[1:]
        if not model_path.endswith("/"):
            model_path = f"{model_path}/"

        data = {
            "copy_source": model_path,
            "s3_path": f"s3://lunar-model-registry-{self.config.ENV.lower()}/{model_name}/{model_version}/",
            "user_id": os.uname()[1].split("-")[2],
        }

        response = requests.post(
            url=self.config.COPY_FILES_URL,
            json=data,
        )

        if response.status_code != 200:
            raise LunarError(code=400, msg=str(response.reason))

        result = response.json()
        if result["status"] != 200:
            raise LunarError(code=400, msg=result.get("error"))

        while True:
            response = requests.post(
                url=self.config.JOB_STATUS_URL,
                json={"job_id": result["result"]["job_id"]},
            )

            if response.status_code != 200:
                raise LunarError(code=400, msg=str(response.reason))

            job_status_result = response.json()
            if job_status_result["status"] == 200:
                if job_status_result["result"]["state"] == "Succeeded":
                    break
                elif job_status_result["result"]["state"] == "Failed":
                    raise LunarError(code=400, msg=str(job_status_result["result"]["error"]))

            time.sleep(1)

        return result

    def copy_table_to_s3(
        self,
        database_name: str,
        table_name: str,
        db_type: str,
        operation: str,
        target_name: str = None,
        s3_dt: str = None,
        edd_table_partition: str = None,
    ) -> Dict[str, Any]:
        """
        Copy a table from EDD S3 to Lunar S3 and Database(dynamodb or docdb).

        ## Args

        - database_name: (str) Database name of EDD S3 ('Datalake' is not available)
        - table_name: (str) Name of a table on EDD S3
        - db_type: (str) Type of database to be loaded on Lunar ('dynamodb' | 'docdb')
        - operation: (str) Type of operation ('put' | 'update' | 'delete')
        - target_name: (optional) (str) Target name on database to be loaded (Default: Value of `table_name`)
        - s3_dt: (optional) (str) Set a dt partition on Lunar S3. If db_type is `docdb`, it is necessary
        - edd_table_partition: (optional) (str) Partition value of table on EDD S3

        ## Returns
        dict

        ## Example

        ```python
        response = copy_table_to_s3(
            database_name="apollo",
            table_name="test_table",
            db_type="docdb",
            operation="put",
            target_name="test_data",
            s3_dt="20211101",
            edd_table_partition="dt=202109/type=put",
        )


        ```
        """

        assert db_type in ["dynamodb", "docdb"], "`db_type` must be one of `dynamodb` or `docdb`"
        assert operation in ["put", "update", "delete"], "`operation` must be one of `put` or `update` or `delete`"

        if db_type == "docdb" and not s3_dt:
            raise LunarError(code=400, msg="Parameter 's3_dt' is necessary when db_type is 'docdb'")

        target_name = target_name if target_name else table_name

        job_name = f"{target_name}-{operation}"
        job_list = self.batch_client.get_batch_list(job_status_list=BATCH_JOB_CHECK_STATUS_LIST)

        if job_name in job_list:
            raise LunarError(code=400, msg=f"Job {job_name} is already submitted to Lunar S3")

        s3_dt_str = f"dt={s3_dt}/" if s3_dt else ""

        data = {
            "database_name": database_name,
            "table_name": table_name,
            "s3_path": f"s3://lunar-loader-{self.config.ENV.lower()}/{db_type}/{target_name}/{s3_dt_str}op={operation}/",
            "user_id": os.uname()[1].split("-")[2],
        }
        if edd_table_partition:
            data["partition"] = edd_table_partition
            data["write_raw_s3_path"] = True

        response = requests.post(
            url=self.config.COPY_DATABASE_URL,
            json=data,
        )

        if response.status_code != 200:
            raise LunarError(code=400, msg=str(response.reason))

        result = response.json()
        if result["status"] != 200:
            raise LunarError(code=400, msg=result.get("error"))

        while True:
            response = requests.post(
                url=self.config.JOB_STATUS_URL,
                json={"job_id": result["result"]["job_id"]},
            )

            if response.status_code != 200:
                raise LunarError(code=400, msg=str(response.reason))

            job_status_result = response.json()
            if job_status_result["status"] == 200:
                if job_status_result["result"]["state"] == "Succeeded":
                    break
                elif job_status_result["result"]["state"] == "Failed":
                    raise LunarError(code=400, msg=str(job_status_result["result"]["error"]))

            time.sleep(1)

        return response.json()
