

import os
import collections


def setFileExt(filePath:str, newFileExt:str):
	if not newFileExt.startswith("."):
		newFileExt = "." + newFileExt

	pos = filePath.rfind("/")
	if pos > 0:
		dirPath = filePath[:pos+1]
		filePath = filePath[pos+1:]
	else:
		dirPath = ""

	pos = filePath.rfind(".")
	if pos > 0:
		filePath = filePath[:pos] + newFileExt
	else:
		filePath += newFileExt

	return dirPath + filePath
#

def getFileExt(filePath:str):
	pos = filePath.rfind("/")
	if pos > 0:
		dirPath = filePath[:pos+1]
		filePath = filePath[pos+1:]
	else:
		dirPath = ""

	pos = filePath.rfind(".")
	if pos > 0:
		return filePath[:pos + 1]
	else:
		return None
#

def makeAbsDirPathAndCheckDirExists(baseDir:str, dirPath:str):
	if baseDir:
		if not os.path.isdir(baseDir):
			raise Exception("Base directory does not exist: " + repr(baseDir))
	if not os.path.isabs(dirPath):
		if baseDir is None:
			dirPath = os.path.abspath(dirPath)
		else:
			dirPath = os.path.abspath(os.path.join(baseDir, dirPath))
	if not os.path.isdir(dirPath):
		raise Exception("Directory does not exist: " + repr(dirPath))
	return dirPath
#

def makeAbsFilePathAndCheckFileExists(baseDir:str, filePath:str):
	if baseDir:
		if not os.path.isdir(baseDir):
			raise Exception("Base directory does not exist: " + repr(baseDir))
	if not os.path.isabs(filePath):
		if baseDir is None:
			filePath = os.path.abspath(filePath)
		else:
			filePath = os.path.abspath(os.path.join(baseDir, filePath))
	if not os.path.isfile(filePath):
		raise Exception("File does not exist: " + repr(filePath))
	return filePath
#

def makeAbsFilePathAndCheckBaseDirExists(baseDir:str, filePath:str):
	if baseDir:
		if not os.path.isdir(baseDir):
			raise Exception("Base directory does not exist: " + repr(baseDir))
	if not os.path.isabs(filePath):
		if baseDir is None:
			filePath = os.path.abspath(filePath)
		else:
			filePath = os.path.abspath(os.path.join(baseDir, filePath))
	baseDir = os.path.dirname(filePath)
	if not os.path.isfile(baseDir):
		raise Exception("Base directory of file does not exist: " + repr(filePath))
	return filePath
#





