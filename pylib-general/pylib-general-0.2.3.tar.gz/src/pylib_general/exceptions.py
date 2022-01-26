class Error(Exception):
	pass

class NumTooLowError(Error):
	def __init__(self, value, message="Value was too low."):
			self.value = value
			self.message = message
			super().__init__(self.message)
	
	def __str__(self):
			return f'{self.value}: {self.message}'

class NumTooHighError(Error):
	def __init__(self, value, message="Value was too high."):
		self.value = value
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		return f'{self.value}: {self.message}'

class NumNotInRangeError(Error):
	def __init__(self, nrange, value, message="Value not in range "):
		if not type(nrange) == list:
			raise TypeError("nrange must be a list.")
	
		elif nrange[0] < value < nrange[1]: 
			raise Exception("Hey, don't misuse exceptions!")

		else: self.nrange = nrange
		self.value = value
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		return f'{self.value}: {self.message} ({self.nrange[0]}, {self.nrange[1]})'
