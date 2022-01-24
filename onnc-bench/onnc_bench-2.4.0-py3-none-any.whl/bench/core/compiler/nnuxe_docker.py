from pathlib import Path
from typing import Dict, List, Any, Callable, Union, Set
import os
import json
import shutil

from loguru import logger

from onnc.bench.core.deployment import Deployment
from ..dataset.dataset import Dataset
from ..model.model import Model
from ..modelpackage import ModelPackage
from onnc.bench.core.common import get_tmp_path
from . import Compilation
from .nnuxe import NNUXEBuilder


class NNUXEDockerBuilder(NNUXEBuilder):
    BUILDER_NAME = "NNUXEDockerBuilder"

    def __init__(self,
                 image_name='nnuxe/nnuxe/nnuxe_image',
                 image_tag="latest"):
        super().__init__()
        self.image_name = image_name
        self.image_tag = image_tag

    def _compile(self, model_name, model_path: str, sample_path: str,
                 params_path: str, output_path: str,
                 local_nnuxe: bool = False):
        build_path = '/build'
        build_tmp = get_tmp_path()
        os.makedirs(build_tmp, exist_ok=True)

        shutil.copy(model_path, os.path.join(build_tmp, 'model.file'))
        shutil.copy(sample_path, os.path.join(build_tmp, 'sample.file'))
        shutil.copy(params_path, os.path.join(build_tmp, 'params.file'))

        os.makedirs(output_path, exist_ok=True)
        output_path = os.path.join(output_path, model_name)

        cmd = [f'docker run -it -v {build_tmp}:{build_path}',
               f'-e PYTHONPATH="/root/nnuxe/nnuxe/external/tvm/python::/root/nnuxe/"',
               f'-e NNUXE_PATH="/root/nnuxe/"',
               f'-e TVM_HOME="/root/nnuxe/nnuxe/external/tvm"',
               f'{self.image_name}:{self.image_tag}',
               f'python /root/nnuxe/cli/compile.py --model {build_path}/model.file',
               f'--sample {build_path}/sample.file',
               f'--params {build_path}/params.file --output {build_path}/out']
        cmd = ' '.join(cmd)

        logger.debug(cmd)

        os.system(cmd)

        with open(os.path.join(build_tmp, 'out', 'report.json'), 'r') as f:
            report = json.load(f)

        shutil.move(os.path.join(build_tmp, 'out'), output_path)

        return report
