


from .MutableString import *




class TextCanvas(object):

	def __init__(self, width = 0):
		self.__rows = []
		self.__width = width
		self.__height = 0
	#

	def _newLine(self):
		self.__rows.append(MutableString(width = self.__width))
		self.__height += 1
	#

	def ensureSize(self, w, h):
		if w > self.__width:
			for i in range(0, self.__height):
				self.__rows[i].ensureWidth(w)
			self.__width = w
		while self.__height < h:
			self._newLine()
	#

	def drawRectangle(self, x1, y1, x2, y2, bDoubleBorderTop = False, bDoubleBorderBottom = False):
		assert isinstance(x1, int)
		assert isinstance(y1, int)
		assert isinstance(x2, int)
		assert isinstance(y2, int)

		self.ensureSize(x2 + 1, y2 + 1)
		for x in range(x1, x2):
			self.__rows[y1].setChar(x, "=" if bDoubleBorderTop else "-")
			self.__rows[y2].setChar(x, "=" if bDoubleBorderBottom else "-")
		for y in range(y1, y2):
			self.__rows[y].setChar(x1, "|")
			self.__rows[y].setChar(x2, "|")
		self.__rows[y1].setChar(x1, "+")
		self.__rows[y1].setChar(x2, "+")
		self.__rows[y2].setChar(x1, "+")
		self.__rows[y2].setChar(x2, "+")
	#

	def drawRectangleEx(self, x1, y1, x2, y2, charBorderTop = "-", charBorderRight = "|", charBorderBottom = "-", charBorderLeft = "|"):
		assert isinstance(x1, int)
		assert isinstance(y1, int)
		assert isinstance(x2, int)
		assert isinstance(y2, int)

		self.ensureSize(x2 + 1, y2 + 1)
		for x in range(x1, x2):
			self.__rows[y1].setChar(x, charBorderTop)
			self.__rows[y2].setChar(x, charBorderBottom)
		for y in range(y1, y2):
			self.__rows[y].setChar(x1, charBorderLeft)
			self.__rows[y].setChar(x2, charBorderRight)

		if (charBorderLeft != " ") or (charBorderRight != " "):
			self.__rows[y1].setChar(x1, "+")	# top left
		if (charBorderRight != " ") or (charBorderRight != " "):
			self.__rows[y1].setChar(x2, "+")	# top right
		if (charBorderLeft != " ") or (charBorderBottom != " "):
			self.__rows[y2].setChar(x1, "+")	# bottom left
		if (charBorderRight != " ") or (charBorderBottom != " "):
			self.__rows[y2].setChar(x2, "+")	# bottom right
	#

	def drawTextLines(self, x, y, textLines):
		assert isinstance(x, int)
		assert isinstance(y, int)
		assert isinstance(textLines, list)

		maxW = 0
		for textLine in textLines:
			if len(textLine) > maxW:
				maxW = len(textLine)
		self.ensureSize(x + maxW + 1, y + len(textLines) + 1)

		for textLine in textLines:
			self.__rows[y].setText(x, textLine)
			y += 1
	#

	def drawText(self, x, y, textLine):
		assert isinstance(x, int)
		assert isinstance(y, int)
		assert isinstance(textLine, str)

		self.ensureSize(x + len(textLine) + 1, y + 1)

		self.__rows[y].setText(x, textLine)
	#

	def print(self, printFunction = None):
		if printFunction is None:
			printFunction = print
		else:
			assert callable(printFunction)

		for line in self.__rows:
			printFunction(str(line))
	#

	def toTextLines(self, prefix = None, bRightStrip = True):
		if prefix is None:
			prefix = ""

		ret = []
		for line in self.__rows:
			s = prefix + str(line)
			if bRightStrip:
				s = s.rstrip()
			ret.append(s)
		return ret
	#

	def toString(self, prefix = None, bRightStrip = True):
		if prefix is None:
			prefix = ""

		ret = ""
		for line in self.__rows:
			s = prefix + str(line)
			if bRightStrip:
				s = s.rstrip()
			ret += s + "\n"
		return ret
	#

	def __str__(self):
		return self.toString()
	#

	def __repr__(self):
		return "TextCanvas(width=" + str(self.__width) + ", height=" + str(self.__height) + ")"
	#

#












