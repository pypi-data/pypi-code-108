

from ..hex import *



class RGB(object):

	def __init__(self, r:float = 0, g:float = 0, b:float = 0, a:float = 1):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
	#

	def __str__(self):
		a, r, g, b = self.toARGB256Tuple()
		return "#" + byteToHex(a) + byteToHex(r) + byteToHex(g) + byteToHex(b)
	#

	def __repr__(self):
		a, r, g, b = self.toARGB256Tuple()
		return "#" + byteToHex(a) + byteToHex(r) + byteToHex(g) + byteToHex(b)
	#

	def toHTML(self) -> str:
		r, g, b = self.toRGB256Tuple()
		return "#" + byteToHex(r) + byteToHex(g) + byteToHex(b)
	#

	def toAlphaHTML(self) -> str:
		a, r, g, b = self.toARGB256Tuple()
		return "#" + byteToHex(a) + byteToHex(r) + byteToHex(g) + byteToHex(b)
	#

	def toRGBTuple(self) -> tuple:
		return (self.r, self.g, self.b)
	#

	def toARGBTuple(self) -> tuple:
		return (self.a, self.r, self.g, self.b)
	#

	def toRGB256Tuple(self) -> tuple:
		rr = int(self.r*255)
		if rr < 0:
			rr = 0
		if rr > 255:
			rr = 255
		gg = int(self.g*255)
		if gg < 0:
			gg = 0
		if gg > 255:
			gg = 255
		bb = int(self.b*255)
		if bb < 0:
			bb = 0
		if bb > 255:
			bb = 255
		return rr, gg, bb
	#

	def toARGB256Tuple(self) -> tuple:
		aa = int(self.a*255)
		if aa < 0:
			aa = 0
		if aa > 255:
			aa = 255
		rr = int(self.r*255)
		if rr < 0:
			rr = 0
		if rr > 255:
			rr = 255
		gg = int(self.g*255)
		if gg < 0:
			gg = 0
		if gg > 255:
			gg = 255
		bb = int(self.b*255)
		if bb < 0:
			bb = 0
		if bb > 255:
			bb = 255
		return aa, rr, gg, bb
	#

	def toInt(self) -> tuple:
		a, r, g, b = self.toARGB256Tuple()
		return a * 256*256*256 + r * 256*256 + g * 256 + b
	#

	def __int__(self):
		a, r, g, b = self.toARGB256Tuple()
		return a * 256*256*256 + r * 256*256 + g * 256 + b
	#

	@staticmethod
	def parse(s:str):
		assert isinstance(s, str)
		assert s
		assert s[0] == "#"
		assert len(s) in [ 7, 9 ]
		s = s[1:]
		data = hexStrToByteArray(s)
		if len(data) == 3:
			return RGB(data[0]/255.0, data[1]/255.0, data[2]/255.0)
		else:
			return RGB(data[1]/255.0, data[2]/255.0, data[3]/255.0, data[0]/255.0)
	#

#



