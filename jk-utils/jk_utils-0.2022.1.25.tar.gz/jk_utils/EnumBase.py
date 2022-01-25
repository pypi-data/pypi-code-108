

import enum





#
# This is a base class for enumerations.
#
class EnumBase(enum.Enum):

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value_ = value
		member.fullname = name
		return member
	#

	#
	# Get an integer representation of this enumeration item.
	#
	def __int__(self):
		return self._value_
	#

	#
	# Get a string representation of this enumeration item.
	#
	def __str__(self):
		return self.fullname
	#

	#
	# Get a string representation of this enumeration item.
	#
	def __repr__(self):
		return self.fullname
	#

	#
	# Get an integer representation of this enumeration item.
	#
	def toJSON(self):
		return self._value_
	#

	#
	# Get a list of all states this enumeration contains.
	#
	@classmethod
	def allStates(cls):
		ret = []
		for key in cls.__dict__["_value2member_map_"]:
			enumItem = cls.__dict__["_value2member_map_"][key]
			ret.append(enumItem)
		return ret
	#

	#
	# This method converts a string or integer representing an enumeration value to an actual enumeration value.
	#
	# @param		mixed data							Either a string or an integer to parse. (A member of this enumeration is
	#													accepted as well and passed through to the caller as in this case there
	#													is no need to parse anything.)
	# @param		bool bRaiseExceptionOnError			If <c>True</c> (which is the default) an exception is thrown if a
	#													value has been specified that could not be parsed. (Please note that
	#													an exception is always thrown if the spcified value is not a string nor
	#													an integer nor of the enumeration type itself.)
	#
	@classmethod
	def parse(cls, data, bRaiseExceptionOnError:bool = True):
		if isinstance(data, int):
			if data in cls.__dict__["_value2member_map_"]:
				return cls.__dict__["_value2member_map_"][data]
			else:
				if bRaiseExceptionOnError:
					raise Exception("Not a member of enumeration '" + str(cls.__name__) + "': " + repr(data))
				else:
					return None
		elif isinstance(data, str):
			for key in cls.__dict__["_value2member_map_"]:
				enumItem = cls.__dict__["_value2member_map_"][key]
				if str(enumItem) == data:
					return enumItem
			if data in cls.__dict__["_member_names_"]:
				return cls.__dict__[data]
			else:
				if bRaiseExceptionOnError:
					raise Exception("Not a member of enumeration '" + str(cls.__name__) + "': " + repr(data))
				else:
					return None
		elif cls == type(data):
			return data
		else:
			raise Exception("Unrecognized enumeration value type: " + repr(data))
	#

#




