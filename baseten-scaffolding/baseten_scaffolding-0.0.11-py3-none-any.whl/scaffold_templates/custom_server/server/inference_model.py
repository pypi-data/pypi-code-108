import importlib
import logging
import os
import pathlib
import sys
import traceback
from typing import Dict

import kfserving

from common.errors import InferenceError


class CustomBasetenModel(kfserving.KFModel):
    def __init__(self, name: str, model_class_name: str, model_class_file: str, model_dir: str):
        super().__init__(name)
        self.name = name
        self.model_class_name = model_class_name
        self.model_class_file = model_class_file
        self.model_dir = model_dir
        self.model = None

    def load(self):
        # Load the python class into memory
        model_class_file = pathlib.PurePath(self.model_dir, self.model_class_file)
        sys.path.append(os.path.dirname(model_class_file))
        modulename = os.path.basename(model_class_file).split('.')[0].replace('-', '_')
        model_class = getattr(importlib.import_module(modulename), self.model_class_name)

        self.model = model_class()
        self.model.load()
        self.ready = True

    def preprocess(self, request: Dict) -> Dict:
        """
        Incorporate any pre-processing information required by the model here.

        These might be feature transformations that are tightly coupled to the model.
        """
        return request

    def postprocess(self, request: Dict) -> Dict:
        """
        Incorporate any post-processing required by the model here.
        """
        return request

    def predict(self, request: Dict) -> Dict:
        response = {}
        try:
            model_inputs = request['instances']
            try:
                return {'predictions': self.model.predict(model_inputs)}
            except Exception as e:
                response['error'] = {'traceback': traceback.format_exc()}
                raise InferenceError('Failed to predict') from e
        except Exception:
            logging.error(traceback.format_exc())
            return response
