import os


def rename(oldname,newname):
	if os.path.exists(oldname):
		os.rename(oldname,newname)
		print('File {} Renamed to {}'.format(oldname,newname))
	else:
		print('File Not Found')

def create(name,cont,mode='w'):

	with open(name,mode) as f:
		f.write(cont)
	f.close()

	print('File {} created'.format(name))


def delete(name):
	if os.path.exists(name):
		os.remove(name)
	else:
		print('File not found please provide full path')

def read_file(name,mode='r'):
	with open(name,mode) as f:
		text = f.readlines()

	return text


