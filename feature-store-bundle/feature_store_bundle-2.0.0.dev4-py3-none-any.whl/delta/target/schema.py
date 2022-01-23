import pyspark.sql.types as t
from featurestorebundle.entity.Entity import Entity


def get_target_id_column_name():
    return "target_id"


def get_id_column_name():
    return "id_column"


def get_time_column_name():
    return "time_column"


def get_entity_targets_schema(entity: Entity):
    return [
        t.StructField("id_column", entity.id_column_type, False),
        t.StructField("time_column", entity.time_column_type, False),
        t.StructField("target_id", t.StringType(), False),
    ]


def get_entity_target_map_schema():
    return [
        t.StructField("entity", t.StringType(), False),
        t.StructField("target_id", t.StringType(), False),
    ]


def get_targets_schema():
    return [
        t.StructField("target_id", t.StringType(), False),
        t.StructField("description", t.StringType(), True),
    ]
