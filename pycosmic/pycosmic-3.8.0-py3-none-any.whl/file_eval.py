import json ,os 

def is_exist(path):
	if os.path.exists(path):
		return True 
	else:
		return False



def return_good(value):
	return " ".join(value).rstrip()


def load_json(name,mode='r'):
	if is_exist(name) == True and not None and name.endswith(".json"):
		with open(name,mode) as f:
			data = json.load(f)

		return data 
	else:
		return "File Name is Set To None || not exists || Not a Json File "




def load(name,mode='r',read_type='rl'):
	if is_exist(name) == True and  not None:
		if read_type in ['rl','readlines','readline']:
			with open(name,mode) as f:
				data = f.readlines()

			return return_good(data)

		if read_type in ['r','read']:
			with open(name,mode) as f:
				data = f.read()

			return return_good(data) 
	else:
		return "File is None || file does not exists"



def create(name=None,cont=None,mode='w'):
	if name is not None:
		with open(name,mode) as f:
			if cont == None:
				cont = ''

			f.write(cont)

		f.close()

	else:
		return "File Name is None"




if __name__ == '__main__':
	data = load_json('file.json',mode='r')
	print(data)


