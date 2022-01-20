#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

class UDFError(Exception):
    pass


class UDF(object):
    version = "0.0.1"

    def __init__(self,
                 scene_engine_client,
                 logger):

        self.scene_engine_client = scene_engine_client
        self.logger = logger


class Enricher(UDF):
    def enrich(self, metadata: dict) -> dict:
        pass


class Script(UDF):
    def __init__(self, scene_engine_client, job_manager_client, es_client, logger):

        super().__init__(scene_engine_client=scene_engine_client,
                         logger=logger)
        self.es_client = es_client
        self.job_manager_client = job_manager_client

    def execute(self, **kwargs):
        pass


class Webhook(UDF):
    def execute(self, user_json_request: dict, api_response: dict, user_params: dict) -> dict:
        '''
        implement this function to execute costume script
        has access to scene_engine_client, scene engine logger (for developer debugging), and user request to API
        and its response

        Args:
            user_json_request: original request user makes to scene engine API, not the request webhook has to execute
            api_response: original response of scene engine to user request API, not the expected webhook response
            user_params: original params in user request to scene engine API, not params for webhook
        '''
        pass
