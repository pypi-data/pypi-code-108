#! /usr/bin/env python

from .misc import url_decode

class WebInterface(object):
	"""
	Allows for easily defining web interfaces for the server.

	Expects the variable "self.host" to be set to a WebHost
	object before calling "connect()".

	See implementation of __init__ class for an example initialization.
	"""

	def __init__(self, host=None, host_kwargs={}, host_addr_kwargs={}, web_dispatcher_ident=None, dispatcher_level=None): # pylint: disable=W0102
		if web_dispatcher_ident is None:
			disp_type = 'web'
		else:
			disp_type = ('web',web_dispatcher_ident)

		# starts a WebHost on port 80 that
		if host is None:
			from guavacado import WebHost # pylint: disable=C0415
			self.host = WebHost(**host_kwargs)
			host_addr_kwargs_add = host_addr_kwargs
			if not web_dispatcher_ident is None:
				host_addr_kwargs_add.update({'disp_type': disp_type})
			self.host.add_addr(**host_addr_kwargs_add)
		else:
			self.host = host
		
		self.resource_dict = {}
		self.host.get_specialized_dispatcher(disp_type).add_resource_handler(self.identify_request, self.handle_request, 'WebInterface', level=dispatcher_level)

		# # add lines like the following:
		# self.connect('/test/:id','GET_ID','GET')
		# self.connect('/test/:id',self.GET_ID,'GET')
		# # to call member function GET_ID() with the argument after "/test/" when a GET request
		# # is received for "/test/<any text here>"
	
	def identify_request(self, req_info={'url':None, 'method':None, 'headers':None, 'body':None, 'clientsocket': None, 'extra_response_headers':{}}): # pylint: disable=W0102
		if req_info['method'] in self.resource_dict:
			url_no_browseparams = req_info['url'].split('?')[0] # remove and ignore anything after a question mark
			for (url_prefix, url_param_count, params) in self.get_possible_split_url_params(url_no_browseparams):
				if url_prefix in self.resource_dict[req_info['method']]:
					if url_param_count in self.resource_dict[req_info['method']][url_prefix]:
						callback = self.resource_dict[req_info['method']][url_prefix][url_param_count]
						args = (req_info['body'],) + params
						return (callback, args)
		return None
	
	def handle_request(self, callback, args):
		return callback(*args)
	
	def get_possible_split_url_params(self, url):
		ret = []
		split_url = url.split('/')
		remaining = split_url
		removed = []
		while len(remaining)>0:
			prefix = '/'.join(remaining)
			param_count = len(split_url)-len(remaining)
			params = removed[:param_count]
			if (prefix+'/')==url:
				ret.append((prefix, param_count, params))
				param_count = param_count-1
				params = removed[:param_count]
			params_decoded = []
			for par in params:
				params_decoded.append(url_decode(par))
			params_decoded_tup = tuple(params_decoded)
			ret.append((prefix, param_count, params_decoded_tup))
			removed = [remaining[-1]] + removed
			remaining = remaining[:-1]
		return ret
	
	def split_url_params(self, url):
		split_url = url.split('/:')
		prefix = split_url[0]
		param_count = len(split_url)-1
		return (prefix, param_count)
	
	def connect(self, resource, action, method, body_included=False):
		if isinstance(action, str):
			callback = getattr(self, action)
		else:
			callback = action
		self.connect_callback(resource, callback, method, body_included=body_included)
	
	def connect_callback(self,resource,callback,method, body_included=False):
		"""
		connects a specified callback (function) in this object
		to the specified resource (URL)
		and http method (GET/PUT/POST/DELETE)
		"""
		self.dispatcher = self.host.get_dispatcher()
		if body_included:
			disp_callback = callback
		else:
			def disp_callback(_body, *args):
				return callback(*args)
		if method not in self.resource_dict:
			self.resource_dict[method] = {}
		(url_prefix, url_param_count) = self.split_url_params(resource)
		if url_prefix not in self.resource_dict[method]:
			self.resource_dict[method][url_prefix] = {}
		self.resource_dict[method][url_prefix][url_param_count] = disp_callback
		# log this connection on the host
		self.host.get_docs().log_connection(resource,callback,method)
	def start_service(self):
		self.host.start_service()
	def stop_service(self):
		self.host.stop_service()
