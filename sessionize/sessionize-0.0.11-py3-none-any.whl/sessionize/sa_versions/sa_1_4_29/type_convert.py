import decimal
import datetime

from sqlalchemy import sql


_type_convert = {
    int: sql.sqltypes.Integer,
    str: sql.sqltypes.Unicode,
    float: sql.sqltypes.Float,
    decimal.Decimal: sql.sqltypes.Numeric,
    datetime.datetime: sql.sqltypes.DateTime,
    bytes: sql.sqltypes.LargeBinary,
    bool: sql.sqltypes.Boolean,
    datetime.date: sql.sqltypes.Date,
    datetime.time: sql.sqltypes.Time,
    datetime.timedelta: sql.sqltypes.Interval,
    list: sql.sqltypes.ARRAY,
    dict: sql.sqltypes.JSON
}