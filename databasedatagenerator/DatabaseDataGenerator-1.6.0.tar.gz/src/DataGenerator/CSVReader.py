from .Column import *
from .Generators import *
import itertools

class CSVReader:
	def __init__(self, table):
		# Table: table also not working...
		self.__table = table
		self.__data = None

	def read(self, filename):
		with open(filename, 'r') as f:
			data = f.readlines()

		self.__data = data[1:]
		self.__data = self.__csvToList()
		self.__data = self.__transpose()
		self.__addColumns(data[0])
		return

	def __csvToList(self):
		arr = []
		for item in self.__data:
			item = item.replace("\n", "")
			item = item.split(",")
			# Casting to int/float might be necessary
			# self.__castItems(item)
			arr.append(item)
		return arr

	def __transpose(self):
		transArr = list(zip(*self.__data))
		return transArr

	def __addColumns(self, header):
		header = header.replace("\n", "")
		columns = header.split(",")
		for i, column in enumerate(columns):
			tempC = Column(column, SequentialSetGenerator(self.__data[i]))
			self.__table.addColumn(tempC)
		return