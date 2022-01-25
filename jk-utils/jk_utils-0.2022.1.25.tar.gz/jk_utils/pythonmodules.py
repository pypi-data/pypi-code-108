

import sys
from typing import Union

from jk_version import Version




class PythonModuleInfo(object):

	def __init__(self, m):
		try:
			self.location = m.__file__
			if self.location.endswith("/__init__.py"):
				self.location = self.location[:-len("/__init__.py")]
		except:
			self.location = "???"
		try:
			self.version = m.__version__
			self.__v = Version(m.__version__)
		except:
			self.version = "???"
			self.__v = None
		self.name = m.__name__
	#

	def __str__(self):
		return self.name + " : " + self.version
	#

	def __repr__(self):
		return "<PythonModuleInfo: " + self.name + ", " + self.version + ", " + self.location + ">"
	#

	def isAtLeastVersion(self, expectedMinimumVersion:Union[str,Version]):
		if isinstance(expectedMinimumVersion, str):
			expectedMinimumVersion = Version(expectedMinimumVersion)
		else:
			assert isinstance(expectedMinimumVersion, Version)

		if self.__v is None:
			return False
		else:
			return expectedMinimumVersion >= self.__v
	#

#


 
class PythonModules(object):

	def __init__(self):
		self.__moduleInfos = self.__listLoadedModules()
	#

	def dump(self, prefix:str = "", printFunction = None):
		if printFunction is None:
			printFunction = print
		else:
			assert callable(printFunction)

		for moduleInfo in self.__moduleInfos:
			printFunction(prefix + str(moduleInfo))
	#

	def moduleInfos(self):
		return self.__moduleInfos
	#

	def getModuleInfo(self, moduleName):
		for m in self.__moduleInfos:
			if m.name == moduleName:
				return m
		return None
	#

	def ensureRequirementsAreMatched(self, moduleNameVersionMap:dict):
		for moduleName, requiredVersion in moduleNameVersionMap.items():
			m = self.getModuleInfo(moduleName)
			if m is None:
				raise Exception("No such module: " + moduleName)

			if requiredVersion:
				if m.isAtLeastVersion(requiredVersion):
					# okay!
					pass
				else:
					raise Exception("Version of module " + m.name + " is " + m.version + " but version " + str(requiredVersion) + " is required!")
	#

	def __listLoadedModules(self) -> tuple:
		moduleNames = set()
		for m in sys.modules:
			p = m.find(".")
			if p > 0:
				moduleNames.add(m[:p])
		moduleNames = sorted(moduleNames)
		#modulenames = set(asys.modules) & set(globals())
		allmodules = [sys.modules[name] for name in moduleNames]
		return tuple([ PythonModuleInfo(m) for m in allmodules ])
	#

#


