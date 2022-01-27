def get_data_lake_files(policy, data_set_name, container, path):
    return {
        "name": f"List {container}/{path} files".replace("/", "-"),
        "type": "GetMetadata",
        "dependsOn": [],
        "policy": policy,
        "userProperties": [],
        "typeProperties": {
            "dataset": {
                "referenceName": data_set_name,
                "type": "DatasetReference",
                "parameters": {
                    "Container": container,
                    "FolderPath": path,
                }
            }
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
