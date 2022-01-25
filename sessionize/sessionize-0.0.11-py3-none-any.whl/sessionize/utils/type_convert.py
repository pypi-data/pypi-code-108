import decimal
import datetime

import sqlalchemy as sa


_type_convert = {
    int: sa.sql.sqltypes.Integer,
    str: sa.sql.sqltypes.Unicode,
    float: sa.sql.sqltypes.Float,
    decimal.Decimal: sa.sql.sqltypes.Numeric,
    datetime.datetime: sa.sql.sqltypes.DateTime,
    bytes: sa.sql.sqltypes.LargeBinary,
    bool: sa.sql.sqltypes.Boolean,
    datetime.date: sa.sql.sqltypes.Date,
    datetime.time: sa.sql.sqltypes.Time,
    datetime.timedelta: sa.sql.sqltypes.Interval,
    list: sa.sql.sqltypes.ARRAY,
    dict: sa.sql.sqltypes.JSON
}