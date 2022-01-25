from table.base_table import BaseTable


class TableConfigurer:
    __slots__ = ['tables']

    tables: dict[str, BaseTable]

    def __getattr__(self, item: str) -> BaseTable:
        return self.tables[item]

    def init_tables(self, **kwargs):
        self.tables = {}
        if kwargs:
            for key in kwargs:
                self.tables[key] = BaseTable(key, kwargs.get(key))


tables: TableConfigurer = TableConfigurer()
