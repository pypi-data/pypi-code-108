sftp_file = {
    "name": "SFTPFile",
    "properties": {
        "linkedServiceName": {},
        "parameters": {
            "FolderPath": {
                "type": "string",
                "defaultValue": "/"
            },
            "FileName": {
                "type": "string"
            }
        },
        "annotations": [],
        "type": "Binary",
        "typeProperties": {
            "location": {
                "type": "SftpLocation",
                "fileName": {
                    "value": "@dataset().FileName",
                    "type": "Expression"
                },
                "folderPath": {
                    "value": "@dataset().FolderPath",
                    "type": "Expression"
                }
            }
        }
    },
    "type": "Microsoft.DataFactory/factories/datasets"
}
sftp_folder = {
    "name": "SFTPFolder",
    "properties": {
        "linkedServiceName": {},
        "parameters": {
            "FolderPath": {
                "type": "string",
                "defaultValue": "/"
            }
        },
        "annotations": [],
        "type": "Binary",
        "typeProperties": {
            "location": {
                "type": "SftpLocation",
                "folderPath": {
                    "value": "@dataset().FolderPath",
                    "type": "Expression"
                }
            }
        }
    },
    "type": "Microsoft.DataFactory/factories/datasets"
}
