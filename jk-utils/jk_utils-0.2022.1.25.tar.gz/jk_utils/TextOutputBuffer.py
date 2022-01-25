



class TextOutputBuffer(object):

	def __init__(self):
		self.__buf = []
	#

	@property
	def lastWasNewLine(self) -> bool:
		if self.__buf:
			return self.__buf[-1].endswith("\n")
		else:
			return True
	#

	def writeLn(self, *args):
		for a in args:
			self.__buf.append(str(a))
		self.__buf.append("\n")
	#

	def write(self, *args):
		for a in args:
			self.__buf.append(str(a))
	#

	def writeNewLines(self, n:int):
		for i in range(0, n):
			self.__buf.append("\n")
	#

	def writeNewLine(self):
		self.__buf.append("\n")
	#

	def __str__(self):
		return "".join(self.__buf)
	#

	def loadFromFile(self, filePath:str):
		with open(filePath, "r") as fin:
			self.__buf = [
				(x + "\n") for x in fin.read().split("\n")
			]
	#

	def saveToFile(self, filePath:str, encoding:str = None):
		with open(filePath, "w", encoding=encoding) as fout:
			fout.write(str(self))
	#

	@staticmethod
	def createFromFile(filePath:str):
		ret = TextOutputBuffer()
		ret.loadFromFile(filePath)
		return ret
	#

#





