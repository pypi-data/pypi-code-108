"""
dict params
type from database type to database
"""
excluded_fields = ["password"]  # fields not using in converter

types_converter_dict = {
    "mysql:pg": {
        "type": {
            "char": "character",
            "varchar": "character varying",
            "tinytext": "text",
            "mediumtext": "text",
            "text": "text",
            "longtext": "text",
            "tinyblob": "bytea",
            "mediumblob": "bytea",
            "longblob": "bytea",
            "binary": "bytea",
            "varbinary": "bytea",
            "bit": "bit varying",
            "tinyint": "smallint",
            "tinyint unsigned": "smallint",
            "smallint": "smallint",
            "smallint unsigned": "integer",
            "mediumint": "integer",
            "mediumint unsigned": "integer",
            "int": "integer",
            "int unsigned": "bigint",
            "bigint": "bigint",
            "bigint unsigned": "numeric",
            "float": "real",
            "float unsigned": "real",
            "double": "double precision",
            "double unsigned": "double precision",
            "decimal": "numeric",
            "decimal unsigned": "numeric",
            "numeric": "numeric",
            "numeric unsigned": "numeric",
            "date": "date",
            "datetime": "timestamp without time zone",
            "time": "time without time zone",
            "timestamp": "timestamp without time zone",
            "year": "smallint",
            "enum": "character varying",
            "set": "ARRAY[]::text[]",
        },
        "default": {"current_timestamp": "now()"},
    },
    "mysql:vertica": {
        "type": {
            "integer": "int",
            "tinyint": "int",
            "text": "long varchar",
            "json": "long varchar",
            "enum": "varchar",
            "char": "varchar",
            "datetime": "timestamp",
            "double": "double precision",
        },
        "default": {"current_timestamp": "now()", "'0000-00-00 00:00:00'": "null"},
    },
    "mysql:exasol": {
        "type": {
            "text": "varchar",
            "json": "varchar",
            "enum": "varchar",
            "blob": "varchar",
            "set": "varchar",
            "tinytext": "varchar",
            "datetime": "timestamp",
        },
        "default": {},
    },
    "ch:vertica": {
        "type": {
            "string": "long varchar",
            "uuid": "long varchar",
            "double": "double precision",
            "uint8": "int",
            "uint16": "int",
            "uint32": "int",
            "uint64": "int",
            "int64": "int",
            "int8": "int",
            "int16": "int",
            "int32": "int",
            "array(string)": "array[varchar]",
        },
        "default": {},
    },
    "pg:vertica": {
        "type": {
            "_text": "long varchar",
            "text": "long varchar",
            "jsonb": "long varchar",
            "json": "long varchar",
            "int2": "bigint",
            "int4": "bigint",
            "int8": "bigint",
            "float4": "double precision",
            "float8": "double precision",
            "numeric": "numeric precision",
        },
        "default": {},
    },
    # toDo remove default values if not cond, varchar(467) - remove numbers for ch
    "pg:ch": {
        "type": {
            "_text": "String",
            "text": "String",
            "jsonb": "String",
            "json": "String",
            "varchar": "String",
            "interval": "String",
            "int2": "Int8",
            "boolean": "UInt8",
            "int4": "Int8",
            "timestamp": "Datetime",
            "int8": "Int8",
            "integer": "Int32",
        },
        "default": {"false": 0, "true": 1},
    },
}

"""
dict params to one way converter
from pandas or json to database
"dialect":"clickhouse+native",
"quote": "`",
"max_length_mult":1  
"""

base_converter_params = {
    "ch": {
        "dialect": "clickhouse+native",
        "quote": "`",
        "max_length_mult": 1,
        "from_python_dict": {
            "str": "Nullable(String)",
            "bool": "UInt8",
            "int": "UInt32",
            "float": "float",
        },
        "to_python_dict": {
            "string": "str",
            "float": "float",
            "uint8": "bool",
            "uint16": "int",
            "uint32": "int",
            "uint64": "int",
            "int8": "int",
            "int16": "int",
            "int32": "int",
            "int64": "int",
            "datetime": "datetime"
        },
        "text": ["string"],
    },
    "pg": {
        "dialect": "postgresql",
        "quote": '"',
        "max_length_mult": 1,
        "to_python_dict": {
            "double precision": "float",
            "integer": "int",
            "json": "json",
            "boolean": "bool",
        },
        "text": ["_text", "text"],
    },
    "mysql": {
        "dialect": "mysql+pymysql",
        "quote": '"',
        "max_length_mult": 1,
        "to_python_dict": {
            "double precision": "float",
            "int": "int",
            "json": "json",
            "boolean": "bool",
        },
        "text": ["_text", "text"],
    },
    "vertica": {
        "dialect": "vertica+vertica_python",
        "quote": '"',
        "max_length_mult": 2.5,
        "constrained_columns_str": " NOT NULL CONSTRAINT {table_name}_pk PRIMARY KEY ENABLED",
        "to_python_dict": {
            "double precision": "float",
            "int": "int",
            "long varbinary": "json",
            "blob": "json",
            "boolean": "bool",
        },
        "from_python_dict": {
            "str": "varchar(1000)",
            "bool": "int",
            "int": "int",
            "float": "float",
        },
    },
    "exasol": {
        "dialect": "exa+pyodbc",
        "quote": '"',
        "max_length_mult": 1,
        "to_python_dict": {
            "double precision": "float",
            "int": "int",
            "json": "json",
            "boolean": "bool",
        },
    },
}
