from feast.value_type import ValueType

def snowflake_to_feast_value_type(snowflake_type_as_str: str) -> ValueType:
    # https://docs.snowflake.com/en/sql-reference/intro-summary-data-types.html
    type_map = {
        "NUMBER": ValueType.INT64,
        "FLOAT": ValueType.FLOAT,
        "BOOLEAN": ValueType.BOOL,
        "CHARACTER": ValueType.STRING,
        "VARCHAR": ValueType.STRING,
        "TIMESTAMP": ValueType.UNIX_TIMESTAMP,
        "TIMESTAMP_TZ": ValueType.UNIX_TIMESTAMP,
        # skip date, geometry, hllsketch, time, timetz
    }

    return type_map[snowflake_type_as_str.lower()]
