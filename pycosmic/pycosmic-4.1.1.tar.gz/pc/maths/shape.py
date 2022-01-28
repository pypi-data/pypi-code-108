




__all__ = ['Shape']


class Shape:
	def __init__(self, arr=[]):
		self.items =  self.filter(arr)

	def filter(self,arr):
		values  = []

		for i in arr:
			if i is not None or not isinstance(i,str):
				values.append(i)


		return values 

	def single_arr_length(self,arr):

		length  = 0 

		for i in arr:
			length += 1

		return (length,)


	def multiple_arr_length(self,arr):
		rows  = 0 
		cols  = 0

		for r in arr:
			rows += 1

		for c in arr[0]:
			cols += 1

		return (rows,cols)

	def get_all_length(self,arr):

		all_length  = []

		for i in arr:
			all_length.append(len(i))


		return all_length

	def check_length(self,arr):
		lengths = self.get_all_length(arr)

		return all(ele  == lengths[0]  for ele in lengths)

	def check_nested(self,arr):
		return any(isinstance(i,list)  for i in self.items)

	def nested_single_arr_length(self,arr):
		total_lists  = 0
		total_ints  = 0

		for i in arr:
			if isinstance(i,int):
				total_ints += 1
			if isinstance(i,list):
				total_lists += 1

		if total_lists != 0 and total_ints !=0:
			return self.single_arr_length(arr)
		if total_lists !=0 and total_ints == 0:
			return self.multiple_arr_length(arr)

	@property
	def shape(self):
		if self.check_nested(self.items) == True :
			if self.check_nested(self.items) == True:
				return self.nested_single_arr_length(self.items)
			else:
				return None
		else:

			return self.single_arr_length(self.items)


	



