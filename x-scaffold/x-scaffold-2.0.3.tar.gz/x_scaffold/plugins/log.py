from x_scaffold.context import ScaffoldContext
from ..runtime import ScaffoldRuntime
from ..steps import ScaffoldStep
from ..plugin import ScaffoldPluginContext
from ..rendering import render_text


def init(context: ScaffoldPluginContext):
    context.add_step('log', LogStep())


class LogStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        message = render_text(step, context)
        runtime.log(message)
