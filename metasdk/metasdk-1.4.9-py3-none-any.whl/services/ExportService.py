import json


class ExportService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

    def export_page(self, app_id, page_id, entity_id, object_id, export_data_ids, params=None, export_format="csv", export_empty=False):
        if params is None:
            params = {"stateParams": {}}
        response = self.__app.native_api_call('export', 'page', params, self.__options, get_params={
            "applicationId": app_id,
            "entityPageId": page_id,
            "entityId": entity_id,
            "objectId": object_id,
            "exportFormat": export_format,
            "exportEmpty": export_empty,
            "exportDataIds": export_data_ids,
        })
        return json.loads(response.text)

    def export_data_source(self, ds_id):
        params = {}
        response = self.__app.native_api_call('export', 'data_source', params, self.__options, get_params={
            "dataSourceId": ds_id,
        })
        return json.loads(response.text)
