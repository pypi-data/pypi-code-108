


#
# This class implements a data matrix for cells of unspecific type.
#
# TODO: Meanwhile we created an own package jk_datamatrix. Maybe merge this class into that package?
#
#
class DataMatrix(object):

	# ================================================================================================================================
	# ==== Constructor / Destructor
	# ================================================================================================================================

	def __init__(self, nCols:int, nRows:int):
		assert isinstance(nCols, int)
		assert nCols > 0
		assert isinstance(nRows, int)
		assert nRows > 0

		self.__rows = []
		for nRow in range(0, nRows):
			self.__rows.append([ None ] * nCols)

		self.__nRows = nRows
		self.__nCols = nCols
	#

	# ================================================================================================================================
	# ==== Properties
	# ================================================================================================================================

	#
	# Get the number of rows in this matrix.
	#
	# @return	int			Returns the number of rows.
	#
	@property
	def nRows(self) -> int:
		return self.__nRows
	#

	#
	# Get the number of colums in this matrix.
	#
	# @return	int			Returns the number of colums.
	#
	@property
	def nColumns(self) -> int:
		return self.__nCols
	#

	#
	# Get the size of this matrix.
	#
	# @return	tuple<int,int>			Returns the number of colums and rows (in this order).
	#
	@property
	def size(self) -> tuple:
		return self.__nCols, self.__nRows
	#

	# ================================================================================================================================
	# ==== Methods
	# ================================================================================================================================

	#
	# Append a matrix to the right of this matrix. For this to succeed both matrixes must have the same number of rows.
	#
	# @param	DataMatrix matrix		Another data matrix of the same height.
	#
	def appendMatrixToRight(self, matrix):
		assert isinstance(matrix, DataMatrix)
		assert matrix.__nRows == self.__nRows

		for rowIndex in range(self.__nRows):
			self.__rows[rowIndex].extend(matrix.__rows[rowIndex])
		self.__nCols += matrix.__nCols
	#

	#
	# Append a matrix to the bottom of this matrix. For this to succeed both matrixes must have the same number of columns.
	#
	# @param	DataMatrix matrix		Another data matrix of the same width.
	#
	def appendMatrixBelow(self, matrix):
		assert isinstance(matrix, DataMatrix)
		assert matrix.__nCols == self.__nCols

		self.__rows.extend([ list(r) for r in matrix.__rows])
		self.__nRows += matrix.__nRows
	#

	#
	# Remove a specific row.
	#
	# @param	int rowIndex		The index of the row to remove.
	#
	def removeRow(self, rowIndex:int):
		assert isinstance(rowIndex, int)
		if rowIndex < 0:
			rowIndex = self.__nRows + rowIndex

		del self.__rows[rowIndex]
		self.__nRows -= 1
	#

	#
	# Get the value of a specific cell.
	#
	def get(self, rowIndex:int, colIndex:int):
		if rowIndex < 0:
			rowIndex = self.__nRows + rowIndex
		if colIndex < 0:
			colIndex = self.__nCols + colIndex
		try:
			return self.__rows[rowIndex][colIndex]
		except IndexError as ee:
			self.dump()
			raise IndexError(str(ee) + " :: " + repr((rowIndex, colIndex)))
	#

	#
	# Set the value of a specific cell.
	#
	def set(self, rowIndex:int, colIndex:int, value):
		if rowIndex < 0:
			rowIndex = self.__nRows + rowIndex
		if colIndex < 0:
			colIndex = self.__nCols + colIndex
		try:
			self.__rows[rowIndex][colIndex] = value
		except IndexError as ee:
			self.dump()
			raise IndexError(str(ee) + " :: " + repr((rowIndex, colIndex)))
	#

	#
	# Add a row to the top of this matrix.
	#
	# @param	object content		(optional) An arbitrary object. The new row will be filled with references to the specified object.
	#
	def addRowAtTop(self, content = None):
		data = [ content for i in range(0, self.__nCols) ]
		self.__rows.insert(0, data)
		self.__nRows += 1
	#

	#
	# Add a row at the bottom of this matrix.
	#
	# @param	object content		(optional) An arbitrary object. The new row will be filled with references to the specified object.
	#
	def addRowAtBottom(self, content = None):
		data = [ content for i in range(0, self.__nCols) ]
		self.__rows.append(data)
		self.__nRows += 1
	#

	#
	# Add a column to the right of this matrix.
	#
	# @param	object content		(optional) An arbitrary object. The new column will be filled with references to the specified object.
	#
	def addColumnAtRight(self, content = None):
		for nRowIndex in range(0, self.__nRows):
			self.__rows[nRowIndex].append(content)
		self.__nCols += 1
	#

	#
	# Add a column to the left of this matrix.
	#
	# @param	object content		(optional) An arbitrary object. The new column will be filled with references to the specified object.
	#
	def addColumnAtLeft(self, content = None):
		for nRowIndex in range(0, self.__nRows):
			self.__rows[nRowIndex].insert(0, content)
		self.__nCols += 1
	#

	#
	# Get a copy of the data row by row as a two-dimensional array where the rows are returned as an immutable tuple.
	#
	def getRowTuple(self) -> tuple:
		return tuple([ tuple(row) for row in self.__rows ])
	#

	#
	# Get a copy of the data row by row as a two-dimensional array where the rows are returned as a list.
	#
	def getRowList(self) -> list:
		return [ list(row) for row in self.__rows ]
	#

	def dump(self):
		print(self.__nRows, "x", self.__nCols)
		for nRowIndex in range(0, self.__nRows):
			print("\t", nRowIndex, "::", len(self.__rows[nRowIndex]), str(self.__rows[nRowIndex]))
	#

#


