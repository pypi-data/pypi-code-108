from collections import defaultdict

from oarepo_model_builder.builders import process
from oarepo_model_builder.stack import ModelBuilderStack
from .invenio_base import InvenioBaseClassPythonBuilder
from ..outputs.json_stack import JSONStack
from ..utils.deepmerge import deepmerge
from ..utils.jinja import package_name, base_name, with_defined_prefix
from ..utils.schema import is_schema_element, match_schema, Ref

OAREPO_MARSHMALLOW_PROPERTY = 'oarepo:marshmallow'


class MarshmallowNode:
    def __init__(self, schema_class_name, schema_class_bases, schema):
        self.schema_class_name = schema_class_name
        self.schema_class_bases = schema_class_bases
        self.schema = schema
        self.fields = {}
        self.prepared_schema = None

    def add(self, field_name, field_type):
        self.fields[field_name] = field_type

    def pop_prepared_schema(self):
        ret = self.prepared_schema
        self.prepared_schema = None
        return ret


class InvenioRecordSchemaBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record_schema'
    class_config = 'record-schema-class'
    template = 'record-schema'

    def begin(self, schema, settings):
        super().begin(schema, settings)
        self.marshmallow_stack = []
        self.imports = defaultdict(set)  # import => aliases
        self.imports['marshmallow'].add('ma')
        self.imports['marshmallow.fields'].add('ma_fields')
        self.imports['marshmallow.validate'].add('ma_valid')
        self.imported_classes = {}

    def finish(self):
        # TODO: generate subschemas as well
        # TODO: generate arrays as well
        # TODO: handle required
        super().finish(
            imports=self.imports,
            imported_classes=self.imported_classes
        )

    @process('/model/**', condition=lambda current, stack: is_schema_element(stack))
    def enter_model_element(self, stack: ModelBuilderStack):
        schema_path = match_schema(stack)
        if isinstance(schema_path[-1], Ref):
            schema_element_type = schema_path[-1].element_type
        else:
            schema_element_type = None

        definition = None
        recurse = True
        if schema_element_type == 'properties':
            parent = stack[-2].data
            definition = parent.get(OAREPO_MARSHMALLOW_PROPERTY, {})

            # set nested if not already set
            if 'nested' not in definition:
                definition['nested'] = True

            generate_schema_class = False
            if 'class' in definition:
                schema_class = definition['class']
                if '.' not in schema_class:
                    schema_class = package_name(
                        self.settings.python.record_schema_class) + '.' + schema_class
                schema_class_base_classes = definition.get('base-classes', ['ma.Schema'])
                generate_schema_class = definition.get('generate', False)
            if generate_schema_class:
                self.marshmallow_stack.append(
                    MarshmallowNode(schema_class, schema_class_base_classes, stack.top.data))
                # add nested to the definition
            else:
                schema_element_type = 'nodef'
            recurse = generate_schema_class

        if recurse:
            # process children
            yield
        else:
            # skip children
            yield stack.SKIP

        data = stack.top.data

        if not self.marshmallow_stack:
            return

        marshmallow_stack_top = self.marshmallow_stack[-1]

        if schema_element_type == 'nodef':
            definition = self.get_marshmallow_definition(data, stack, definition=definition)
            self.marshmallow_stack[-1].prepared_schema = definition
        elif schema_element_type == 'items':
            definition = self.get_marshmallow_definition(data, stack)
            definition['field'] = f"ma.List({definition['field']})"
            self.marshmallow_stack[-1].prepared_schema = definition
        elif schema_element_type == 'property':
            prepared_schema = marshmallow_stack_top.pop_prepared_schema()
            if prepared_schema:
                deepmerge(data.setdefault(OAREPO_MARSHMALLOW_PROPERTY, {}), prepared_schema)
            definition = self.get_marshmallow_definition(data, stack)
            key = definition.get('field_name', stack.top.key)
            marshmallow_stack_top.add(key, definition['field'])
        elif schema_element_type == 'properties':
            node = self.marshmallow_stack.pop()
            self.process_template(
                self.class_to_path(node.schema_class_name),
                'object-schema',
                schema_class=node.schema_class_name,
                schema_bases=node.schema_class_bases,
                fields=node.fields,
                imports=self.imports,
                imported_classes=self.imported_classes,
                current_package_name=package_name(node.schema_class_name)
            )

    def get_marshmallow_definition(self, data, stack, definition=None):
        if not definition:
            definition = data.setdefault(OAREPO_MARSHMALLOW_PROPERTY, {})

        definition = self.call_components('invenio_before_set_marshmallow_definition', definition, stack=stack)

        data_type = data.get('type', 'object')
        generator = self.schema.settings.python.marshmallow.mapping.get(data_type, None)
        if isinstance(generator, dict):
            # a value, not a callable => merge it
            definition = deepmerge(generator, definition)
            data['marshmallow'] = definition
            generator = None

        # add imports if required
        for imp in definition.get('imports', []):
            self.imports[imp['import']].add(imp['alias'])

        self.imported_classes.update(definition.get('imported-classes', {}))

        if 'field' in definition:
            # do not modify the field
            return definition

        if 'class' in definition:
            class_name = definition['class']
            if '.' in class_name:
                if not with_defined_prefix(self.settings.python.always_defined_import_prefixes, class_name):
                    class_base_name = self.imported_classes[definition['class']] = base_name(class_name)
                else:
                    class_base_name = class_name
            else:
                class_base_name = class_name

            # generate instance of the class, filling the options and validators

            definition['field'] = create_field(class_base_name, options=(), validators=(),
                                               definition=definition)
            return definition

        # if no generator from settings, get the default one
        if not generator:
            generator = default_marshmallow_generators.get(data_type, None)
            if not generator:
                if data_type == 'object':
                    raise Exception(
                        f'Do not have marshmallow field generator for type "{data_type}" at path "{stack.path}". '
                        f'Either supply an existing schema class or instruct the compiler to generate one. '
                        f'See the documentation (docs/model.md, section oarepo:marshmallow) for details.')
                raise Exception(
                    f'Do not have marshmallow field generator for type "{data_type}" at path "{stack.path}". '
                    f'Define it either in invenio_record_schema.py or in your own config')

        # and generate the field
        definition['field'] = generator(data, definition, self.schema, self.imports)
        definition = self.call_components('invenio_after_set_marshmallow_definition', definition, stack=stack)
        return definition


def create_field(field_type, options=(), validators=(), definition=None):
    opts = [*options, *definition.get('options', [])]
    validators = [*validators, *definition.get('validators', [])]
    nested = definition.get('nested', False)
    if validators:
        opts.append(f'validate=[{",".join(validators)}]')
    kwargs = definition.get('field_args', '')
    if kwargs and opts:
        kwargs = ', ' + kwargs
    if not nested:
        ret = f'{field_type}({", ".join(opts)}{kwargs})'
    else:
        ret = f'{field_type}'
    if nested:
        if opts or kwargs:
            ret = f'ma_fields.Nested({ret}, {", ".join(opts)}{kwargs})'
        else:
            ret = f'ma_fields.Nested({ret})'
    return ret


def marshmallow_string_generator(data, definition, schema, imports):
    validators = []
    min_length = data.get('minLength', None)
    max_length = data.get('maxLength', None)
    if min_length is not None or max_length is not None:
        validators.append(f'ma_valid.Length(min={min_length}, max={max_length})')
    return create_field('ma_fields.String', [], validators, definition)


def marshmallow_integer_generator(data, definition, schema, imports):
    validators = []
    minimum = data.get('minimum', None)
    maximum = data.get('maximum', None)
    exclusive_minimum = data.get('exclusiveMinimum', None)
    exclusive_maximum = data.get('exclusiveMaximum', None)

    if minimum is not None or maximum is not None or exclusive_minimum is not None or exclusive_maximum is not None:
        validators.append(
            f'ma_valid.Range('
            f'min={minimum or exclusive_minimum or "None"}, max={maximum or exclusive_maximum or "None"}, '
            f'min_inclusive={exclusive_minimum is None}, max_inclusive={exclusive_maximum is None})')
    return create_field('ma_fields.Integer', [], validators, definition)


# TODO: rest of supported schema types

default_marshmallow_generators = {
    'string': marshmallow_string_generator,
    'integer': marshmallow_integer_generator
}
