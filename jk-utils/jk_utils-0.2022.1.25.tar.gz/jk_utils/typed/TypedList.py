

import typing

from ..ImplementationError import ImplementationError






class TypedList(list):

	################################################################################################################################
	## Constructors
	################################################################################################################################

	def __init__(self, items = None, dataType:type = None, checkDataTypeCallback = None, keyFunc = None):
		tempList = tuple(items) if (items is not None) else None

		super().__init__()

		if (dataType is None) and (checkDataTypeCallback is None):
			raise Exception("On construction either specify a data type or a callback that verifies the data type!")

		self.__nCompareWith = -1

		if dataType is not None:
			assert isinstance(dataType, type)
			self.__nCompareWith = 1
		self.__dataType = dataType
		self.__checkDataType = self.__default_checkValue

		if checkDataTypeCallback is not None:
			assert callable(checkDataTypeCallback)
			self.__nCompareWith = 2
			self.__checkDataType = checkDataTypeCallback

		if keyFunc is not None:
			assert callable(keyFunc)
		self.__keyFunc = keyFunc

		if tempList is not None:
			for item in tempList:
				self.__checkDataType(item)
			super().extend(tempList)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def dataType(self) -> type:
		return self.__dataType
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __default_checkValue(self, item) -> bool:
		return isinstance(item, self.__dataType)
	#

	def __checkDataTypeE(self, item):
		if not self.__checkDataType(item):
			raise TypeError(repr(item) + " (" + type(item).__name__ + ")")
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def append(self, item):
		self.__checkDataTypeE(item)
		super().append(item)
	#

	def extend(self, iterable):
		tempList = tuple(iterable)
		for item in tempList:
			self.__checkDataTypeE(item)
		super().extend(tempList)
	#

	def insert(self, index:int, item):
		self.__checkDataTypeE(item)
		super().insert(index, item)
	#

	def sort(self, reverse:bool = False):
		super().sort(key=self.__keyFunc, reverse=reverse)
	#

	def copy(self):
		return TypedList(
			items = self,
			dataType = self.__dataType,
			checkDataTypeCallback = self.__checkDataType,
			keyFunc = self.__keyFunc,
		)
	#

	def clone(self):
		return TypedList(
			items = self,
			dataType = self.__dataType,
			checkDataTypeCallback = self.__checkDataType,
			keyFunc = self.__keyFunc,
		)
	#

	def isCompatibleSequence(self, sequence) -> bool:
		for item in sequence:
			if not self.__checkDataType(item):
				return False
		return True
	#

	def isCompatibleSequenceE(self, sequence) -> bool:
		for item in sequence:
			if not self.__checkDataType(item):
				raise TypeError("Sequence contains values of incompatible type!")
		return True
	#

	def isCompatibleCollection(self, otherList) -> bool:
		if isinstance(otherList, TypedList):
			if self.__nCompareWith != otherList.__nCompareWith:
				return False

			if self.__nCompareWith == 1:
				if self.__dataType != otherList.__dataType:
					return False
			elif self.__nCompareWith == 2:
				if self.__checkDataType != otherList.__checkDataType:
					return False
			else:
				raise ImplementationError()

			return True
		else:
			return False
	#

	def isCompatibleCollectionE(self, otherList):
		if isinstance(otherList, TypedList):
			if self.__nCompareWith != otherList.__nCompareWith:
				raise TypeError("Other list is of incompatible type!")

			if self.__nCompareWith == 1:
				if self.__dataType != otherList.__dataType:
					raise TypeError("Other list is of incompatible type!")
			elif self.__nCompareWith == 2:
				if self.__checkDataType != otherList.__checkDataType:
					raise TypeError("Other list is of incompatible type!")
			else:
				raise TypeError("Other list is of incompatible type!")

			return

		raise TypeError("Other list is of incompatible type!")
	#

	def __add__(self, otherList):
		if self.isCompatibleCollection(otherList):
			ret = self.clone()
			ret.extend(otherList)
			return ret

		if isinstance(otherList, (tuple,list)):
			if self.isCompatibleSequence(otherList):
				ret = self.clone()
				ret.extend(otherList)
				return ret
			else:
				return NotImplemented

		return NotImplemented
	#

	def __iadd__(self, otherList):
		if self.isCompatibleCollection(otherList):
			self.extend(otherList)
			return self

		if isinstance(otherList, (tuple,list)):
			if self.isCompatibleSequence(otherList):
				self.extend(otherList)
				return self
			else:
				return NotImplemented

		return NotImplemented
	#

	def __mul__(self, n):
		if not isinstance(n, int):
			return NotImplemented

		items = super().__mul__(n)
		return TypedList(
			items = items,
			dataType = self.__dataType,
			checkDataTypeCallback = self.__checkDataType,
			keyFunc = self.__keyFunc,
		)
	#

	def __rmul__(self, n):
		if not isinstance(n, int):
			return NotImplemented

		items = super().__mul__(n)
		return TypedList(
			items = items,
			dataType = self.__dataType,
			checkDataTypeCallback = self.__checkDataType,
			keyFunc = self.__keyFunc,
		)
	#

	def __imul__(self, n):
		if not isinstance(n, int):
			return NotImplemented

		items = super().__mul__(n)
		self.clear()
		super().extend(items)
	#

	def __setitem__(self, ii, item):
		assert isinstance(ii, int)
		self.__checkDataTypeE(item)
		super().__setitem__(ii, item)
	#

	"""
	All necessary methods have been implemented, except:
	* __reduce__()
	* __reduce_ex__()
	"""

#





