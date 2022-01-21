class Column:
	def __init__(self, name, generator=None, pk=False):
		self.name = name
		self.pk = pk

		self.__generator = None
		if generator is not None:
			self.__assignGenerator(generator)

	def __assignGenerator(self, generator):
		# TODO: for generator: Generator Generator is not defined; huh?
		self.__generator = generator

	def generate(self):
		return self.__generator.generate()