from pc import SetCode 


def get_model(name):
	try:
		SetCode(filename=name,repo="models")
	except:
		print('Model Not Found')



