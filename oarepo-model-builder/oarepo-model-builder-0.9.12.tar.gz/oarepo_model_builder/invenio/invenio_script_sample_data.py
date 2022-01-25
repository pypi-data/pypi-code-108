from typing import List

import faker
from jinja2 import Environment, FunctionLoader

from oarepo_model_builder.builders import OutputBuilder
from oarepo_model_builder.builders.utils import ensure_directory
from oarepo_model_builder.templates import templates
from ..builder import ModelBuilder
from ..builders import process
from ..builders.json_base import JSONBaseBuilder
from ..property_preprocessors import PropertyPreprocessor
from ..utils.schema import is_schema_element, match_schema, Ref


class InvenioScriptSampleDataBuilder(JSONBaseBuilder):
    TYPE = 'script_sample_data'
    output_file_type = 'yaml'
    output_file_name = 'script-import-sample-data'
    parent_module_root_name = 'jsonschemas'

    def __init__(self, builder: ModelBuilder, property_preprocessors: List[PropertyPreprocessor]):
        super().__init__(builder, property_preprocessors)
        self.faker = faker.Faker()

    @process('/model/**', condition=lambda current, stack: is_schema_element(stack))
    def model_element(self):
        schema_path = match_schema(self.stack)
        if isinstance(schema_path[-1], Ref):
            schema_element_type = schema_path[-1].element_type
        else:
            schema_element_type = None
        if schema_element_type == 'property':
            if not self.skip(self.stack):
                if 'properties' in self.stack.top.data:
                    self.output.enter(self.stack.top.key, {})
                elif 'items' in self.stack.top.data:
                    self.output.enter(self.stack.top.key, [])
                else:
                    self.output.primitive(self.stack.top.key, self.generate_fake(self.stack))
        self.build_children()
        if schema_element_type == 'property':
            if not self.skip(self.stack):
                if 'properties' in self.stack.top.data or 'items' in self.stack.top.data:
                    self.output.leave()

    def build(self, schema):
        output_name = schema.settings[self.output_file_name]
        output = self.builder.get_output(self.output_file_type, output_name)
        if not output.created:
            return
        count = schema.settings.get('oarepo:sample', {}).get('count', 50)
        for _ in range(count):
            super().build(schema)

    def skip(self, stack):
        return stack.top.data.get('oarepo:sample', {}).get('skip', False)

    def on_enter_model(self, output_name):
        self.output.next_document()

    def generate_fake(self, stack):
        params = {}
        method = None
        if 'oarepo:sample' in stack.top.data:
            config = stack.top.data['oarepo:sample']
            method = config.get('faker')
            params = config.get('params', params)

        if not method:
            if hasattr(self.faker, stack.top.key):
                method = stack.top.key
            else:
                method = 'sentence'
        return getattr(self.faker, method)()


class InvenioScriptSampleDataShellBuilder(OutputBuilder):
    TYPE = 'invenio_script_runserver'

    def finish(self):
        context = {
            'settings': self.schema.settings
        }

        env = Environment(
            loader=FunctionLoader(lambda tn: templates.get_template(tn, context['settings'])),
            autoescape=False,
        )

        ensure_directory(self.builder, 'scripts')
        output = self.builder.get_output('diff', 'scripts/load_sample_data.sh')
        output.write(env.get_template('script-import-sample-data-shell').render(context))
        output.make_executable()
