from oarepo_model_builder.stack import ModelBuilderStack


class SchemaPathValidator:
    valid = False

    def get(self, path_el):
        raise NotImplementedError()

    @property
    def real(self):
        return self


class Invalid(SchemaPathValidator):
    def get(self, path_el):
        return self


invalid = Invalid()


class PrimitiveValidator(SchemaPathValidator):
    valid = True

    def get(self, path_el):
        return invalid


primitive = PrimitiveValidator()


class DictValidator(SchemaPathValidator):
    valid = True

    def __init__(self, dict=None, primitives=None):
        self.dict = dict or {}
        if primitives:
            for p in primitives.split(','):
                p = p.strip()
                if not p:
                    continue
                self.dict[p] = primitive

    def get(self, path_el):
        if path_el in self.dict:
            return self.dict[path_el]
        return invalid


class AnyKeyDictValidator(SchemaPathValidator):
    valid = True

    def __init__(self, _next):
        self._next = _next

    def get(self, path_el):
        return self._next


class Ref(SchemaPathValidator):
    refs = {}
    valid = True

    def __init__(self, element_type, refstr):
        self.element_type = element_type
        self.refstr = refstr

    def get(self, path_el):
        return self.refs[self.refstr].get(path_el)

    @property
    def real(self):
        return self.refs[self.refstr]

    def __str__(self):
        return self.element_type

    def __repr__(self):
        return str(self)


Ref.refs['type'] = DictValidator(dict={
    "properties": Ref('properties', 'properties'),
    "patternProperties": Ref('patternProperties', 'properties'),
    "additionalProperties": Ref('additionalProperties', 'additionalProperties'),
    "propertyNames": Ref('propertyNames', 'propertyNames'),
    "items": Ref('items', 'type'),
    "prefixItems": Ref('prefixItems', 'type'),
    "contains": Ref('contains', 'type'),
    "type": Ref('type', 'type_value')
},
    primitives="enum,const,"  # enums and consts
               "required,minProperties,maxProperties,"  # object
               "minItems,maxItems,uniqueItems,minContains,maxContains,"  # array
               "minLength,maxLength,pattern,format,"  # string
               "minimum,exclusiveMinimum,maximum,exclusiveMaximum,multipleOf"  # numbers
)

Ref.refs['additionalProperties'] = DictValidator(primitives='type')

Ref.refs['propertyNames'] = DictValidator(primitives='pattern'),

Ref.refs['properties'] = AnyKeyDictValidator(Ref('property', 'type'))

Ref.refs['type_value'] = PrimitiveValidator()

schema_paths = DictValidator(
    {
        "$vocabulary": AnyKeyDictValidator(primitive),
        "properties": Ref('properties', 'properties')
    }, primitives='$schema,$id,type'
)

model_paths = DictValidator(
    {
        'model': schema_paths
    }
)


def match_schema(stack: ModelBuilderStack):
    sc = model_paths
    parents = [sc]
    for entry in stack.stack:
        key = entry.key
        if key is None:
            continue
        if isinstance(key, int):
            continue
        sc = sc.get(key)
        if not sc.valid:
            return None
        parents.append(sc)
    return parents


def is_schema_element(stack: ModelBuilderStack):
    return match_schema(stack) is not None
