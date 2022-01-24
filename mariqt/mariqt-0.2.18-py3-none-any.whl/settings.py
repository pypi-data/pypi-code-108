import os
import json
try:
	import yaml
except ModuleNotFoundError as er:
    raise ModuleNotFoundError(str(er.args) + "\n Install with e.g. $ pip install pyyaml")


def parseReplaceVal(cfg:dict,key:str):
	""" Uses the fields in cfg to replace any placeholders (___KEY1:KEY2___) in the value cfg[key] by the respective values in cfg"""
	if not key in cfg:
		raise Exception("key",key,"not in", cfg)

	val = cfg[key]
	if isinstance(val,dict) or isinstance(val,list) or isinstance(val,int) or isinstance(val,float):
		return val
	vals = val.split("___")
	for i in range(1,len(vals),2):
		if not vals[i].lower() in cfg:
			raise Exception("key",vals[i].lower(),"referenced in field",key,"not in", cfg)
		val = val.replace("___"+vals[i]+"___",cfg[vals[i].lower()])
	return val


class Settings:

	def __init__(self,params:dict = {},path:str = "",default:bool = False,project:str = ""):

		if len(params) > 0:
			self.settings = params
		elif default:
			self.loadProjectDefault(project)
		elif not path == "":
			miqtc.assertExists(path)
			self.load(path,ft)
		self.used_settings = []

	def load(self,path:str):
		""" Tries to read a json or yaml file from disk and returns the entire content as a dict"""

		file_name, ft = os.path.splitext(path.lower())

		if ft == ".json":
			with open(path,encoding='utf8',errors='ignore') as f:
				self.settings = json.load(f)
		elif ft == ".yaml":
			with open(path,encoding='utf8',errors='ignore') as f:
				self.settings = yaml.safe_load(f)
		else:
			raise ValueError("Could not find config file parser for type "+ ft)


	def loadProjectDefault(self,project:str = ""):
		""" Expects a file called <project>_curation-settings.yaml in a folder ../files/ relative to the current work directory, loads it and returs the content"""

		path = "../files/"
		if not os.path.exists(path):
			raise ValueError("Path for config file not found:",path)
		files = os.listdir(path)
		found = []
		for file in files:
			if project != "" and file == project+"_curation-settings.yaml":
				found.append(file)
				break
			elif project == "" and "_curation-settings.yaml" in file:
				found.append(file)
		if len(found) == 0:
			raise ValueError("No config file found in:",path)
		elif len(found) > 1:
			raise ValueError("More than one config file found in:",path)
		else:
			self.load(path+found[0])


	def val(self, key:str):
		""" Tries to return a value from a configuration file

		Nice thing is it employs a URN like syntax so to descend into the configuration file content use something like cfgValue(cfg,'key-a:key-1:key-N')
		"""

		keys = key.split(":")
		ar = self.settings
		for k in keys:
			if k in ar:
				ar = ar[k]
			else:
				try:
					k = int(k)
					if len(ar) < k:
						raise ValueError("Index",k,"out of bounds",len(ar))
				except:
					raise ValueError("Could not parse int",k)
				ar = ar[k]
		return ar


	def __getitem__(self, key:str):
		""" Tries to parse a value from a configuration file meaning that placeholder variables (___<var>___) are replaced by available content"""

		val = self.val(key)

		if not key in self.used_settings:
			self.used_settings.append(key)

		if isinstance(val,dict) or isinstance(val,list) or isinstance(val,int) or isinstance(val,float):
			return val
		vals = val.split("___")
		for i in range(1,len(vals),2):
			val = val.replace("___"+vals[i]+"___",self.val(vals[i].lower()))
		return val

	def __setitem__(self,key:str,val):
		""" Sets a value in the dict, specified by the given key (also allows URN notation)"""

		keys = key.split(":")
		ar = self.settings

		for i,k in enumerate(keys):
			if k in ar:
				ar = ar[k]
			else:
				if i == len(keys)-1:
					ar[k] = val
				else:
					ar[k] = {}


	def getDefaultAndOverload(self, default_key:str, overload_key:str):
		""" Returns the dict behind default_key and overloads its values with those behind the overload_key."""

		default = {}
		for val in self[default_key]:
			default[val] = self[default_key][val]
		for val in self[overload_key]:
			default[val] = self[overload_key][val]
		return default


	def used(self):
		""" Returns a list of key names for all settings values that were requested from this settings object."""
		return self.used_settings

	def resetUsed(self):
		""" Resets the list of used variables."""
		self.used_settings = []
