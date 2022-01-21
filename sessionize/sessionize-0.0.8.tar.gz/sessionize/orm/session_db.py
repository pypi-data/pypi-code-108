from sqlalchemy.orm import Session
from sqlalchemy import inspect

from sessionize.orm.selection import TableSelection
from sessionize.orm.session_parent import SessionParent
from sessionize.utils.sa_orm import get_schemas


class SessionDatabase(SessionParent):
    def __init__(self, engine):
        SessionParent.__init__(self, engine)
        self.tables = {}

    def __repr__(self) -> str:
        return f"""SessionDatabase(table_names={self.table_names()})"""

    def __getitem__(self, key: str) -> TableSelection:
        # SessionDataBase[table_name]
        if isinstance(key, str):
            # Pull out schema if key has period.
            if '.' in key:
                schema, name = key.split('.')
            else:
                schema, name = None, key
            if key not in self.tables:
                self.tables[key] = TableSelection(self, name, schema=schema)
            return self.tables[key]
        raise KeyError('SessionDataBase key type can only be str.')

    def table_names(self, schema=None):
        if schema is not None:
            names = inspect(self.engine).get_table_names(schema)
            return [f'{schema}.{name}' for name in names]
        out = []
        for schema in get_schemas(self.engine):
            names = inspect(self.engine).get_table_names(schema)
            names = [f'{schema}.{name}' for name in names]
            out.extend(names)
        return out