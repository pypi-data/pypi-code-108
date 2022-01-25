from .context import ScaffoldContext
from .runtime import ScaffoldRuntime


class ScaffoldStep:
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        pass