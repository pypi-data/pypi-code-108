import logging
import traceback
from typing import Dict, List

import kfserving
import numpy as np

from tensorflow import keras


class KerasModel(kfserving.KFModel):
    def __init__(self, name: str = 'model', model_dir: str = 'model'):
        super().__init__(name)
        self.model_dir = model_dir
        self._model = None

    def load(self):
        self._model = keras.models.load_model(self.model_dir)
        self.ready = True

    def predict(self, request: Dict) -> Dict[str, List]:
        response = {}
        try:
            instances = request['instances']
            inputs = np.array(instances)
            result = self._model.predict(inputs).tolist()
            response['predictions'] = result
            return response
        except Exception as e:
            response['error'] = {'traceback': traceback.format_exc()}
            logging.error(traceback.format_exc())
            return response
