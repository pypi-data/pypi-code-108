class Query:
	def __init__(self):
		self.query = ""
		self.table = None
		self.values = None
		self.names = None

	def generate(self, table):
		if self.table is None:
			self.table = table

		self.query = f"INSERT INTO {table.name}({', '.join(self.__generateColumnNames(table))}) VALUES ({self.__generateValues(table)});"

		self.query = self.query.replace("[", "")
		self.query = self.query.replace("]", "")

		return self.query

	def __generateColumnNames(self, table):
		self.names = []
		for i in table.columns:
			self.names.append(i.name)
		return self.names

	@DeprecationWarning
	def __enumerateColumns(self, table):
		names = ""
		for i in range(1, table.columns.__len__() + 1):
			names += f"${i},"
		names = names[:-1]
		return names

	def __generateValues(self, table):
		self.values = []
		for column in table.columns:
			self.values.append(column.generate())
		return self.values