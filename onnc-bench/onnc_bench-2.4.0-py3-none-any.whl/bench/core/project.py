from pathlib import Path
from typing import Dict, Union, List, Tuple
import json
from .modelpackage import ModelPackage
from .dataset.dataset import Dataset
from .model import ModelFormat, ModelDataType

from .dataset import DatasetFormat


class ProjectData:

    def __init__(self):
        self.project_id = None  # str
        self.model_packages = []  # List[ModelPackage]

    def add_model(self, model_package: ModelPackage) -> None:
        self.model_packages.append(model_package)

    def dump(self) -> Dict:
        # TODO
        # check evaluators, preprocessors, trainers is scirpt type

        mp = [m.dump() for m in self.model_packages]

        meta = {
            "project_id": self.project_id,
            "model_packages": mp
        }
        return meta

    def load(self, meta: Dict):
        self.project_id = meta["project_id"]
        self.model_packages = []
        for model_package in meta["model_packages"]:
            mp = ModelPackage(model_package["model"]["src"],
                              model_package["dataset"]["src"])

            mp.load(model_package)
            self.model_packages.append(mp)
