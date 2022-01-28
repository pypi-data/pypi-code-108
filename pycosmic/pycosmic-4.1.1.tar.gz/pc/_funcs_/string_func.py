import re 






class Parser:
	def __init__(self,exp):
		self.exp = self.extract_exp(exp)

	def extract_exp(self,value):

		exp = re.sub("[A-Za-z]","",value)
		return exp

class String(str):
	def __init__(self,a):
		self.a  =  a
		super().__init__() 

	def has(self,a):
		if a in self.a :
			return True 
		else:
			return False 

	def break_(self,sep=None):
		return self.a.split(sep)

	def tolist(self,whitespaces=False,lower=True):

		ans = []


		for i in self.a:
			if lower == True:
				i =  i.lower()
			else:
				pass 

			if whitespaces == False:
				if i  == ' ' or i == '':
				   i = None 
			else:
				pass 



			ans.append(i)

		return [i for i in ans if i != None]


	def length(self):
		return len(self.a)

	def ex_eq(self):  # Extracts Equation from String 
		return Parser(self.a)

	def to_int(self):
		try:
			return int(self.a)
		except Exception as e:
			return "Can't Convert :) !"






if __name__ == '__main__':
	print(String("Hello"))




