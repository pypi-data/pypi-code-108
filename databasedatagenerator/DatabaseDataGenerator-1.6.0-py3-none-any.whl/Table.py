from .Column import *
from .CSVReader import *

class Table:
	def __init__(self, name):
		self.name = name
		self.columns = []

	def addColumn(self, column: Column):
		self.columns.append(column)

	def addColumns(self, columns):
		for i in columns:
			self.addColumn(i)

	def getPkColumnName(self):
		for i in self.columns:
			if i.pk:
				return i.name
		return ""

	def fromCsv(self, filename):
		csvreader = CSVReader(self)
		csvreader.read(filename)
		pass