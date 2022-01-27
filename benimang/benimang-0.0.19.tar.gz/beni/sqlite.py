# import sqlite3
# from pathlib import Path
# from typing import Any, Iterable

# import aiosqlite


# class SqliteConn():

#     default_db_file: str | Path = ':memory:'

#     def __init__(self, db_file: str | Path | None = None):
#         self._db_file = db_file or SqliteConn.default_db_file

#     async def __aenter__(self):
#         self.db = await aiosqlite.connect(self._db_file)
#         self.db.row_factory = sqlite3.Row
#         return self

#     async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
#         if self.db:
#             if exc_type:
#                 await self.db.rollback()
#             else:
#                 await self.db.commit()
#             await self.db.close()

#     async def insert(self, table: str, data: dict[str, Any]):
#         keylist = sorted(data.keys())
#         fieldname_list = ','.join([f'`{x}`' for x in keylist])
#         placement_list = ','.join(['?' for _ in range(len(keylist))])
#         fieldvalue_list = [data[x] for x in keylist]
#         async with self.db.execute(
#             f'''
#             INSERT INTO "{table}" ({fieldname_list}) 
#             VALUES 
#                 ({placement_list});
#             ''',
#             fieldvalue_list,
#         ) as cursor:
#             return cursor.lastrowid

#     async def insert_many(self, table: str, data_list: list[dict[str, Any]]):
#         keylist = sorted(data_list[0].keys())
#         fieldname_list = ','.join([f'`{x}`' for x in keylist])
#         placement_list = ','.join(['?' for _ in range(len(keylist))])
#         fieldvalue_list = [[data[x] for x in keylist] for data in data_list]
#         cursor = await self.db.executemany(
#             f'''
#             INSERT INTO "{table}" ({fieldname_list}) 
#             VALUES 
#                 ({placement_list});
#             ''',
#             fieldvalue_list
#         )
#         await cursor.close()

#     async def fetch_all(self, sql: str, parameters: Iterable[Any] | None = None):
#         async with self.db.execute(sql, parameters) as cursor:
#             return await cursor.fetchall()

#     async def fetch_one(self, sql: str, parameters: Iterable[Any] | None = None):
#         async with self.db.execute(sql, parameters) as cursor:
#             return await cursor.fetchone()

#     async def execute(self, sql: str, parameters: Iterable[Any] | None = None):
#         async with self.db.execute(sql, parameters) as cursor:
#             return cursor.rowcount
