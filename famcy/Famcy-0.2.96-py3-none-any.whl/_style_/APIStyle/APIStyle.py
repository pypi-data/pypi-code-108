import Famcy
import json
from flask import render_template

class APIStyle(object):
	def __init__(self):
		super(APIStyle, self).__init__()
		self.action = None
		self.return_dict = {"indicator": False, "message": ""}

	def setReturnValue(self, indicator=None, message=None):
		if indicator:
			self.return_dict["indicator"] = indicator
		if message:
			self.return_dict["message"] = message
	def setAction(self, action=None):
		if action:
			self.action = action

	def render(self, *args, **kwargs):
		if self.action:
			self.action()
		return json.dumps(self.return_dict)
