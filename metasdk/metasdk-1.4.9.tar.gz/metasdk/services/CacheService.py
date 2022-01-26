import json


class CacheService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

    def warm_page_cache(self, app_id, page_id, entity_id, object_id, params=None):
        if params is None:
            params = {"stateParams": {}}
        response = self.__app.native_api_call('cache', 'warm-page-cache', params, self.__options, get_params={
            "applicationId": app_id,
            "entityPageId": page_id,
            "entityId": entity_id,
            "objectId": object_id,
        })
        return json.loads(response.text)
