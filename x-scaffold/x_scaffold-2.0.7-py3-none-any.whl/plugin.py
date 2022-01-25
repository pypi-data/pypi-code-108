from typing import Dict
from .runtime import ScaffoldRuntime
from .steps import ScaffoldStep


class ScaffoldPlugin:
    def init(runtime: ScaffoldRuntime):
        pass


class ScaffoldPluginContext(dict):
    steps: Dict[str, ScaffoldStep] = {}
    
    def add_step(self, step_name: str, step: ScaffoldStep):
        self.steps[step_name] = step
