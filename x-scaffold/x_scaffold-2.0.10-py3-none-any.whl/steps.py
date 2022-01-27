import collections
import logging

from x_scaffold.rendering import render_options, render_text, render_value
from .context import ScaffoldContext
from .runtime import ScaffoldRuntime


_log = logging.getLogger(__name__)

class ScaffoldStep:
    def resolve_fn(self, obj_name: str, fn_name: str, context: ScaffoldContext):
        pass
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        pass


class ScaffoldStepExecution():
    def __init__(self, plugin_context) -> None:
        self.plugin_context = plugin_context
    
    def get_executor(self, step_name: str, context):
        name_parts = step_name.split(':')
        obj_name = name_parts[0]
        fn_name = name_parts[1] if len(name_parts) > 1 else 'run'

        if obj_name in self.plugin_context.steps:
            _log.debug('locating %s in plugin', obj_name)
            step = self.plugin_context.steps[obj_name]
            if hasattr(step, fn_name):
                return getattr(step, fn_name), True
            else:
                if hasattr(step, 'resolve_fn'):
                    return step.resolve_fn(obj_name, fn_name, context)
            _log.warning('%s executor not found in context', fn_name)

        elif obj_name in context:
            _log.debug('locating %s in context', obj_name)
            ctx = context[obj_name]
            if hasattr(ctx, fn_name):
                return getattr(ctx, fn_name), False
            _log.warning('%s executor not found in context', fn_name)
        return None, False
    
    def execute(self, context: ScaffoldContext, runtime, steps_context, steps):
        step: dict
        for step in steps:
            if 'if' in step:
                enabled = render_value(step['if'], context)
                if enabled == False:
                    continue
            if 'group' in step:
                group_steps = step['group']
                self.execute(context, runtime, steps_context, group_steps)
            elif 'foreach' in step:
                foreach_steps = step['foreach']
                items = render_value(foreach_steps.get('items', []), context)
                step_id = step.get('id', 'foreach')
                for item in items:
                    context.set_step(step_id, item)
                    self.execute(context, runtime, steps_context, foreach_steps.get('steps', []))
            else:
                executor = None
                executor_step_name = None
                is_plugin = False
                action_name = step.get('action', None)
                executor, is_plugin = self.get_executor(action_name, context)
                if executor:
                    step_options = step.get('with', {})

                    step_id = step.get('id', action_name)
                    description = render_text(step.get('description', None), context)
                    if description:
                        _log.info(f'[{step_id}] {description}')
                    
                    _log.debug(f'[{step_id}] running')
                    if is_plugin:
                        if isinstance(executor_step_name, collections.Mapping):
                            step_options['__id'] = step_id
                        result = executor(context, step_options, runtime)
                    else:
                        if isinstance(step_options, collections.Mapping):
                            step_options = render_options(step_options, context)
                            args = step_options.get('args', [])
                            kwargs = step_options.get('kwargs', {})
                            result = executor(*args, **kwargs)
                        else:
                            result = executor(render_value(step_options, context))
                    if 'output_to_context' in step:
                        context[step['output_to_context']] = result
                    context.set_step(step_id, result)