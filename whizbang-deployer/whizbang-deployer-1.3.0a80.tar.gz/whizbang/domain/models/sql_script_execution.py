from typing import List

from pydantic import BaseModel


class DatabaseExecution(BaseModel):
    database: str = None
    scripts: List[str] = []


class SqlExecution(BaseModel):
    database_execution_objects: List[DatabaseExecution]
