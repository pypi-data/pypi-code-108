#! /usr/bin/env python

import hashlib
import base64

from .misc import url_decode
from .WebSocketHandler import WebSocketHandler

class WebSocketInterface(object):
	def __init__(self, host=None, host_kwargs=None, host_addr_kwargs=None, web_dispatcher_ident=None, dispatcher_level=None, recv_timeout=None):
		if host_kwargs is None:
			host_kwargs = {}
		if host_addr_kwargs is None:
			host_addr_kwargs = {}
		if web_dispatcher_ident is None:
			disp_type = 'web'
		else:
			disp_type = ('web',web_dispatcher_ident)

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
		self.recv_timeout = recv_timeout
		self.host.get_specialized_dispatcher(disp_type).add_resource_handler(self.identify_request, self.handle_request, 'WebInterface', level=dispatcher_level, call_after_handled=self.after_http_handled, override_status_code=101)
	
	def identify_request(self, req_info={'url':None, 'method':None, 'headers':None, 'body':None, 'clientsocket': None, 'web_request_handler': None, 'extra_response_headers':{}}): # pylint: disable=W0102
		if req_info['method'] in self.resource_dict:
			url_no_browseparams = req_info['url'].split('?')[0] # remove and ignore anything after a question mark
			for (url_prefix, url_param_count, params) in self.get_possible_split_url_params(url_no_browseparams):
				if url_prefix in self.resource_dict[req_info['method']]:
					if url_param_count in self.resource_dict[req_info['method']][url_prefix]:
						callbacks_dict = self.resource_dict[req_info['method']][url_prefix][url_param_count]
						callback = callbacks_dict['http_callback']
						args = (req_info['body'],) + params
						websocket_callbacks = {
							'connected': callbacks_dict['connected'],
							'msg_received': callbacks_dict['received'],
							'closed': callbacks_dict['closed'],
						}
						return (callback, websocket_callbacks, args, req_info['clientsocket'], req_info['web_request_handler'], req_info['headers'], req_info['extra_response_headers'])
		return None
	
	def handle_request(self, callback, _websocket_callbacks, args, _clientsocket, _web_request_handler, headers, extra_response_headers):
		_version = headers['Sec-WebSocket-Version'] # only valid value is "13"
		_upgrade_value = headers['Upgrade'] # only valid value is "websocket"
		extra_response_headers['Upgrade'] = 'websocket'
		extra_response_headers['Connection'] = 'Upgrade'
		extra_response_headers['Sec-WebSocket-Accept'] = WebSocketInterface.calc_response_nonce(headers['Sec-WebSocket-Key'])
		if callback is None:
			return b''
		return callback(*args)
	
	def after_http_handled(self, _callback, websocket_callbacks, args, clientsocket, web_request_handler, _headers, _extra_response_headers):
		def msg_received(msg):
			if websocket_callbacks['msg_received'] is not None:
				websocket_callbacks['msg_received'](handler, msg, *args)
		clientsocket.settimeout(self.recv_timeout)
		handler = WebSocketHandler(web_request_handler, msg_received)
		if websocket_callbacks['connected'] is not None:
			websocket_callbacks['connected'](handler, *args)
		handler.run()
		if websocket_callbacks['closed'] is not None:
			websocket_callbacks['closed'](handler, *args)
	
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
	
	def connect(self, resource, connected=None, received=None, closed=None, http_action=None, method='GET', body_included=False):
		def getattr_if_str(action):
			if isinstance(action, str):
				return getattr(self, action)
			else:
				return action
		connected_callback = getattr_if_str(connected)
		received_callback = getattr_if_str(received)
		closed_callback = getattr_if_str(closed)
		http_callback = getattr_if_str(http_action)
		self.connect_callback(resource, connected_callback, received_callback, closed_callback, http_callback, method, body_included=body_included)
	
	def connect_callback(self,resource,connected=None,received=None,closed=None,http_callback=None,method='GET', body_included=False):
		"""
		connects a specified callback (function) in this object
		to the specified resource (URL)
		and http method (GET/PUT/POST/DELETE)
		"""
		def gen_callback_no_body(cb, body_pos=0):
			def sub_callback(*args):
				return cb(*(args[:body_pos] + args[body_pos+1:]))
			if cb is not None:
				return sub_callback
			else:
				return None
		def gen_callback_no_body_if_inluded(cb, body_pos=0):
			if body_included:
				return cb
			else:
				return gen_callback_no_body(cb, body_pos=body_pos)
		self.dispatcher = self.host.get_dispatcher()
		if method not in self.resource_dict:
			self.resource_dict[method] = {}
		(url_prefix, url_param_count) = self.split_url_params(resource)
		if url_prefix not in self.resource_dict[method]:
			self.resource_dict[method][url_prefix] = {}
		self.resource_dict[method][url_prefix][url_param_count] = {
			'http_callback':gen_callback_no_body_if_inluded(http_callback),
			'connected':gen_callback_no_body_if_inluded(connected, body_pos=1),
			'received':gen_callback_no_body_if_inluded(received, body_pos=2),
			'closed':gen_callback_no_body_if_inluded(closed, body_pos=1),
		}
		# log this connection on the host
		self.host.get_docs().log_connection(resource,http_callback,method, websock_actions={
			'connected':connected,
			'received':received,
			'closed':closed,
		})
	def start_service(self):
		self.host.start_service()
	def stop_service(self):
		self.host.stop_service()
	
	@staticmethod
	def calc_response_nonce(client_nonce):
		nonce_hash=hashlib.sha1()
		nonce_hash.update(client_nonce.encode('utf-8'))
		nonce_hash.update(b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
		return base64.b64encode(nonce_hash.digest()).decode('utf-8')
