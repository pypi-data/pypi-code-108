import dataclasses
from collections import OrderedDict as OD
from dataclasses import fields, MISSING
from typing import Callable, Any, List, Type, Optional, OrderedDict, Dict, Generator, cast, Tuple, Union, ContextManager

from psycopg import connection, sql

__all__ = [
    'model',
]

from .datatypes import NO_DEFAULT, AUTO_FILLED
from .columns import Column
from .exceptions import PrimaryKeyError, FieldDefaultValueError
from .protocols import Dataclass, DatabaseModel
from .helper import classproperty


class MutationContext:
    def __init__(self, connection: 'connection.Connection[Any]', model: 'DatabaseModel',
                 insertOrUpdateOnExit: bool) -> None:
        self.connection = connection
        self.model = model
        self.insertOrUpdateOnExit = insertOrUpdateOnExit

        self.data: Dict[str, Any] = {}

    def __enter__(self) -> None:
        for f in fields(self.model):
            self.data[f.name] = getattr(self.model, f.name)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None:
            if self.insertOrUpdateOnExit:
                self.model.insertOrUpdate(self.connection)
        else:
            for k, v in self.data.items():
                setattr(self.model, k, v)


def model(_schema: Optional[str] = None, _table: Optional[str] = None, *, useInstanceCache: bool = True) -> \
        Callable[[Type['Dataclass']], Type['DatabaseModel']]:
    def wrapped(cls: Union[Type['Dataclass'], Type[Any]]) -> Type['DatabaseModel']:
        if not isinstance(cls, Dataclass):
            cls = dataclasses.dataclass(cls)

        if _table is None:
            tableName = cls.__name__.lower()
        else:
            tableName = _table

        if _schema is None:
            schemaName = 'public'
        else:
            schemaName = _schema

        columnDefinitions: OrderedDict[str, 'Column'] = OD()
        _primaryKey: Optional['Column'] = None
        primaryKeyIndex: Optional[int] = None

        argsNames: List[str] = []
        allFieldsName: List[str] = []

        # PyCharm does not recognize cls as a Dataclass despite being type hinted as one
        # noinspection PyDataclass
        for i, field in enumerate(fields(cls)):
            definition = Column.fromField(field)

            allFieldsName.append(field.name)
            if field.default is not AUTO_FILLED:
                argsNames.append(field.name)

            columnDefinitions[definition.name] = definition

            if definition.type.primary:
                if _primaryKey is not None:
                    raise PrimaryKeyError(f'{schemaName}.{tableName} ({cls.__name__}) Has two primary keys defined')
                _primaryKey = definition
                primaryKeyIndex = i

            if not (field.default is MISSING or field.default is NO_DEFAULT or field.default is AUTO_FILLED):
                raise FieldDefaultValueError(f'{field.name} does not declare default type of MISSING, NO_DEFAULT, '
                                             f'or AUTO_FILLED')

        argsString = ', '.join(argsNames)
        settersString = '\n'.join(f'    self.{a} = {a}' for a in argsNames)

        replaceAutofilledString = '    for a in dir(self):\n'\
                                  '        if getattr(self, a) is AUTO_FILLED:\n'\
                                  '            setattr(self, a, None) '

        funcString = f"def __init__(self, {argsString}):\n{settersString}\n{replaceAutofilledString}"

        # mypy doesn't support this yet so have to silence the error
        class WrappedClass(cls):  # type: ignore
            __column_definitions__: OrderedDict[str, 'Column'] = columnDefinitions
            __primary_key__: Optional['Column'] = _primaryKey

            __schema_name__: str = schemaName
            __table_name__: str = tableName

            __instance_cache__: Dict[Any, 'WrappedClass'] = {}

            def _create(self, conn: 'connection.Connection[Any]', record: Tuple[Any, ...]) -> None:
                kwargs = {}

                for kc, v in zip(WrappedClass.__column_definitions__.items(), record):
                    k, c = kc
                    kwargs[k] = c.type.convertDataFromString(conn, v)

                for k, v in kwargs.items():
                    setattr(self, k, v)

            def __str__(self) -> str:
                dictlike = ', '.join(f'{a}={getattr(self, a)}' for a in self.__column_definitions__.keys())
                return f'{self.__schema_name__}.{self.__table_name__}({dictlike})'

            def __repr__(self) -> str:
                return str(self)

            def __dir__(self) -> List[str]:
                return list(set(dir(type(self)) + list(self.__dict__.keys())))

            @classmethod
            def getColumn(cls, name: str) -> 'Column':
                return cls.__column_definitions__[name]

            @classproperty
            def primaryKeyColumn(cls: Type['DatabaseModel']) -> Optional['Column']:
                return cls.__primary_key__

            @property
            def primaryKey(self) -> Optional[Any]:
                primary = self.primaryKeyColumn
                if primary is None:
                    return None
                return getattr(self, primary.name)

            @classproperty
            def schema(cls: Type['DatabaseModel']) -> str:
                return cls.__schema_name__

            @classproperty
            def table(cls: Type['DatabaseModel']) -> str:
                return cls.__table_name__

            @classproperty
            def columns(cls: Type['DatabaseModel']) -> List['Column']:
                return list(cls.__column_definitions__.values())

            @classmethod
            def createTable(cls, conn: 'connection.Connection[Any]', *, recreateSchema: bool = False,
                            recreateTable: bool = False) -> None:
                for defini in cls.columns:
                    defini.initialize(conn)

                createSchema = sql.SQL(
                    'CREATE SCHEMA IF NOT EXISTS {};'
                ).format(
                    sql.Identifier(schemaName)
                )

                createTable = sql.SQL(
                    'CREATE TABLE IF NOT EXISTS {} ({});'
                ).format(
                    sql.Identifier(schemaName, tableName),
                    sql.SQL(', ').join(
                        [d.columnDefinition for d in cls.columns]
                    )
                )

                with conn.cursor() as cur:
                    if recreateSchema:
                        cur.execute(sql.SQL('DROP SCHEMA IF EXISTS {} CASCADE').format(
                            sql.Identifier(schemaName)
                        ))

                    cur.execute(createSchema)

                    if recreateTable:
                        cur.execute(sql.SQL('DROP TABLE IF EXISTS {} CASCADE').format(
                            sql.Identifier(schemaName, tableName)
                        ))

                    cur.execute(createTable)

            @classmethod
            def instantiateAll(cls, conn: 'connection.Connection[Any]', query: Union[str, 'sql.Composable'] = '') -> Tuple['WrappedClass', ...]:
                return tuple(cls.instantiate(conn, query))

            @classmethod
            def instantiateOne(cls, conn: 'connection.Connection[Any]', query: Union[str, 'sql.Composable'] = '') -> 'WrappedClass':
                return next(cls.instantiate(conn, query))

            @classmethod
            def instantiate(cls, conn: 'connection.Connection[Any]', query: Union[str, 'sql.Composable'] = '') -> \
                    Generator['WrappedClass', None, None]:
                if isinstance(query, sql.Composable):
                    additionalQuery = query
                else:
                    additionalQuery = sql.SQL(query)

                queryStatement = sql.SQL('SELECT ({}) FROM {} {};').format(
                    sql.SQL(', ').join(
                        [sql.Identifier(c.name) for c in cls.columns]
                    ),
                    sql.Identifier(schemaName, tableName),
                    additionalQuery
                )

                with conn.cursor() as cur:
                    cur.execute(queryStatement)

                    record = cur.fetchone()

                    while record is not None:
                        record = record[0]
                        if type(record) != tuple:
                            record = (record,)

                        if cls.__primary_key__ is None:
                            # Abuse duck-typing to get "2 init methods" sort of
                            obj = cls(*argsNames)

                            obj._create(conn, record)

                            record = cur.fetchone()

                            yield obj
                        else:
                            primaryKey = cls.__primary_key__.type.convertDataFromString(conn, record[primaryKeyIndex])

                            if useInstanceCache and primaryKey in cls.__instance_cache__:
                                obj = cls.__instance_cache__[primaryKey]
                            else:
                                obj = cls(*argsNames)

                                obj._create(conn, record)

                            if useInstanceCache:
                                cls.__instance_cache__[primaryKey] = obj

                            record = cur.fetchone()

                            yield obj

            @classmethod
            def instantiateFromPrimaryKey(cls, conn: 'connection.Connection[Any]', primaryKey: Any) -> 'DatabaseModel':
                if cls.__primary_key__ is None:
                    raise PrimaryKeyError(f'Model {cls.__name__} has no primary key to instantiate from')

                if useInstanceCache and primaryKey in cls.__instance_cache__:
                    return cls.__instance_cache__[primaryKey]

                obj = cls.instantiateOne(conn, sql.SQL('WHERE {} = {}').format(
                    sql.Identifier(cls.__primary_key__.name),
                    sql.Literal(primaryKey)
                ))

                if useInstanceCache:
                    cls.__instance_cache__[primaryKey] = obj

                return obj

            def insert(self, conn: 'connection.Connection[Any]', *, doTypeConversion: bool = True) -> 'DatabaseModel':
                if doTypeConversion:
                    data = [c.type.convertInsertableFromData(conn, getattr(self, c.name)) for c in self.columns if c.name in argsNames]
                else:
                    data = [getattr(self, c.name) for c in self.columns if c.name in argsNames]

                allColumns = [sql.Identifier(c.name) for c in self.columns]

                insertStatement = sql.SQL('INSERT INTO {} ({}) VALUES ({}) RETURNING ({});').format(
                    sql.Identifier(schemaName, tableName),
                    sql.SQL(', ').join(
                        [sql.Identifier(c.name) for c in self.columns if c.name in argsNames]
                    ),
                    sql.SQL(', ').join(
                        list(map(sql.Literal, data))
                    ),
                    sql.SQL(', ').join(
                        allColumns
                    )
                )

                with conn.cursor() as cur:
                    cur.execute(insertStatement)

                    # After insertion of this object go back and fill in any defaulted fields
                    record = cast(Tuple[Any], cur.fetchone())[0]

                    if type(record) != tuple:
                        record = (record,)

                    self._create(conn, record)

                    if self.__primary_key__ is not None and useInstanceCache:
                        self.__instance_cache__[self.primaryKey] = self

                return self

            def update(self, conn: 'connection.Connection[Any]', *, doTypeConversion: bool = True) -> 'DatabaseModel':
                primary = self.primaryKeyColumn

                if primary is None:
                    raise PrimaryKeyError('Can not update a database model without a primary key.')

                if doTypeConversion:
                    data = [c.type.convertInsertableFromData(conn, getattr(self, c.name)) for c in self.columns]
                else:
                    data = [getattr(self, c.name) for c in self.columns]

                updateStatement = sql.SQL('UPDATE {} SET ({}) = ({}) WHERE {} = {};').format(
                    sql.Identifier(schemaName, tableName),
                    sql.SQL(', ').join(
                        [sql.Identifier(c.name) for c in self.columns]
                    ),
                    sql.SQL(', ').join(
                        list(map(sql.Literal, data))
                    ),
                    sql.Identifier(primary.name),
                    sql.Literal(self.primaryKey)
                )

                with conn.cursor() as cur:
                    cur.execute(updateStatement)

                return self

            def insertOrUpdate(self, conn: 'connection.Connection[Any]', *, doTypeConversion: bool = True) -> 'DatabaseModel':
                if self.primaryKeyColumn is None:
                    raise PrimaryKeyError('Can not insert/update a database model without a primary key.')

                if self.primaryKey is None:
                    return self.insert(conn, doTypeConversion=doTypeConversion)

                instances = WrappedClass.instantiateAll(conn, sql.SQL('WHERE {} = {}').format(
                    sql.Identifier(self.primaryKeyColumn.name),
                    sql.Literal(self.primaryKey)
                ))

                if len(instances) == 0:
                    return self.insert(conn, doTypeConversion=doTypeConversion)
                else:
                    return self.update(conn, doTypeConversion=doTypeConversion)

            def delete(self, conn: 'connection.Connection[Any]') -> bool:
                if self.primaryKeyColumn is None:
                    raise PrimaryKeyError('Can not delete a database model without a primary key.')

                if self.primaryKey is None:  # Never was in the database so it was "deleted"
                    return True

                deleteStatement = sql.SQL('DELETE FROM {} WHERE {} = {} RETURNING {}').format(
                    sql.Identifier(schemaName, tableName),
                    sql.Identifier(self.primaryKeyColumn.name),
                    sql.Literal(self.primaryKey),
                    sql.Identifier(self.primaryKeyColumn.name)
                )

                with conn.cursor() as cur:
                    cur.execute(deleteStatement)

                    return cur.fetchone() is not None

            def mutate(self, conn: 'connection.Connection[Any]', updateOnExit: bool) -> ContextManager[None]:
                return MutationContext(conn, self, updateOnExit)

        miniLocals: Dict[str, Callable[..., None]] = {}

        # Builds init method
        exec(funcString, {'AUTO_FILLED': AUTO_FILLED}, miniLocals)

        # Ignored because this must be done to set init method properly
        WrappedClass.__init__ = miniLocals['__init__']  # type: ignore

        # Transfer wrapped class data over
        WrappedClass.__module__ = cls.__module__
        WrappedClass.__name__ = cls.__name__
        WrappedClass.__qualname__ = cls.__qualname__
        WrappedClass.__doc__ = cls.__doc__

        return WrappedClass

    return wrapped
