import json
from pathlib import Path

import boto3
import cloudpickle
from botocore.exceptions import ClientError

from lunar.config import Config
from lunar.lunar_client import LunarError
from lunar.ml import EDDService, LunarModel


class ModelRegistryError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ModelRegistry:
    def __init__(self, config: Config):
        self.config = config

    def save(self, lunar_model: LunarModel, force: bool = False, to_local: bool = False) -> None:
        relative_path = Path("myfiles", "models") if self.config.RUNTIME_ENV == "EDD" else Path("models")
        relative_path = relative_path.joinpath(lunar_model.name, lunar_model.version)

        path = Path.home().joinpath(relative_path)
        path.mkdir(parents=True, exist_ok=True)

        with open(path.joinpath("model.joblib"), "wb") as f:
            cloudpickle.dump(lunar_model, f)

        with path.joinpath("model.json").open("w") as f:
            json.dump(
                {
                    "name": lunar_model.name,
                    "version": lunar_model.version,
                    "models": [m.__class__.__name__ for m in lunar_model.models],
                    **lunar_model.attrs,
                },
                f,
            )

        if to_local:
            return

        if self.config.RUNTIME_ENV == "EDD":
            res = EDDService(self.config).copy_model_to_s3(
                model_path=f"{relative_path}/", model_name=lunar_model.name, model_version=lunar_model.version
            )
            if res["status"] != 200:
                raise LunarError(code=400, msg=res["error"])

        elif self.config.RUNTIME_ENV == "LOCAL":
            client = boto3.client("s3")
            bucket_name = f"lunar-model-registry-{self.config.ENV.lower()}"

            try:
                client.head_bucket(Bucket=bucket_name)
            except ClientError:
                raise LunarError(code=400, msg=f"Bucket {bucket_name} does not exist.")

            model_path = f"{lunar_model.name}/{lunar_model.version}"

            if not force:
                paginator = client.get_paginator("list_objects_v2")
                for response in paginator.paginate(Bucket=bucket_name, Prefix=model_path):
                    if "Contents" in response:
                        raise LunarError(code=400, msg=f"Model binary & meta files already exist on {model_path}.")

            for file_name in ["model.joblib", "model.json"]:
                try:
                    client.upload_file(
                        Filename=f"{str(path)}/{file_name}", Bucket=bucket_name, Key=f"{model_path}/{file_name}"
                    )
                except ClientError as e:
                    raise LunarError(code=400, msg=str(e))
