


import os
import array
import math




#
# Base class for RNGs.
#
class AbstractRandomNumberGenerator(object):

	_bits64n = int(-(65536//2*65536*65536*65536) + 1)
	_bits32n = int(-(65536//2*65536) + 1)
	_bits16n = int(-(65536//2) + 1)
	_bits8n = -127

	def nextUInt32(self) -> int:
		raise NotImplementedError()
	#

	def nextInt32(self) -> int:
		return self.nextUInt32() + AbstractRandomNumberGenerator._bits32n
	#

	def nextInt16(self) -> int:
		return self.nextUInt16() + AbstractRandomNumberGenerator._bits16n
	#

	def nextInt8(self) -> int:
		return self.nextUInt8() + AbstractRandomNumberGenerator._bits8n
	#

	def nextInt64(self) -> int:
		return self.nextUInt64() + AbstractRandomNumberGenerator._bits64n
	#

	def nextBytes(self, count:int) -> bytes:
		raise NotImplementedError()
	#

	def nextUInt8(self) -> int:
		return self.nextUInt32() & 255
	#

	def nextUInt16(self) -> int:
		return self.nextUInt32() & 65535
	#

	def nextUInt64(self) -> int:
		a = self.nextUInt32()
		b = self.nextUInt32()
		return (a << 32) | b
	#

	def nextString(self, poolOfCharacters:str, count:int):
		assert isinstance(poolOfCharacters, str)
		assert len(poolOfCharacters) > 1
		maxCharacters = len(poolOfCharacters)

		s = []
		while len(s) < count:
			s.append(poolOfCharacters[int(self.nextFloat() * maxCharacters)])

		return "".join(s)
	#

	def nextCharacter(self, poolOfCharacters:str):
		assert isinstance(poolOfCharacters, str)
		assert len(poolOfCharacters) > 1
		maxCharacters = len(poolOfCharacters)

		return poolOfCharacters[int(self.nextFloat() * maxCharacters)]
	#

	def nextUInt32Bounded(self, maxValue:int) -> int:
		assert isinstance(maxValue, int)
		assert maxValue > 1

		return int(self.nextFloat() * maxValue)
	#

	def nextFloat(self) -> float:
		raise NotImplementedError()
	#

#




#
# This class provides a linear congruential generator which is a pseudo number generator that if instantiated will always return the same random values.
# (See: https://en.wikipedia.org/wiki/Linear_congruential_generator)
# The internal values used here are the values Donald Knuth used for his MMIX.
#
class LinearCongruentialGenerator(AbstractRandomNumberGenerator):

	_bits64 = int("0xffffffffffffffff", 16)
	_bits32 = int("0xffffffff", 16)

	def __init__(self):
		super().__init__()

		self.__x = 0
		self.__a = 6364136223846793005
		self.__c = 1442695040888963407
	#

	def nextFloat(self) -> float:
		return self.nextUInt32() / LinearCongruentialGenerator._bits32
	#

	def nextUInt32(self) -> int:
		self.__x = (self.__a * self.__x + self.__c) & LinearCongruentialGenerator._bits64
		return self.__x & LinearCongruentialGenerator._bits32
	#

	def nextBytes(self, count:int) -> bytes:
		assert isinstance(count, int)
		assert count >= 1

		vals = []
		for i in range(0, (count + 3) // 4):
			self.__x = (self.__a * self.__x + self.__c) & LinearCongruentialGenerator._bits64
			v32 = self.__x & LinearCongruentialGenerator._bits32
			vals.append(v32)
		return array.array("I", vals).tobytes()[0:count]
	#

#




#
# This is a true /dev/urandom based random number generator. Please note that it will likely be quite inefficient as for every call
# to a random number generation method a <c>open()</c>, <c>read()</c> and <c>close()</c> is performed.
#
class URandomGenerator(AbstractRandomNumberGenerator):

	_bits64 = int("0xffffffffffffffff", 16)
	_bits32 = int("0xffffffff", 16)

	def __init__(self):
		super().__init__()
	#

	def nextFloat(self) -> float:
		vals = bytearray()
		with open("/dev/urandom", "rb") as f:
			while len(vals) < 8:
				vals.extend(f.read(8 - len(vals)))

		return int.from_bytes(vals, byteorder='big', signed=False) / URandomGenerator._bits64
	#

	def nextUInt32(self) -> int:
		vals = bytearray()
		with open("/dev/urandom", "rb") as f:
			while len(vals) < 4:
				vals.extend(f.read(4 - len(vals)))

		return int.from_bytes(vals, byteorder='big', signed=False)
	#

	def nextUInt64(self) -> int:
		vals = bytearray()
		with open("/dev/urandom", "rb") as f:
			while len(vals) < 8:
				vals.extend(f.read(8 - len(vals)))

		return int.from_bytes(vals, byteorder='big', signed=False)
	#

	def nextBytes(self, count:int) -> bytes:
		assert isinstance(count, int)
		assert count >= 1

		vals = bytearray()
		bytesToRead = count
		with open("/dev/urandom", "rb") as f:
			while bytesToRead > 0:
				vals.extend(f.read(bytesToRead))
				bytesToRead = count - len(vals)
		return vals
	#

#






