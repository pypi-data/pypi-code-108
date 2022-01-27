data_lake_folder = {
    "name": "DataLakeFolder",
    "properties": {
        "linkedServiceName": {},
        "parameters": {
            "Container": {
                "type": "string"
            },
            "FolderPath": {
                "type": "string"
            }
        },
        "annotations": [],
        "type": "Binary",
        "typeProperties": {
            "location": {
                "type": "AzureBlobFSLocation",
                "folderPath": {
                    "value": "@dataset().FolderPath",
                    "type": "Expression"
                },
                "fileSystem": {
                    "value": "@dataset().Container",
                    "type": "Expression"
                }
            }
        }
    },
    "type": "Microsoft.DataFactory/factories/datasets"
}
data_lake_file = {
    "name": "DataLakeFile",
    "properties": {
        "linkedServiceName": {},
        "parameters": {
            "Container": {
                "type": "string"
            },
            "FolderPath": {
                "type": "string"
            },
            "FileName": {
                "type": "string"
            }
        },
        "annotations": [],
        "type": "Binary",
        "typeProperties": {
            "location": {
                "type": "AzureBlobFSLocation",
                "fileName": {
                    "value": "@dataset().FileName",
                    "type": "Expression"
                },
                "folderPath": {
                    "value": "@dataset().FolderPath",
                    "type": "Expression"
                },
                "fileSystem": {
                    "value": "@dataset().Container",
                    "type": "Expression"
                }
            }
        }
    },
    "type": "Microsoft.DataFactory/factories/datasets"
}
