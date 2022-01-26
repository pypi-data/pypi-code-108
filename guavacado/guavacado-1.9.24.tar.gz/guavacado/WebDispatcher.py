#! /usr/bin/env python

from .misc import init_logger, addr_rep
from .WebRequestHandler import WebRequestHandler

from .version_number import guavacado_version
WebServerNameAndVer = "Guavacado/"+guavacado_version


class WebDispatcher(object):
	'''handles requests by identifying function based on the URL, then dispatching the request to the appropriate function'''
	def __init__(self, addr=None, timeout=None, error_404_page_func=None, auth_handler=None):
		self.log_handler = init_logger(__name__)
		self.addr = addr
		self.timeout = timeout
		self.error_404_page_func = error_404_page_func
		self.resource_handlers = []
		self.auth_handler = auth_handler

	def handle_connection(self, clientsocket, address, client_id):
		def do_nothing(): # blank function for default if call_after_handled not set
			pass
		call_after_handled = {'call_after_handled':do_nothing} # stored as dictionary so that scope of the contained function can edit the value freely
		handler = None
		extra_response_headers = {}
		def request_handler_noclient(url=None, method=None, headers=None, body=None):
			ret = self.request_handler(url=url,method=method,headers=headers,body=body, clientsocket=clientsocket, web_request_handler=handler, extra_response_headers=extra_response_headers)
			handler.add_headers.update(extra_response_headers)
			if ret is not None:
				call_after_handled['call_after_handled'] = ret[1]
				override_status_code = ret[2]
				if override_status_code is not None:
					handler.setSuccessStatusCode(override_status_code)
				return ret[0]
			else:
				return None
		handler = WebRequestHandler(clientsocket, address, client_id, request_handler_noclient, timeout=self.timeout, auth_handler=self.auth_handler)
		handler.handle_connection()
		if call_after_handled['call_after_handled'] is not None:
			call_after_handled['call_after_handled']()
	
	def get_resource_handler_index(self,name):
		for i,r in enumerate(self.resource_handlers):
			if r['name']==name:
				return i

	def add_resource_handler(self,check_valid,handler_callback,name,level=None,call_after_handled=None,override_status_code=None):
		'''
		adds a resource handler to the list of resources to check when handling a request
			check_valid should be a callable which returns a tuple of valid arguments for handler_callback if the resource is valid or None if the resource is invalid
			handler_callback should be a callable which accepts the arguments returned by check_valid and handles the request, then returns the body of the message (in byte form) that should be returned
			level should be None to take precedence over all previous handlers
				or an index of a handler under which it should be placed in priority (returned by a previous call to add_resource_handler)
				or the name of the handler under which it should be placed in priority
			call_after_handled should be a callable which accepts the same arguments as handler_callback, and will be called after handling the http response but before closing the socket
			override_status_code should be None or a numeric status code to override for a successful message (if check_valid returns not Null) - defaults to 200 if None
		'''
		self.log_handler.debug('Adding resource handler "{name}" with valid checker {valid}() and handler {handler}()'.format(name=name,valid=check_valid.__name__,handler=handler_callback.__name__))
		if level is None:
			level = len(self.resource_handlers)
		if isinstance(level, str):
			level = self.get_resource_handler_index(level)
		self.resource_handlers.insert(level, {
			'name':name,
			'valid':check_valid,
			'handler':handler_callback,
			'call_after_handled':call_after_handled,
			'override_status_code':override_status_code,
		})
		return level
	
	def request_handler(self, url=None, method=None, headers=None, body=None, clientsocket=None, web_request_handler=None, extra_response_headers={}): # pylint: disable=W0102
		for handler in reversed(self.resource_handlers):
			req_info = {
				'url':url,
				'method':method,
				'headers':headers,
				'body':body,
				'clientsocket':clientsocket,
				'web_request_handler':web_request_handler,
				'extra_response_headers':extra_response_headers,
			}
			valid = handler['valid'](req_info=req_info)
			def call_after_handled(handler=handler, valid=valid):
				if handler['call_after_handled'] is not None:
					handler['call_after_handled'](*valid)
			if not valid is None:
				return (handler['handler'](*valid), call_after_handled, handler['override_status_code'])

	def get_address_string(self):
		return "{server} Server at {addr}".format(server=WebServerNameAndVer, addr=addr_rep(self.addr, pretty=True))
	
	def get_404_page(self, _request_handler_instance, url=""):
		if not self.error_404_page_func is None:
			return self.error_404_page_func(url=url)
		return ("<html><head><title>404 Not Found</title></head>"+\
		"<body><h1>Not Found</h1><p>The requested URL {url} was not found on this server.</p><hr>"+\
		"<address>{address}</address>"+\
		"</body></html>").format(url=url, address=self.get_address_string())
