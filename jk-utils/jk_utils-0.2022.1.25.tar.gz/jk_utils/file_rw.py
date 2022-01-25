

import os
import gzip
import bz2
import lzma
import json




class openReadBinary(object):

	def __init__(self, filePath):
		self.__filePath = filePath
		if filePath.endswith(".gz") or filePath.endswith(".gzip"):
			self.__open = gzip.open
		elif filePath.endswith(".bz2") or filePath.endswith(".bzip2"):
			self.__open = bz2.open
		elif filePath.endswith(".lzma") or filePath.endswith(".xz"):
			self.__open = lzma.open
		else:
			self.__open = open
	#

	def __enter__(self):
		self.__f = self.__open(self.__filePath, "rb")
		return self.__f
	#

	def __exit__(self, *args):
		self.__f.close()
	#

#

class openReadText(object):

	class _BinaryWrapper(object):

		def __init__(self, f):
			self.__f = f
		#

		def read(self, length = None):
			data = self.__f.read()
			return data.decode("utf-8")
		#

		def close(self):
			self.__f.close()
		#

	#

	def __init__(self, filePath):
		self.__filePath = filePath
		if filePath.endswith(".gz") or filePath.endswith(".gzip"):
			self.__open = gzip.open
			self.__bToText = True
		elif filePath.endswith(".bz2") or filePath.endswith(".bzip2"):
			self.__open = bz2.open
			self.__bToText = True
		elif filePath.endswith(".lzma") or filePath.endswith(".xz"):
			self.__open = lzma.open
			self.__bToText = True
		else:
			self.__open = open
			self.__bToText = False
	#

	def __enter__(self):
		if self.__bToText:
			self.__f = openReadText._BinaryWrapper(self.__open(self.__filePath, "rb"))
		else:
			self.__f = self.__open(self.__filePath, "r")
		return self.__f
	#

	def __exit__(self, *args):
		self.__f.close()
	#

#

class openReadJSON(object):

	class _BinaryWrapper(object):

		def __init__(self, f):
			self.__f = f
		#

		def read(self, length = None):
			data = self.__f.read()
			return data.decode("utf-8")
		#

		def close(self):
			self.__f.close()
		#

	#

	class _JSONWrapper(object):

		def __init__(self, f):
			self.__f = f
		#

		def read(self):
			data = self.__f.read()
			return json.loads(data)
		#

		def close(self):
			self.__f.close()
		#

	#

	def __init__(self, filePath):
		self.__filePath = filePath
		if filePath.endswith(".gz") or filePath.endswith(".gzip"):
			self.__open = gzip.open
			self.__bToText = True
		elif filePath.endswith(".bz2") or filePath.endswith(".bzip2"):
			self.__open = bz2.open
			self.__bToText = True
		elif filePath.endswith(".lzma") or filePath.endswith(".xz"):
			self.__open = lzma.open
			self.__bToText = True
		else:
			self.__open = open
			self.__bToText = False
	#

	def __enter__(self):
		if self.__bToText:
			self.__f = openReadJSON._JSONWrapper(openReadJSON._BinaryWrapper(self.__open(self.__filePath, "rb")))
		else:
			self.__f = openReadJSON._JSONWrapper(self.__open(self.__filePath, "r"))
		return self.__f
	#

	def __exit__(self, *args):
		self.__f.close()
	#

#





class openWriteBinary(object):

	def __init__(self, filePath, bSafeWrite:bool = True, compression:str = None):
		self.__filePath = filePath
		self.__bSafeWrite = bSafeWrite
		if self.__bSafeWrite:
			self.__filePathTmp = filePath + ".tmp"

		self.__format = None
		if compression:
			if (compression == "gzip") or (compression == "gz"):
				self.__open = gzip.open
			elif (compression == "bz2") or (compression == "bzip2"):
				self.__open = bz2.open
			elif compression == "lzma":
				self.__format = lzma.FORMAT_ALONE
				self.__open = lzma.open
			elif compression == "xz":
				self.__format = lzma.FORMAT_XZ
				self.__open = lzma.open
			else:
				raise Exception("Unknown compressor: " + compression)
		else:
			self.__open = open
	#

	def __enter__(self):
		if self.__bSafeWrite:
			if self.__format:
				self.__f = self.__open(self.__filePathTmp, "wb", format=self.__format)
			else:
				self.__f = self.__open(self.__filePathTmp, "wb")
		else:
			if self.__format:
				self.__f = self.__open(self.__filePath, "wb", format=self.__format)
			else:
				self.__f = self.__open(self.__filePath, "wb")
		return self.__f
	#

	def __exit__(self, *args):
		self.__f.close()
		if self.__bSafeWrite:
			if os.path.isfile(self.__filePath):
				os.unlink(self.__filePath)
			os.rename(self.__filePathTmp, self.__filePath)
	#

#



class openWriteText(object):

	#
	# Write text data to an underlying binary stream
	#
	class _BinaryWrapper(object):

		def __init__(self, f):
			self.__f = f
		#

		def write(self, textData):
			self.__f.write(textData.encode("utf-8"))
		#

		def close(self):
			self.__f.close()
		#

	#

	def __init__(self, filePath, bSafeWrite:bool = True, compression:str = None):
		self.__filePath = filePath
		self.__bSafeWrite = bSafeWrite
		if self.__bSafeWrite:
			self.__filePathTmp = filePath + ".tmp"
		self.__bToBinary = False

		self.__format = None
		if compression:
			if (compression == "gzip") or (compression == "gz"):
				self.__open = gzip.open
				self.__bToBinary = True
			elif (compression == "bz2") or (compression == "bzip2"):
				self.__open = bz2.open
				self.__bToBinary = True
			elif compression == "lzma":
				self.__format = lzma.FORMAT_ALONE
				self.__open = lzma.open
				self.__bToBinary = True
			elif compression == "xz":
				self.__format = lzma.FORMAT_XZ
				self.__open = lzma.open
				self.__bToBinary = True
			else:
				raise Exception("Unknown compressor: " + compression)
		else:
			self.__open = open
	#

	def __enter__(self):
		if self.__bSafeWrite:
			if self.__bToBinary:
				if self.__format:
					self.__f = openWriteText._BinaryWrapper(self.__open(self.__filePathTmp, "wb", format=self.__format))
				else:
					self.__f = openWriteText._BinaryWrapper(self.__open(self.__filePathTmp, "wb"))
			else:
				if self.__format:
					self.__f = self.__open(self.__filePathTmp, "w", format=self.__format)
				else:
					self.__f = self.__open(self.__filePathTmp, "w")
		else:
			if self.__bToBinary:
				if self.__format:
					self.__f = openWriteText._BinaryWrapper(self.__open(self.__filePath, "wb", format=self.__format))
				else:
					self.__f = openWriteText._BinaryWrapper(self.__open(self.__filePath, "wb"))
			else:
				if self.__format:
					self.__f = self.__open(self.__filePath, "w", format=self.__format)
				else:
					self.__f = self.__open(self.__filePath, "w")
		return self.__f
	#

	def __exit__(self, *args):
		self.__f.close()
		if self.__bSafeWrite:
			if os.path.isfile(self.__filePath):
				os.unlink(self.__filePath)
			os.rename(self.__filePathTmp, self.__filePath)
	#

#

class openWriteJSON(object):

	#
	# Write JSON data to an underlying text stream
	#
	class _JSONWrapper(object):

		def __init__(self, f, bPretty:bool):
			self.__f = f
			self.__bPretty = bPretty
		#

		def write(self, objData):
			assert isinstance(objData, (bool, int, float, str, tuple, list, dict, None))
			if self.__bPretty:
				self.__f.write(json.dumps(objData, indent="\t", sort_keys=True))
			else:
				self.__f.write(json.dumps(objData))
		#

		def close(self):
			self.__f.close()
		#

	#

	class _BinaryWrapper(object):

		def __init__(self, f):
			self.__f = f
		#

		def write(self, textData):
			self.__f.write(textData.encode("utf-8"))
		#

		def close(self):
			self.__f.close()
		#

	#

	def __init__(self, filePath, bSafeWrite:bool = True, compression:str = None, bPretty:bool = False):
		self.__filePath = filePath
		self.__bSafeWrite = bSafeWrite
		if self.__bSafeWrite:
			self.__filePathTmp = filePath + ".tmp"
		self.__bToBinary = False
		self.__bPretty = bPretty

		self.__format = None
		if compression:
			if (compression == "gzip") or (compression == "gz"):
				self.__open = gzip.open
				self.__bToBinary = True
			elif (compression == "bz2") or (compression == "bzip2"):
				self.__open = bz2.open
				self.__bToBinary = True
			elif compression == "lzma":
				self.__format = lzma.FORMAT_ALONE
				self.__open = lzma.open
				self.__bToBinary = True
			elif compression == "xz":
				self.__format = lzma.FORMAT_XZ
				self.__open = lzma.open
				self.__bToBinary = True
			else:
				raise Exception("Unknown compressor: " + compression)
		else:
			self.__open = open
	#

	def __enter__(self):
		if self.__bSafeWrite:
			if self.__bToBinary:
				if self.__format:
					self.__f = openWriteJSON._BinaryWrapper(self.__open(self.__filePathTmp, "wb", format=self.__format))
				else:
					self.__f = openWriteJSON._BinaryWrapper(self.__open(self.__filePathTmp, "wb"))
			else:
				if self.__format:
					self.__f = self.__open(self.__filePathTmp, "w", format=self.__format)
				else:
					self.__f = self.__open(self.__filePathTmp, "w")
		else:
			if self.__bToBinary:
				if self.__format:
					self.__f = openWriteJSON._BinaryWrapper(self.__open(self.__filePath, "wb", format=self.__format))
				else:
					self.__f = openWriteJSON._BinaryWrapper(self.__open(self.__filePath, "wb"))
			else:
				if self.__format:
					self.__f = self.__open(self.__filePath, "w", format=self.__format)
				else:
					self.__f = self.__open(self.__filePath, "w")
		self.__f = openWriteJSON._JSONWrapper(self.__f, self.__bPretty)
		return self.__f
	#

	def __exit__(self, *args):
		self.__f.close()
		if self.__bSafeWrite:
			if os.path.isfile(self.__filePath):
				os.unlink(self.__filePath)
			os.rename(self.__filePathTmp, self.__filePath)
	#

#





def writePrivateBinaryFile(binaryData, filePath:str):
	assert isinstance(filePath, str)
	assert isinstance(binaryData, (bytes, bytearray))

	try:
		os.remove(filePath)
	except OSError:
		pass

	umask_original = os.umask(0)
	try:
		fdesc = os.open(filePath, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
	finally:
		os.umask(umask_original)

	with os.fdopen(fdesc, "wb") as fout:
		fout.write(binaryData)
#



def writePrivateJSONFile(jsonData, filePath:str, bPretty:bool = False):
	assert isinstance(filePath, str)
	assert isinstance(jsonData, (int, float, bool, str, list, tuple, dict))

	if bPretty:
		s = json.dumps(jsonData, indent="\t", sort_keys=True)
	else:
		s = json.dumps(jsonData)

	writePrivateBinaryFile(s.encode("utf-8"), filePath)
#



def loadBinaryFile(filePath:str):
	assert isinstance(filePath, str)

	with open(filePath, "rb") as fin:
		return fin.read()
#







