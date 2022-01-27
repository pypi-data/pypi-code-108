sftp_basic_key_vault = {
    "name": "SFTPBasic",
    "type": "Microsoft.DataFactory/factories/linkedservices",
    "properties": {
        "type": "Sftp",
        "parameters": {
            "Host": {
                "type": "String"
            },
            "KeyVaultSecretName": {
                "type": "String"
            },
            "UserName": {
                "type": "String"
            },
            "Port": {
                "type": "Int",
                "defaultValue": 22
            },
        },
        "annotations": [],
        "typeProperties": {
            "host": "@{linkedService().Host}",
            "port": "@linkedService().Port",
            "skipHostKeyValidation": True,
            "authenticationType": "Basic",
            "userName": "@{linkedService().UserName}",
            "password": {
                "type": "AzureKeyVaultSecret",
                "store": {
                    "referenceName": "Credentials Store",
                    "type": "LinkedServiceReference"
                },
                "secretName": "@{linkedService().KeyVaultSecretName}"
            }
        }
    }
}
