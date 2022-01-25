import json

class classifier:
	def __init__(self, dict1):
		self.__dict__.update(dict1)
def dictionary(dict1):
	return json.loads(json.dumps(dict1), object_hook=classifier)