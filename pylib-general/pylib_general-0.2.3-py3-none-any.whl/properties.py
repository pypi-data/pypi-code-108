class Property:
	def __init__(self):
		pass

	def add(self, name, val):
		if type(name) == str:
			if " " in name or "1" in name or "2" in name or "3" in name or "4" in name or "5" in name or "6" in name or "7" in name or "8" in name or "9" in name:
				raise SyntaxError("You put a number or space in the name!")
				return
			else: self.__dict__[name] = val
		else: raise TypeError("That is not a string!")

	def remove(self, name):
		if type(name) == str:
			if " " in name or "1" in name or "2" in name or "3" in name or "4" in name or "5" in name or "6" in name or "7" in name or "8" in name or "9" in name:
				raise SyntaxError("You put a number or space in the name!")
				return
			else: del self.__dict__[name]
		else: raise TypeError("That is not a string!")

	def get(self, name):
		if type(name) == str:
			if " " in name or "1" in name or "2" in name or "3" in name or "4" in name or "5" in name or "6" in name or "7" in name or "8" in name or "9" in name:
				raise SyntaxError("You put a number or space in the name!")
				return
			else: return self.__dict__[name]
		else: raise TypeError("That is not a string!")

	def __getattr__(self, name):
		return self.get(name)

	def __setattr__(self, name, val):
		self.add(name, val)

	def __delattr__(self, name):
		self.remove(name)
	
	def __exit__(self, exception_type, exception_value, exception_traceback):
		del self.__dict__
