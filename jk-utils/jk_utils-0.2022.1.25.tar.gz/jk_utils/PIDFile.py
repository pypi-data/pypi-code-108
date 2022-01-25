


import os
import atexit



def _delPIDFile(filePath:str):
	if os.path.isfile(filePath):
		os.unlink(filePath)
#


def writeProcessPIDFile(filePath:str):
	dirPath = os.path.dirname(filePath)
	os.makedirs(dirPath, exist_ok=True)

	pid = os.getpid()
	with open(filePath, "w") as f:
		f.write(str(pid) + "\n")

	atexit.register(_delPIDFile, filePath)
#

