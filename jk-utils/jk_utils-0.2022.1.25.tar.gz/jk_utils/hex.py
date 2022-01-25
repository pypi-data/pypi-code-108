


__HEXCODE = "0123456789abcdef"




def byteToHex(someValue:int) -> str:
	assert isinstance(someValue, int)
	someValue = someValue & 255
	return __HEXCODE[int(someValue / 16)] + __HEXCODE[someValue % 16]

def byteArrayToHexStr(someByteArray) -> str:
	assert isinstance(someByteArray, (bytes, bytearray))
	ret = ""
	for someValue in someByteArray:
		assert isinstance(someValue, int)
		someValue = someValue & 255
		ret += __HEXCODE[int(someValue / 16)] + __HEXCODE[someValue % 16]
	return ret

def hexStrToByteArray(someHexArray:str) -> bytearray:
	if (len(someHexArray) % 2) != 0:
		raise Exception("Not a valid hex string!")
	someHexArray = someHexArray.lower()
	dataArray = bytearray()
	for offset in range(0, len(someHexArray), 2):
		charA = someHexArray[offset]
		charB = someHexArray[offset + 1]
		pA = __HEXCODE.find(charA)
		pB = __HEXCODE.find(charB)
		if (pA < 0) or (pB < 0):
			raise Exception("Not a valid hex string!")
		dataArray.append(pA * 16 + pB)
	return dataArray

def hexToByte(someHexString:str, offset:int) -> int:
	someHexString = someHexString.lower()
	charA = someHexString[offset]
	charB = someHexString[offset + 1]
	pA = __HEXCODE.find(charA)
	pB = __HEXCODE.find(charB)
	if (pA < 0) or (pB < 0):
		raise Exception("Not a valid hex string!")
	return pA * 16 + pB



