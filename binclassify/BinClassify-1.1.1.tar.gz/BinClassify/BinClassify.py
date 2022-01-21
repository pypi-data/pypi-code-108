import math


class BinClassifyError(Exception):
	pass
	
	
def validtype(var, vartype):
	tvar = type(var)
	if tvar != vartype:
		raise TypeError("must be real " + vartype.__name__ + ", not " + type(var).__name__)
		
		
def validnumber(number, minnumber):
	validtype(number, int)
	if number < minnumber:
		raise ValueError("The number must be greater than " + str(minnumber))


class BinClassify(object):
	def __init__(self):
		self.val = True
		self.varQuestion = 0
		
	def CoutGroups(self, nqustion):
		validnumber(nqustion, 1)
		if nqustion == 1:
			return [2, 2]
		else:
			nmin = 2 ** (nqustion - 1) + 1
			nmax = 2 ** nqustion
			return [nmin, nmax]
			
	def CoutQustion(self, number):
		validnumber(number, 2)
		self.varHigh = number
		self.varQuestion = math.ceil(math.log(number, 2))
		self.val = False
		return self.varQuestion
	
	def Answer(self, arr):
		validtype(arr, list)
		if self.val:
			raise BinClassifyError("First you need to use the method CoutQustion")
		if len(arr) != self.varQuestion:
			raise ValueError("The number of elements in the array does not match the returned number of the CoutQustion method.")
		low = 1
		high = self.varHigh 
		for i in arr:
			mid = (low + high) // 2
			if i == 0:
				high = mid 
			elif i == 1:
				low = mid  
			else:
				ValueError("One of the array elements is not binary (not 1, not 0)")
		return high