from re import T
from x_scaffold.context import ScaffoldContext
from x_scaffold.runtime import ScaffoldRuntime
from x_scaffold.steps import ScaffoldStep
from ..plugin import ScaffoldPluginContext
from ..engine import execute_scaffold
from ..rendering import render_options


def init(context: ScaffoldPluginContext):
    context.add_step('scaffold', Scaffolder())

class Scaffolder(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        options = render_options(step, context)
        orig_package = context['__package']
        has_private_context = False
        if 'context' in options:
            has_private_context = True
            actual_context = ScaffoldContext(options['context'])
        else:
            actual_context = context
        execute_scaffold(actual_context, options, runtime)
        if has_private_context:
            context.todos.extend(actual_context.todos)
            context.notes.extend(actual_context.notes)
        context['__package'] = orig_package
