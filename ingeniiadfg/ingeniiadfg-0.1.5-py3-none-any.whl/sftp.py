from .base import DataFactoryPipeline
from .templates.linked_service import config_table_storage, data_lake, \
    ftp_basic_key_vault, sftp_basic_key_vault
from .templates.dataset import config_table, data_lake_folder, ftp_folder, \
    ftp_file, sftp_folder, sftp_file


class FTPBasePipeline(DataFactoryPipeline):

    target_linked_service = data_lake
    target_data_sets = {
        "target_folder": data_lake_folder
    }

    config_linked_service = config_table_storage
    config_data_sets = {
        "config_table": config_table
    }

    default_schedule = {
        "type": "day",
        "time": "06:00"
    }

    required_table_parameters = ["name", "path"]
    # TODO: implement prefix and suffix checks
    # optional_table_parameters = ["zipped", "prefix", "suffix"]

    def __init__(self, data_provider, authentication,
                 config, table_definition, data_sets):
        self.data_provider = data_provider
        self.authentication = authentication
        self.config = config
        self.table_definition = table_definition
        self.data_sets = data_sets

        self.table_storage_partition_key = \
            f"{data_provider}-{table_definition['name']}"

        self.data_lake_path = self.data_provider + \
            "/" + self.table_definition["name"]

        self.source_parameters = {
            "Host": self.config["host"],
            "UserName": self.config["username"],
            "KeyVaultSecretName": self.config["key_vault_secret_name"],
            "FolderPath": self.table_definition["path"]
        }
        if self.config.get("custom_port"):
            self.source_parameters["Port"] = self.config["custom_port"]

        super(FTPBasePipeline, self).__init__(
            self.data_lake_path.replace("/", "-"),
            variables={
                "SFTPKnownFiles": {
                    "type": "Array"
                }
            }
        )

    @staticmethod
    def handle_path(path_str):
        if path_str == "/":
            return "root path"
        else:
            return path_str.strip("/").replace("/", "-")

    def list_source_files(self):
        return {
            "name": "List files at " +
                    self.handle_path(self.table_definition['path']),
            "type": "GetMetadata",
            "dependsOn": [],
            "policy": self.default_policy,
            "userProperties": [],
            "typeProperties": {
                "dataset": self.create_pipeline_dataset_reference(
                    self.data_sets["source_folder"], self.source_parameters),
                "fieldList": ["childItems"],
                "storeSettings": {
                    "type": self.name.title() + "ReadSettings",
                    "recursive": True,
                    "enablePartitionDiscovery": False
                },
                "formatSettings": {"type": "BinaryReadSettings"}
                }
            }

    def list_known_files(self):
        return {
            "name": "Get known files",
            "type": "Lookup",
            "dependsOn": [],
            "policy": self.default_policy,
            "userProperties": [],
            "typeProperties": {
                "source": {
                    "type": "AzureTableSource",
                    "azureTableSourceQuery": {
                        "value": f"PartitionKey eq "
                                 f"'{self.table_storage_partition_key}'",
                        "type": "Expression"
                    },
                    "azureTableSourceIgnoreTableNotFound": True
                },
                "dataset": {
                    "referenceName": self.data_sets["config_table"]["name"],
                    "type": "DatasetReference",
                    "parameters": {
                        "TableName": "SFTPKnownFiles"
                    }
                },
                "firstRowOnly": False
            }
        }

    def generate_known_files_array(self, known_files_activity):
        return {
            "name": "Each known file",
            "type": "ForEach",
            "userProperties": [],
            "typeProperties": {
                "items": {
                    "value": "@activity('" +
                             known_files_activity['name'] +
                             "').output.value",
                    "type": "Expression"
                },
                "activities": [
                    {
                        "name": "Add file name",
                        "type": "AppendVariable",
                        "dependsOn": [],
                        "userProperties": [],
                        "typeProperties": {
                            "variableName": "SFTPKnownFiles",
                            "value": {
                                "value": "@item().RowKey",
                                "type": "Expression"
                            }
                        }
                    }
                ]
            }
        }

    def filter_new_files(self, source_files_activity):
        return {
            "name": "Find new files",
            "type": "Filter",
            "userProperties": [],
            "typeProperties": {
                "items": {
                    "value": "@activity('" +
                             source_files_activity['name'] +
                             "').output.childItems",
                    "type": "Expression"
                },
                "condition": {
                    "value": "@not(contains(variables('SFTPKnownFiles'), " +
                             "item().name))",
                    "type": "Expression"
                }
            }
        }

    def move_new_files(self, new_files_activity):
        sub_activities = [
            {
                "name": "Move file",
                "type": "Copy",
                "dependsOn": [],
                "policy": self.default_policy,
                "userProperties": [],
                "typeProperties": {
                    "source": {
                        "type": "BinarySource",
                        "storeSettings": self.source_store_settings,
                        "formatSettings": {
                            "type": "BinaryReadSettings"
                        }
                    },
                    "sink": {
                        "type": "BinarySink",
                        "storeSettings": {
                            "type": "AzureBlobFSWriteSettings"
                        }
                    },
                    "enableStaging": False
                },
                "inputs": [self.create_pipeline_dataset_reference(
                    self.data_sets["source_file"],
                    {
                        **self.source_parameters,
                        "FileName": {
                            "value": "@item().name",
                            "type": "Expression"
                        }
                     }
                )],
                "outputs": [self.create_pipeline_dataset_reference(
                    self.data_sets["target_folder"],
                    {
                        "Container": "raw",
                        "FolderPath": self.data_lake_path
                    }
                )]
            },
            {
                "name": "Create new known file entry",
                "type": "Copy",
                "dependsOn": [
                    {
                        "activity": "Move file",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    }
                ],
                "policy": self.default_policy,
                "userProperties": [],
                "typeProperties": {
                    "source": {
                        "type": "AzureTableSource",
                        "additionalColumns": [
                            {
                                "name": "Row",
                                "value": {
                                    "value": "@item().name",
                                    "type": "Expression"
                                }
                            },
                            {
                                "name": "DateMoved",
                                "value": {
                                    "value": "@utcnow()",
                                    "type": "Expression"
                                }
                            }
                        ],
                        "azureTableSourceQuery": {
                            "value": "PartitionKey eq '1'",
                            "type": "Expression"
                        },
                        "azureTableSourceIgnoreTableNotFound": False
                    },
                    "sink": {
                        "type": "AzureTableSink",
                        "azureTableInsertType": "merge",
                        "azureTableDefaultPartitionKeyValue": {
                            "value": self.table_storage_partition_key,
                            "type": "Expression"
                        },
                        "azureTableRowKeyName": {
                            "value": "Row",
                            "type": "Expression"
                        },
                        "writeBatchSize": 10000
                    },
                    "enableStaging": False,
                    "translator": {
                        "type": "TabularTranslator",
                        "typeConversion": True,
                        "typeConversionSettings": {
                            "allowDataTruncation": True,
                            "treatBooleanAsNumber": False
                        }
                    }
                },
                "inputs": [
                    self.create_pipeline_dataset_reference(
                        self.data_sets["config_table"],
                        parameters={"TableName": "Select1"}
                    )
                ],
                "outputs": [
                    self.create_pipeline_dataset_reference(
                        self.data_sets["config_table"],
                        parameters={"TableName": "SFTPKnownFiles"}
                    )
                ]
            }
        ]
        return {
            "name": "For each new file",
            "type": "ForEach",
            "userProperties": [],
            "typeProperties": {
                "items": {
                    "value": "@activity('" +
                             new_files_activity['name'] +
                             "').output.value",
                    "type": "Expression"
                },
                "activities": sub_activities
            }
        }

    def generate_pipeline(self):

        # --

        find_known_files_raw = self.list_known_files()
        self.add_activity(find_known_files_raw)

        known_files_array = self.generate_known_files_array(
            find_known_files_raw)
        self.add_activity(known_files_array, depends_on=[find_known_files_raw])

        # --

        source_files = self.list_source_files()
        self.add_activity(source_files)

        only_new_files = self.filter_new_files(source_files)
        self.add_activity(only_new_files, depends_on=[
                          known_files_array, source_files])

        # --

        move_files = self.move_new_files(only_new_files)
        self.add_activity(move_files, depends_on=[only_new_files])


class FTPPipeline(FTPBasePipeline):

    name = "ftp"
    authentications = {
        "basic": {
            "reqired_config": [
                "host", "username", "key_vault_name", "key_vault_secret"],
            "linked_service": ftp_basic_key_vault
        }
    }
    source_data_sets = {
        "source_folder": ftp_folder,
        "source_file": ftp_file
    }

    source_store_settings = {
        "type": "FtpReadSettings",
        "recursive": False,
        "useBinaryTransfer": True,
        "deleteFilesAfterCompletion": False
    }

    def __init__(self, data_provider, authentication,
                 config, table_definition, data_sets):
        super(FTPPipeline, self).__init__(
            data_provider, authentication,
            config, table_definition, data_sets)


class SFTPPipeline(FTPBasePipeline):

    name = "sftp"
    authentications = {
        "basic": {
            "required_config": [
                "host", "username", "key_vault_name", "key_vault_secret"],
            "linked_service": sftp_basic_key_vault
        }
    }
    source_data_sets = {
        "source_folder": sftp_folder,
        "source_file": sftp_file
    }

    source_store_settings = {
        "type": "SftpReadSettings",
        "recursive": False,
        "deleteFilesAfterCompletion": False
    }

    def __init__(self, data_provider, authentication,
                 config, table_definition, data_sets):
        super(SFTPPipeline, self).__init__(
            data_provider, authentication,
            config, table_definition, data_sets)
