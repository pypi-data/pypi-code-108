#! /usr/bin/env python
'''
	"Basic" authentication scheme handler
'''
import base64

class BasicAuth(object):
	'''
		"Basic" authentication scheme handler
	'''
	def __init__(self, auth_handler=None, auth_dict=None, realm='Guavacado Server'):
		self.auth_type = "Basic"
		self.realm = realm
		self.auth_dict = auth_dict
		self.auth_handler = auth_handler
		if self.auth_handler is None:
			self.auth_handler = self.check_auth_dict
	
	def authenticate(self, _auth_type, credentials):
		'''Convert the credentials to plain-text and call auth_handler to check if they are valid'''
		decoded = base64.b64decode(credentials).decode('utf-8')
		username, password = tuple(decoded.split(':',1))
		return self.auth_handler(username, password)
	
	def check_auth_dict(self, username, password):
		'''checks the `auth_dict` dictionary for the given username and password combination'''
		if self.auth_dict is None:
			return False
		if username not in self.auth_dict:
			return False
		if self.auth_dict[username]==password:
			return True
		return False
