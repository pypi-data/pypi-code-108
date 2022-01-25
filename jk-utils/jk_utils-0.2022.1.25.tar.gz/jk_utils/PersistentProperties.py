import os
import json




#
# Maybe use https://stackoverflow.com/questions/18406165/creating-a-timer-in-python/18406263
# in order to delay writes for 2 seconds?
#




class PersistentProperties(object):

	def __init__(self, filePath:str, bAutoStore:bool = True):
		self.__filePath = filePath
		self.__data = self.__tryLoad()
		self.__bChanged = False
		self.__bAutoStore = bAutoStore
	#

	@property
	def isAutoStore(self):
		return self.__bAutoStore
	#

	@property
	def isChanged(self):
		return self.__bChanged
	#

	def __tryLoad(self):
		if os.path.isfile(self.__filePath):
			with open(self.__filePath, "r") as f:
				return json.loads(f.read())
		else:
			dirPath = os.path.dirname(self.__filePath)
			if not os.path.isdir(dirPath):
				raise Exception("Won't be able to store persistent data: Directory does not exist!")
			return {}
	#

	def put(self, key:str, value):
		assert isinstance(key, str)
		assert isinstance(value, (int, float, str, type(None), list, tuple, dict))

		if key in self.__data:
			if value != self.__data[key]:
				self.__data[key] = value

				if self.__bAutoStore:
					self.__store()
				else:
					self.__bChanged = True
		else:
			self.__data[key] = value

			if self.__bAutoStore:
				self.__store()
			else:
				self.__bChanged = True
	#

	def get(self, key:str, defaultValue = None):
		assert isinstance(key, str)

		return self.__data.get(key, defaultValue)
	#

	def remove(self, key:str):
		assert isinstance(key, str)

		if key in self.__data:
			del self.__data[key]

			if self.__bAutoStore:
				self.__store()
			else:
				self.__bChanged = True
	#

	def store(self):
		if self.__bChanged:
			self.__store()
			self.__bChanged = False
	#

	def __store(self):
		with open(self.__filePath, "w") as f:
			f.write(json.dumps(self.__data))
	#

#







