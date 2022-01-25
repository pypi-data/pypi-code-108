


"""
from .EnumBase import EnumBase



################################################################################################################################
## class EnumNodeType
################################################################################################################################

class EnumNodeType(EnumBase):

	# The element contains a boolean value
	BOOLEAN = 10, 'boolean'
	# The element contains an integer value
	INTEGER = 20, 'integer'
	# The element contains a floatingpoint value
	FLOAT = 30, 'float'
	# The element contains a text that does not exceed 255 characters
	STRING = 40, 'string'
	# The element contains a larger amount of text (CLOB)
	TEXT = 50, 'text'
	# The element contains a timestamp (since epoch)
	TIMESTAMP = 60, 'timestamp'
	# The element contains a temperature value
	TEMPERATURE = 70, 'temperature'

	# The element contains a string list
	STRINGLIST = 140, 'stringlist'

	# The element is a new node with data.
	NODE = 200, 'node'
	# The element is a list of nodes.
	NODELIST = 210, 'nodelist'
	# The element is a map of nodes (with keys of type 'string').
	NODEMAP = 220, 'nodemap'

#




################################################################################################################################
## class DataNode
################################################################################################################################

class DataNode(dict):

	def __init__(self):
		super().__init__()

		self.description = None
	#

	def setValueIfNotNone(self, key:str, value):
		if value is None:
			return
		self[key] = value
	#

	def setIntIfNotNone(self, key:str, value):
		if value is None:
			return
		if not isinstance(value, int):
			value = int(value)
		self[key] = value
	#

	def setFloatIfNotNone(self, key:str, value):
		if value is None:
			return
		if not isinstance(value, float):
			value = float(value)
		self[key] = value
	#

	def setStrIfNotNone(self, key:str, value):
		if value is None:
			return
		if not isinstance(value, str):
			value = str(value)
		self[key] = value
	#

	def appendToListIfNotNone(self, key:str, value):
		if key in self:
			myList = self[key]
			if not isinstance(myList, list):
				raise Exception("Element at key '" + key + "' is of type '" + str(type(myList)) + "', not of type 'list'!")
			if value is None:
				return
		else:
			if value is None:
				return
			myList = []
			self[key] = myList
		myList.append(value)
	#

	def getCreateList(self, key:str):
		if key in self:
			myList = self[key]
			if not isinstance(myList, list):
				raise Exception("Element at key '" + key + "' is of type '" + str(type(myList)) + "', not of type 'list'!")
		else:
			myList = []
			self[key] = myList
		return myList
	#

#




################################################################################################################################
## class DataNodeDef
################################################################################################################################

#
# This class represents a node description: A specification of the type of data node generated.
#
class DataNodeDef(object):

	#
	# Initialization method
	#
	def __init__(self, name:str, nodeType:EnumNodeType, bMandatory:bool = False, description:str = None, children:list = None):
		assert isinstance(name, (type(None), str))
		assert isinstance(nodeType, EnumNodeType)
		assert isinstance(bMandatory, bool)
		assert isinstance(description, (type(None), str))
		assert isinstance(children, (type(None), list))

		self.__name = name
		self.__nodeType = nodeType
		self.__bMandatory = bMandatory
		self.__description = description
		self.__children = children
	#

	@property
	def children(self):
		return self.__children
	#

	@property
	def name(self):
		return self.__name
	#

	@property
	def nodeType(self):
		return self.__nodeType
	#

	@property
	def isMandatory(self):
		return self.__bMandatory
	#

	@property
	def description(self):
		return self.__description
	#

	def toJSON(self):
		ret = {
			"name": self.__name,
			"type": str(self.__nodeType),
			"mandatory": self.__bMandatory,
			"description": self.__description
		}
		if self.__children:
			jsonChildren = []
			ret["children"] = jsonChildren
			for c in self.__children:
				jsonChildren.append(c.toJSON())
		return ret
	#

	def dump(self, prefix:str=None, printFunc:callable=None):
		if prefix is None:
			prefix = ""
		if printFunc is None:
			printFunc = print

		s = "DataNodeDef( "
		if self.__name:
			s += "\"" + repr(self.__name)[1:-1] + "\""
		else:
			s += "---"
		s += ": " + str(self.__nodeType)
		if self.__bMandatory:
			s += ", mandatory"
		if self.__children:
			printFunc(prefix + s + ", children=[")
			for c in self.__children:
				c.dump(prefix + "\t", printFunc)
			printFunc(prefix + "])")
		else:
			printFunc(prefix + s + " )")
	#

	@staticmethod
	def fromJSON(jsonData:dict):
		name = jsonData.get("name", None)
		nodeType = EnumNodeType.parse(jsonData["type"])
		bMandatory = jsonData.get("mandatory", None)
		description = jsonData.get("description", None)
		children = None
		if "children" in jsonData:
			children = []
			for c in jsonData["children"]:
				children.append(DataNodeDef.fromJSON(c))
		return DataNodeDef(name, nodeType, bMandatory, description, children)
	#

#
"""













