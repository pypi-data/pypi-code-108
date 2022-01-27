from pathlib import Path

from oarepo_model_builder.stack import ModelBuilderStack
from . import process
from .json_base import JSONBaseBuilder
from .utils import ensure_parent_modules
from ..utils.schema import is_schema_element


class JSONSchemaBuilder(JSONBaseBuilder):
    TYPE = 'jsonschema'
    output_file_type = 'jsonschema'
    output_file_name = 'schema-file'
    parent_module_root_name = 'jsonschemas'

    @process('/model/**', condition=lambda current, stack: is_schema_element(stack))
    def model_element(self):
        self.model_element_enter()
        self.build_children()
        self.model_element_leave()

    def on_enter_model(self, output_name):
        ensure_parent_modules(self.builder, Path(output_name),
                              ends_at=self.parent_module_root_name)
