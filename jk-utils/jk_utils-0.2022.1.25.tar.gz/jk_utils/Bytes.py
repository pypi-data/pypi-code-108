


import binascii



#
# This is a convenience wrapper around an array of bytes.
#
class Bytes(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, data):
		if isinstance(data, (bytes,bytearray)):
			self.__data = bytes(data)
		elif isinstance(data, str):
			self.__data = binascii.unhexlify(data.encode("ascii"))
		else:
			raise Exception()
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def hexStr(self):
		return binascii.hexlify(self.__data).decode("ascii")
	#

	def __repr__(self):
		return "Bytes<(" + self.__str__() + ")>"
	#

	def __bytes__(self):
		return self.__data
	#

	def __str__(self):
		return binascii.hexlify(self.__data).decode("ascii")
	#

	def __add__(self, other):
		assert isinstance(other, Bytes)
		return Bytes(self.__data + other.__data)
	#

	def __len__(self):
		return len(self.__data)
	#

	def __eq__(self, other):
		if isinstance(other, Bytes):
			return self.__data == other.__data
		elif isinstance(other, (bytes, bytearray)):
			return self.__data == other
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, Bytes):
			return self.__data != other.__data
		elif isinstance(other, (bytes, bytearray)):
			return self.__data != other
		else:
			return False
	#

#














