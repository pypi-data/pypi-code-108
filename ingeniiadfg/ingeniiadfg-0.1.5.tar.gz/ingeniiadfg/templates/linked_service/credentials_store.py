credentials_store = {
	"name": "Credentials Store",
	"type": "Microsoft.DataFactory/factories/linkedservices",
	"properties": {
		"annotations": [],
		"type": "AzureKeyVault",
		"typeProperties": {
			"baseUrl": "https://examplekeyvaultname.vault.azure.net/"
		}
	}
}