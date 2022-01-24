"""
This module is the wrapper for overseer api according provided swagger

** example of overseer layers request:
        *** 'metadata', 'originDirectory', 'fileNames' are mandatory fields ***
    {
      "metadata": {
        "type": "RECORD_RASTER",
        "classification": "string",
        "productId": "string",
        "productName": "string",
        "productVersion": "string",
        "productType": "Orthophoto",
        "description": "string",
        "srsId": "string",
        "srsName": "string",
        "producerName": "string",
        "creationDate": "2021-12-02T09:56:01.264Z",
        "ingestionDate": "2021-12-02T09:56:01.264Z",
        "updateDate": "2021-12-02T09:56:01.264Z",
        "sourceDateStart": "2021-12-02T09:56:01.264Z",
        "sourceDateEnd": "2021-12-02T09:56:01.264Z",
        "resolution": 0.072,
        "maxResolutionMeter": 8000,
        "accuracyCE90": 0,
        "sensorType": [
          "VIS"
        ],
        "region": "string",
        "rms": 0,
        "scale": "string",
        "footprint": {
          "type": "Point",
          "coordinates": [
            0,
            0
          ]
        },
        "layerPolygonParts": {
          "type": "FeatureCollection",
          "features": [
            {
              "type": "Feature",
              "properties": {},
              "geometry": {
                "type": "GeometryCollection",
                "geometries": [
                  {
                    "type": "Point"
                  }
                ]
              },
              "bbox": [
                0,
                0,
                0,
                0
              ]
            }
          ],
          "bbox": [
            0,
            0,
            0,
            0
          ]
        },
        "rawProductData": {
          "type": "FeatureCollection",
          "features": [
            {
              "type": "Feature",
              "properties": {},
              "geometry": {
                "type": "GeometryCollection",
                "geometries": [
                  {
                    "type": "Point"
                  }
                ]
              },
              "bbox": [
                0,
                0,
                0,
                0
              ]
            }
          ],
          "bbox": [
            0,
            0,
            0,
            0
          ]
        },
        "productBoundingBox": "string"
      },
      "originDirectory": "string",
      "fileNames": [
        "string"
      ]
    }
"""
import json
from mc_automation_tools.configuration import config
from mc_automation_tools import base_requests, common


class Overseer:
    __layers = 'layers'
    __tasks = 'tasks'
    __completed = 'completed'
    __toc = 'toc'

    def __init__(self, end_point_url):
        self.__end_point_url = end_point_url

    @property
    def get_class_params(self):
        params = {
            'layers': self.__layers,
            'tasks': self.__tasks,
            'completed': self.__completed,
            'toc': self.__toc,
            "API url's": {'layers': common.combine_url(self.__end_point_url, self.__layers),
                          'tasks': common.combine_url(self.__end_point_url, '{jobId}', '{taskId}', self.__completed),
                          'toc': common.combine_url(self.__end_point_url, self.__toc)
                          }
        }
        return params

    # ==============================================layers api's========================================================

    def create_layer(self, params):
        """
        This method start a process of creating new layer from raw data
        * user should provide request body (json/dict) that include all field requested
        :param params: query params -> request parameters -> *** Example provided on module description
        :return: Status
        """
        url = common.combine_url(self.__end_point_url, self.__layers)
        resp = base_requests.send_post_request(url, params)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[create_layer]:failed on send create layer to overseer, return with error:[{resp.status_code}], '
                f'error msg:[{str(resp.content)}]')

        return str(resp.text), resp.request.body

    # ===============================================tasks api's========================================================

    def update_completion(self, job_id, task_id):
        """
        This method update overseer on completion of tiling task
        :param job_id: The uuid of job on job manager
        :param task_id: The uuid of the task on job manager
        :return: status
        """
        url = common.combine_url(self.__end_point_url, self.__tasks, job_id, task_id)
        resp = base_requests.send_post_request(url)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[update_completion]:failed on update overseer completion [job:{job_id}-task:{task_id}]'
                f', return with error:[{resp.status_code}], '
                f'error msg:[{str(resp.content)}]')

        return str(resp.text)

    # =================================================toc api's========================================================

    def toc(self, params):
        """
        This method get a toc file representing the given layer.
        ** body sample:
            {
              "productId": "string",
              "productVersion": "string",
              "operation": "ADD",
              "productType": "Orthophoto"
            }
        :param params: dict (json) -> body of the request with parameters to get
        :return: dict -> json with results:

            {
              "operation": "ADD",
              "productType": "Orthophoto",
              "metadata": {
                "type": "RECORD_RASTER",
                "classification": "string",
                "productId": "string",
                "productName": "string",
                "productVersion": "string",
                "productType": "Orthophoto",
                "description": "string",
                "srsId": "string",
                "srsName": "string",
                "producerName": "string",
                "creationDate": "2021-12-02T11:58:52.593Z",
                "ingestionDate": "2021-12-02T11:58:52.593Z",
                "updateDate": "2021-12-02T11:58:52.593Z",
                "sourceDateStart": "2021-12-02T11:58:52.593Z",
                "sourceDateEnd": "2021-12-02T11:58:52.593Z",
                "resolution": 0.072,
                "maxResolutionMeter": 8000,
                "accuracyCE90": 0,
                "sensorType": [
                  "VIS"
                ],
                "region": "string",
                "rms": 0,
                "scale": "string",
                "footprint": {
                  "type": "Point",
                  "coordinates": [
                    0,
                    0
                  ]
                },
                "layerPolygonParts": {
                  "type": "FeatureCollection",
                  "features": [
                    {
                      "type": "Feature",
                      "properties": {},
                      "geometry": {
                        "type": "GeometryCollection",
                        "geometries": [
                          {
                            "type": "Point"
                          }
                        ]
                      },
                      "bbox": [
                        0,
                        0,
                        0,
                        0
                      ]
                    }
                  ],
                  "bbox": [
                    0,
                    0,
                    0,
                    0
                  ]
                },
                "rawProductData": {
                  "type": "FeatureCollection",
                  "features": [
                    {
                      "type": "Feature",
                      "properties": {},
                      "geometry": {
                        "type": "GeometryCollection",
                        "geometries": [
                          {
                            "type": "Point"
                          }
                        ]
                      },
                      "bbox": [
                        0,
                        0,
                        0,
                        0
                      ]
                    }
                  ],
                  "bbox": [
                    0,
                    0,
                    0,
                    0
                  ]
                },
                "productBoundingBox": "string"
              }
            }
        """
        url = common.combine_url(self.__end_point_url, self.__toc)
        resp = base_requests.send_post_request(url, params)
        if resp.status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[toc]:failed on getting toc file]'
                f', return with error:[{resp.status_code}], '
                f'error msg:[{str(resp.content)}]')

        return json.loads(resp.content)
