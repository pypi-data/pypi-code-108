import importlib
import os
from typing import Dict, List, Optional

from rich.table import Table
from sqlmodel import SQLModel, create_engine


def get_db_url(database_url: Optional[str] = None):
    """A helper function to get the database url."""
    if not database_url:
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            msg = "Please ensure that an environment variable is set for `DATABASE_URL` or pass in the url to the database_url option."
            raise NameError(msg)
        
    return database_url


def get_tables(models_module) -> Dict[str, SQLModel]:
    """Find all of the SQLModel tables."""
    tables = {}
    for name, obj in models_module.__dict__.items():
        if isinstance(obj, type(SQLModel)) and name != "SQLModel":
            tables[name.lower()] = obj
    return tables


def get_models(models_path: Optional[str] = None):
    # Load the models provided by the user.
    if not models_path:
        models_path = os.getenv("MODELS_PATH")
        if not models_path:
            raise NameError("No modules_path specific")
        
    models_path = os.path.normpath(models_path)
    path, filename = os.path.split(models_path)
    module_name, ext = os.path.split(filename)

    spec = importlib.util.spec_from_file_location(module_name, models_path)
    models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models)
        
    return models


def sqlmodel_setup(models_path: str, database_url: str):
    """Quickstart for getting required objects"""
    models = get_models(models_path)
    url = get_db_url(database_url)
    engine = create_engine(url)
    tables = get_tables(models)
    return models, url, engine, tables


def create_rich_table(data: List[SQLModel]) -> Table:
    table = Table()
    for col_name in data[0].dict().keys():
        table.add_column(col_name)
    for row in data:
        table.add_row(*[str(i) for i in row.dict().values()])
    return table
