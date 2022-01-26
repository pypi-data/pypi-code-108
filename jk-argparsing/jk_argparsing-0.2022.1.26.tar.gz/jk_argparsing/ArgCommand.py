


from .ArgItemBase import *




class ArgCommand(ArgItemBase):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, name:str, description:str, bHidden:bool = False):
		super().__init__()

		assert isinstance(name, str)
		assert isinstance(description, str)
		assert isinstance(bHidden, bool)

		self.__name = name
		self.__description = description
		self.__bHidden = bHidden
	#

	################################################################################################################################
	## Public Property
	################################################################################################################################

	@property
	def name(self) -> str:
		return self.__name
	#

	@property
	def description(self) -> str:
		return self.__description
	#

	@property
	def isHidden(self) -> bool:
		return self.__bHidden
	#

	################################################################################################################################
	## Helper Method
	################################################################################################################################

	################################################################################################################################
	## Public Method
	################################################################################################################################

	def __str__(self):
		return self.__name
	#

	def expectStringList(self,
			displayName:str,
			minLength:int = None,
			maxLength:int = None,
			strEnumValues:typing.Union[list,tuple] = None,
			strRegEx:str = None,
		):

		if self._canHaveNoMoreExpectations:
			raise Exception("After a list argument no other arguments can be used!")

		assert isinstance(displayName, str)
		if not displayName.endswith("..."):
			displayName += "..."

		if strEnumValues is not None:
			assert isinstance(strEnumValues, (tuple,list))
			assert len(strEnumValues) > 0
			for v in strEnumValues:
				assert isinstance(v, str)

			minLength = None
			maxLength = None
			strRegEx = None
		else:
			if minLength is not None:
				assert isinstance(minLength, int)
			else:
				minLength = 1
			if maxLength is not None:
				assert isinstance(maxLength, int)
			if strRegEx is not None:
				assert isinstance(strRegEx, str)
				if not strRegEx.startswith("^"):
					strRegEx = "^" + strRegEx
				if not strRegEx.endswith("$"):
					strRegEx = strRegEx + "$"

		#if self._isShortOption:
		#	raise Exception("Short options cannot have arguments!")

		p = OptionParameter(displayName, self, EnumParameterType.StringList)
		p.minLength = minLength
		p.maxLength = maxLength
		p.strEnumValues = strEnumValues
		p.strRegEx = strRegEx
		self._optionParameters.append(p)

		self._canHaveNoMoreExpectations = True

		return self
	#

#










