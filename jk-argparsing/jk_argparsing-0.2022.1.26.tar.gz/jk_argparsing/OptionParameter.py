




import re
import os

from .EnumParameterType import EnumParameterType






class OptionParameter(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self, displayName:str, option, ptype:EnumParameterType):
		assert isinstance(displayName, str)
		#assert isinstance(option, ArgOption)
		assert isinstance(ptype, EnumParameterType)

		self.displayName = displayName
		self.option = option
		self.type = ptype
		self.minLength = None
		self.maxLength = None
		self.minValue = None
		self.maxValue = None
		self.strEnumValues = None
		self.strRegEx = None
		self.mustExist = None
		self.baseDir = None
		self.toAbsolutePath = None
	#


	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __parseFile(self, sinput):
		assert isinstance(sinput, str)

		if self.minLength is not None:
			if len(sinput) < self.minLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.maxLength is not None:
			if len(sinput) < self.maxLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.toAbsolutePath:
			if self.baseDir:
				sinput = os.path.join(self.baseDir, sinput)
			sinput = os.path.abspath(sinput)

		if self.mustExist:
			if not os.path.isfile(sinput):
				raise Exception("File specified for option " + repr(str(self.option)) + " does not exist: " + repr(sinput))			# NEW FIX

		return sinput
	#

	def __parseFileOrDirectory(self, sinput):
		assert isinstance(sinput, str)

		if self.minLength is not None:
			if len(sinput) < self.minLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.maxLength is not None:
			if len(sinput) < self.maxLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.toAbsolutePath:
			if self.baseDir:
				sinput = os.path.join(self.baseDir, sinput)
			sinput = os.path.abspath(sinput)

		if self.mustExist:
			if not os.path.exists(sinput):
				raise Exception("File or directory specified for option " + repr(str(self.option)) + " does not exist: " + repr(sinput))

		return sinput
	#

	def __parseDirectory(self, sinput):
		assert isinstance(sinput, str)

		if self.minLength is not None:
			if len(sinput) < self.minLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.maxLength is not None:
			if len(sinput) < self.maxLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.toAbsolutePath:
			if self.baseDir:
				sinput = os.path.join(self.baseDir, sinput)
			sinput = os.path.abspath(sinput)

		if self.mustExist:
			if not os.path.isdir(sinput):
				raise Exception("Directory specified for option " + repr(str(self.option)) + " does not exist: " + repr(sinput))

		return sinput
	#

	def __parseString(self, sinput):
		assert isinstance(sinput, str)

		if self.strEnumValues is not None:
			for v in self.strEnumValues:
				if sinput == v:
					return sinput
			raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.minLength is not None:
			if len(sinput) < self.minLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.maxLength is not None:
			if len(sinput) < self.maxLength:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.strRegEx is not None:
			regex = re.compile(self.strRegEx)
			m = regex.match(sinput)
			if m is None:
				raise Exception("Invalid argument value specified for option " + repr(str(self.option)) + ": " + repr(sinput))

		return sinput
	#

	def __parseInt32(self, sinput):
		try:
			n = int(sinput)
		except:
			raise Exception("Argument is not a valid integer value at option " + repr(str(self.option)) + ": " + repr(sinput))

		if self.minValue is not None:
			if n < self.minValue:
				raise Exception("Argument too small for option " + repr(str(self.option)) + ": " + repr(sinput))
		if self.maxValue is not None:
			if n > self.maxValue:
				raise Exception("Argument too big for option " + repr(str(self.option)) + ": " + repr(sinput))
		return n
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# This is the old version of the parsing method. This should be replaced by a new implementation, but right now this old version is still in use.
	#
	def parse(self, sinput):
		assert isinstance(sinput, str)

		if self.type == EnumParameterType.String:
			return self.__parseString(sinput)
		elif self.type == EnumParameterType.Int32:
			return self.__parseInt32(sinput)
		elif self.type == EnumParameterType.File:
			return self.__parseFile(sinput)
		elif self.type == EnumParameterType.Directory:
			return self.__parseDirectory(sinput)
		elif self.type == EnumParameterType.FileOrDirectory:
			return self.__parseFileOrDirectory(sinput)
		elif self.type == EnumParameterType.StringList:
			raise NotImplementedError()
		else:
			raise Exception("Implementation error!")
	#

	#
	# This is the new version of the parsing method. This should replace the old version one day to avoid redundancies, but right now the old version is still in use.
	#
	# @return		object parsingResult		The value created by the parsing implementation.
	# @return		int n						The number of arguments processed. This is typically 1, except for the case that a list is expected.
	#
	def parse2(self, parameters:list, pos:int):
		assert isinstance(parameters, list)
		assert isinstance(pos, int)

		if pos == len(parameters):
			# no more data
			return None, 0

		if self.type == EnumParameterType.String:
			sinput = parameters[pos]
			return self.__parseString(sinput), 1
		elif self.type == EnumParameterType.Int32:
			sinput = parameters[pos]
			return self.__parseInt32(sinput), 1
		elif self.type == EnumParameterType.File:
			sinput = parameters[pos]
			return self.__parseFile(sinput), 1
		elif self.type == EnumParameterType.Directory:
			sinput = parameters[pos]
			return self.__parseDirectory(sinput), 1
		elif self.type == EnumParameterType.FileOrDirectory:
			sinput = parameters[pos]
			return self.__parseFileOrDirectory(sinput), 1
		elif self.type == EnumParameterType.StringList:
			ret = []
			n = 0
			for sinput in parameters[pos:]:
				ret.append(self.__parseString(sinput))
				n += 1
			return ret, n
		else:
			raise Exception("Implementation error!")
	#

#





















