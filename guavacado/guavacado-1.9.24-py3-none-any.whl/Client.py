#! /usr/bin/env python
'''
Class allowing client connections to web servers and sockets
'''

import socket
import ssl
import threading
from datetime import datetime
import base64
import os

from .misc import addr_rep, init_logger
from .WebRequestHandler import WebRequestHandler
from .WebSocketHandler import WebSocketHandler
from .ClientCookieStore import ClientCookieStore, ClientCookie
from .WebSocketInterface import WebSocketInterface

class Client(object):
	'''
	Class allowing client connections to web servers and sockets
	'''
	def __init__(self, addr='localhost', port=80, TLS=False, UDP=False, disp_type='web', TLS_check_cert=True):
		self.log_handler = init_logger(__name__)
		self.addr = addr
		self.port = port
		self.TLS = TLS
		self.UDP = UDP
		self.disp_type = disp_type
		self.TLS_check_cert = TLS_check_cert
	
	@staticmethod
	def from_url(url, TLS_check_cert=True):
		'''
		returns a `Client` instance and resource path with settings for the given URL
		- returns: `(client:Client, resource:string)`
			 - `client` - a Client instance with settings (TLS, address, port) derived from the provided URL
			 - `resource` - the path on the server to the resource - can be used directly in the `resource` argument of `Client.request_web`, `Client.request_web_async`, or `Client.open_websocket`
		- `url:string` - the URL to parse
		- `TLS_check_cert:bool` - marks in the `Client` instance whether to validate the certificate from the server - setting this to `False` allows self-signed certificates on the server without errors
		'''
		prot_split = url.split('://',1)
		if len(prot_split)>1:
			protocol = prot_split[0]
			url_noprot = prot_split[1]
		else:
			protocol = 'http'
			url_noprot = url
		if protocol.lower() in ['https', 'wss']:
			TLS = True
		else:
			TLS = False
		host_port_split = url_noprot.split('/',1)
		if len(host_port_split)>1:
			host_port = host_port_split[0]
			resource = '/'+host_port_split[1]
		else:
			host_port = url_noprot
			resource = '/'
		host_split = host_port.split(':',1)
		if len(host_split)>1:
			host = host_split[0]
			try:
				port = int(host_split[1])
			except ValueError:
				host = host_port
				if TLS:
					port = 443
				else:
					port = 80
		else:
			host = host_port
			if TLS:
				port = 443
			else:
				port = 80
		
		return (Client(addr=host, port=port, TLS=TLS, disp_type='web', TLS_check_cert=TLS_check_cert), resource)
	
	@staticmethod
	def request_url(url, method='GET', body=None, TLS_check_cert=True, include_response_headers=False, response_headers_as_lists=False, follow_redir=False, redir_persist_cookies=True, cookie_store=None, timeout=None, extra_headers={}): # pylint: disable=W0102
		'''
		performs a HTTP(S) request to the given URL and returns the response
		- `url:string` - standardized URL for the request, starting with 'http://' or 'https://' - if the protocol is missing (string does not contain '://'), assumes HTTP (non-encrypted)
		- `method:string` - HTTP method for the request - allows any space-free string, but most (almost all) servers will only accept the methods listed at https://datatracker.ietf.org/doc/html/rfc2068#section-5.1.1
		- `TLS_check_cert:bool` - specifies whether to validate the certificate from the server - setting this to `False` allows self-signed certificates on the server without errors
		- `include_response_headers:bool` - specifies whether to include the response headers in the return value of the function. See return value below for further details.
		- `response_headers_as_lists:bool` - specifies that the response headers should be in a dict-of-lists-of-strings instead of dict-of-strings format in the return value of the function. See return value below for further details.
		- `follow_redir:bool` - specifies whether redirect responses should be followed automatically, instead of returning the intermediate redirect page
		- `redir_persist_cookies:bool` - specifies whether a redirect should implement temporary cookie storage to prevent losing state during a redirect.  
			This improves compatibility with many servers with a server-side session, but may be disabled for performance if needed.
		- `cookie_store:guavacado.ClientCookieStore` - can be used to pass in a `ClientCookieStore` instance that will persist cookies between requests.  Can be implemented as follows:
			- `cookies = guavacado.ClientCookieStore()`
			- `body1, code1 = guavacado.Client.request_url(url1, cookie_store=cookies)`
			- `body2, code2 = guavacado.Client.request_url(url2, cookie_store=cookies)`
		- `timeout:numeric` - specifies the time before the request times out
		- `extra_headers:dict` - dictionary of strings or lists-of-strings providing the value of each header to send in the request.  
			The key is used as the header name, and the value can be either a string for the header value, or a list of header values for mltiple instances of the same header.
		- returns one of the following: 
			- if `include_response_headers==True`: `(body:bytes, code:int, headers:dict)`
			- if `include_response_headers==False`: `(body:bytes, code:int)`
				- `body` is the body of the HTTP response
				- `code` is the numeric code returned by the server - typical success codes are 200 and other responses between 200 and 299
				- `headers` is a dictionary of the response headers returned by the server.  It takes the form of one of the following:
					- if `response_headers_as_lists==False`: `{header_name: header_value}`
					- if `response_headers_as_lists==True`: `{header_name: [header_value_1, header_value_2]}`
						- `response_headers_as_lists==True` allows multiple response headers with the same name, at the added cost of making the values more complicated to access.  
							Since duplicate headers are rare, `response_headers_as_lists` defaults to `False` for easier access to headers.
		'''
		c, r = Client.from_url(url, TLS_check_cert=TLS_check_cert)
		return c.request_web(
			resource=r, 
			method=method, 
			body=body, 
			include_response_headers=include_response_headers, 
			response_headers_as_lists=response_headers_as_lists, 
			follow_redir=follow_redir, 
			redir_persist_cookies=redir_persist_cookies, 
			cookie_store=cookie_store, 
			timeout=timeout,
			extra_headers=extra_headers
		)
	
	@staticmethod
	def open_websocket_url( # pylint: disable=W0102
			url, 
			connected=None, received=None, closed=None, http_callback=None, 
			method='GET', body=None, TLS_check_cert=True, include_response_headers=False, response_headers_as_lists=False, follow_redir=False, redir_persist_cookies=True, cookie_store=None, timeout=None, extra_headers={}):
		'''
		opens a websocket connection to the given URL and calls the specified functions when the websocket connects, closes, or receives messages
		- callbacks are called in the following order:
			- calls `http_callback` with arguments matching the return values of `Client.request_url`
			- calls `connected(handler)` with `handler` being a `guavacado.WebSocketHandler` instance which can be used for sending data to the websocket
			- calls `received(handler, msg)` for each received message 
				with `handler` being the same `guavacado.WebSocketHandler` as in `connected` 
				and `msg` being a `guavacado.WebSocketMessage` instance representing the content of the received message
			- calls `closed(handler)` when the websocket closes with `handler` being the same `guavacado.WebSocketHandler` as in `connected`
		- all other parameters match those in `Client.request_url` with the following exceptions:
			- `url` is expected to have the protocol 'ws://' or 'wss://', and an unspecified protocol will be assumed to be 'ws://'
				- a protocol of 'http://' or 'https://' will work, and is implemented identically to 'ws://' or 'wss://', respectively, however it is discouraged to rely on this non-standard behavior
		'''
		c, r = Client.from_url(url, TLS_check_cert=TLS_check_cert)
		return c.open_websocket(
			connected=connected, 
			received=received, 
			closed=closed, 
			http_callback=http_callback,
			resource=r, 
			method=method, 
			body=body, 
			include_response_headers=include_response_headers, 
			response_headers_as_lists=response_headers_as_lists, 
			follow_redir=follow_redir, 
			redir_persist_cookies=redir_persist_cookies, 
			cookie_store=cookie_store, 
			timeout=timeout,
			extra_headers=extra_headers
		)
	
	def connect_socket(self):
		'''
		creates and returns a socket connection to the server using the saved settings created by the constructor or `Client.from_url`
		- call `Client.close_socket` with the returned socket to close the socket
		'''
		self.log_handler.debug('making connection to {addr}.'.format(addr=addr_rep({'addr':self.addr, 'port':self.port, 'TLS':self.TLS, 'UDP':self.UDP})))
		if self.TLS:
			tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
			# tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
			if self.TLS_check_cert:
				tls_context.verify_mode = ssl.CERT_REQUIRED
				tls_context.check_hostname = True
			else:
				tls_context.check_hostname = False
				tls_context.verify_mode = ssl.CERT_NONE
			tls_context.load_default_certs()
			raw_sock = socket.socket(socket.AF_INET)
			sock = tls_context.wrap_socket(raw_sock, server_hostname=self.addr)
		elif self.UDP:
			# create an INET, DATAGRAM (UDP) socket
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		else:
			# create an INET, STREAMing (TCP) socket
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.addr, self.port))
		return sock

	def close_socket(self, sock):
		'''closes a socket returned by `Client.connect_socket`'''
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	
	def request_web(self, resource='/', method='GET', body=None, include_response_headers=False, response_headers_as_lists=False, follow_redir=False, redir_persist_cookies=True, cookie_store=None, timeout=None, extra_headers={}): # pylint: disable=W0102
		'''
		performs a HTTP(S) request to the given resource using the server information stored in this `Client` instance and returns the response
		- all parameters and return value match those in `Client.request_url` with the following exceptions:
			- `resource` is a path from the root of the server specified by the constructor or `Client.from_url`
				- if `Client.from_url` is called, the second member of the response can be used directly as a value for `resource`
		'''
		ret = []
		ret_event = threading.Event()
		def req_callback(body, code, headers, ret=ret, ret_event=ret_event, include_response_headers=include_response_headers): # pylint: disable=W0102
			if include_response_headers:
				ret.append((body, code, headers))
			else:
				ret.append((body, code))
			ret_event.set()
		self.request_web_async(
			req_callback, 
			resource=resource, 
			method=method, 
			body=body, 
			include_response_headers=True, 
			response_headers_as_lists=response_headers_as_lists, 
			follow_redir=follow_redir, 
			redir_persist_cookies=redir_persist_cookies, 
			cookie_store=cookie_store, 
			timeout=timeout,
			extra_headers=extra_headers
		)
		ret_event.wait()
		return ret[0]

	def request_web_async(self, # pylint: disable=W0102
			callback, 
			resource='/', 
			method='GET', body=None, include_response_headers=False, response_headers_as_lists=False, follow_redir=False, redir_persist_cookies=True, cookie_store=None, timeout=None, extra_headers={}, include_web_request_handler=False):
		'''
		performs a HTTP(S) request to the given resource using the server information stored in this `Client` instance and calls `callback` with the response
		- calls `callback` with arguments matching the return values of `Client.request_url`
			- if `include_web_request_handler==True`: inserts a third argument with the `guavacado.WebRequestHandler` instance for the request
		- all other parameters match those in `Client.request_url` with the following exceptions:
			- `resource` is a path from the root of the server specified by the constructor or `Client.from_url`
				- if `Client.from_url` is called, the second member of the response can be used directly as a value for `resource`
			- `include_web_request_handler:bool` - specifies to insert the `guavacado.WebRequestHandler` instance for the request as the third argument to `callback`
				- this can be used for manipulation of the request communication channel after the HTTP communication is complete, for cases such as changes of protocols (`code==101`)
		'''
		sock = self.connect_socket()
		# buf = b''
		if follow_redir:
			def redir_callback(body, code, headers, callback=callback, cookie_store=cookie_store):
				if code in [301,302,307,308]:
					redir_url = headers['Location'][0]
					if redir_url.startswith('/'):
						c = Client(addr=self.addr, port=self.port, TLS=self.TLS, UDP=self.UDP, disp_type=self.disp_type, TLS_check_cert=self.TLS_check_cert)
						r=redir_url
					else:
						c, r = Client.from_url(redir_url, TLS_check_cert=self.TLS_check_cert)
					if redir_persist_cookies:
						if cookie_store is None:
							cookie_store = ClientCookieStore()
						if 'Set-Cookie' in headers:
							SetCookieHeaders = headers['Set-Cookie']
							for cookie_header in SetCookieHeaders:
								cookie_store.AddCookie(ClientCookie.from_header(cookie_header, self.addr, resource))
					c.request_web_async(
						callback,
						resource=r,
						method=method,
						body=body,
						include_response_headers=include_response_headers,
						response_headers_as_lists=response_headers_as_lists,
						follow_redir=follow_redir,
						redir_persist_cookies=redir_persist_cookies,
						cookie_store=cookie_store,
						timeout=timeout,
						extra_headers=extra_headers,
						include_web_request_handler=include_web_request_handler,
					)
				else:
					if include_response_headers:
						if response_headers_as_lists:
							ret_headers = headers
						else:
							ret_headers = dict([(k,v[0]) for k, v in headers.items()])
						if include_web_request_handler:
							callback(body, code, req_handler, ret_headers)
						else:
							callback(body, code, ret_headers)
					else:
						if include_web_request_handler:
							callback(body, code, req_handler)
						else:
							callback(body, code)
			req_callback = redir_callback
			req_include_response_headers = True
			req_response_headers_as_lists = True
		else:
			def nonredir_callback(body, code, headers, callback=callback):
				if include_response_headers:
					if response_headers_as_lists:
						ret_headers = headers
					else:
						ret_headers = dict([(k,v[0]) for k, v in headers.items()])
					if include_web_request_handler:
						callback(body, code, req_handler, ret_headers)
					else:
						callback(body, code, ret_headers)
				else:
					if include_web_request_handler:
						callback(body, code, req_handler)
					else:
						callback(body, code)
			req_callback = nonredir_callback
			req_include_response_headers = True
			req_response_headers_as_lists = True
			# req_callback = callback
			# req_include_response_headers = include_response_headers
			# req_response_headers_as_lists = response_headers_as_lists

		if cookie_store is not None:
			# do 2-level deep copy of extra_headers, converting strings into 1-element lists of strings - this generates a dictionary that we can modify without changing the original dictionary's contents
			req_extra_headers = dict([(k,{True:v,False:[v]}[isinstance(v,list)].copy()) for k,v in extra_headers.items()])
			if 'Cookie' not in req_extra_headers:
				req_extra_headers['Cookie'] = []
			req_extra_headers['Cookie'].append(
				ClientCookieStore.GetClientCookiesHeaderText(
					cookie_store.GetCookiesMatchingCriteria(
						Domain=self.addr, 
						Path=resource, 
						Expiration=datetime.now(), 
						Secure={True:True, False:None}[self.TLS is not None]
					)
				)
			)
		else:
			req_extra_headers = extra_headers

		req_handler = WebRequestHandler(
			sock, 
			(self.addr, self.port), 
			None, 
			req_callback, 
			timeout=timeout, 
			is_client=True, 
			client_resource=resource, 
			client_body=body, 
			client_method=method, 
			client_host=self.addr,
			client_include_response_headers=req_include_response_headers, 
			client_headers_as_lists=req_response_headers_as_lists, 
			add_headers=req_extra_headers
		)
		req_handler.handle_connection()
	
	def open_websocket(self, # pylint: disable=W0102
			connected=None, received=None, closed=None, http_callback=None, 
			resource='/', 
			method='GET', body=None, include_response_headers=False, response_headers_as_lists=False, follow_redir=False, redir_persist_cookies=True, cookie_store=None, timeout=None, extra_headers={}):
		'''
		opens a websocket connection to the given resource using the server information stored in this `Client` instance and calls the specified functions when the websocket connects, closes, or receives messages
		- callbacks are called in the following order:
			- calls `http_callback` with arguments matching the return values of `Client.request_url`
			- calls `connected(handler)` with `handler` being a `guavacado.WebSocketHandler` instance which can be used for sending data to the websocket
			- calls `received(handler, msg)` for each received message 
				with `handler` being the same `guavacado.WebSocketHandler` as in `connected` 
				and `msg` being a `guavacado.WebSocketMessage` instance representing the content of the received message
			- calls `closed(handler)` when the websocket closes with `handler` being the same `guavacado.WebSocketHandler` as in `connected`
		- all parameters match those in `Client.open_websocket_url` with the following exceptions:
			- `resource` is a path from the root of the server specified by the constructor or `Client.from_url`
				- if `Client.from_url` is called, the second member of the response can be used directly as a value for `resource`
		'''
		sec_websocket_key = base64.b64encode(os.urandom(16)).decode('utf-8')
		sec_websocket_accept = WebSocketInterface.calc_response_nonce(sec_websocket_key)
		
		def req_callback(body, code, req_handler, ret_headers):
			def get_header(header):
				if response_headers_as_lists:
					return ret_headers[header][0]
				else:
					return ret_headers[header]
			if code!=101:
				raise Exception('Invalid response code {code} in expected websocket connection!'.format(code=code))
			if get_header('Upgrade').lower() != 'websocket':
				raise Exception('Missing "Upgrade: websocket" response header!')
			if get_header('Connection').lower() != 'Upgrade'.lower():
				raise Exception('Missing "Connection: Upgrade" response header!')
			if get_header('Sec-WebSocket-Accept') != sec_websocket_accept:
				raise Exception('Invalid WebSocket response key!')
			if include_response_headers:
				if http_callback is not None:
					http_callback(body, code, ret_headers)
			else:
				if http_callback is not None:
					http_callback(body, code)
			def msg_received(msg):
				if received is not None:
					received(handler, msg)
			handler = WebSocketHandler(req_handler, msg_received, is_client=True)
			def run_websocket():
				if connected is not None:
					connected(handler)
				handler.run()
				if closed is not None:
					closed(handler)
			thr = threading.Thread(target=run_websocket, name='websocket_clientprocessor_{self.addr}_{self.port}_{resource}')
			thr.start()
			
		req_headers = {}
		req_headers.update(extra_headers)
		req_headers.update({
			'Connection': 'Upgrade',
			'Upgrade': 'websocket',
			'Sec-WebSocket-Version': '13',
			'Sec-WebSocket-Key': sec_websocket_key,
		})
		
		self.request_web_async(
			req_callback,
			resource=resource,
			method=method,
			body=body,
			include_response_headers=True,
			response_headers_as_lists=response_headers_as_lists,
			follow_redir=follow_redir,
			redir_persist_cookies=redir_persist_cookies,
			cookie_store=cookie_store,
			timeout=timeout,
			extra_headers=req_headers,
			include_web_request_handler=True,
		)

		
