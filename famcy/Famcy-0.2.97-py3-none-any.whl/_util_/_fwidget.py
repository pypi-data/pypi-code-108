import abc
import json
import Famcy
from Famcy._util_._fthread import *
from Famcy._util_._fsubmission import *

class FamcyWidget(metaclass=abc.ABCMeta):
	"""
	This represents the widget interface for
	all Famcy visual objects to follow. 

	Rep:
		* id, name, etc.

	Interface:
		* render(): render the page
		* register(): register the page to the Famcy env
		* preload(): action before the rendering
		* postload(): actions after the rendering
	""" 
	def __init__(self):
		self.id = "famcy"+str(id(self))
		self.name = "famcy_name"+str(id(self))
		self.action = ""
		self.loader = False
		self.parent = None
		self.body = None
		self.clickable = False
		self.configs = {}
		self.attributes = {}

		# Header script
		self.header_script = ""
		self.js_after_func_dict = {} # post js script input
		self.js_after_func_name = "" # post js script function name

		# Style related
		self.css_style_dict = {}

		# Submission related
		self.submission_obj = FSubmission(self)
		self.submission_obj_key = self.id
		self.post_submission_js = ""

		self.link = Famcy.FManager["ConsoleConfig"]["main_url"]+"/"+self.id

	def __setitem__(self, key, value):
		self.attributes[key] = value

	def __getitem__(self, key):
		return self.attributes[key]

	def __delitem__(self, item):
		if item in self.attributes.keys():
			del self.attributes[item]

	def find_parent(self, item, className):
		if not type(item.parent).__name__ == className:
			if item.parent:
				return self.find_parent(item.parent, className)
			else:
				return item.parent
		else:
			return item.parent

	def find_class(self, item, className):
		return_list = []
		if hasattr(item, "layout"):
			for _item, _, _, _, _ in item.layout.content:
				if type(_item).__name__ == className:
					return_list.append(_item)
				return_list.extend(self.find_class(_item, className))

			for _item, _ in item.layout.staticContent:
				if type(_item).__name__ == className:
					return_list.append(_item)
				return_list.extend(self.find_class(_item, className))
		return return_list

	def find_all_widget(self, item):
		return_list = []
		if hasattr(item, "layout"):
			for _item, _, _, _, _ in item.layout.content:
				return_list.append(_item)
				return_list.extend(self.find_all_widget(_item))

			for _item, _ in item.layout.staticContent:
				return_list.append(_item)
				return_list.extend(self.find_all_widget(_item))
		return return_list

	def find_obj_by_id(self, item, obj_id):
		if hasattr(item, "layout"):
			for _item, _, _, _, _ in item.layout.content:
				if _item.submission_obj_key == obj_id:
					return _item.submission_obj
				_children = self.find_obj_by_id(_item, obj_id)
				if _children:
					return _children

			for _item, _ in item.layout.staticContent:
				if _item.submission_obj_key == obj_id:
					return _item.submission_obj
				_children = self.find_obj_by_id(_item, obj_id)
				if _children:
					return _children
		return None

	# def generate_obj_id_dict(self, item):
	# 	return_dict = {}
	# 	if hasattr(item, "layout"):
	# 		for _item, _, _, _, _ in item.layout.content:
	# 			return_dict[_item.submission_obj_key] = _item.submission_obj
	# 			return_dict.update(self.generate_obj_id_dict(_item))

	# 		for _item, _ in item.layout.staticContent:
	# 			return_dict[_item.submission_obj_key] = _item.submission_obj
	# 			return_dict.update(self.generate_obj_id_dict(_item))
	# 	return return_dict
		
	def render(self):
		"""
		The main render flow is as
		follow. 
		1. Check permission
		2. preload function
		3. render inner
		4. start post load thread
		5. return render inner stuffs
		"""
		self.preload()

		self.body = self.render_inner()
		if self.js_after_func_name != "" and self.js_after_func_name:
			script = Famcy.script()
			script.innerHTML = self.js_after_func_name + '("' + self.id + '", ' + json.dumps(self.js_after_func_dict) + ')'
			self.body.addElement(script)
		
		# Set daemon to true to ensure thread dies when main thread dies
		post_thread = FamcyThread(target=self.postload, daemon=True)
		post_thread.start()
		return self.body

	def connect(self, submission_func, target=None):
		"""
		This is the function to setup the
		submission object type. 
		"""
		self.clickable = True
		self.submission_obj.func_link = id(submission_func)
		self.submission_obj.func = submission_func
		self.submission_obj.origin = self
		self.submission_obj.target = target if target else self

	def disconnect(self):
		self.clickable = False
		self.submission_obj.func_link = None
		self.submission_obj.func = None
		self.submission_obj.origin = self
		self.submission_obj.target = self

	def tojson(self):
		_widget_dict = {}
		


		return json.dumps(_widget_dict)

	@abc.abstractmethod
	def render_inner(self):
		"""
		This is the customizable inner render
		function for famcy page. 
		"""
		pass
		
	@abc.abstractmethod
	def preload(self):
		"""
		This is the preload function
		that should be executed before 
		the inner render function. 
		"""
		pass

	@abc.abstractmethod
	def postload(self):
		"""
		After the page is rendered, 
		apply async post load function. 
		"""
		pass