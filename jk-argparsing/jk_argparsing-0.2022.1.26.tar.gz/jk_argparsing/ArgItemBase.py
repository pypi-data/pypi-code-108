	


import os
import re
import typing

from .EnumParameterType import EnumParameterType
from .OptionParameter import OptionParameter






class ArgItemBase(object):

	################################################################################################################################
	## Nested Classes
	################################################################################################################################

	################################################################################################################################
	## Constructors
	################################################################################################################################

	def __init__(self):
		self._optionParameters = []							# receives instances of OptionParameter that indicate what kind of arguments are expected
		self._isShortOption = False
		self._canHaveNoMoreExpectations = False				# set this to True in order to prevent any more calls to an expect...-method
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def optionParameters(self) -> list:
		return self._optionParameters
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def expectFileOrDirectory(self,
			displayName:str,
			minLength:int = None,
			maxLength:int = None,
			mustExist:bool = False,
			toAbsolutePath:bool = False,
			baseDir:str = None,
		):

		if self._canHaveNoMoreExpectations:
			raise Exception("After a list argument no other arguments can be used!")

		assert isinstance(displayName, str)

		if minLength is not None:
			assert isinstance(minLength, int)
		else:
			minLength = 1
		if maxLength is not None:
			assert isinstance(maxLength, int)
		if mustExist is not None:
			assert isinstance(mustExist, bool)
		if toAbsolutePath is not None:
			assert isinstance(toAbsolutePath, bool)
		if baseDir is not None:
			assert isinstance(baseDir, str)

		#if self._isShortOption:
		#	raise Exception("Short options cannot have arguments!")

		p = OptionParameter(displayName, self, EnumParameterType.FileOrDirectory)
		p.minLength = minLength
		p.maxLength = maxLength
		p.mustExist = mustExist
		p.toAbsolutePath = toAbsolutePath
		p.baseDir = baseDir
		self._optionParameters.append(p)

		return self
	#

	def expectFile(self,
			displayName:str,
			minLength:int = None,
			maxLength:int = None,
			mustExist:bool = False,
			toAbsolutePath:bool = False,
			baseDir:str = None,
		):

		if self._canHaveNoMoreExpectations:
			raise Exception("After a list argument no other arguments can be used!")

		assert isinstance(displayName, str)

		if minLength is not None:
			assert isinstance(minLength, int)
		else:
			minLength = 1
		if maxLength is not None:
			assert isinstance(maxLength, int)
		if toAbsolutePath is not None:
			assert isinstance(toAbsolutePath, bool)
		if baseDir is not None:
			assert isinstance(baseDir, str)

		#if self._isShortOption:
		#	raise Exception("Short options cannot have arguments!")

		p = OptionParameter(displayName, self, EnumParameterType.File)
		p.minLength = minLength
		p.maxLength = maxLength
		p.mustExist = mustExist
		p.toAbsolutePath = toAbsolutePath
		p.baseDir = baseDir
		self._optionParameters.append(p)

		return self
	#

	def expectDirectory(self,
			displayName:str,
			minLength:int = None,
			maxLength:int = None,
			mustExist:bool = False,
			toAbsolutePath:bool = False,
			baseDir:str = None,
		):

		if self._canHaveNoMoreExpectations:
			raise Exception("After a list argument no other arguments can be used!")

		assert isinstance(displayName, str)

		if minLength is not None:
			assert isinstance(minLength, int)
		else:
			minLength = 1
		if maxLength is not None:
			assert isinstance(maxLength, int)
		if toAbsolutePath is not None:
			assert isinstance(toAbsolutePath, bool)
		if baseDir is not None:
			assert isinstance(baseDir, str)

		#if self._isShortOption:
		#	raise Exception("Short options cannot have arguments!")

		p = OptionParameter(displayName, self, EnumParameterType.Directory)
		p.minLength = minLength
		p.maxLength = maxLength
		p.mustExist = mustExist
		p.toAbsolutePath = toAbsolutePath
		p.baseDir = baseDir
		self._optionParameters.append(p)

		return self
	#

	def expectString(self,
			displayName:str,
			minLength:int = None,
			maxLength:int = None,
			enumValues:typing.Union[list,tuple] = None,
			regex:str = None,
		):

		if self._canHaveNoMoreExpectations:
			raise Exception("After a list argument no other arguments can be used!")

		assert isinstance(displayName, str)

		if enumValues is not None:
			assert isinstance(enumValues, (tuple,list))
			assert len(enumValues) > 0
			for v in enumValues:
				assert isinstance(v, str)

			minLength = None
			maxLength = None
			regex = None
		else:
			if minLength is not None:
				assert isinstance(minLength, int)
			else:
				minLength = 1
			if maxLength is not None:
				assert isinstance(maxLength, int)
			if regex is not None:
				assert isinstance(regex, str)
				if not regex.startswith("^"):
					regex = "^" + regex
				if not regex.endswith("$"):
					regex = regex + "$"

		#if self._isShortOption:
		#	raise Exception("Short options cannot have arguments!")

		p = OptionParameter(displayName, self, EnumParameterType.String)
		p.minLength = minLength
		p.maxLength = maxLength
		p.strEnumValues = enumValues
		p.strRegEx = regex
		self._optionParameters.append(p)

		return self
	#

	def expectInt32(self,
			displayName,
			minValue:int = None,
			maxValue:int = None,
		):

		if self._canHaveNoMoreExpectations:
			raise Exception("After a list argument no other arguments can be used!")

		assert isinstance(displayName, str)

		if minValue is not None:
			assert isinstance(minValue, int)
		if maxValue is not None:
			assert isinstance(maxValue, int)

		#if self._isShortOption:
		#	raise Exception("Short options cannot have arguments!")

		p = OptionParameter(displayName, self, EnumParameterType.Int32)
		p.minValue = minValue
		p.maxValue = maxValue
		self._optionParameters.append(p)

		return self
	#

#







