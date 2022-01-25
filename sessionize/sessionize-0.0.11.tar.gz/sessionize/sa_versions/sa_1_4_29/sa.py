"""
All SqlAlchemy functionality used in Sessionize is defined here.
"""
from typing import Optional, Any, Union, Generator

from sqlalchemy import PrimaryKeyConstraint, Table, Column, MetaData
from sqlalchemy.schema import DropTable, CreateTable
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import sql, func, inspect, select
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.sql.elements import and_, or_
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError, NoSuchTableError
from sqlalchemy import VARCHAR, INTEGER

from sessionize.exceptions import MissingPrimaryKey, SliceError
from sessionize.sa_versions.sa_1_4_29.type_convert import _type_convert


Record = dict[str, Any]
SqlConnection = Union[Engine, Session, Connection]


class SqlAlchemy:
    __version__ = '1.4.29'

    @staticmethod
    def primary_key_columns(sa_table: Table) -> list[Column]:
        return sa_table.primary_key.columns.values()
    
    @classmethod
    def primary_key_names(cls, sa_table: Table) -> list[str]:
        return [c.name for c in cls.primary_key_columns(sa_table)]

    @staticmethod
    def get_connection(connection):
        if isinstance(connection, Session):
            return connection.connection()
        return connection

    @staticmethod
    def get_metadata(connection, schema=None):
        return MetaData(bind=connection, schema=schema)

    @classmethod
    def get_table(
        cls,
        name: str,
        connection: SqlConnection,
        schema: Optional[str] = None
    ) -> Table:
        metadata = cls.get_metadata(connection, schema)
        autoload_with = cls.get_connection(connection)

        return Table(name,
                     metadata,
                     autoload=True,
                     autoload_with=autoload_with,
                     extend_existing=True,
                     schema=schema)

    @classmethod
    def get_class(
        cls,
        name: str,
        connection: SqlConnection,
        schema: Optional[str] = None
    ):
        metadata = cls.get_metadata(connection, schema)
        connection = cls.get_connection(connection)

        metadata.reflect(connection, only=[name], schema=schema)
        Base = automap_base(metadata=metadata)
        Base.prepare()
        return Base.classes[name]

    @staticmethod
    def get_column(
        sa_table: Table,
        column_name: str
    ) -> Column:
        return sa_table.c[column_name]

    @staticmethod
    def get_table_constraints(sa_table: Table):
        return sa_table.constraints

    @classmethod
    def get_primary_key_constraints(
        cls,
        sa_table: Table
    ) -> tuple[str, list[str]]:
        cons = cls.get_table_constraints(sa_table)
        for con in cons:
            if isinstance(con, PrimaryKeyConstraint):
                return con.name, [col.name for col in con.columns]

    @staticmethod
    def get_column_types(sa_table: Table) -> dict[str, sql.sqltypes]:
        return {c.name: c.type for c in sa_table.c}

    @staticmethod
    def get_column_names(sa_table: Table) -> list[str]:
        return [c.name for c in sa_table.columns]

    @staticmethod
    def get_table_names(engine: Engine, schema: Optional[str] = None) -> list[str]:
        return inspect(engine).get_table_names(schema)

    @classmethod
    def get_row_count(cls, sa_table: Table, session: Session) -> int:
        col_name = cls.get_column_names(sa_table)[0]
        col = cls.get_column(sa_table, col_name)
        return session.execute(func.count(col)).scalar()

    @staticmethod
    def get_schemas(engine: Engine) -> list[str]:
        insp = inspect(engine)
        return insp.get_schema_names()

    @classmethod
    def delete_records_session(
        cls,
        sa_table: Table,
        col_name: str,
        values: list,
        session: Session
    ) -> None:
        col = cls.get_column(sa_table, col_name)
        session.query(sa_table).filter(col.in_(values)).delete(synchronize_session=False)

    @staticmethod
    def get_where_clause(sa_table: Table, record: Record):
        return [sa_table.c[key_name]==key_value for key_name, key_value in record.items()]

    @classmethod
    def delete_record_by_values_session(
        cls,
        sa_table: Table,
        record: Record,
        session: Session
    ) -> None:
        # Delete any records that match the given record values.
        where_clause = cls.get_where_clause(sa_table, record)
        if len(where_clause) == 0:
            return
        session.query(sa_table).where((and_(*where_clause))).delete(synchronize_session=False)

    @classmethod
    def delete_records_by_values_session(
        cls,
        sa_table: Table,
        records: list[Record],
        session: Session,
    ) -> None:
        where_clauses = []
        for record in records:
            where_clause = cls.get_where_clause(sa_table, record)
            where_clauses.append(and_(*where_clause))
        if len(where_clauses) == 0:
            return
        session.query(sa_table).where((or_(*where_clauses))).delete(synchronize_session=False)

    @classmethod
    def delete_records(
        cls,
        sa_table: Table,
        col_name: str,
        values: list,
        engine: Engine
    ) -> None:
        with Session(engine) as session, session.begin():
            cls.delete_records_session(sa_table, col_name, values, session)

    @staticmethod
    def delete_all_records_session(table: Table, session: Session) -> None:
        session.query(table).delete()

    @classmethod
    def delete_all_records(cls, sa_table: Table, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            cls.delete_all_records_session(sa_table, session)

    @staticmethod
    def insert_from_table_session(sa_table1: Table, sa_table2: Table, session: Session) -> None:
        session.execute(sa_table2.insert().from_select(sa_table1.columns.keys(), sa_table1))

    @classmethod
    def insert_from_table(
        cls,
        sa_table1: Table,
        sa_table2: Table,
        engine: Engine
    ) -> None:
        with sessionmaker(engine).begin() as session:
            cls.insert_from_table_session(sa_table1, sa_table2, session)

    @classmethod
    def insert_records_session(
        cls,
        sa_table: Table,
        records: list[Record],
        session: Session
    ) -> None:
        table_class = cls.get_class(sa_table.name, session, schema=sa_table.schema)
        mapper = inspect(table_class)
        session.bulk_insert_mappings(mapper, records)

    @classmethod
    def insert_records(
        cls,
        sa_table: Table,
        records: list[Record],
        engine: Engine
    ) -> None:
        with sessionmaker(engine).begin() as session:
            cls.insert_records_session(sa_table, records, session)

    @classmethod
    def select_records_all(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        sorted: bool = False,
        include_columns: Optional[list[str]] = None
    ) -> list[Record]:
        if include_columns is not None:
            columns = [cls.get_column(sa_table, column_name) for column_name in include_columns]
            query = select(*columns)
        else:
            query = select(sa_table)

        if sorted:
            query = query.order_by(*cls.primary_key_columns(sa_table))
        results = connection.execute(query)
        return [dict(r) for r in results]

    @classmethod
    def select_records_chunks(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        chunksize: int = 2,
        sorted: bool = False,
        include_columns: Optional[list[str]] = None
    ) -> Generator[list[Record], None, None]:
        if include_columns is not None:
            columns = [cls.get_column(sa_table, column_name) for column_name in include_columns]
            query = select(*columns)
        else:
            query = select(sa_table)

        if sorted:
            query = query.order_by(*cls.primary_key_columns(sa_table))
        stream = connection.execute(query, execution_options={'stream_results': True})
        for results in stream.partitions(chunksize):
            yield [dict(r) for r in results]

    @classmethod
    def select_existing_values(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        column_name: str,
        values: list,
    ) -> list:
        column = cls.get_column(sa_table, column_name)
        query = select([column]).where(column.in_(values))
        return connection.execute(query).scalars().fetchall()

    @classmethod
    def select_column_values_all(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        column_name: str
    ) -> list:
        query = select(cls.get_column(sa_table, column_name))
        return connection.execute(query).scalars().all()

    @classmethod
    def select_column_values_chunks(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        column_name: str,
        chunksize: int
    ) -> Generator[list, None, None]:
        query = select(cls.get_column(sa_table, column_name))
        stream = connection.execute(query, execution_options={'stream_results': True})
        for results in stream.scalars().partitions(chunksize):
            yield results

    @classmethod
    def _convert_slice_indexes(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        start: Optional[int] = None,
        stop: Optional[int] = None
    ) -> tuple[int, int]:
        # start index is 0 if None
        start = 0 if start is None else start
        row_count = cls.get_row_count(sa_table, connection)
        
        # stop index is row count if None
        stop = row_count if stop is None else stop
        # convert negative indexes
        start = _calc_positive_index(start, row_count)
        start = _stop_underflow_index(start, row_count)
        stop = _calc_positive_index(stop, row_count)
        stop = _stop_overflow_index(stop, row_count)

        if row_count == 0:
            return 0, 0

        return start, stop

    @classmethod
    def select_records_slice(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        sorted: bool = False,
        include_columns: Optional[list[str]] = None
    ) -> list[Record]:
        start, stop = cls._convert_slice_indexes(sa_table, connection, start, stop)
        if stop < start:
            raise SliceError('stop cannot be less than start.')
        if include_columns is not None:
            columns = [cls.get_column(sa_table, column_name) for column_name in include_columns]
            query = select(*columns)
        else:
            query = select(sa_table)
        if sorted:
            query = query.order_by(*cls.primary_key_columns(sa_table))
        query = query.slice(start, stop)
        results = connection.execute(query)
        return [dict(r) for r in results]

    @classmethod
    def select_column_values_by_slice(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        column_name: str,
        start: Optional[int] = None,
        stop: Optional[int] = None
    ) -> list:
        start, stop = cls._convert_slice_indexes(sa_table, connection, start, stop)
        if stop < start:
            raise SliceError('stop cannot be less than start.')
        query = select(cls.get_column(sa_table, column_name)).slice(start, stop)
        return connection.execute(query).scalars().all()

    @classmethod
    def select_column_value_by_index(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        column_name: str,
        index: int
    ) -> Any:
        if index < 0:
            row_count = cls.get_row_count(sa_table, connection)
            if index < -row_count:
                raise IndexError('Index out of range.') 
            index = _calc_positive_index(index, row_count)
        query = select(cls.get_column(sa_table, column_name)).slice(index, index+1)
        return connection.execute(query).scalars().all()[0]

    @classmethod
    def select_primary_key_records_by_slice(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        _slice: slice,
        sorted: bool = False
    ) -> list[Record]:
        start = _slice.start
        stop = _slice.stop
        start, stop = cls._convert_slice_indexes(sa_table, connection, start, stop)
        if stop < start:
            raise SliceError('stop cannot be less than start.')
        primary_key_values = cls.primary_key_columns(sa_table)
        if sorted:
            query = select(primary_key_values).order_by(*primary_key_values).slice(start, stop)
        else:
            query = select(primary_key_values).slice(start, stop)
        results = connection.execute(query)
        return [dict(r) for r in results]

    @classmethod
    def select_record_by_primary_key(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        primary_key_value: Record,
        include_columns: Optional[list[str]] = None
    ) -> Record:
        # TODO: check if primary key values exist
        where_clause = cls.get_where_clause(sa_table, primary_key_value)
        if len(where_clause) == 0:
            return []
        if include_columns is not None:
            columns = [cls.get_column(sa_table, column_name) for column_name in include_columns]
            query = select(*columns).where((and_(*where_clause)))
        else:
            query = select(sa_table).where((and_(*where_clause)))
        results = connection.execute(query)
        results = [dict(x) for x in results]
        if len(results) == 0:
            raise MissingPrimaryKey('Primary key values missing in table.')
        return results[0]

    @classmethod
    def select_records_by_primary_keys(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        primary_keys_values: list[Record],
        schema: Optional[str] = None,
        include_columns: Optional[list[str]] = None
    ) -> list[Record]:
        # TODO: check if primary key values exist
        where_clauses = []
        for record in primary_keys_values:
            where_clause = cls.get_where_clause(sa_table, record)
            where_clauses.append(and_(*where_clause))
        if len(where_clauses) == 0:
            return []
        if include_columns is not None:
            columns = [cls.get_column(sa_table, column_name) for column_name in include_columns]
            query = select(*columns).where((or_(*where_clauses)))
        else:
            query = select(sa_table).where((or_(*where_clauses)))
        results = connection.execute(query)
        return [dict(r) for r in results]

    @classmethod
    def select_column_values_by_primary_keys(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        column_name: str,
        primary_keys_values: list[Record]
    ) -> list:
        # TODO: check if primary key values exist
        where_clauses = []
        for record in primary_keys_values:
            where_clause = cls.get_where_clause(sa_table, record)
            where_clauses.append(and_(*where_clause))

        if len(where_clauses) == 0:
            return []
        query = select(cls.get_column(sa_table, column_name)).where((or_(*where_clauses)))
        results = connection.execute(query)
        return results.scalars().fetchall()

    @classmethod
    def select_value_by_primary_keys(
        cls,
        sa_table: Table,
        connection: SqlConnection,
        column_name: str,
        primary_key_value: Record,
        schema: Optional[str] = None
    ) -> Any:
            # TODO: check if primary key values exist
            where_clause = cls.get_where_clause(sa_table, primary_key_value)
            if len(where_clause) == 0:
                raise KeyError('No such primary key values exist in table.')
            query = select(cls.get_column(sa_table, column_name)).where((and_(*where_clause)))
            return connection.execute(query).scalars().all()[0]

    @classmethod
    def update_records_session(
        cls,
        sa_table: Table,
        records: list[Record],
        session: Session
    ) -> None:
        table_name = sa_table.name
        table_class = cls.get_class(table_name, session, schema=sa_table.schema)
        mapper = inspect(table_class)
        session.bulk_update_mappings(mapper, records)

    @classmethod
    def update_records(
        cls,
        sa_table: Table,
        records: list[Record],
        engine: Engine
    ) -> None:
        with Session(engine) as session, session.begin():
            cls.update_records_session(sa_table, records, session)

    @classmethod
    def create_table(
        cls,
        table_name: str,
        column_names: list[str],
        column_types: list[type],
        primary_key: str,
        engine: Engine,
        schema: Optional[str] = None,
        autoincrement: Optional[bool] = True,
        if_exists: Optional[str] = 'error'
    ) -> Table:
        
        cols = []
        
        for name, python_type in zip(column_names, column_types):
            sa_type = _type_convert[python_type]
            if name == primary_key:
                col = Column(name, sa_type,
                             primary_key=True,
                             autoincrement=autoincrement)
            else:
                col = Column(name, sa_type)
            cols.append(col)

        metadata = MetaData(engine)
        table = Table(table_name, metadata, *cols, schema=schema)
        if if_exists == 'replace':
            drop_table_sql = DropTable(table, if_exists=True)
            engine.execute(drop_table_sql)
        table_creation_sql = CreateTable(table)
        engine.execute(table_creation_sql)
        return cls.get_table(table_name, engine, schema=schema)

    @classmethod
    def drop_table(
        cls,
        table: Union[Table, str],
        engine: Engine,
        if_exists: Optional[bool] = True,
        schema: Optional[str] = None
    ) -> None:
        if isinstance(table, str):
            if table not in inspect(engine).get_table_names(schema=schema):
                if if_exists:
                    return
            table = cls.get_table(table, engine, schema=schema)
        sql = DropTable(table, if_exists=if_exists)
        engine.execute(sql)


def _calc_positive_index(index: int, row_count: int) -> int:
    # convert negative index to real index
    if index < 0:
        index = row_count + index
    return index


def _stop_overflow_index(index: int, row_count: int) -> int:
    if index > row_count - 1:
        return row_count
    return index

    
def _stop_underflow_index(index: int, row_count: int) -> int:
    if index < 0 and index < -row_count:
        return 0
    return index


