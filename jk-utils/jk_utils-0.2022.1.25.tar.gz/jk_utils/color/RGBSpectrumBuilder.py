


from .RGB import RGB
from .RGBSpectrum import RGBSpectrum



class RGBSpectrumBuilder(object):

	def __init__(self):
		self.__parts = []
	#

	def __buildRGBSpectrumPart(self, c1:RGB, c2:RGB, length:int):
		values = []
		for i in range(0, length):
			v = i / (length -1)
			vv = 1 - v
			r = c1.r * vv + c2.r * v
			g = c1.g * vv + c2.g * v
			b = c1.b * vv + c2.b * v
			values.append(RGB(r, g, b))
		return values
	#

	def appendGradientBand(self, fromRGB:RGB, toRGB:RGB, length:int):
		self.__parts.extend(self.__buildRGBSpectrumPart(fromRGB, toRGB, length))
		return self
	#

	def insertGradientBand(self, position:int, fromRGB:RGB, toRGB:RGB, length:int):
		parts1 = self.__parts[0:position]
		parts2 = self.__parts[position:]
		self.__parts = parts1 + self.__buildRGBSpectrumPart(fromRGB, toRGB, length) + parts2
		return self
	#

	def appendFlatBand(self, rgb:RGB, length:int):
		self.__parts.extend([ rgb ] * length)
		return self
	#

	def insertFlatBand(self, position:int, rgb:RGB, length:int):
		parts1 = self.__parts[0:position]
		parts2 = self.__parts[position:]
		self.__parts = parts1 + ([ rgb ] * length) + parts2
		return self
	#

	def length(self) -> int:
		return len(self.__parts)
	#

	def __len__(self) -> int:
		return len(self.__parts)
	#

	def compile(self) -> RGBSpectrum:
		return RGBSpectrum(self.__parts)
	#

#




