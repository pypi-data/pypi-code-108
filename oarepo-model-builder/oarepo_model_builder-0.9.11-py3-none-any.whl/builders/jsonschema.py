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
    def model_element(self, stack: ModelBuilderStack):
        self.model_element_enter(stack)
        yield
        self.model_element_leave(stack)

    def on_enter_model(self, output_name, stack: ModelBuilderStack):
        ensure_parent_modules(self.builder, Path(output_name),
                              ends_at=self.parent_module_root_name)
