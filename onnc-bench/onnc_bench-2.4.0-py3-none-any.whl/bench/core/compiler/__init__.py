from typing import Any, Dict


class Compilation:
    def __init__(self):
        self.compilation_id: str  # SaaS compilation_id
        self.model_path: str
        self.sample_path: str
        self.model_meta: Dict[str, Any]
        self.sample_meta: Dict[str, Any]
        self.calibrator_params: Dict[str, Any]
        self.compiler_params: Dict[str, Any]


from .onnc_saas import ONNCSaaSBuilder
from .nnuxe import NNUXEBuilder
from .nnuxe_docker import NNUXEDockerBuilder

