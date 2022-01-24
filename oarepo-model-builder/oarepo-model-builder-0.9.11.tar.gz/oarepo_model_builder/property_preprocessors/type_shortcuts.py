from oarepo_model_builder.builders.jsonschema import JSONSchemaBuilder
from oarepo_model_builder.builders.mapping import MappingBuilder
from oarepo_model_builder.invenio.invenio_record_schema import InvenioRecordSchemaBuilder
from oarepo_model_builder.property_preprocessors import PropertyPreprocessor, process
from oarepo_model_builder.utils.deepmerge import deepmerge
from oarepo_model_builder.stack import ModelBuilderStack
from oarepo_model_builder.utils.schema import is_schema_element, match_schema, Ref


class TypeShortcutsPreprocessor(PropertyPreprocessor):
    TYPE = 'type_shortcuts'

    @process(model_builder='*', path='/model/**',
             condition=lambda current, stack: is_schema_element(stack))
    def modify_type_shortcuts(self, data, stack: ModelBuilderStack, **kwargs):
        schema_types = match_schema(stack)
        top = schema_types[-1]

        if not isinstance(top, Ref):
            return data

        self.set_type(top.element_type, data)
        self.set_child_arrays(top.element_type, data)

        return data

    def set_type(self, element_type, data):
        if 'type' in data:
            return

        if element_type in ('property', 'items'):
            if 'properties' in data:
                data['type'] = 'object'
            elif 'items' in data:
                data['type'] = 'array'

    def set_child_arrays(self, element_type, data):
        if element_type == 'properties':
            for k, v in list(data.items()):
                if k.endswith('[]'):
                    data.pop(k)
                    data[k[:-2]] = self.create_array(v)

    @staticmethod
    def create_array(value):
        ret = {}
        array = {}
        for k, v in value.items():
            if k.endswith('[]'):
                ret[k[:-2]] = v
            else:
                array[k] = v
        ret['type'] = 'array'
        ret['items'] = array
        return ret

    @process(model_builder='*', path='/model',
             condition=lambda current, stack: is_schema_element(stack))
    def add_model_type(self, data, stack: ModelBuilderStack, **kwargs):
        if 'type' not in data:
            data['type'] = 'object'
        return data
