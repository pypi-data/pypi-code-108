import datetime
import decimal
import re
import uuid
from typing import List

from strong_typing.auxiliary import (
    Annotated,
    MaxLength,
    Precision,
    Storage,
    int64,
    int32,
    int16,
)


def sql_to_python_type(sql_type: str) -> type:
    "Maps a PostgreSQL type to a native Python type."

    if sql_type.endswith("[]"):
        return List[sql_to_python_type(sql_type[:-2])]

    sql_type = sql_type.lower()

    if sql_type == "boolean":
        return bool
    if sql_type == "smallint":
        return int16
    if sql_type in ["int", "integer"]:
        return int32
    if sql_type == "bigint":
        return int64
    if sql_type == "real":
        return Annotated[float, Storage(4)]
    if sql_type in ["double", "double precision"]:
        return Annotated[float, Storage(8)]
    if sql_type in ["character varying", "text"]:
        return str
    if sql_type == "date":
        return datetime.date
    if sql_type in ["time", "time with time zone", "time without time zone"]:
        return datetime.time
    if sql_type in [
        "timestamp",
        "timestamp with time zone",
        "timestamp without time zone",
    ]:
        return datetime.datetime
    if sql_type == "jsonb":
        return str
    if sql_type == "uuid":
        return uuid.UUID

    m = re.match(r"^character varying[(](\d+)[)]$", sql_type)
    if m is not None:
        len = int(m.group(1))
        return Annotated[str, MaxLength(len)]

    m = re.match(r"^(?:decimal|numeric)[(](\d+)(?:,\s*(\d+))?[)]$", sql_type)
    if m is not None:
        precision = int(m.group(1))
        scale = int(m.group(2)) if m.group(2) else 0
        return Annotated[decimal.Decimal, Precision(precision, scale)]

    m = re.match(r"^time[(](\d+)[)](?: with(?:out)? time zone)?$", sql_type)
    if m is not None:
        precision = int(m.group(1))
        return Annotated[datetime.time, Precision(precision)]

    m = re.match(r"^timestamp[(](\d+)[)](?: with(?:out)? time zone)?$", sql_type)
    if m is not None:
        precision = int(m.group(1))
        return Annotated[datetime.datetime, Precision(precision)]

    raise NotImplementedError(f"unrecognized database type: {sql_type}")
