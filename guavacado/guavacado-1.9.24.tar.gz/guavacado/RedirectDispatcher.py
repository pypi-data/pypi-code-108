#! /usr/bin/env python

from .misc import generate_redirect_page_w_statuscode, init_logger
from .WebRequestHandler import WebRequestHandler

from .version_number import guavacado_version
WebServerNameAndVer = "Guavacado/"+guavacado_version


class RedirectDispatcher(object):
	'''handles requests by identifying function based on the URL, then dispatching the request to the appropriate function'''
	def __init__(self, timeout=None, target_domain='https://localhost/'):
		self.log_handler = init_logger(__name__)
		self.timeout = timeout
		self.target_domain = target_domain

	def handle_connection(self, clientsocket, address, client_id):
		handler = WebRequestHandler(clientsocket, address, client_id, self.request_handler, timeout=self.timeout)
		handler.handle_connection()
	
	def request_handler(self, url=None, method=None, headers=None, body=None):
		_method=method # suppressing linter messages
		_headers=headers
		_body=body
		if url[0]=='/':
			rel_url = url[1:]
		else:
			rel_url = url
		if self.target_domain[-1]=='/':
			sep = ''
		else:
			sep = '/'
		dest = self.target_domain + sep + rel_url
		return generate_redirect_page_w_statuscode(dest)
