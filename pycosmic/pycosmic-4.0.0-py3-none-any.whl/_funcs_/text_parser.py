import re 

__all__ = ["Parser"]

class Parser:
	def __init__(self,exp):
		self.exp = self.extract_exp(exp)

	def extract_exp(self,value):

		exp = re.sub("[A-Za-z]","",value)
		return exp
