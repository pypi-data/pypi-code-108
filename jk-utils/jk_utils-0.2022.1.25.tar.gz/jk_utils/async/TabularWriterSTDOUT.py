




class TabularWriterSTDOUT(object):

	def __init__(self, columns:list, colWidth:int):
		self.__columns = columns
		self.__colWidth = colWidth

		s = ""
		self.__proto = []
		for i in range(0, len(columns)):
			self.__proto.append("-")
			n = i * colWidth
			while len(s) < n:
				s += " "
			s += columns[i]
		print(s)

		n = len(columns) * colWidth
		print("=" * n)

		self.__separator = "- " * (n // 2)
	#

	def print(self, column:str, text:str):
		outList = list(self.__proto)
		outList[self.__columns.index(column)] = text

		s = ""
		for item in outList:
			while len(item) < self.__colWidth:
				item += " "
			s += item
		print(s)

		print(self.__separator)
	#

	def close(self):
		pass
	#

#






