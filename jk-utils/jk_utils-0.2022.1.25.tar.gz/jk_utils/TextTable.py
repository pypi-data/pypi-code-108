


from .MutableString import *
from .TextCanvas import *







#
# This object represents a table cell
#
class TextTableCell(object):

	def __init__(self, x, y, colSpan, rowSpan, textLines):
		assert isinstance(textLines, list)
		assert isinstance(colSpan, int)
		assert isinstance(rowSpan, int)
		assert x >= 0
		assert y >= 0
		assert colSpan >= 1
		assert rowSpan >= 1

		self.__x = x
		self.__y = y
		self.__textLines = textLines
		self.__maxTextWidth = 0
		for line in textLines:
			assert isinstance(line, str)
			if len(line) > self.__maxTextWidth:
				self.__maxTextWidth = len(line)
		self.__colSpan = colSpan
		self.__rowSpan = rowSpan
	#

	#
	# Tests if the specified position is covered by this cell. This method is useful especially for cells that span across multiple cells as this method
	# will return the correct results even in this case.
	#
	# @return		bool		Returns <c>True</c> or <c>False</c> wether the specified coordinates are covered by this cell or not.
	#
	def coversXY(self, x, y):
		return (x >= self.__x) and (x < self.__x + self.__colSpan) and (y >= self.__y) and (y < self.__y + self.__rowSpan)
	#

	def __repr__(self):
		s = ""
		for line in self.__textLines:
			s += "\n"
			s += line
		s = s[1:]
		if len(s) > 20:
			s = s[:20]
			s += "..."
		return "{ " + str(self.__x) + "," + str(self.__y) + " - " + str(self.__colSpan) + "," + str(self.__rowSpan) + " - " + repr(s) + " }"
	#

	def __str__(self):
		return self.__repr__()
	#

	#
	# The text lines stored in this cell
	#
	@property
	def textLines(self):
		return self.__textLines
	#

	#
	# The width the cell requires
	#
	@property
	def innerWidth(self):
		return self.__maxTextWidth
	#

	#
	# The height the cell requires
	#
	@property
	def innerHeight(self):
		return len(self.__textLines)
	#

	@property
	def x(self):
		return self.__x
	#

	@property
	def y(self):
		return self.__y
	#

	@property
	def rowSpan(self):
		return self.__rowSpan
	#

	@property
	def colSpan(self):
		return self.__colSpan
	#

#




#
# This class represents a table, which actually is a grid of cells. Text is organized in lines.
# After text has been added to the table you get it printed to an instance of <c>TextCanvas</c>
# which in turn can then be printed to STDOUT.
#
class TextTable(object):

	class __RowCreator(object):
		def __init__(self, table, rowNo):
			self.table = table
			self.rowNo = rowNo
			self.__pos = 0
		#
		def createCell(self, textLines, colSpan = 1, rowSpan = 1):
			while self.table.getCell(self.__pos, self.rowNo) != None:
				self.__pos += 1
			self.table.setCell(self.__pos, self.rowNo, textLines, colSpan, rowSpan)
			self.__pos += colSpan
			return self
		#
	#

	def __init__(self):
		self.__rows = []
		self.__countColumns = 0
		self.__headingRows = set()
	#

	def setHeadingRow(self, rowNo):
		self.__headingRows.add(rowNo)
	#

	def ensureSize(self, w, h):
		while len(self.__rows) < h:
			self.__rows.append([])
		self.__countColumns = max(w, self.__countColumns)
		for row in self.__rows:
			while len(row) < self.__countColumns:
				row.append(None)
	#

	def numberOfRows(self):
		return len(self.__rows)
	#

	def numberOfColumns(self):
		return self.__countColumns
	#

	def setCell(self, x, y, textLines, colSpan = 1, rowSpan = 1):
		if isinstance(textLines, str):
			textLines = [ textLines ]
		elif isinstance(textLines, list):
			pass
		else:
			raise Exception("Invalid data for text lines specified!")

		self.ensureSize(x + colSpan, y + rowSpan)
		self.__rows[y][x] = TextTableCell(x, y, colSpan, rowSpan, textLines)

		for ix in range(x, x + colSpan):
			for iy in range(y, y + rowSpan):
				if (ix != x) and (iy != y):
					self.__rows[y][x] = None
	#

	@staticmethod
	def __calcSpans(valueList, ofs, len):
		n = 0
		for i in range(ofs, ofs + len):
			n += valueList[ofs]
		return n
	#

	def _calcRowHeights(self):
		rowHeights = []
		numberOfRows = len(self.__rows)

		# get height of all cells that do not span across multiple cells

		multiRowCells = []
		for i in range(0, numberOfRows):
			rowHeights.append(0)
			row = self.__rows[i]
			for cell in row:
				if cell is None:
					continue
				if cell.rowSpan == 1:
					h = cell.innerHeight
					if h > rowHeights[i]:
						rowHeights[i] = h
				else:
					# collect the cells we need to deal with later
					multiRowCells.append(cell)

		# now make room for all cells spanning across multiple cells

		for cell in multiRowCells:
			currentHeightAvailable = TextTable.__calcSpans(rowHeights, cell.y, cell.rowSpan)	# get cell height
			currentHeightAvailable += cell.rowSpan - 1	# add intermediate borders
			# currentHeightAvailable is now the amount of height this cell can cover (without outer border)
			heightRequired = cell.innerHeight
			# heightRequired will contain the height the cell will need
			while currentHeightAvailable < heightRequired:
				# expand all heights by 1
				for i in range(0, cell.rowSpan):
					rowHeights[i] += 1
					currentHeightAvailable += 1

		return rowHeights
	#

	def _calcColumnWidths(self, extraHGapLeft, extraHGapRight):
		columnWidths = []
		numberOfRows = len(self.__rows)

		# get width of all cells that do not span across multiple cells

		#print("countColumns=" + str(self.__countColumns))
		for i in range(0, self.__countColumns):
			columnWidths.append(0)
		#print("columnWidths=" + str(columnWidths))
		#print("numberOfRows=" + str(numberOfRows))

		multiRowCells = []
		for i in range(0, numberOfRows):
			row = self.__rows[i]
			#print(str(i) + "\t" + str(row))
			j = -1
			for cell in row:
				j += 1
				if cell is None:
					continue
				if cell.colSpan == 1:
					w = cell.innerWidth + extraHGapLeft + extraHGapRight
					if w > columnWidths[j]:
						columnWidths[j] = w
				else:
					# collect the cells we need to deal with later
					multiRowCells.append(cell)

		# now make room for all cells spanning across multiple cells

		for cell in multiRowCells:
			currentWidthAvailable = TextTable.__calcSpans(columnWidths, cell.x, cell.colSpan)	# get cell width
			currentWidthAvailable += cell.colSpan - 1	# add intermediate borders
			# currentWidthAvailable is now the amount of height this cell can cover (without outer border)
			widthRequired = cell.innerWidth
			# widthRequired will contain the width the cell will need
			while currentWidthAvailable < widthRequired:
				# expand all widths by 1
				for i in range(0, cell.colSpan):
					columnWidths[i] += 1
					currentWidthAvailable += 1

		return columnWidths
	#

	def paintToTextCanvas(self, textCanvas = None, extraHGapLeft = 1, extraHGapRight = 1, bCompact = False):
		if textCanvas is None:
			textCanvas = TextCanvas()

		if bCompact:
			self.__paintToTextCanvasNoBorders(textCanvas, extraHGapLeft, extraHGapRight)
		else:
			self.__paintToTextCanvasWithBorders(textCanvas, extraHGapLeft, extraHGapRight)

		return textCanvas
	#

	def __paintToTextCanvasWithBorders(self, textCanvas, extraHGapLeft, extraHGapRight):
		columnWidths = self._calcColumnWidths(extraHGapLeft, extraHGapRight)
		xPositions = [ 0 ]
		for w in columnWidths:
			xPositions.append(xPositions[-1] + w + 1)

		rowHeights = self._calcRowHeights()
		yPositions = [ 0 ]
		for h in rowHeights:
			yPositions.append(yPositions[-1] + h + 1)

		#print("columnWidths=" + str(columnWidths))
		#print("xPositions=" + str(xPositions))
		#print("rowHeights=" + str(rowHeights))
		#print("yPositions=" + str(yPositions))

		textCanvas.ensureSize(xPositions[-1] + 1, yPositions[-1] + 1)

		for row in self.__rows:
			for cell in row:
				if cell is None:
					continue
				x1 = xPositions[cell.x]
				y1 = yPositions[cell.y]
				x2 = xPositions[cell.x + cell.colSpan]
				y2 = yPositions[cell.y + cell.rowSpan]
				textCanvas.drawRectangle(
					x1, y1, x2, y2,
					bDoubleBorderTop = (cell.y - 1) in self.__headingRows)
				textCanvas.drawTextLines(x1 + 1 + extraHGapLeft, y1 + 1, cell.textLines)

		return textCanvas
	#

	def __paintToTextCanvasNoBorders(self, textCanvas, extraHGapLeft, extraHGapRight):
		columnWidths = self._calcColumnWidths(extraHGapLeft, extraHGapRight)
		xPositions = [ 0 ]
		for w in columnWidths:
			xPositions.append(xPositions[-1] + w + 1)

		rowHeights = self._calcRowHeights()
		yPositions = [ 0 ]
		for h in rowHeights:
			yPositions.append(yPositions[-1] + h)

		#print("columnWidths=" + str(columnWidths))
		#print("xPositions=" + str(xPositions))
		#print("rowHeights=" + str(rowHeights))
		#print("yPositions=" + str(yPositions))

		textCanvas.ensureSize(xPositions[-1] + 1, yPositions[-1] + 1)

		for row in self.__rows:
			for cell in row:
				if cell is None:
					continue
				x1 = xPositions[cell.x]
				y1 = yPositions[cell.y]
				x2 = xPositions[cell.x + cell.colSpan]
				y2 = yPositions[cell.y + cell.rowSpan]
				textCanvas.drawTextLines(x1 + 1 + extraHGapLeft, y1 + 1, cell.textLines)

		return textCanvas
	#

	def createRow(self, bIsHeading = False):
		n = len(self.__rows)
		if bIsHeading:
			self.__headingRows.add(n)
		self.ensureSize(self.__countColumns, n + 1)
		return TextTable.__RowCreator(self, n)
	#

	#
	# Get the cell at position (x, y). This method is useful especially for cells that span across multiple cells as this method
	# will return the apropriate table cell even in this case.
	#
	def getCell(self, x, y):
		if (y >= len(self.__rows)) or (x >= self.__countColumns):
			return None
		iy = y
		while iy >= 0:
			ix = x
			while ix >= 0:
				cell = self.__rows[iy][ix]
				if cell != None:
					if cell.coversXY(x, y):
						return cell
				ix -= 1
			iy -= 1
		return None
	#

	def print(self, bCompact = False, printFunction = None):
		textCanvas = self.paintToTextCanvas(extraHGapLeft = 1, extraHGapRight = 1, bCompact = bCompact)
		textCanvas.print(printFunction = printFunction)
	#

	def dump(self, printFunction = None):
		if printFunction is None:
			printFunction = print
		else:
			assert callable(printFunction)

		printFunction("TextTable(")
		printFunction("\tcountColumns=" + str(self.__countColumns))
		printFunction("\tcountRows=" + str(len(self.__rows)))
		printFunction("\theadingRows=" + str(self.__headingRows))
		printFunction("\trows=[")
		i = 0
		for row in self.__rows:
			printFunction("\t\t" + str(i) + "\t" + str(row))
			i += 1
		printFunction("\t]")
		printFunction(")")
	#

#








