
# Taken from kfserving: https://github.com/kubeflow/kfserving/blob/master/python/pytorchserver/pytorchserver/model.py

import importlib
import logging
import os
import pathlib
import sys
import traceback
from typing import Dict

import kfserving

import torch


PYTORCH_FILE = 'model.pt'


class PyTorchModel(kfserving.KFModel):
    def __init__(self, name: str, model_class_name: str, model_class_file: str, model_dir: str, use_gpu: bool = False):
        super().__init__(name)
        self.name = name
        self.model_class_name = model_class_name
        self.model_class_file = model_class_file
        self.model_dir = model_dir
        self.model = None
        self.device = torch.device('cuda:0' if torch.cuda.is_available() and use_gpu else 'cpu')
        self.model_dtype = None

    def load(self):
        # Load the python class into memory
        model_class_file = pathlib.PurePath(self.model_dir, self.model_class_file)
        sys.path.append(os.path.dirname(model_class_file))
        modulename = os.path.basename(model_class_file).split('.')[0].replace('-', '_')
        model_class = getattr(importlib.import_module(modulename), self.model_class_name)

        # Make sure the model weights are transformed to the right device in this machine
        weights_file = pathlib.PurePath(self.model_dir, PYTORCH_FILE).as_posix()
        self.model = model_class().to(self.device)
        self.model.load_state_dict(torch.load(weights_file, map_location=self.device))
        self.model.eval()
        self.model_dtype = list(self.model.parameters())[0].dtype
        self.ready = True

    def predict(self, request: Dict) -> Dict:
        response = {}
        try:
            with torch.no_grad():
                inputs = torch.tensor(request['instances'], dtype=self.model_dtype, device=self.device)
                response = {}
                response['predictions'] = self.model(inputs).tolist()
                return response
        except Exception as e:
            response['error'] = {'traceback': traceback.format_exc()}
            logging.error(traceback.format_exc())
            return response
