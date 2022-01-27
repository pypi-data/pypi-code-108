import abc
import json
import Famcy

class FElement(metaclass=abc.ABCMeta):
	def __init__(self):
		self.style = {}
		self.classList = []
		self.attributes = {}

		self.innerHTML = ""
		self.html = ""
		self.parentElement = None
		self.children = []
		self.script = []

	def __setitem__(self, key, value):
		if key == "className":
			if value not in self.classList:
				self.classList.append(value)
		else:
			self.attributes[key] = value

	def __getitem__(self, key):
		return self.attributes[key]

	def __delitem__(self, item):
		if item in self.attributes.keys():
			del self.attributes[item]

	def addStaticScript(self, script):
		if script not in self.script:
			self.script.append(script)

	def removeStaticScript(self, script=None):
		if script:
			i = self.script.index(script)
			del self.script[i]

	def addElement(self, child):
		if child not in self.children:
			child.parentElement = self
			self.children.append(child)

	def removeElement(self, child=None, index=None):
		if child and child in self.children:
			i = self.children.index(child)
			del self.children[i]
		elif index and len(self.children) > index:
			del self.children[index]

	def setAttrTag(self):
		"""
		All input should be string
		"""
		return_attr = ""

		_ = ""
		for key, val in self.style.items():
			_ += key + ': ' + val + ';'
		return_attr += ' style="' + _ + '"' if _ != "" else ""

		_ = ""
		for _class in self.classList:
			_ += _class + " "
		return_attr += ' class="' + _[:-1] + '"' if self.classList != [] else ""

		for key, val in self.attributes.items():
			return_attr += ' ' + key + '="' + val + '"'

		return return_attr

	def render_inner(self):
		temp = self.render_element()
		if self.parentElement:
			if not set(self.parentElement.script).intersection(set(self.script)):
				self.parentElement.script.extend(self.script)
		return temp

	def render_script(self):
		# update script
		_ = self.render_inner()
		
		return_script = ""
		for _s in self.script:
			return_script += _s.render_inner()
		return return_script

	@abc.abstractmethod
	def render_element(self):
		"""
		This is the customizable inner render
		function for famcy page. 
		"""
		pass