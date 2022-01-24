from pathlib import Path
from typing import Dict, Union, List, Tuple
import os
import json
import shutil

from loguru import logger

from .core.modelpackage import ModelPackage
from .core.dataset.dataset import Dataset


from .core.model import ModelFormat, TF_MODEL_FORMATS, ModelDataType
from .core.model.model import Tensor

from .core.dataset import DatasetFormat
from .core.dataset.layout import DataLayout
from .core.project import ProjectData
from .core.compiler.onnc_saas import ONNCSaaSBuilder
# from .core.compiler.nnuxe import NNUXEBuilder
# from .config import api_protocol, api_url, api_port
from .core.common import get_tmp_path, get_temp_base
from .config import default_builder, default_builder_params


def login(api_key: str, password: str=""):
    os.environ['ONNC_API_USER'] = api_key
    os.environ['ONNC_API_PASSWD'] = password


def get_api_key():
    return (os.environ.get('ONNC_API_USER'), os.environ.get('ONNC_API_PASSWD'))


class Project:
    def __init__(self, name, builder=default_builder,
                 builder_params=default_builder_params):
        self.builder = builder(*builder_params)

        if isinstance(self.builder, ONNCSaaSBuilder):
            self.builder.saas_login(*get_api_key())
            proj_info_sr = self.builder.saas_get_project_id_by_name(name)
            if len(proj_info_sr.data) == 0:
                self.builder.saas_create_project(name)

            logger.info(f"ProjectID: {self.builder._project_id}")

    @classmethod
    def get_model_meta(cls, model_package, inputs_as_nchw):
        if inputs_as_nchw is None:
            if model_package.model.format in TF_MODEL_FORMATS:
                inputs_as_nchw = "as_inputs_name"
            else:
                inputs_as_nchw = False

        model_meta = {
            "inputs": [x.dump() for x in model_package.model.inputs],
            "inputs_as_nchw": inputs_as_nchw,
            "outputs": [x.dump() for x in model_package.model.outputs],
            "format": model_package.model.format.name
        }

        return model_meta

    @classmethod
    def get_dataset_meta(cls, model_package):
        dataset_meta = {
            "shape": model_package.dataset.shape,
            "format": model_package.dataset.format.name
        }

        if isinstance(model_package.dataset.layout, DataLayout):
            dataset_meta["layout"] = model_package.dataset.layout.dump()

        return dataset_meta

    def add_model(self,
                  model: Union[object, str, Path],
                  samples: Union[object, str, Path, Dataset],
                  model_format: ModelFormat = ModelFormat.NON_SPECIFIED,
                  sample_format: DatasetFormat = DatasetFormat.NON_SPECIFIED,
                  # [name: str, shape:Tuple, dtype:ModelDataType]
                  model_inputs: List[Union[List, Tuple, Tensor]] = [],
                  # [name: str, shape:Tuple, dtype:ModelDataType]
                  model_outputs: List[Union[List, Tuple, Tensor]] = [],
                  inputs_as_nchw: Union[str, bool, None, List[str]] = None):
        """Add a model and its corresponding calibration samples.

        :param Union[object, str, Path] model:
            A file or a directory path to a serialized model file,
            or a neurl network model object.

            Check https://docs-tinyonnc.skymizer.com/model-formats.html for
            a list of supported formats.

        :param Union[object, str, Path, Dataset] samples:
            A file or a directory path to a serialized dataset or object.

            Check https://docs-tinyonnc.skymizer.com/dataset-formats.html for
            a list of supported formats.

        :param ModelFormat model_format:
            The format/framework of the model file/object. onnc-bench will
            identify the format if this param is ModelFormat.NON_SPECIFIED.

            Check https://docs-tinyonnc.skymizer.com/model-formats.html for
            a list ofsupported formats.

        :param DatasetFormat sample_format:
            The format/framework of the model file/object. onnc-bench will
            identify the format if this param is DatasetFormat.NON_SPECIFIED.

            Check https://docs-tinyonnc.skymizer.com/dataset-formats.html for
            a list of supported formats.
        :param List[Union[List, Tuple, Tensor]] model_inputs:
            A list of input tensor(s), which include(s) 3 fields:
                1. name: str
                2. shape(optional): Union[List, Tuple]
                3. dtype(optional): onnc.bench.core.model.ModelDataType

        :param List[Union[List, Tuple, Tensor]] model_outputs:
            A list of input tensor(s), which include(s) 3 fields:
                1. name: str
                2. shape(optional): Union[List, Tuple]
                3. dtype(optional): onnc.bench.core.model.ModelDataType


        """
        model_package = ModelPackage(model, samples,
                                     model_format, sample_format,
                                     model_inputs, model_outputs)

        model_tmp_path = Path(get_tmp_path())
        dataset_tmp_path = Path(get_tmp_path())

        model_package.serialize(model_tmp_path, dataset_tmp_path)

        model_meta = self.get_model_meta(model_package, inputs_as_nchw)
        dataset_meta = self.get_dataset_meta(model_package)

        model_id = self.builder.prepare_model(model_package.model.src,
                                              model_package.dataset.src,
                                              model_meta=model_meta,
                                              dataset_meta=dataset_meta)

        self.builder.calibrate(model_id, params={})
        self.builder.compile(model_id, params={})

    def compile(self, target: str, **params):
        """Trigger the compilation process and transform the given
        model into C function calls.

        :param str device:
            The name of the supported SoC board, for example, NUMAKER_IOT_M487.

            Check https://docs-tinyonnc.skymizer.com/devices.html for
            a list of supported devices.

        : param dict params:
            Parameters for the compiler.

            Check https://docs-tinyonnc.skymizer.com/compiler-params.html for
            more details.

        """
        target_id = self.builder.get_device_id(target)
        res = self.builder.build(target_id)

        if isinstance(self.builder, ONNCSaaSBuilder):
            logger.info(f"You can visit: https://app.onnc.skymizer.com"
                        f"/app/builds/{res['id']}")

        return res

    def save(self, path: Union[str, Path]):
        """Save the compiled artifact(s).

        :param Union[str, Path] path:
            A path to store the artifact(s).

        :returns:
            A Deployment object that contains `files`, `report`.
        :rtype:
            Deployment
        """
        if isinstance(path, str):
            path = Path(path)

        return self.builder.save(path)

    def prune(self, params={}):
        raise NotImplementedError("Model pruning is not implemented yet.")

    def __del__(self):
        shutil.rmtree(get_temp_base())
