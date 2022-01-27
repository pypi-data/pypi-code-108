from pydantic import BaseModel
from typing import Any, List, Optional


class SimpleColumn(BaseModel):
    columnName: str
    dataType: str


class SimpleTable(BaseModel):
    tableName: str
    databaseName: str
    schemaName: str
    fqtn: Optional[str]


class SimpleTableWithColumns(SimpleTable):
    columns: Optional[List[SimpleColumn]]