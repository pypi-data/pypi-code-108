from pathlib import Path
from typing import Dict, List, Any, Callable, Union, Set
from abc import abstractmethod
from pathlib import Path
import inspect
import os
import time
import re
import zipfile
from dataclasses import dataclass
import sys
from collections import OrderedDict
import json
import shutil

import requests
from loguru import logger

from onnc.bench.core.project import ProjectData
from onnc.bench.core.deployment import Deployment
from .builder import IBuilder
from ..dataset.dataset import Dataset
from ..model.model import Model
from .saas_config import URI_MAP, timeout, poll_interval
from ..modelpackage import ModelPackage
from onnc.bench.core.common import get_tmp_path
from . import Compilation


def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


class NNUXEBuilder(IBuilder):
    BUILDER_NAME = "NNUXEBuilder"

    def __init__(self):
        self._compilations: Dict[int, Compilation] = {}
        self.output_path: str = ""

    def prepare_model(self, model_path, dataset_path,
                      model_meta, dataset_meta) -> int:
        """ Upload a model and its corresponding calibration dataset.
            And create a compilation.

        :param str model:
            A path to a model file
        :param str dataset:
            A path to a model file
        :param Dict model_meta
            Metadata of the model
        :param Dict dataset_meta
            Metadata of the dataset
        :returns:
            internal compilation id
        :rtype:
            int
        """

        compilation = Compilation()
        compilation.model_path = model_path
        compilation.sample_path = dataset_path
        compilation.model_meta = model_meta
        compilation.sample_meta = dataset_meta

        _internal_cid = id(model_path)
        self._compilations[_internal_cid] = compilation
        return _internal_cid

    def calibrate(self, model_id: int, params: Dict):
        """Update calibration parameters
        """
        self._compilations[model_id].calibrator_params = params

    def compile(self, model_id, params: Dict):
        """Update compilation parameters
        """
        self._compilations[model_id].compiler_params = params

    def _compile(self, model_name, model_path: str, sample_path: str,
                 params_path: str, output_path: str,
                 local_nnuxe: bool = True):

        from nnuxe.drivers.compiler import compile as nnuxe_compile

        report = nnuxe_compile(model_path, sample_path, params_path,
                               os.path.join(output_path, model_name),
                               local_nnuxe=local_nnuxe)
        return report

    def build(self, target: str, converter_params={}) -> Dict:

        compilation_list = []
        params = {}
        res = {}

        # Upload files and create compilation
        for iternal_cid in self._compilations:
            compilation = self._compilations[iternal_cid]

            compilation.compiler_params['target'] = target

            params["model_meta"] = compilation.model_meta
            params["sample_meta"] = compilation.sample_meta
            params["compiler_params"] = compilation.compiler_params
            params["calibrator_params"] = compilation.calibrator_params
            params["converter_params"] = converter_params
            compilation_list.append((compilation.model_path,
                                     compilation.sample_path,
                                     params))
        output_path = get_tmp_path()
        os.makedirs(output_path, exist_ok=True)
        for idx, compi in enumerate(compilation_list):
            model_path = compi[0]
            sample_path = compi[1]
            params = compi[2]
            params_path = get_tmp_path()
            open(params_path, 'w').write(json.dumps(params))
            report = self._compile(f'model_{idx}', model_path, sample_path,
                                   params_path, output_path)
            res[f'model_{idx}'] = report
            os.remove(params_path)

            logger.info(params)

        self.output_path = output_path

        return res

    def save(self, output: Path) -> Union[Dict, Deployment]:
        res = {}
        shutil.rmtree(output, ignore_errors=True)
        shutil.copytree(self.output_path, output)
        shutil.rmtree(self.output_path, ignore_errors=True)

        for i in os.listdir(output):
            try:
                out = Path(os.path.join(output, i))
                deployment = Deployment(out)
            except Exception as e:
                deployment = Deployment(None)

            res[i] = deployment

        return Deployment(None, report=res, logs=res)

    @property
    def supported_devices(self) -> Dict:
        devices = {'CMSIS-NN': 'CMSIS-NN',
                   'ANDES-LIBNN': 'ANDES-LIBNN',
                   'NVDLA-NV-SMALL': 'NVDLA-NV-SMALL',
                   'NVDLA-NV-LARGE': 'NVDLA-NV-LARGE',
                   'NVDLA-NV-FULL': 'NVDLA-NV-FULL',
                   'CMSIS-NN-DEFAULT': 'CMSIS-NN-DEFAULT',
                   'NVDLA-NV-SMALL-DEFAULT': 'NVDLA-NV-SMALL-DEFAULT',
                   'NVDLA-NV-LARGE-DEFAULT': 'NVDLA-NV-LARGE-DEFAULT',
                   'NVDLA-NV-FULL-DEFAULT': 'NVDLA-NV-FULL-DEFAULT'}
        return devices
