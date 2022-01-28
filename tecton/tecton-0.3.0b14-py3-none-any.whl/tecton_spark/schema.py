class Schema:
    def __init__(self, proto):
        self._proto = proto

    def to_proto(self):
        return self._proto

    def tecton_type(self, column_name):
        c = self._column(column_name)
        return c.feature_server_type if c.HasField("feature_server_type") else None

    def spark_type(self, column_name):
        c = self._column(column_name)
        if not c.HasField("raw_spark_type"):
            raise ValueError(f"Column {column_name} is missing raw_spark_type")
        return c.raw_spark_type

    def _column(self, column_name):
        cs = [c for c in self._proto.columns if c.name == column_name]
        if not cs:
            raise ValueError(f"Unknown column: {column_name}. Schema is: {self._proto}")
        return cs[0]

    def column_names(self):
        return [c.name for c in self._proto.columns]

    def column_name_raw_spark_types(self):
        return [(c.name, c.raw_spark_type) for c in self._proto.columns]
