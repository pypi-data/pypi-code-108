from typing import Any, List, Union, Dict, Set
from abc import abstractmethod
from pathlib import Path

from loguru import logger

from onnc.bench.core.project import ProjectData
from onnc.bench.core.deployment import Deployment

class IBuilder:

    BUILDER_NAME = ""

    def __init__(self, project_data: ProjectData):
        self.project_data = project_data
        self.model_ids: List = []

    @abstractmethod
    def prepare_model(self, model, dataset, model_meta, dataset_meta) -> Any:
        """Make files of a model and its corresponding dataset ready in given
           path and place.
        """
        pass

    @abstractmethod
    def calibrate(self, model_id, params) -> Any:
        """Calibrate a model package(model and its corresponding samples)
        """
        pass

    @abstractmethod
    def compile(self, model_id, params) -> Any:
        """Compile a model package(model and its corresponding samples)
        """
        pass

    @abstractmethod
    def build(self, target, converter_params: Dict = {}) -> Any:
        """build a project witch contains multiple models

        for model in model_ids:
            ...
        """
        pass

    @abstractmethod
    def save(self, output: Path) -> Union[Dict, Deployment]:
        pass

    @property
    def supported_devices(self) -> Dict:
        pass

    def get_device_id(self, target):
        supported_devices = self.supported_devices
        try:
            return supported_devices[target]
        except KeyError:
            logger.error(f'`{target}` is not a supported device/format.')
            logger.error(f'Supported devices/formats are: '
                         f'{str([x for x in supported_devices])} ')
            raise Exception(f'`{target}` is not supported')
