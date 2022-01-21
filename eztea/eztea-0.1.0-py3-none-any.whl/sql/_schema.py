import sqlalchemy as sa

_default_table_kwargs = dict(
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_bin",
)


class TableMetaData(sa.MetaData):
    def define_table(self, name: str, *args, **kwargs) -> sa.Table:
        for k, v in _default_table_kwargs.items():
            kwargs.setdefault(k, v)
        return sa.Table(name, self, *args, **kwargs)
