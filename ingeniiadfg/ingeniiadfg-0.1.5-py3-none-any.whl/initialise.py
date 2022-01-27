from copy import deepcopy
import json
from os import listdir, makedirs, path, remove
from re import sub

from .defaults import default_annotations
from .schedule import create_schedule_id, create_recurrence_object, \
    trigger_name
from .sftp import FTPPipeline, SFTPPipeline
from .templates.dataset import all_data_sets
from .templates.linked_service import all_linked_services


class CreateDataFactoryObjects:

    connection_types = {
        "ftp": FTPPipeline,
        "sftp": SFTPPipeline
    }

    base_integration_runtime = "AutoResolveIntegrationRuntime"

    def __init__(self, config_folder=None, generated_folder=None,
                 overwrite=False, remove_not_generated=False):
        self.config_folder = config_folder or "configs"
        self.generated_folder = generated_folder or "generated"
        self.overwrite = overwrite
        self.remove_not_generated = remove_not_generated

        self.shir_folder = f"{self.generated_folder}/integrationRuntime"
        self.linked_service_folder = f"{self.generated_folder}/linkedService"
        self.data_set_folder = f"{self.generated_folder}/dataset"
        self.pipeline_folder = f"{self.generated_folder}/pipeline"
        self.trigger_folder = f"{self.generated_folder}/trigger"

        self.check_folders()

        self.all_linked_services = set()
        self.all_data_sets = set()

        self.all_config_jsons = []
        self.all_self_hosted_integration_runtimes = {}
        self.all_linked_service_jsons = {}
        self.all_data_set_jsons = {}
        self.all_pipelines = {}
        self.all_triggers = {}
        self.all_trigger_jsons = {}

        self.credentials_store_per_ir = {}

        self.source_data_sets_per_type = {}
        self.target_data_sets = {}

    def check_folders(self):
        for folder in [
            self.shir_folder, self.linked_service_folder,
            self.data_set_folder, self.pipeline_folder,
            self.trigger_folder
        ]:
            if not path.exists(folder):
                makedirs(folder)

    def get_configs(self):
        if not self.all_config_jsons:
            for config_file_name in listdir(self.config_folder):

                if not config_file_name.endswith(".json"):
                    continue

                file_path = f"{self.config_folder}/{config_file_name}"

                with open(file_path, "r") as json_file:
                    self.all_config_jsons.append(json.load(json_file))

        for config_json in self.all_config_jsons:
            yield config_json

    def find_self_hosted_integration_runtimes(self):
        for config in self.get_configs():
            if "self_hosted_integration_runtime" in config:
                shir_name = config["self_hosted_integration_runtime"]
                if shir_name not in self.all_self_hosted_integration_runtimes:
                    self.all_self_hosted_integration_runtimes[shir_name] = {
                        "name": shir_name,
                        "properties": {
                            "type": "SelfHosted"
                        }
                    }

    def find_all_connections(self):
        # Find all unique instances of connection and authentication types

        if not self.all_linked_services:
            for config in self.get_configs():
                conn = self.connection_types[config["connection"]]
                auth = config["authentication"]
                ir_name = config.get(
                    "self_hosted_integration_runtime",
                    self.base_integration_runtime)

                source_ls = conn.get_source_linked_service(auth)["name"]
                self.all_linked_services.add((source_ls, ir_name))

                for _, source_dataset in conn.source_data_sets.items():
                    self.all_data_sets.add(
                        (source_ls, ir_name, source_dataset["name"]))

                target_ls = conn.target_linked_service["name"]
                self.all_linked_services.add((target_ls, ir_name))

                for _, target_dataset in conn.target_data_sets.items():
                    self.all_data_sets.add(
                        (target_ls, ir_name, target_dataset["name"]))

                if conn.config_linked_service:
                    config_ls = conn.config_linked_service["name"]
                    self.all_linked_services.add((config_ls, ir_name))

                    for _, config_dataset in conn.config_data_sets.items():
                        self.all_data_sets.add(
                            (config_ls, ir_name, config_dataset["name"]))

            # Add the credentials store, if required
            add_credentials_store = set()
            for ls_name, ir_name in self.all_linked_services:
                base_json = all_linked_services[ls_name]

                for _, v in base_json["properties"]["typeProperties"].items():
                    if not isinstance(v, dict):
                        continue
                    if v.get("type") == "AzureKeyVaultSecret":
                        add_credentials_store.add(ir_name)

            # Add this outside the loop so the set doesn't change size
            for name in add_credentials_store:
                self.all_linked_services.add(("Credentials Store", name))
                self.credentials_store_per_ir[name] = \
                    self.create_linked_service_name(
                        "Credentials Store", name)

    @staticmethod
    def get_file_path(folder_path, json_to_write):
        return f"{folder_path}/{json_to_write['name']}.json"
    
    def get_current_json(self, folder_path, json_to_write):
        file_path = self.get_file_path(folder_path, json_to_write)

        if not path.isfile(file_path):
            return

        with open(file_path) as json_file:
            return json.load(json_file)

    def create_linked_service_name(self, base_name, integration_runtime_name):
        if integration_runtime_name == self.base_integration_runtime:
            return base_name
        else:
            return f"{base_name}{integration_runtime_name}"

    linked_service_preservation = (
        ("AzureBlobFS", "url"),
        ("AzureKeyVault", "baseUrl")
    )

    def create_linked_service(self, base_json, integration_runtime_name):
        new_ls_json = deepcopy(base_json)
        if integration_runtime_name != self.base_integration_runtime:
            new_ls_json["name"] = \
                self.create_linked_service_name(base_json["name"],
                                                integration_runtime_name)
            new_ls_json["properties"]["connectVia"] = {
                "referenceName": integration_runtime_name,
                "type": "IntegrationRuntimeReference"
            }

            for _, v in new_ls_json["properties"]["typeProperties"].items():
                if not isinstance(v, dict):
                    continue
                if v.get("type") == "AzureKeyVaultSecret":
                    v["store"]["referenceName"] = \
                        self.credentials_store_per_ir[integration_runtime_name]

        curr_file = self.get_current_json(
            self.linked_service_folder, new_ls_json)
        if curr_file and not self.overwrite:
            for ls_type, replace_str in self.linked_service_preservation:
                if curr_file["properties"]["type"] == ls_type:
                    new_ls_json["properties"]["typeProperties"][
                        replace_str
                    ] = curr_file["properties"]["typeProperties"][
                        replace_str
                    ]

        return new_ls_json

    def create_dataset_name(self, linked_service_name, data_set_template_name):

        ds_name = data_set_template_name
        if ds_name.lower().startswith(linked_service_name.lower()):
            ds_name = ds_name[len(linked_service_name):]

        prefix = 0
        while ds_name[:prefix + 1] == linked_service_name[:prefix + 1]:
            prefix += 1
        ds_name = ds_name[prefix:]

        return sub("[^0-9a-zA-Z_]+", "", linked_service_name + ds_name)

    def find_all_linked_services(self):
        # Find only the required linked services
        self.find_all_connections()

        for ls_name, ir_name in self.all_linked_services:

            template_linked_service = all_linked_services[ls_name]

            ls_json = self.create_linked_service(
                template_linked_service, ir_name)
            if ls_json["name"] not in self.all_linked_service_jsons:
                self.all_linked_service_jsons[ls_json["name"]] = ls_json

    def find_all_data_sets(self):
        for ls_name, ir_name, ds_name in self.all_data_sets:

            linked_service_json = self.all_linked_service_jsons[
                self.create_linked_service_name(
                    ls_name, ir_name)
            ]
            data_set_template = all_data_sets[ds_name]

            ds_id = (linked_service_json["name"], data_set_template["name"])
            if ds_id not in self.all_data_set_jsons:

                data_set_json = deepcopy(data_set_template)

                data_set_json["name"] = \
                    self.create_dataset_name(
                        linked_service_json["name"], ds_name)

                parameters = linked_service_json["properties"].get(
                    "parameters", {})

                # Add linked service definition, including required parameters
                data_set_json["properties"]["linkedServiceName"] = {
                    "referenceName": linked_service_json["name"],
                    "type": "LinkedServiceReference",
                }
                if parameters:
                    data_set_json["properties"]["linkedServiceName"]["parameters"] = {
                        param: {
                            "value": f"@dataset().{param}",
                            "type": "Expression"
                        }
                        for param in parameters
                    }
                # Add linked service parameters to data set parameters
                for param, val in parameters.items():
                    data_set_json["properties"]["parameters"][param] = val

                self.all_data_set_jsons[ds_id] = data_set_json

    def generate_pipelines(self):

        for config in self.get_configs():
            conn = config["connection"]
            auth = config["authentication"]
            ir_name = config.get(
                "self_hosted_integration_runtime",
                self.base_integration_runtime)

            # Get the required pipeline type for this configuation
            pipeline_class = self.connection_types[conn]

            # Add the schedule if we don't know about it already
            schedule_details = \
                config.get("schedule", pipeline_class.default_schedule)
            schedule_id = create_schedule_id(schedule_details)
            if schedule_id not in self.all_triggers:
                self.all_triggers[schedule_id] = []

            # Take the linked services and add the required data sets
            source_linked_service_name = \
                self.create_linked_service_name(
                    pipeline_class.get_source_linked_service(auth)["name"],
                    ir_name)
            target_linked_service_name = \
                self.create_linked_service_name(
                    pipeline_class.target_linked_service["name"],
                    ir_name)

            pipeline_datasets = {
                **{
                    data_set_id: self.all_data_set_jsons[(
                        source_linked_service_name, data_set_template["name"])]
                    for data_set_id, data_set_template
                    in pipeline_class.source_data_sets.items()
                },
                **{
                    data_set_id: self.all_data_set_jsons[(
                        target_linked_service_name, data_set_template["name"])]
                    for data_set_id, data_set_template
                    in pipeline_class.target_data_sets.items()
                }
            }

            # Add a configuration linked service, separate to source and
            # target, if required
            if pipeline_class.config_linked_service:
                config_linked_service_name = self.create_linked_service_name(
                    pipeline_class.config_linked_service["name"], ir_name)
                pipeline_datasets.update({
                    data_set_id: self.all_data_set_jsons[(
                        config_linked_service_name, data_set_template["name"])]
                    for data_set_id, data_set_template
                    in pipeline_class.config_data_sets.items()
                })

            # Create a pipeline per table
            for table_definition in config["tables"]:
                pipeline_obj = pipeline_class(
                    config["name"], config["authentication"],
                    config["config"], table_definition, pipeline_datasets
                )
                pipeline_obj.generate_pipeline()
                self.all_pipelines[pipeline_obj.pipeline_json["name"]] = \
                    pipeline_obj.pipeline_json
                self.all_triggers[schedule_id].append(
                    pipeline_obj.pipeline_json["name"])

    def generate_triggers(self):

        for schedule_id, pipelines in self.all_triggers.items():
            self.all_trigger_jsons[schedule_id] = {
                "name": trigger_name(*schedule_id),
                "properties": {
                    "annotations": [],
                    "runtimeState": "Started",
                    "pipelines": [
                        {
                            "pipelineReference": {
                                "referenceName": pipeline,
                                "type": "PipelineReference"
                            }
                        }
                        for pipeline in sorted(pipelines)
                    ],
                    "type": "ScheduleTrigger",
                    "typeProperties": {
                        "recurrence": create_recurrence_object(*schedule_id)
                    }
                }
            }

    @staticmethod
    def add_defaults(objects_json):
        for _, v in objects_json.items():
            v["properties"]["annotations"] = list(set(
                default_annotations + 
                v["properties"].get("annotations", [])
            ))
        
            if v.get("type", "").split("/")[-1] == "pipelines":
                if not v["properties"]["parameters"]:
                    del v["properties"]["parameters"]
                if not v["properties"]["variables"]:
                    del v["properties"]["variables"]

    def create_all_jsons(self):
        self.find_self_hosted_integration_runtimes()

        self.find_all_linked_services()
        self.add_defaults(self.all_linked_service_jsons)

        self.find_all_data_sets()
        self.add_defaults(self.all_data_set_jsons)

        self.generate_pipelines()
        self.add_defaults(self.all_pipelines)

        self.generate_triggers()
        self.add_defaults(self.all_trigger_jsons)

    def write_json(self, folder_path, json_to_write):
        file_path = self.get_file_path(folder_path, json_to_write)
        with open(file_path, "w") as json_file:
            json.dump(json_to_write, json_file, indent=4)

    @staticmethod
    def clean_unused_jsons(folder_path, generated_jsons):
        generated_json_names = [
            f"{json['name']}.json"
            for _, json in generated_jsons.items()
        ]
        all_files = [
            f 
            for f in listdir(folder_path) 
            if path.isfile(path.join(folder_path, f)) and f.endswith(".json")
        ]
        for file in all_files:
            if file not in generated_json_names:
                remove(f"{folder_path}/{file}")

    def create_all(self):
        self.create_all_jsons()

        for _, shir_json in self.all_self_hosted_integration_runtimes.items():
            self.write_json(self.shir_folder, shir_json)

        for _, ls_json in self.all_linked_service_jsons.items():
            self.write_json(self.linked_service_folder, ls_json) 

        for _, data_set_json in self.all_data_set_jsons.items():
            self.write_json(self.data_set_folder, data_set_json)

        for _, pipeline_json in self.all_pipelines.items():
            self.write_json(self.pipeline_folder, pipeline_json)

        for _, trigger_json in self.all_trigger_jsons.items():
            self.write_json(self.trigger_folder, trigger_json)

        if self.remove_not_generated:
            self.clean_unused_jsons(self.shir_folder, self.all_self_hosted_integration_runtimes)
            self.clean_unused_jsons(self.linked_service_folder, self.all_linked_service_jsons)
            self.clean_unused_jsons(self.data_set_folder, self.all_data_set_jsons)
            self.clean_unused_jsons(self.pipeline_folder, self.all_pipelines)
            self.clean_unused_jsons(self.trigger_folder, self.all_trigger_jsons)
