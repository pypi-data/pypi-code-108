



__all__ = ['make_','validate']




def is_exist(path):
	if os.path.exists(path):
		return True 
	else:
		return False


def make_(name):
	if is_exist(name) == False:
		os.mkdir(name)







def validate(a,not_be=[],instance_type=[]):


	ans = []

	for i in not_be:
		if a != i:
			ans.append(True)
		else:
			ans.append(False)
	for x in instance_type:
		if isinstance(a,x) == True:
			ans.append(True)
		else:
			ans.append(False)

	if False in ans:
		return False
	else:
		return True 




