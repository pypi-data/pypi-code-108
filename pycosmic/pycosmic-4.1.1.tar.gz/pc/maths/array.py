import itertools as it 
from .shape import Shape  


__all__ = ['flatten_','array']



def flatten_(a=[]):
	return list(it.chain.from_iterable(a))


class array:
	def __init__(self,a=[]):

		self.a = a 


	@property
	def shape(self):
		return Shape(self.a).shape

	def __repr__(self):
		return str(self.a)

	def __str__(self):
		return "array"

	def flatten(self):
		try:
			return flatten_(self.a)
		except Exception as e:
			return self.a 

	def __getitem__(self,idx):
		return self.a[idx]
	







