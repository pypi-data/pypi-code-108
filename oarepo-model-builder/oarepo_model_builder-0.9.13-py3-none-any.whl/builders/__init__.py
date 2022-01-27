from __future__ import annotations

import copy
import functools
import inspect
from typing import TYPE_CHECKING, Union, List

from oarepo_model_builder.property_preprocessors import PropertyPreprocessor
from oarepo_model_builder.utils.json_pathlib import JSONPaths
from oarepo_model_builder.stack import ModelBuilderStack, ReplaceElement
from oarepo_model_builder.utils.verbose import log

if TYPE_CHECKING:
    from oarepo_model_builder.builder import ModelBuilder


def process(path, priority=0, condition=None):
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        wrapped.model_builder_path = path
        wrapped.model_builder_priority = priority
        wrapped.model_builder_condition = condition
        return wrapped

    return wrapper


class OutputBuilder:
    TYPE = None
    stack: ModelBuilderStack

    def __init__(self, builder: ModelBuilder, property_preprocessors: List[PropertyPreprocessor]):
        self.builder = builder
        self.property_preprocessors = property_preprocessors
        self.stack = None
        # TODO: move this to metaclass and initialize only once per class
        self.json_paths = JSONPaths()
        arr = []
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if not hasattr(method, 'model_builder_priority'):
                continue
            arr.append(
                (
                    -method.model_builder_priority,
                    -len(method.model_builder_path),
                    method.model_builder_path,
                    id(method),
                    method.model_builder_condition,
                    method
                )
            )
        arr.sort()
        for _prior, _lpath, path, _mid, condition, method in arr:
            self.json_paths.register(path, condition, method)

    def begin(self, schema, settings):
        self.schema = schema
        self.settings = settings
        self.stack = ModelBuilderStack()
        self.stack.push(None, schema)
        log.enter(2, 'Creating %s', self.TYPE)
        pass

    def finish(self):
        log.leave()

    def build(self, schema):
        self.begin(schema.schema, schema.settings)

        for proc in self.property_preprocessors:
            proc.begin(schema, schema.settings)

        try:
            processing_order = self.schema.schema.processing_order
        except AttributeError:
            processing_order = None

        self.build_children(ordering=processing_order)

        for proc in self.property_preprocessors:
            proc.finish()

        self.finish()

    def build_node(self, key, data):
        data = copy.deepcopy(data)
        self.stack.push(key, data)

        try:
            for property_preprocessor in self.property_preprocessors:
                data = property_preprocessor.process(self.TYPE, data, self.stack) or data
        except ReplaceElement as e:
            data = e
        if isinstance(data, ReplaceElement):
            self.stack.pop()
            if data.data is not None:
                if isinstance(data.data, dict):
                    for k, v in data.data.items():
                        self.build_node(k, v)
                elif isinstance(data.data, (list, tuple)):
                    for k, v in enumerate(data.data):
                        self.build_node(k, v)
                else:
                    raise AttributeError(f'Do not know how to handle {type(data.data)} in ReplaceElement')
            return
        self.stack.top.data = data
        self.process_stack_top()
        self.stack.pop()

    def build_children(self, ordering=None):
        data = self.stack.top.data
        if isinstance(data, (list, tuple)):
            for k, v in enumerate(data):
                self.build_node(k, v)
        elif isinstance(data, dict):
            children = list(data.items())
            if ordering:
                def key_function(x):
                    try:
                        return ordering.index(x)
                    except ValueError:
                        pass
                    try:
                        return ordering.index('*')
                    except ValueError:
                        pass
                    return len(ordering)

                children = children.sort(key=key_function)
            for k, v in children:
                self.build_node(k, v)

    def process_stack_top(self):
        try:
            self.call_components('before_process_element', value=self.stack.top.data, stack=self.stack)
            for method in self.json_paths.match(self.stack.path, self.stack.top.data, extra_data={
                'stack': self.stack
            }):
                return method()
            # do not skip stack top
            if self.stack.level <= 1:
                self.build_children()
        finally:
            self.call_components('after_process_element', value=self.stack.top.data, stack=self.stack)

    @process('/model')
    def enter_model(self):
        self.build_children()

    def call_components(self, method_name, value, **kwargs):
        for component in self.builder.get_output_builder_components(self.TYPE):
            if hasattr(component, method_name):
                value = getattr(component, method_name)(self, value, **kwargs) or value
        return value


class OutputBuilderComponent:
    def before_process_element(self, builder: OutputBuilder, value, *, stack: ModelBuilderStack, **kwargs):
        return value

    def after_process_element(self, builder: OutputBuilder, value, *, stack: ModelBuilderStack, **kwargs):
        return value


__all__ = [
    'process',
    'OutputBuilder',
    'ModelBuilderStack',
    'ReplaceElement'
]
