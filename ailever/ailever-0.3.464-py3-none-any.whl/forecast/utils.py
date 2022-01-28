import os

def directory(name):
	if not os.path.exists(name):
		os.makedirs(name)
