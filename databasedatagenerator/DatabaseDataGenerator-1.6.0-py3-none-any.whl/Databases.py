from .Table import *
from .Query import *
from tqdm import tqdm

class Database:
	def __init__(self):
		self.__connection = None


class PostgreSQLDB(Database):
	import postgresql
	global postgresql

	def __init__(self, override=False, wipe=False):
		self.__connection = None
		self.__table = None
		self.__wipe = wipe
		self.__override = override

	def connect(self, user="demo", password="demo", ip="127.0.0.1",
				port="5432", dbName="demo"):
		self.__connection = postgresql.open(
			f'pq://{user}:{password}@{ip}:{port}/{dbName}')

	def wipeTable(self, table: Table):
		self.__connection.execute(f"DELETE FROM {table.name} *;")

	def insertRow(self):
		query = self.__generateQuery()
		try:
			self.__connection.execute(query.query)
		except postgresql.exceptions.UniqueError:
			if self.__override:
				pkColumn = query.table.getPkColumnName()
				pk = query.values[query.names.index(pkColumn)]
				self.__connection.execute(
					f"DELETE FROM {query.table.name} WHERE {pkColumn}={pk};")
				self.__connection.execute(query.query)
		return

	def insertRows(self, table, numRows):
		self.setTable(table)
		query = self.__generateBigQuery(numRows)
		self.__connection.execute(query.query)

	def __generateBigQuery(self, rows):
		query = Query()
		query.generateBig(self.__table, rows)
		return query

	def __generateQuery(self):
		query = Query()
		query.generate(self.__table)
		return query

	def getPkSet(self, table: Table):
		test = self.__connection.prepare(
			f"SELECT {table.getPkColumnName()} FROM {table.name}")
		arr = test()
		arr = [i[0] for i in arr]
		return set(arr)

	def setTable(self, table: Table):
		self.__table = table
		if self.__wipe:
			self.wipeTable(table)


class Sqlite3DB(Database):
	import sqlite3
	global sqlite3

	def __init__(self, override=False, wipe=False):
		self.__connection = None
		self.__cursor = None
		self.__table = None
		self.__wipe = wipe
		self.__override = override

	def connect(self, dbName="demo.db"):
		self.__connection = sqlite3.connect(dbName)
		self.__cursor = self.__connection.cursor()

	def wipeTable(self, table: Table):
		self.__cursor.execute(f"DELETE FROM {table.name};")
		self.__connection.commit()

	@DeprecationWarning
	def insertRow(self):
		query = self.__generateQuery()
		# try:
		self.__cursor.execute(query.query)
		self.__connection.commit()
		# 	TODO: Fix exception
		# except postgresql.exceptions.UniqueError:
		# 	if self.__override:
		# 		pkColumn = query.table.getPkColumnName()
		# 		pk = query.values[query.names.index(pkColumn)]
		# 		self.__cursor.execute(
		# 			f"DELETE FROM {query.table.name} WHERE {pkColumn}={pk};")
		# 		self.__connection.commit()
		# 		self.__cursor.execute(query.query)
		# 		self.__connection.commit()
		return

	def insertRows(self, table, numRows):
		self.setTable(table)
		query = self.__generateBigQuery(numRows)
		self.__cursor.execute(query.query)
		self.__connection.commit()

	def __generateQuery(self):
		query = Query()
		query.generate(self.__table)
		return query

	def __generateBigQuery(self, rows):
		query = Query()
		query.generateBig(self.__table, rows)
		return query

	def getPkSet(self, table: Table):
		# TODO: add exception for no pk found
		arr = []
		for row in self.__cursor.execute(
			f"SELECT {table.getPkColumnName()} FROM {table.name}"):
			arr.append(row[0])
		return set(arr)

	def setTable(self, table: Table):
		self.__table = table
		if self.__wipe:
			self.wipeTable(table)
