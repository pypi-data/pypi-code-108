class CustomPropertyType:

    def __init__(self, type, external_type):
        self.type = type
        self.external_type = external_type

    def __str__(self):
        return self.type

    def __eq__(self, other):
        if other is None or not isinstance(other, CustomPropertyType):
            return False

        return self.type == other.type

    def __hash__(self):
        return hash(self.type)


CustomPropertyType.STRING = CustomPropertyType('string', 'String')
CustomPropertyType.BOOL = CustomPropertyType('bool', 'Boolean')
CustomPropertyType.INT = CustomPropertyType('int', 'Number')
CustomPropertyType.FLOAT = CustomPropertyType('double', 'Number')
CustomPropertyType.SEMVER = CustomPropertyType('semver', 'Semver')
