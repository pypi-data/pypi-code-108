from askdata.integrations import alphavantage
import json
import dataset
import pandas as pd

""" QUERY """

class Alphavantage(dataset.Dataset):
    
    dataset_settings = """{
            "payload": {
                "page": 0,
                "totalElements": 8,
                "data": [
                    {
                        "datasetId": "f324ef9a-279b-4105-901b-c47c624edf7f-DATA_TABLE-0d129d26-58e5-441f-b9b3-8c80efdeb094",
                        "schemaMetaData": {
                            "columnId": "area_geografica",
                            "columnName": "area_geografica",
                            "dataType": "VARCHAR",
                            "dataExample": "Calabria",
                            "internalDataType": "STRING",
                            "indexedWith": null,
                            "join": null,
                            "details": {}
                        },
                        "parameterType": "ENTITY_TYPE",
                        "code": "AREA_GEOGRAFICA",
                        "name": "Area geografica",
                        "description": null,
                        "synonyms": [
                            "area",
                            "geografia",
                            "area geografica",
                            "area geograficas",
                            "regione"
                        ],
                        "icon": "",
                        "sampleQueries": [],
                        "importValues": true,
                        "mandatory": false,
                        "enabled": true,
                        "advancedConfiguration": {},
                        "viewValues": "View",
                        "custom": false,
                        "dynamicParameterValues": [],
                        "searchable": false,
                        "nameTransformer": null,
                        "synonymTransformers": null
                    }
                ]
            }
        }"""

    def discovery(self):
        return self.dataset_settings
