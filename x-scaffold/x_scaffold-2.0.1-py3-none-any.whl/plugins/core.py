import importlib
import importlib
from importlib import util
import subprocess
import sys
from x_scaffold.context import ScaffoldContext
from x_scaffold.runtime import ScaffoldRuntime
from ..steps import ScaffoldStep
from ..plugin import ScaffoldPluginContext
from ..rendering import render_options, render_text


def init(context: ScaffoldPluginContext):
    context.add_step("set_context", SetStep())
    context.add_step("add_note", AddNoteStep())
    context.add_step("add_todo", AddTodoStep())
    context.add_step("module", ModuleStep())


class SetStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        context_names = step
        for context_name in context_names:
            context[context_name] = render_text(
                context_names[context_name], context)


class AddNoteStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: str, runtime: ScaffoldRuntime):
        message = render_text(step, context)
        context.notes.append(message)


class AddTodoStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: str, runtime: ScaffoldRuntime):
        message = render_text(step, context)
        context.todos.append(message)


class ModuleStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        options = render_options(step, context)

        install_dependencies(options.get('dependencies', []))
        file = options['path']
        spec = util.spec_from_file_location("module.name", file)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        main_fn = getattr(foo, 'main')

        return main_fn(context, options, runtime)


def install_dependencies(dependencies):
    for dep in dependencies:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
