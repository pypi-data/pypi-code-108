from abc import ABC, abstractmethod
from typing import List


class DataFactoryPipeline(ABC):

    # The general name of the connection type
    name = None

    # Dictionary where the keys are the names of the possible authentication
    # options e.g. 'basic', 'token'. The values are a sub-dictionary with 2
    # keys, 'required', and 'optional', and those values are a list of the
    # corresponding parameters required or optional for this connection type
    authentications = {}

    # A list of strings giving the names of the required and optional
    # parameters to define for each table
    required_table_parameters = []
    optional_table_parameters = []

    default_policy = {
        "timeout": "0.00:01:00",
        "retry": 3,
        "retryIntervalInSeconds": 30,
        "secureOutput": False,
        "secureInput": False
    }

    data_provider = None
    authentication = None
    config = {}
    table_definition = {}
    data_sets = {}
    source_store_settings = {}

    source_data_sets = {}
    target_linked_service = None
    target_data_sets = {}
    config_linked_service = None
    config_data_sets = {}

    default_schedule = {}

    @classmethod
    def is_valid_authentication(cls, authentication_method: str) -> bool:
        return authentication_method in cls.authentications

    @classmethod
    def all_authentications(cls) -> List[str]:
        return list(cls.authentications.keys())

    @staticmethod
    def _validate_config(config: dict, required_parameters: List[str],
                         optional_parameters: List[str]) -> None:
        """
        Validate any config given the lists of parameters
        """
        errors = []

        missing_parameters = [
            rp for rp in required_parameters
            if rp not in config
        ]
        if missing_parameters:
            errors.append(f"Fields missing from config: {missing_parameters}")

        unknown_parameters = [
            c for c in config
            if c not in required_parameters + optional_parameters
        ]
        if unknown_parameters:
            errors.append(f"Unknown fields in config: {unknown_parameters}")

        if errors:
            raise Exception(errors)

    def __init__(self, name, parameters={}, variables={}, annotations=[]):
        self.pipeline_json = {
            "name": name,
            "type": "Microsoft.DataFactory/factories/pipelines",
            "properties": {
                "activities": [],
                "parameters": parameters,
                "variables": variables,
                "annotations": annotations
            }
        }
        if not self.source_store_settings:
            raise Exception(
                f"source_store_settings not set for data type {self.name}!")

    @classmethod
    def get_source_linked_service(cls, connection_name):
        return cls.authentications[connection_name]["linked_service"]

    def add_activity(self, activity_json, depends_on=[]):
        self.pipeline_json["properties"]["activities"].append({
            **activity_json,
            "dependsOn": [
                {
                    "activity": activity["name"],
                    "dependencyConditions": ["Succeeded"]
                }
                for activity in depends_on
                ]
            })

    def create_pipeline_dataset_reference(self, data_set_json, parameters={}):
        missing_parameters = [
            parameter_name
            for parameter_name, val
            in data_set_json["properties"].get("parameters", {}).items()
            if parameter_name not in parameters
            and val.get("defaultValue") is None
        ]
        if missing_parameters:
            raise Exception(f"Missing parameters when accessing dataset "
                            f"{data_set_json['name']}: {missing_parameters}")
        return {
            "referenceName": data_set_json["name"],
            "type": "DatasetReference",
            "parameters": parameters
        }

    def list_target_files(
                self, container, path,
                policy_ovverride={}):
        return {
            "name": f"List {container}/{path} files".replace("/", "-"),
            "type": "GetMetadata",
            "dependsOn": [],
            "policy": {**self.default_policy, **policy_ovverride},
            "userProperties": [],
            "typeProperties": {
                "dataset": self.create_pipeline_dataset_reference(
                    self.data_sets["target_folder"], {
                        "Container": container,
                        "FolderPath": path
                    })
            },
            "fieldList": [
                "childItems"
            ],
            "storeSettings": {
                "type": "AzureBlobFSReadSettings",
                "recursive": True,
                "enablePartitionDiscovery": False
            },
            "formatSettings": {
                "type": "BinaryReadSettings"
            }
        }

    @abstractmethod
    def generate_pipeline(self):
        ...
