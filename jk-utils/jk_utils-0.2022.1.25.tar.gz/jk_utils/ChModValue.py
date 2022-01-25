import re
import stat



#
# This class represents a mode value such as in <c>stat.st_mode</c>.
# It provides easy ways for parsing and modification.
#
class ChModValue:

	################################################################
	## Constants
	################################################################

	################################################################
	## Constructor
	################################################################

	def __init__(self,
		v = None,
		userR:bool = False,
		userW:bool = False,
		userX:bool = False,
		groupR:bool = False,
		groupW:bool = False,
		groupX:bool = False,
		otherR:bool = False,
		otherW:bool = False,
		otherX:bool = False,
		):

		if v is None:
			self.userR = userR
			self.userW = userW
			self.userX = userX
			self.groupR = groupR
			self.groupW = groupW
			self.groupX = groupX
			self.otherR = otherR
			self.otherW = otherW
			self.otherX = otherX
		elif isinstance(v, str):
			self.fromStr(v)
		elif isinstance(v, int):
			self.fromInt(v)
		else:
			raise Exception("Unexected type: " + repr(type(v)))
	#

	################################################################
	## Properties
	################################################################

	################################################################
	## Helper Methods
	################################################################

	def __setBit(self, value, bitNo):
		mask = 1 << bitNo		# Compute mask, an integer with just bit 'index' set.
		value |= mask			# If x was True, set the bit indicated by the mask.
		return value
	#

	################################################################
	## Public Methods
	################################################################

	def cloneObject(self):
		return ChModValue(self.toInt())
	#

	def __str__(self):
		v = [ "-" ] * 9
		if self.userR:
			v[0] = "r"
		if self.userW:
			v[1] = "w"
		if self.userX:
			v[2] = "x"
		if self.groupR:
			v[3] = "r"
		if self.groupW:
			v[4] = "w"
		if self.groupX:
			v[5] = "x"
		if self.otherR:
			v[6] = "r"
		if self.otherW:
			v[7] = "w"
		if self.otherX:
			v[8] = "x"
		return "".join(v)
	#

	def __repr__(self):
		return self.__str__()
	#

	def __int__(self):
		return self.toInt()
	#

	def toStr(self):
		return self.__str__()
	#

	def toStrChMod(self) -> str:
		vU = ""
		if self.userR:
			vU += "r"
		if self.userW:
			vU += "w"
		if self.userX:
			vU += "x"
		vG = ""
		if self.groupR:
			vG += "r"
		if self.groupW:
			vG += "w"
		if self.groupX:
			vG += "x"
		vO = ""
		if self.otherR:
			vO += "r"
		if self.otherW:
			vO += "w"
		if self.otherX:
			vO += "x"
		return "u=" + vU + ",g=" + vG + ",o=" + vO
	#

	#
	# Accept data from the specified integer value.
	#
	def fromInt(self, v:int):
		if (v < 0) or (v > 0o777):
			raise Exception("Unrecognized int!")

		self.userR = v & stat.S_IRUSR == stat.S_IRUSR
		self.userW = v & stat.S_IWUSR == stat.S_IWUSR
		self.userX = v & stat.S_IXUSR == stat.S_IXUSR
		self.groupR = v & stat.S_IRGRP == stat.S_IRGRP
		self.groupW = v & stat.S_IWGRP == stat.S_IWGRP
		self.groupX = v & stat.S_IXGRP == stat.S_IXGRP
		self.otherR = v & stat.S_IROTH == stat.S_IROTH
		self.otherW = v & stat.S_IWOTH == stat.S_IWOTH
		self.otherX = v & stat.S_IXOTH == stat.S_IXOTH

		return self
	#

	#
	# Accept data from the specified string value.
	# The data in this object is set to exactly match the specified argument.
	# An exception is thrown if the specified string could not be parsed.
	#
	# @param	str s			A string to parse. You should specify something like this:
	#							* "-rwxr--r--" (10 characters, the first must be '-')
	# 							* "rwxr--r--" (9 characters)
	#							* an octal number such as "755"
	#							* "a=rw", "ug=rwx", "o=x", etc.
	#
	def fromStr(self, v:str):
		assert isinstance(v, str)
		v = v.lower()

		if re.match("^[0-7][0-7][0-7]$", v):
			# ocal form
			return self.fromInt(int(v, 8))

		if re.match("^[r-][w-][x-][r-][w-][x-][r-][w-][x-]$", v):
			self.userR = v[0] == "r"
			self.userW = v[1] == "w"
			self.userX = v[2] == "x"
			self.groupR = v[3] == "r"
			self.groupW = v[4] == "w"
			self.groupX = v[5] == "x"
			self.otherR = v[6] == "r"
			self.otherW = v[7] == "w"
			self.otherX = v[8] == "x"
			return self

		if re.match("^-[r-][w-][x-][r-][w-][x-][r-][w-][x-]$", v):
			self.userR = v[1] == "r"
			self.userW = v[2] == "w"
			self.userX = v[3] == "x"
			self.groupR = v[4] == "r"
			self.groupW = v[5] == "w"
			self.groupX = v[6] == "x"
			self.otherR = v[7] == "r"
			self.otherW = v[8] == "w"
			self.otherX = v[9] == "x"
			return self

		if re.match("^[ugoa]*[=][rwx]{1-3}$", v):
			self.modify(v)
			return self

		raise Exception("Unrecognized string!")
	#

	#
	# Modifies the current object data.
	# An exception is thrown if the specified string could not be parsed.
	#
	# @param	str s			A string to parse. You should specify something like "a+rw", "ug=rwx" or "o-x" here.
	#
	def modify(self, s:str):
		for sPart in s.split(","):
			sPart = sPart.strip()
			m = re.match("^([ugoa]+)([+-=])([rwx]+)$", sPart)
			if m:
				keys = []
				for t in m.group(1):
					if t == "a":
						for rwx in m.group(3):
							keys.append("user" + rwx.upper())
							keys.append("group" + rwx.upper())
							keys.append("other" + rwx.upper())
					elif t == "u":
						for rwx in m.group(3):
							keys.append("user" + rwx.upper())
					elif t == "g":
						for rwx in m.group(3):
							keys.append("group" + rwx.upper())
					else:
						for rwx in m.group(3):
							keys.append("other" + rwx.upper())

				if m.group(2) == "+":
					for key in keys:
						setattr(self, key, True)
				elif m.group(2) == "-":
					for key in keys:
						setattr(self, key, False)
				else:
					self.userR = False
					self.userW = False
					self.userX = False
					self.userR = False
					self.userW = False
					self.userX = False
					self.otherR = False
					self.otherW = False
					self.otherX = False
					for key in keys:
						setattr(self, key, True)
			else:
				raise Exception("Unrecognized string!")

		return self
	#

	def toInt(self) -> int:
		v = 0
		if self.userR:
			v = self.__setBit(v, 8)
		if self.userW:
			v = self.__setBit(v, 7)
		if self.userX:
			v = self.__setBit(v, 6)
		if self.groupR:
			v = self.__setBit(v, 5)
		if self.groupW:
			v = self.__setBit(v, 4)
		if self.groupX:
			v = self.__setBit(v, 3)
		if self.otherR:
			v = self.__setBit(v, 2)
		if self.otherW:
			v = self.__setBit(v, 1)
		if self.otherX:
			v = self.__setBit(v, 0)
		return v
	#

	#
	# Convert to octal, e.g. "755"
	#
	def toStrOcal(self) -> str:
		v = self.toInt()
		s = oct(v)
		assert s.startswith("0o")
		s = s[2:]
		assert len(s) <= 3
		while len(s) < 3:
			s = "0" + s
		return s
	#

	################################################################
	## Public Static Methods
	################################################################

	@staticmethod
	def create(v):
		if isinstance(v, ChModValue):
			return v
		elif isinstance(v, (int,str)):
			return ChModValue(v)
		else:
			raise Exception("Unexpected value: " + repr(v))
	#

#

