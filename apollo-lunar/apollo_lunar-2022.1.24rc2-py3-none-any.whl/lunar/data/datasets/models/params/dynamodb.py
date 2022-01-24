from typing import List, Optional

from pydantic import BaseModel, validator


class DynamoDBParams(BaseModel):
    main_table: str
    tables: List[str]

    class Config:
        fields = {
            "main_table": {"title": "Name of a main table"},
            "tables": {
                "min_items": 1,
                "title": "Table list",
                "description": "'tables' must have at least one DynamoDB table name.",
            },
        }

    @validator("tables")
    def check_main_table_in_tables(cls, tables, values):
        if main_table := values.get("main_table"):
            if main_table not in tables:
                raise ValueError("'main_table' not in 'tables'")
        return tables


class DynamoDBParamsPatchIn(DynamoDBParams):
    main_table: Optional[str] = None
    tables: Optional[List[str]] = None
