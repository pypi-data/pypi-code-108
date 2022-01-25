from peewee import Field


class PeeweeFields:
    mysql_mapping = {
        'bigint': 'BigIntegerField',
        'blob': 'BigBitField',
        'char': 'FixedCharField',
        'date': 'DateField',
        'datetime': 'DateTimeField',
        'double': 'DoubleField',
        'float': 'FloatField',
        'int': 'IntegerField',
        'integer': 'IntegerField',
        'numeric': 'DecimalField',
        'real': 'FloatField',
        'set': 'CharField',
        'smallint': 'SmallIntegerField',
        'text': 'TextField',
        'time': 'TimeField',
        'timestamp': 'TimestampField',
        'tinyint': 'IntegerField',
        'varbinary': 'CharField',
        'varchar': 'CharField',
        }
    __support_sql = {'mysql': mysql_mapping}

    @classmethod
    def update(cls, sql_type="mysql", **kwargs):
        cls.__support_sql[sql_type].update(**kwargs)

    @classmethod
    def get(cls, sql_type="mysql"):
        return cls.__support_sql[sql_type]

    class UnknownField(Field):
        pass
