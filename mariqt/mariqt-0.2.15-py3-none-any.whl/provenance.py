import os
import yaml
import datetime

import mariqt.core as miqtc
import mariqt.variables as miqtv
import mariqt.settings as miqts


class Provenance:

	def __init__(self,executable:str,version:str = "",arguments:list = [],prev_provenances:list = []):
		""" Creates a provenance object

		Creates a new provenance object with or without catching up on a provenance history,
		depending on whether paths to valid previous provenance files are given
		Provide the arguments in a dict like so: ['name':...,'value':...[,'hash':...]] where the
		hash is optional but required for files. If a file path is given without a hash
		this function will compute it.
		"""

		if version == "":
			version = miqtv.version

		self.executable = executable
		self.version = version
		self.prov = []
		self.prev_hashes = []
		self.logs = []
		self.arguments = []

		if prev_provenances != []:
			for prev_provenance in prev_provenances:
				if isinstance(prev_provenance,dict) and 'path' in prev_provenance and 'name' in prev_provenance:
					tmp = getLastProvenanceFile(prev_provenance['path'],prev_provenance['name'])
					if len(tmp) == 1:
						prev_provenance = tmp[0]
					else:
						continue
				self.addPreviousProvenance(prev_provenance)

		# Validate that the arguments dict has an appropriate format
		# and hash files in arguments (if hashes are not available)
		for i in range(0,len(arguments)):
			if 'name' in arguments[i] and 'value' in arguments[i]:
				if not 'hash' in arguments[i]:
					self.addArgument(arguments[i]['name'],arguments[i]['value'])
				else:
					self.addArgument(arguments[i]['name'],arguments[i]['value'],hash)
			else:
				raise ValueError("argument",i," has no name or no value")


	def addPreviousProvenance(self,prev_provenance):
		""" Adds a file's content as a previous provenance information.

		The file dost not have to contain a valid provenance yaml format.
		In case it does, this information is copied.
		In case it does not, only the log block will be populated.
		"""

		if isinstance(prev_provenance,list):
			if len(prev_provenance) == 0:
				return
			else:
				prev_provenance = prev_provenance[0]

		miqtc.assertExists(prev_provenance)
		tmp_prev_hash = miqtc.md5HashFile(prev_provenance)

		with open(prev_provenance) as file:

			file_name = os.path.basename(prev_provenance)
			file_content = file.read()
			file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(prev_provenance),tz=datetime.timezone.utc)

			try:
				tmp_prov = yaml.load(file_content)
				if not 'provenance' in tmp_prov:
					# This is a yaml file but not in the expected mariqt provenance style
					self.prov.append({'executable':{'name':file_name},'log':file_content,'time':file_mtime.strftime(miqtv.date_formats['mariqt'])})
				else:
					# This is a mariqt provenance file, just copy its entire content
					for tp in tmp_prov['provenance']:
						self.prov.append(tp)
			except:
				# This is not a yaml file, just dump it as a log file into the provenance list
				self.prov.append({'executable':{'name':file_name},'log':file_content,'time':file_mtime.strftime(miqtv.date_formats['mariqt'])})

		self.prev_hashes.append(tmp_prev_hash)


	def log(self,txt,show:bool = False):
		""" Add a text string to the log and eventually show (i.e. print) it."""

		if isinstance(txt,str) and txt != "":
			self.logs.append(txt)
			if show:
				print(txt)
		elif isinstance(txt,list) and txt != []:
			self.logs += txt


	def addArgument(self,name,value,hash:str = "",overwrite=False):
		""" Adds one argument to the provenance arguments list"""
		i = 0
		for p in self.arguments:
			if p['name'] == name:
				if overwrite:
					del self.arguments[i]
				else:
					print("argument",name,"already set")
					return
			i += 1

		if hash == "" and isinstance(value,str) and os.path.exists(value) and os.path.isfile(value):
			hash = miqtc.md5HashFile(value)

		if hash == "":
			self.arguments.append({'name':name,'value':value})
		else:
			self.arguments.append({'name':name,'value':value,'hash':hash})


	def addUsedSettings(self,cfg:miqts.Settings):
		""" Adds all used settings from a settings object to the provenance arguments."""
		for u in cfg.used():
			if not isinstance(cfg[u],dict) and not isinstance(cfg[u],list):
				self.addArgument(u,cfg[u])


	def write(self,path:str,name:str = ""):
		""" Write the provenance info to disk.

		The provenance file is created in the folder given by path and named:
		<name>_provenance-<executable>-<datetime>.yaml"""

		miqtc.assertExists(path)

		now = datetime.datetime.now(tz=datetime.timezone.utc)

		if name != "" and name[-1] != "_":
			name += "_"
		write_path = miqtc.assertSlash(path) + name + "provenance_" + self.executable + "_" + now.strftime(miqtv.date_formats['mariqt_files']) + ".yaml"

		with open(write_path,"w") as yaml_doc:

			# Append provenance information of this process to the general provenance dict
			self.prov.append({'executable':{'name':self.executable,'version':self.version},'arguments':self.arguments,'log':self.logs,'hashes':self.prev_hashes,'time':now.strftime(miqtv.date_formats['mariqt'])})

			yaml.dump({'provenance':self.prov},yaml_doc)

			del self.prov[-1]


def getLastProvenanceFile(path:str,search_str:str,graceful:bool=False):
	if not os.path.exists(path):
		if graceful:
			return []
		else:
			raise Exception(path+" does not exist, cannot search provenance files there")
	files = os.listdir(path)
	max_dt = datetime.datetime(1970,1,1,0,0)
	max_file = False
	for file in files:
		if search_str in file:
			tmp = file.replace(".yaml","").split("_")
			try:
				dt = datetime.datetime.strptime(tmp[-2]+"_"+tmp[-1]+"+0000",miqtv.date_formats['mariqt_files']+"%z")
				if dt.timestamp() > max_dt.timestamp():
					max_dt = dt
					max_file = file
			except:
				continue
	if not max_file == False:
		return [path+max_file]
	else:
		return []
