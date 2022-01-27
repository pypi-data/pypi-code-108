import os
import sys
import enum
import importlib
from os import listdir

from gadgethiServerUtils.GadgethiClient import *
from gadgethiServerUtils.file_basics import *

import hmac
from hashlib import sha1
from flask import session, request, abort
from werkzeug.security import safe_str_cmp

class FamcyFileImportMode(enum.IntEnum):
	name = 0
	fixed = 1

class FamcyManager:
	"""
	This is the class that manage all modules
	importing, file systems, HTTP GET POST functions, 
	etc. Mostly inheritance from the gadgethiServerUtils
	functions -> choosing things that are needed for
	Famcy architecture.
	
	Rep:
		* global_var_dictionary
		* http_client

	Method:
		* __getitem__
		* __setitem__
		* main
		* console
		* importclass
		* importclassdir
		* read
		* init_http_client
	"""
	def __init__(self, famcy_id, famcy_url, production=False):
		# Constant Definition
		self.PACKAGE_NAME = "Famcy"
		self.USER_DEFAULT_FOLDER = "_CONSOLE_FOLDER_"
		self.USER_STATIC_FOLDER = "_static_"
		self.PRODUCTION_FOLDER = os.path.join(os.path.expanduser("~"), ".local/share/famcy", famcy_id, "console")

		self.famcy_id = famcy_id
		self.main = famcy_url
		self.console = os.path.join(self.main, self.USER_DEFAULT_FOLDER) if not production else self.PRODUCTION_FOLDER
		self.http_client = None
		# Append famcy system path and user console folder path
		sys.path.append(self.main)
		sys.path.append(self.console)

		# Init header definition
		self.global_var_dict = {}
		self.global_var_dict["PACKAGE_NAME"] = self.PACKAGE_NAME
		self.global_var_dict["USER_DEFAULT_FOLDER"] = self.USER_DEFAULT_FOLDER

	def __getitem__(self, key):
		return self.global_var_dict.get(key, None)

	def __setitem__(self, key, item):
		self.global_var_dict[key] = item

	def get(self, key, default=None):
		return self.global_var_dict.get(key, default)

	def get_credentials(self, key, default=""):
		return self.read(self["ConsoleConfig"]["credentials_url"]).get(key, default)

	def read(self, path):
		return read_config_yaml(path)

	def lg_transform(self, group, name, language, reverse=False):
		"""
		This function transform the information to the specific language
		Input	
			- group: Need to be ALL CAPITAL WORDS
			- name: the name you would like to translate
			- language: The language you would like to use
			- * reverse: if True 
		Output
			- string 
		Ex. file
			SEASON_CHOICE:
				season: {"CH": "月票","EN": "Monthly pass"}
				dailyseason: {"CH": "早上優惠票","EN": "Morning pass"}
			SEASON_DATABASE:
				season: {"CH": "月票資料庫","EN": "season database"}
				daily:  {"CH": "月票資料庫"}
		Usage:
			1. Lg_transform("SEASON_CHOICE","season","CH") -> "月票"
			2. Lg_transform("SEASON_CHOICE","dailyseason","EN") -> "Morning pass"
			3. Lg_transform("SEASON_DATABASE","season","EN") -> "season database"
			4. Lg_transform("SEASON_CHOICE","月票","CH",True) -> "season"
		Error Usage:
			In most of case, will return the origin name value to avoid fatal crash.
			However, when reverse=True and the name points to different value will raise error.
			1. Lg_transform("SEASON_DATABASE","月票資料庫","CH",True) -> raise error
		"""
		language_yaml = self.read(self["ConsoleConfig"]["lg_yaml"])

		if reverse:
			if group not in language_yaml.keys():
				raise ValueError("group spelling fail")
			else:
				return_name_list = []
				for i in language_yaml[group].keys():
					try:
						if language_yaml[group][i][language] == name:
							return_name_list.append(i)
					except:
						pass
				if len(return_name_list) == 0:
					raise ValueError("Could not find the specific name for reference")
				elif len(return_name_list) >= 2:
					raise ValueError("Duplicate Return")
				else:
					return_name = return_name_list[0]
		else:
			# print("not here")		
			try:
				return_name = language_yaml[group][name][language]
			except:
				return_name = name

		return return_name

	def init_http_client(self, **configs):
		self.http_client = GadgetHiClient(custom_credentials_loc=self["ConsoleConfig"]["credentials_url"], 
				**configs)

	def get_pruned_url(self, url):
		"""
		This is the helper function
		to get the pruned url without
		/ at the beginning
		"""
		return url if len(url) == 0 or url[0] != "/" else url[1:]

	def get_module_name(self, module):
		"""
		This is the helper function to get the
		module name from the module object. 
		"""
		return module.__name__.split(".")[-1]

	def importclass(self, module_url, class_name, otherwise=None):
		"""
		This is the helper function to help import a class at the
		module url. The otherwise keyword define the alternate return
		if anything wrong happens. 
		- Input:
			* module_url: a string that defines the url to the module. 
				the path must be separated with / and ends without /
			* class_name: a string that defines the class that we 
				are looking for. 
		- Output:
			* The class instance, or otherwise
		"""
		module_string = module_url.replace("/", ".").replace("\\", ".")
		try:
			class_inst = getattr(importlib.import_module(module_string), class_name)
		except:
			class_inst = otherwise

		return class_inst

	def assign_to_global(self, global_dict, system_items):
		"""
		This assign system item modules to 
		global dictionary. 
		"""
		# Check no repeat names
		assert len(system_items) == len(list(set(system_items))), "System Fblocks definition have duplicated names"

		# Assign flocks to global
		for module in system_items:
			block = self.get_module_name(module)
			global_dict[block] = getattr(module, block)

	def importclassdir(self, header_url, module_url, file_import_mode, import_arg, 
			exclude=[], recursive=False, otherwise=None):
		"""
		This is the helper function to import
		all classes from a directory. The way
		the file is imported is depend on file_import_mode. 
		Usage assume the top level directory is full of folders
		and we are looking for name or fixed module in all of
		these folders. 

		name:
			* import the module that is the same name as
			the folder itself.
		fixed:
			* import the module with the name import_arg

		- Input:
			* header_url: a string that defines the url to the module. 
				the path must be separated with / and ends without /.
				Need to prune when importing modules
			* module_url: a string that defines the url to the module. 
				the path must be separated with / and ends without /
			* file_import_mode: FamcyFileImportMode
			* import_arg: arg for specific import mode.
		"""
		# Default return
		ret_list = otherwise

		# Get all dir path
		dir_list = self.listdir_exclude(header_url, module_url, exclude_list=exclude, 
				recursive=recursive, only_dir=True)

		import_dir_list = []
		for dir_path in dir_list:
			# Switch the file import mode. 
			if file_import_mode == FamcyFileImportMode.name:
				module_name = dir_path.split("/")[-1]
			elif file_import_mode == FamcyFileImportMode.fixed:
				module_name = import_arg

			# Import class instance. 
			# Prune root directory
			pruned_url = dir_path + "/" + module_name
			module_string = pruned_url.replace("/", ".").replace("\\", ".")
			try:
				class_inst = importlib.import_module(module_string)
			except Exception as e:
				# Continue if no import lib
				print("Import Error: ", module_string, e)
				continue

			if class_inst:
				import_dir_list.append(class_inst)

		# I think aliasing is ok here
		if import_dir_list != []:
			ret_list = import_dir_list

		return ret_list

	def listdir_exclude(self, header, path, exclude_list=[], recursive=False, 
			only_dir=False):
		"""
		This is the helper function to list
		all the files in the directory: path
		and exclude the exclude list
		- Input:
			path: path for the directory
			exclude_list: exclude the files start with
				entries in exclude_list
		- Return:
			file_list: a list of files that 
			are in the path but not in the exclude
			list. [Full Path]
		"""
		directory_list = []
		for f in listdir(header + path):
			full_path_f = header + path + "/" + f
			# If we only want to return directories, 
			# Check this condition. 
			if only_dir and not os.path.isdir(full_path_f):
				continue

			# Handle exclude list
			for exclude in exclude_list:
				if f.startswith(exclude):
					break
			else:
				# If recursive mode and the file is a directory
				if recursive and os.path.isdir(full_path_f):
					sub_dir_list = self.listdir_exclude(header, path + "/" + f, exclude_list=exclude_list, recursive=recursive, 
						only_dir=only_dir)
					# Extend recursively
					directory_list.extend(sub_dir_list)

				# Add the current path f
				directory_list.append(self.get_pruned_url(path + "/" + f))

		return directory_list

	def register_csrf(self, app):
		"""
		This is the security method to 
		prevent csrf. Prereq: MainBlueprint
		needs to be defined
		"""
		def csrf_token():
			"""
			Generate a token string from bytes arrays. The token in the session is user
			specific.
			"""
			if "_csrf_token" not in session:
				session["_csrf_token"] = os.urandom(128)
			return hmac.new(app.secret_key, session["_csrf_token"],
					digestmod=sha1).hexdigest()

		def check_csrf_token():
			"""Checks that token is correct, aborting if not"""
			if request.method in ("GET",): # not exhaustive list
				return
			token = request.form.get("csrf_token")
			print(request.form)
			if token is None:
				app.logger.warning("Expected CSRF Token: not present")
				abort(400)
			if not safe_str_cmp(token, csrf_token()):
				app.logger.warning("CSRF Token incorrect")
				abort(400)

		app.template_global('csrf_token')(csrf_token)
		app.before_request(check_csrf_token)
