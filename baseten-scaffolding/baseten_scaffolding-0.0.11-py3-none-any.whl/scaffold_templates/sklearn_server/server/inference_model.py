import logging
import os
import traceback
from typing import Dict, List

import joblib
import kfserving

from common.util import model_supports_predict_proba

MODEL_BASENAME = 'model'
MODEL_EXTENSIONS = ['.joblib', '.pkl', '.pickle']


class SKLearnModel(kfserving.KFModel):
    def __init__(self, name: str = MODEL_BASENAME, model_dir: str = 'model'):
        super().__init__(name)
        self.model_dir = model_dir
        self._model = None
        self._model_supports_predict_proba = False

    def load(self):
        model_path = kfserving.Storage.download(self.model_dir)
        paths = [os.path.join(model_path, MODEL_BASENAME + model_extension)
                 for model_extension in MODEL_EXTENSIONS]
        model_file = next(path for path in paths if os.path.exists(path))
        self._model = joblib.load(model_file)
        self.ready = True
        self._model_supports_predict_proba = model_supports_predict_proba(self._model)

    def predict(self, request: Dict) -> Dict[str, List]:
        response = {}
        try:
            inputs = request['instances']
            result = self._model.predict(inputs)
            response['predictions'] = result
            if self._model_supports_predict_proba:
                response['probabilities'] = self._model.predict_proba(inputs).tolist()
            return response
        except Exception as e:
            logging.error(traceback.format_exc())
            response['error'] = {'traceback': traceback.format_exc()}
            return response
