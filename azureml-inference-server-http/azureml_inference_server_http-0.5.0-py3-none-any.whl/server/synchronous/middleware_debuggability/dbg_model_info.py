import json
import os

AML_APP_ROOT = os.environ.get('AML_APP_ROOT', '/var/azureml-app')
MODEL_FILE_PATH = os.path.join(AML_APP_ROOT, 'model_config_map.json')

def enabled():
    return os.path.exists(MODEL_FILE_PATH) and 'AML_DBG_MODEL_INFO' in os.environ

class WSGIRequest(object):
    def __init__(self, logger, inner_app):
        if not inner_app:
            raise Exception('WSGI application was required but not provided')
        self._inner_app = inner_app
        self.logger = logger
        self._model_infos = None
    
    @property
    def model_infos(self):
        if self._model_infos is not None:
            return self._model_infos
        self._model_infos = ""
        try:
            with open(MODEL_FILE_PATH) as f:
                contents = json.load(f)
                models = contents['models']
                self._model_infos = ','.join(model['id'] for model in models.values())
        except Exception as ex:
            self._model_infos = ""
            self.logger.error(ex)
        return self._model_infos

    def __call__(self, environ, start_response):

        def request_start_response(status_string, headers_array, exc_info=None):
            headers_array.append(('x-ms-aml-model-info', self.model_infos))
            start_response(status_string, headers_array, exc_info)

        return self._inner_app(environ, request_start_response)
