from converter.advanced_ddl.text_size_generator import TextSizeGenerator
from converter.advanced_ddl.keys_generator import KeysGenerator


class AdvancedDDLCreator(TextSizeGenerator, KeysGenerator):
    def __init__(self, fields_converter, advanced_features):
        """
        Additional staff for ddl
        :param fields_converter:
        :param advanced_features: 0-get size for text fields, 1 - get p
        """
        self.advanced_features = advanced_features
        self.fields_converter = fields_converter
        if 0 in self.advanced_features:
            TextSizeGenerator.__init__(self, db_worker=fields_converter.db_worker_from)
        if 1 in self.advanced_features:
            KeysGenerator.__init__(self, db_worker=fields_converter.db_worker_from)

    def get_attributes(self, table_name):
        result = {"text_sizes": [], "constrained_columns": []}
        if 0 in self.advanced_features:
            result["text_sizes"] = self.get_text_sizes(table_name)
        if 1 in self.advanced_features:
            result["constrained_columns"] = self.get_pk_constraint(table_name)
        return result
