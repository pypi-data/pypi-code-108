


class MutableString(object):

	def __init__(self, text = "", width = None):
		self.__text = text
		if width != None:
			self.ensureWidth(width)
	#

	def ensureWidth(self, w):
		while len(self.__text) < w:
			self.__text += " "
	#

	def __len__(self):
		return len(self.__text)
	#

	def __str__(self):
		return self.__text
	#

	def __repr__(self):
		return self.__text
	#

	def __eq__(self, other):
		if isinstance(other, str):
			return self.__text == other
		elif isinstance(other, MutableString):
			return self.__text == other.__text
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, str):
			return self.__text != other
		elif isinstance(other, MutableString):
			return self.__text != other.__text
		else:
			return True
	#

	def setChar(self, x, char):
		self.ensureWidth(x + 1)
		self.__text = self.__text[0:x] + char[0] + self.__text[x+1:]
	#

	def setText(self, x, textString):
		self.ensureWidth(x + len(textString))
		self.__text = self.__text[0:x] + textString + self.__text[x+len(textString):]
	#

#








