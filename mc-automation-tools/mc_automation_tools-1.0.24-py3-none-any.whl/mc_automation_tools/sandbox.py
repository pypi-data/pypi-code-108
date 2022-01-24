from mc_automation_tools.ingestion_api import overseer_api
from mc_automation_tools.validators import pycsw_validator, mapproxy_validator
from discrete_kit.functions.shape_functions import *
from mc_automation_tools.models import structs

# url = 'https://discrete-ingestion-qa-overseer-route-raster.apps.v0h0bdx6.eastus.aroapp.io'
# overseer = overseer_api.Overseer(url)
# overseer.get_class_params


meta = {
  "metadata": {
      "type": "RECORD_RASTER",
      "srsId": "4326",
      "region": "ישראל, ירדן",
      "srsName": "WGS84GEO",
      "footprint": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              35.1722581489948,
              31.7732841960031
            ],
            [
              35.0884731110009,
              31.7732841960031
            ],
            [
              35.0884731110009,
              31.8285061529974
            ],
            [
              35.1722581489948,
              31.8285061529974
            ],
            [
              35.1722581489948,
              31.7732841960031
            ]
          ]
        ]
      },
      "productId": "2022_01_12T08_36_34Z_MAS_6_ORT_247557",
      "resolution": 0.0439453125,
      "sensorType": [
        "UNDEFINED"
      ],
      "updateDate": "2022-01-12T08:36:38.162Z",
      "description": "תשתית אורתופוטו באיזור איו\"ש עדכני למאי 2020",
      "productName": "O_ayosh_10cm",
      "productType": "OrthophotoHistory",
      "accuracyCE90": 3,
      "creationDate": "2022-01-12T08:36:47.852Z",
      "producerName": "IDFMU",
      "ingestionDate": "2022-01-12T08:36:47.852Z",
      "sourceDateEnd": "2020-05-21T00:00:00.000Z",
      "classification": "4",
      "productVersion": "4.0",
      "rawProductData": {
        "bbox": [
          35.0884731109971,
          31.7732841960024,
          35.172258148995,
          31.828506152999
        ],
        "type": "FeatureCollection",
        "features": [
          {
            "type": "Feature",
            "geometry": {
              "type": "Polygon",
              "coordinates": [
                [
                  [
                    35.172258148995,
                    31.7732841960024
                  ],
                  [
                    35.0884731109971,
                    31.7732841960024
                  ],
                  [
                    35.0884731109971,
                    31.828506152999
                  ],
                  [
                    35.172258148995,
                    31.828506152999
                  ],
                  [
                    35.172258148995,
                    31.7732841960024
                  ]
                ]
              ]
            },
            "properties": {
              "Name": "O_ayosh_w84geo_Apr17-May20_tiff_2",
              "Type": "Orthophoto",
              "Resolution": "2"
            }
          }
        ]
      },
      "includedInBests": [],
      "sourceDateStart": "2020-05-21T00:00:00.000Z",
      "layerPolygonParts": {
        "bbox": [
          35.0884731110009,
          31.7732841960031,
          35.1722581489948,
          31.8285061529974
        ],
        "type": "FeatureCollection",
        "features": [
          {
            "type": "Feature",
            "geometry": {
              "type": "Polygon",
              "coordinates": [
                [
                  [
                    35.1722581489948,
                    31.7732841960031
                  ],
                  [
                    35.0884731110009,
                    31.7732841960031
                  ],
                  [
                    35.0884731110009,
                    31.8285061529974
                  ],
                  [
                    35.1722581489948,
                    31.8285061529974
                  ],
                  [
                    35.1722581489948,
                    31.7732841960031
                  ]
                ]
              ]
            },
            "properties": {
              "Dsc": "תשתית אורתופוטו באיזור איו\"ש עדכני למאי 2020",
              "Rms": None,
              "Ep90": "3",
              "Scale": None,
              "Cities": "ג'נין, ירושלים, יריחו, שכם",
              "Source": "2022_01_12T08_36_34Z_MAS_6_ORT_247557-4.0",
              "Countries": "ישראל, ירדן",
              "Resolution": "0.1",
              "SensorType": "OTHER",
              "SourceName": "O_ayosh_w84geo_Tiff_10cm",
              "UpdateDate": "21/05/2020"
            }
          }
        ]
      },
      "maxResolutionMeter": 0.1,
      "productBoundingBox": "35.0884731110009,31.7732841960031,35.1722581489948,31.8285061529974"
    },
  "operation": "ADD",
  "tileCount": 5,
  "productType": "OrthophotoHistory"
}
params = {
    "service": "CSW",
    "version": "2.0.2",
    "request": "GetRecords",
    "typenames": "mc:MCRasterRecord",
    "ElementSetName": "full",
    "resultType": "results",
    "outputSchema": "http://schema.mapcolonies.com/raster"
}

s3_credential = structs.S3Provider("http://10.8.1.13:9000/minio/", "raster", "rasterPassword", "raster")
pycsw_conn = pycsw_validator.PycswHandler(
    "http://catalog-qa-raster-catalog-pycsw-route-raster.apps.v0h0bdx6.eastus.aroapp.io", params)
toc_json = {'metadata': ShapeToJSON().create_metadata_from_toc(meta['metadata'])}
res = pycsw_conn.validate_pycsw(toc_json, "2022_01_12T08_36_34Z_MAS_6_ORT_247557", "4.0")
res_dict = res['results']
pycsw_records = res['pycsw_record']
links = res['links']
mapproxy_conn = mapproxy_validator.MapproxyHandler("http://mapproxy-qa-map-proxy-map-proxy-route-raster.apps.v0h0bdx6.eastus.aroapp.io/", "s3","ul", s3_credential,nfs_tiles_url="/tmp")
r = mapproxy_validator.MapproxyHandler.extract_from_pycsw(pycsw_records)
res = mapproxy_conn.validate_layer_from_pycsw(pycsw_records, "2022_01_12T08_36_34Z_MAS_6_ORT_247557", "4.0")
print(res)

