




class TabularWriterMediaWiki(object):

	def __init__(self, columns:list):
		self.__columns = columns

		print("{| class=\"wikitable\"")
		print("|-")
		print("!" + " !! ".join(columns))

		self.__proto = [ "" for x in columns ]
	#

	def print(self, column:str, text:str):
		outList = list(self.__proto)
		outList[self.__columns.index(column)] = text

		print("|-")
		print(("|" + " || ".join(outList)).replace("  ", " "))
	#

	def close(self):
		print("|}")
	#

#







