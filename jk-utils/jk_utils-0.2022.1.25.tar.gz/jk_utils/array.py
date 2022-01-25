


def create1D(n:int, value=None) -> list:
	return [ value for i in range(0, n) ]
#

def create2D(w:int, h:int, value=None) -> list:
	return [
		[ value for i in range(0, w) ]
		for j in range(0, h)
		]
#

def create3D(w:int, h:int, d:int, value=None) -> list:
	return [
			[
				[ value for i in range(0, w) ]
				for j in range(0, h)
			]
			for k in range(0, d)
		]
#






