import logging
import traceback
from typing import Dict

import kfserving

import torch
from transformers import pipeline


class TransformerModel(kfserving.KFModel):
    def __init__(self, name: str, task: str, has_named_args: bool = False, has_hybrid_args: bool = False):
        super().__init__(name)
        self._model = None
        self._task = task
        self._has_named_args = has_named_args
        self._has_hybrid_args = has_hybrid_args

    def load(self):
        transformer_config = {}
        if torch.cuda.is_available():
            transformer_config = {'device': 0}
        self._model = pipeline(self._task, **transformer_config)
        self.ready = True

    def predict(self, request: Dict) -> str:
        response = {}
        instances = request['instances']
        try:
            with torch.no_grad():
                if self._has_named_args:
                    result = [self._model(**instance) for instance in instances]
                elif self._has_hybrid_args:
                    result = []
                    for instance in instances:
                        prompt = instance.pop('prompt')
                        result.append(self._model(prompt, **instance))
                else:
                    result = self._model(instances)
            response['predictions'] = result
            return response
        except Exception as e:
            logging.error(traceback.format_exc())
            response['error'] = {'traceback': traceback.format_exc()}
            return response
