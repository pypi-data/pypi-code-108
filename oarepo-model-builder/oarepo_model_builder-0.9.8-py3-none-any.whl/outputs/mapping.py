from .json import JSONOutput


class MappingOutput(JSONOutput):
    TYPE = 'mapping'

    def merge_mapping(self, mapping):
        self.stack.merge(mapping)

