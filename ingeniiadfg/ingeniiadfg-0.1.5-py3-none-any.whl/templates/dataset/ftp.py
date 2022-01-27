ftp_file = {
    "name": "FTPFile",
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
                "type": "FtpServerLocation",
                "FileName": {
                    "value": "@dataset().FileName",
                    "type": "Expression"
                },
                "FolderPath": {
                    "value": "@dataset().FolderPath",
                    "type": "Expression"
                }
            }
        }
    },
    "type": "Microsoft.DataFactory/factories/datasets"
}
ftp_folder = {
    "name": "FTPFolder",
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
                "type": "FtpServerLocation",
                "folderPath": {
                    "value": "@dataset().FolderPath",
                    "type": "Expression"
                }
            }
        }
    },
    "type": "Microsoft.DataFactory/factories/datasets"
}
