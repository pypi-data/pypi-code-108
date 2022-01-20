import enum


class AllMetaFieldTypes(enum.Enum):
    """所有支持的field types

    marshmallow field types: https://marshmallow.readthedocs.io/en/stable/marshmallow.fields.html

    postgres field types: https://www.postgresql.org/docs/current/rangetypes.html
    mariadb field types: https://mariadb.com/kb/en/data-types/

    elasticsearch field types: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html
    """

    BOOL = 'bool'
    STRING = 'str'
    TEXT = 'text'
    BINARY = 'binary'
    DATE = 'date'
    INT = 'int'
    FLOAT = 'float'
    IP = 'ip'
    NESTED = 'nested'
    OBJECT = 'object'
    GEO_POINT = 'point' # GEO Point Type
