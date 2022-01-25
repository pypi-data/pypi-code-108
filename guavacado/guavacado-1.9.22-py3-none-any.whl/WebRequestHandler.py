#! /usr/bin/env python

import mimetypes
import traceback
import socket

from .misc import init_logger, addr_rep
from .http_status_codes import http_status_codes

def parse_headers(headers, as_lists=False):
	ret = {}
	for t in [tuple(l.split(': ',1)) for l in headers.split('\r\n') if ': ' in l]:
		# if cookie name is already used, append it with a comma as described in RFC 2616 section 4.2 - https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2
		# this allows the multiple headers to be represented in a python dictionary without special cases of lists, and clients/servers following the spec should work with this rule

		# if as_lists is True, instead use a python list to make it easier to use later
		if t[0] in ret:
			if as_lists:
				ret[t[0]].append(t[1])
			else:
				ret[t[0]] = ret[t[0]] + ',' + t[1]
		else:
			if as_lists:
				ret[t[0]] = [t[1]]
			else:
				ret[t[0]] = t[1]
	return ret

class WebRequestHandlingException(Exception):
	'''base class for all exceptions related to web requests'''

class RequestTimedOut(WebRequestHandlingException):
	'''indicates there was a timeout receiving required data'''

class IncompleteRequest(WebRequestHandlingException):
	'''indicates not enough data was received with the request'''

class IncompleteRequestHeader(WebRequestHandlingException):
	'''indicates the request header was not terminated properly'''

class IncorrectRequestSyntax(WebRequestHandlingException):
	'''indicates the syntax of the main request line was incorrect'''

class WebRequestHandler(object):
	'''handles requests by identifying function based on the URL, then dispatching the request to the appropriate function'''
	def __init__(self,  # pylint: disable=W0102
			clientsocket, address, client_id, request_handler, timeout=None, 
			is_client=False, client_resource=None, client_body=None, client_method=None, client_host=None, client_include_response_headers=False, client_headers_as_lists=False, 
			auth_handler=None, add_headers={}):
		self.log_handler = init_logger(__name__)
		self.clientsocket = clientsocket
		self.address = address
		self.client_id = client_id
		self.request_handler = request_handler
		self.is_client = is_client
		self.client_resource = client_resource
		self.client_body = client_body
		self.client_method = client_method
		self.client_host = client_host
		self.client_include_response_headers = client_include_response_headers
		self.client_headers_as_lists = client_headers_as_lists
		self.auth_handler = auth_handler
		self.add_headers = add_headers
		self.success_status_code = 200
		self.clientsocket.settimeout(timeout)

		self.is_received = False
		self.buf = b''
	
	def setSuccessStatusCode(self, code):
		self.success_status_code = code

	def handle_connection(self):
		if not self.is_client:
			self.recv()
			if self.is_received:
				self.send()
		else:
			self.send()
			self.recv()
			if self.is_received:
				if self.client_include_response_headers:
					if self.client_headers_as_lists:
						self.request_handler(self.body, self.code, self.headers_lists)
					else:
						self.request_handler(self.body, self.code, self.headers)
				else:
					self.request_handler(self.body, self.code)

	def recv(self):
		try:
			self.req = self.recv_until()
			if self.req is None:
				raise IncompleteRequest()
			self.head = self.recv_until(terminator=b'\r\n\r\n')
			if self.head is None:
				raise IncompleteRequestHeader()
			self.headers = parse_headers(self.head.decode('utf-8'))
			if self.client_headers_as_lists:
				self.headers_lists = parse_headers(self.head.decode('utf-8'), as_lists=True)
			self.content_length_str = self.headers.get('Content-Length','0')
			self.content_length = int(self.content_length_str)
			self.transfer_encoding = self.headers.get('Transfer-Encoding','')
			if self.transfer_encoding=='chunked':
				self.body = b''
				chunk_len = 1
				while chunk_len>0:
					chunk_len = int(self.recv_until(terminator=b'\r\n').decode('utf-8'), 16)
					self.content_length = self.content_length + chunk_len
					self.body = self.body + self.recv_bytes(chunk_len)
					self.recv_until(terminator=b'\r\n') # throw away the rest of the current line
			else:
				self.body = self.recv_bytes(self.content_length)
			if not self.is_client:
				req_parts = self.req.replace(b'\r\n',b'').split(None,2)
				if len(req_parts) < 2:
					raise IncorrectRequestSyntax()
				self.method_bytes, self.url_bytes = req_parts[:2]
				self.method = self.method_bytes.decode('utf-8')
				self.url = self.url_bytes.decode('utf-8')
			else:
				req_parts = self.req.replace(b'\r\n',b'').split(None,2)
				self.protocol_bytes, self.code_bytes, self.desc_bytes = req_parts[:3]
				self.protocol = self.protocol_bytes.decode('utf-8')
				self.code = int(self.code_bytes.decode('utf-8'))
				self.desc = self.desc_bytes.decode('utf-8')
			self.is_received = True
		except RequestTimedOut:
			self.log_handler.info('{addr} [id {id}] Request timed out!'.format(addr=addr_rep(self.address), id=self.client_id))
		except IncompleteRequestHeader:
			self.log_handler.error('{addr} [id {id}] Incomplete request header!'.format(addr=addr_rep(self.address), id=self.client_id))
		except IncompleteRequest:
			self.log_handler.error('{addr} [id {id}] Incomplete request!'.format(addr=addr_rep(self.address), id=self.client_id))
		except Exception:
			self.log_handler.error('{addr} [id {id}] An Error was encountered while receiving the request!'.format(addr=addr_rep(self.address), id=self.client_id))

	def send(self):
		if not self.is_client:
			try:
				if self.auth_handler is not None:
					auth_info = self.headers.get('Authorization',None)
					if auth_info is None:
						self.log_handler.info('{addr} [id {id}] 401 Unauthorized: {method} {url}'.format(addr=addr_rep(self.address), id=self.client_id, method=self.method, url=self.url))
						self.send_header_as_code(status_code=401, url='401.html', extra_header_keys={'WWW-Authenticate': '{auth_type} realm="{realm}"'.format(auth_type=self.auth_handler.auth_type, realm=self.auth_handler.realm)})
						return
					auth_type, credentials = tuple(auth_info.split(' ', 1))
					if not self.auth_handler.authenticate(auth_type, credentials):
						self.log_handler.info('{addr} [id {id}] 403 Forbidden: {method} {url}'.format(addr=addr_rep(self.address), id=self.client_id, method=self.method, url=self.url))
						ret_buf = self.get_403_page().encode('utf-8')
						self.send_header_as_code(status_code=403, url='403.html', content_length=len(ret_buf))
						self.clientsocket.sendall(ret_buf)
						return
				self.log_handler.info('{addr} [id {id}] Handling request: {method} {url} [body len {blen}]'.format(addr=addr_rep(self.address), id=self.client_id, method=self.method, url=self.url, blen=len(self.body)))
				ret_data = self.request_handler(url=self.url, method=self.method, headers=self.headers, body=self.body)
				if ret_data is None:
					ret_buf = self.get_404_page().encode('utf-8')
					self.send_header_as_code(status_code=404, url='404.html', content_length=len(ret_buf))
					self.clientsocket.sendall(ret_buf)
				elif type(ret_data) in [tuple, list] and len(ret_data)>=2:
					if isinstance(ret_data[1], bytes):
						ret_buf = ret_data[1]
					else:
						ret_buf = ret_data[1].encode('utf-8')
					header_data = {'url':self.url}
					if not ret_buf is None:
						header_data['content_length'] = len(ret_buf)
					header_data['status_code'] = self.success_status_code # pass this in as part of dictionary so it can be overridden by update line below
					header_data.update(ret_data[0])
					self.send_header_as_code(**header_data)
					if not ret_buf is None:
						self.clientsocket.sendall(ret_buf)
				else:
					if isinstance(ret_data, bytes):
						ret_buf = ret_data
					else:
						ret_buf = ret_data.encode('utf-8')
					self.send_header_as_code(status_code=self.success_status_code, content_length=len(ret_buf))
					self.clientsocket.sendall(ret_buf)
			except Exception:
				self.log_handler.warning('{addr} [id {id}] An Error was encountered while handling the request!'.format(addr=addr_rep(self.address), id=self.client_id))
				tb = traceback.format_exc()
				try:
					ret_buf = self.get_500_page(tb=tb).encode('utf-8')
					self.send_header_as_code(status_code=500, url='500.html', content_length=len(ret_buf))
					self.clientsocket.sendall(ret_buf)
				except Exception:
					self.log_handler.error('{addr} [id {id}] An Error was encountered while attempting to send a 500 Error response!'.format(addr=addr_rep(self.address), id=self.client_id))
		else:
			self.clientsocket.sendall('{method} {resource} HTTP/1.1\r\n'.format(method=self.client_method, resource=self.client_resource).encode('utf-8'))
			self.clientsocket.sendall('Host: {host}\r\n'.format(host=self.client_host).encode('utf-8'))
			for key in self.add_headers:
				vals = self.add_headers[key]
				if not isinstance(vals, list):
					vals = [vals]
				for val in vals:
					self.clientsocket.sendall('{key}: {val}\r\n'.format(key=key, val=val).encode('utf-8'))
			if not (self.client_body is None or len(self.client_body)==0):
				self.clientsocket.sendall('Content-Length: {length}\r\n'.format(length=len(self.client_body)).encode('utf-8'))
			self.clientsocket.sendall('\r\n'.encode('utf-8'))
			if not (self.client_body is None or len(self.client_body)==0):
				self.clientsocket.sendall(self.client_body)
		
	def recv_until(self, terminator=b'\r\n', recv_size=128):
		try:
			while not terminator in self.buf:
				recv_data = self.clientsocket.recv(recv_size)
				self.buf = self.buf + recv_data
				if len(recv_data)==0:
					return None
		except socket.timeout as e:
			raise RequestTimedOut() from e
		(ret, rem) = self.buf.split(terminator, 1)
		self.buf = rem
		return ret+terminator
	
	def recv_bytes(self, num_bytes):
		try:
			while len(self.buf) < num_bytes:
				recv_size = num_bytes-len(self.buf)
				recv_data = self.clientsocket.recv(recv_size)
				self.buf = self.buf + recv_data
				if len(recv_data)==0:
					ret = self.buf
					self.buf = b''
					return ret
		except socket.timeout as e:
			raise RequestTimedOut() from e
		ret = self.buf[:num_bytes]
		self.buf = self.buf[num_bytes:]
		return ret
	
	def send_header_as_code(self, status_code=200, url=None, content_length=None, extra_header_keys={}): # pylint: disable=W0102
		"""send the header of the response with the given status code"""
		if url is None:
			url = self.url
		mime_url = url
		if mime_url[-1]=='/':
			mime_url = url+"index.html"
		mime_type = mimetypes.MimeTypes().guess_type(mime_url)[0]
		if mime_type is None:
			mime_type = "text/html"
		header_keys = {'Content-type':mime_type}
		if not content_length is None:
			header_keys['Content-Length'] = content_length
		header_keys.update(extra_header_keys)
		header_keys.update(self.add_headers)
		self.clientsocket.sendall('HTTP/1.1 {code} {desc}\r\n'.format(code=status_code, desc=http_status_codes[status_code]).encode('utf-8'))
		for key, vals in header_keys.items():
			if not isinstance(vals, list):
				vals = [vals]
			for val in vals:
				self.clientsocket.sendall('{key}: {val}\r\n'.format(key=key, val=val).encode('utf-8'))
		self.clientsocket.sendall(b'\r\n')
	
	def get_403_page(self):
		return ('<head><title>Error 403: Forbidden</title></head>'+ \
		'<body><h1>Error response</h1><p>Error code 403.<p>Message: The given credentials do not have access to the URI "{url}".'+ \
		'<p>Error code explanation: 403 = The given credentials do not have access to the given URI.</body>').format(url=self.url)
	
	def get_404_page(self):
		return ('<head><title>Error 404: Not Found</title></head>'+ \
		'<body><h1>Error response</h1><p>Error code 404.<p>Message: The URI "{url}" is not available.'+ \
		'<p>Error code explanation: 404 = Nothing matches the given URI.</body>').format(url=self.url)
	
	def get_500_page(self, tb=""):
		return ('<head><title>Error 500: Internal Server Error</title></head>'+ \
		'<body><h1>Error response</h1><p>Error code 500.<p>Message: The server encountered an error processing the request "{url}".'+ \
		'<p>Error code explanation: <br /> <br />{tb}</body>').format(url=self.url, tb=tb.replace('\n','<br />\n'))
