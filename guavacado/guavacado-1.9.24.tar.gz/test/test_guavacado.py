'''
test cases for Guavacado

to run tests, run `pytest` in the same folder as this file
you must first run the `tls_keygen.sh` script to generate a self-signed certificate
'''

import ssl
import socket
import time
import threading
import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))

import guavacado # pylint: disable= E0401,C0413

class GuavacadoTestEnvironment(object):
	'''Testing environment for Guavacado used by class `TestGuavacado`'''
	def __init__(self):
		self.tls_args = (os.path.join('..','TLS_keys','self_signed.crt'),os.path.join('..','TLS_keys','self_signed.key'))
		with open(os.path.join('served_files','test_serve_file.txt'), 'rb') as fp:
			self.test_serve_file_contents = fp.read()
		self.test_function_contents = b'The test content works!!!'
		self.test_function_contents_1200 = os.urandom(1200)

	def start_test_server(self):
		'''starts the server for the test'''
		self.host = guavacado.WebHost(loglevel='ERROR')
		self.host.add_addr(port=80, disp_type=('redirect', 'https://localhost/'))
		self.host.add_addr(port=88)
		self.host.add_addr(port=443, TLS=self.tls_args)
		self.host.add_addr(port=4444, TLS=self.tls_args, disp_type=('web', 'no_files'))
		self.host.add_addr(port=9090, disp_type=('raw_socket', self.sock_connect_TCP))
		self.host.add_addr(port=9091, disp_type=('raw_socket', self.sock_connect_UDP), UDP=True)
		self.host.add_addr(port=9092, disp_type=('raw_socket', self.sock_connect_TLS), TLS=self.tls_args)
		self.files = guavacado.WebFileInterface(self.host, staticdir='served_files')
		self.web_int = guavacado.WebInterface(self.host)
		self.web_int.connect('/echo/', self.echo_body, 'GET', body_included=True)
		self.web_int.connect('/echo/:param', self.echo_body, 'GET')
		self.websock_int = guavacado.WebSocketInterface(self.host)
		self.websock_int.connect('/websock_echo/', received=self.websock_msg_recv)
		self.web_int_no_files = guavacado.WebInterface(self.host, web_dispatcher_ident='no_files')
		self.web_int_no_files.connect('/rev/', self.reverse_body, 'GET', body_included=True)
		self.host.start_service()
	
	def stop_test_server(self):
		'''starts the test server'''
		self.host.stop_service()
	
	def sock_connect_TCP(self, sock, _addr, _client_id):
		'''TCP socket connected'''
		val = sock.recv(len(self.test_function_contents))
		sock.sendall(val)
	
	def sock_connect_UDP(self, sock, _addr, _client_id):
		'''UDP socket connected'''
		val = b''
		while len(val)==0:
			val, add = sock.recvfrom(len(self.test_function_contents))
			if len(val)>0:
				sock.sendto(val, add)
	
	def sock_connect_TLS(self, sock, _addr, _client_id):
		'''TLS socket connected'''
		val = sock.recv(len(self.test_function_contents))
		sock.sendall(val)
	
	def websock_msg_recv(self, handler, msg):
		'''WebSocket message received'''
		msg_body = msg.read_all()
		send_msg = guavacado.WebSocketMessage()
		send_msg.write(msg_body)
		send_msg.end_message()
		handler.send_message(send_msg)
	
	def echo_body(self, body):
		'''returns the body exactly as sent'''
		return body
	
	def echo_param(self, param):
		'''returns the parameter in the response body exactly as sent'''
		return param
	
	def reverse_body(self, body):
		'''returns the body in reverse'''
		return body[::-1]

class AssertionTestError(Exception):
	'''Incorrect value in testing'''
class IsNotTrueError(AssertionTestError):
	'''assertTrue failed'''
class NotEqualError(AssertionTestError):
	'''assertEqual failed'''
class NotInError(AssertionTestError):
	'''assertIn failed'''
class DidNotRaiseError(AssertionTestError):
	'''assertRaises failed'''

class helperFuncs:
	'''helper functions for assertions'''
	def assertTrue(self, val):
		'''asserts that the value is true'''
		if not val:
			raise IsNotTrueError('The asserted value is false!')

	def assertEqual(self, a, b):
		'''asserts that the values are equal'''
		if a!=b:
			raise NotEqualError(f'The values "{a}" and "{b}" do not match!')
	
	def assertIn(self, a, b):
		'''asserts that the second value contains the first'''
		if not a in b:
			raise NotInError(f'The value "{a}" is not in "{b}"!')
	
	def assertRaises(self, e, f, *a, **k):
		'''asserts that the provided function raises the provided exception when called with the specified arguments'''
		try:
			f(*a, **k)
			raise DidNotRaiseError(f'The function did not raise the exception "{e}"!')
		except e:
			return

class TestGuavacado:
	'''test case class for Guavacado'''
	def setup_class(self):
		'''setup environment before running all tests'''
		self.helpers = helperFuncs()
		self.test_env = GuavacadoTestEnvironment()
		self.test_env.start_test_server()

	def teardown_class(self):
		'''teardown environment after running all tests'''
		self.test_env.stop_test_server()
	
	def test_external_website(self):
		'''test accessing an external website'''
		self.helpers.assertEqual(guavacado.Client.request_url('http://www.bing.com')[1], 200)
		self.helpers.assertEqual(guavacado.Client.request_url('https://www.bing.com')[1], 200)
	
	def test_file_serve(self):
		'''test serving a specific file from multiple ports'''
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/served_files/test_serve_file.txt', TLS_check_cert=False), (self.test_env.test_serve_file_contents,200))
		self.helpers.assertEqual(guavacado.Client.request_url('http://localhost:88/served_files/test_serve_file.txt'), (self.test_env.test_serve_file_contents,200))

	def test_static_redirect(self):
		'''test the same files with the static directory redirect'''
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/test_serve_file.txt', TLS_check_cert=False), (self.test_env.test_serve_file_contents,200))
		self.helpers.assertEqual(guavacado.Client.request_url('http://localhost:88/test_serve_file.txt'), (self.test_env.test_serve_file_contents,200))

	def test_index_page(self):
		'''test serving an index of files from multiple ports'''
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/served_files/', TLS_check_cert=False)[1], 200)
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/', TLS_check_cert=False)[1], 200)
		self.helpers.assertEqual(guavacado.Client.request_url('http://localhost:88/')[1], 200)
	
	def test_index_page_identical(self):
		'''check that two different ports will serve the same index page (not absolutely necessary)'''
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/', TLS_check_cert=False), guavacado.Client.request_url('http://localhost:88/'))

	def test_https_redirect(self):
		'''test redirecting from http to https'''
		self.helpers.assertEqual(guavacado.Client.request_url('http://localhost/served_files/test_serve_file.txt')[1], 301)
		self.helpers.assertEqual(guavacado.Client.request_url('http://localhost/test_serve_file.txt')[1], 301)
		self.helpers.assertEqual(guavacado.Client.request_url('http://localhost/served_files/')[1], 301)
		self.helpers.assertEqual(guavacado.Client.request_url('http://localhost/')[1], 301)
	
	def test_server_authentication(self):
		'''test that server authentication works'''
		self.helpers.assertRaises(ssl.SSLCertVerificationError, guavacado.Client.request_url, 'https://localhost/', TLS_check_cert=True)
	
	def test_index_file_list(self):
		'''check that index pages are properly listing files'''
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost/served_files/', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost/', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('http://localhost:88/')[0])
	
	def test_index_multi_slash_security(self):
		'''
		check that multiple slashes still give the correct index page (instead of root of file system)
		IMPORTANT SECURITY CONCERN IF TEST FAILS!!!
		'''
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost/served_files//', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost//served_files/', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost//served_files//', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('http://localhost:88//')[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost//', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost///', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost/////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost//////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost///////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost////////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost/////////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost//////////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost///////////', TLS_check_cert=False)[0])
		self.helpers.assertIn(b'test_serve_file.txt', guavacado.Client.request_url('https://localhost////////////', TLS_check_cert=False)[0])

	def test_dynamic_content(self):
		'''test that dynamic content works'''
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/echo/', body=self.test_env.test_function_contents, TLS_check_cert=False), (self.test_env.test_function_contents, 200))
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/echo/test_echo', TLS_check_cert=False), (b'test_echo', 200))
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost:4444/rev/', body=self.test_env.test_function_contents, TLS_check_cert=False), (self.test_env.reverse_body(self.test_env.test_function_contents), 200))

	def test_secondary_dispatcher(self):
		'''test isolation of different Web Dispatchers prevents accessing resources from the wrong port'''
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost:4444/echo/', body=self.test_env.test_function_contents, TLS_check_cert=False)[1], 404)
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost/rev/', body=self.test_env.test_function_contents, TLS_check_cert=False)[1], 404)
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost:4444/', body=self.test_env.test_function_contents, TLS_check_cert=False)[1], 404)
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost:4444/served_files/', body=self.test_env.test_function_contents, TLS_check_cert=False)[1], 404)
		self.helpers.assertEqual(guavacado.Client.request_url('https://localhost:4444/served_files/test_serve_file.txt', body=self.test_env.test_function_contents, TLS_check_cert=False)[1], 404)

	def test_TCP_connection(self):
		'''test TCP socket connection'''
		self.client_TCP = guavacado.Client(port=9090, disp_type='raw_socket')
		self.client_TCP_socket = self.client_TCP.connect_socket()
		self.client_TCP_socket.sendall(self.test_env.test_function_contents)
		self.helpers.assertEqual(self.client_TCP_socket.recv(len(self.test_env.test_function_contents)), self.test_env.test_function_contents)
		self.client_TCP_socket.shutdown(socket.SHUT_RDWR)
		self.client_TCP_socket.close()

	def test_UDP_connection(self):
		'''test UDP socket connection'''
		self.client_UDP = guavacado.Client(port=9091, disp_type='raw_socket', UDP=True)
		self.client_UDP_socket = self.client_UDP.connect_socket()
		time.sleep(1)
		self.client_UDP_socket.send(self.test_env.test_function_contents)
		self.helpers.assertEqual(self.client_UDP_socket.recv(len(self.test_env.test_function_contents)), self.test_env.test_function_contents)
		self.client_UDP_socket.shutdown(socket.SHUT_RDWR)
		self.client_UDP_socket.close()
	
	def test_TLS_connection(self):
		'''test TLS socket connection'''
		self.client_TLS = guavacado.Client(port=9092, disp_type='raw_socket', TLS=True, TLS_check_cert=False)
		self.client_TLS_socket = self.client_TLS.connect_socket()
		self.client_TLS_socket.sendall(self.test_env.test_function_contents)
		self.helpers.assertEqual(self.client_TLS_socket.recv(len(self.test_env.test_function_contents)), self.test_env.test_function_contents)
		self.client_TLS_socket.shutdown(socket.SHUT_RDWR)
		self.client_TLS_socket.close()
	
	def test_WebSocket_connection(self):
		'''test WebSocket connection'''
		def test_websocket_echo_url(url, TLS_check_cert=True, follow_redir=False, data=self.test_env.test_function_contents):
			closed = threading.Condition()
			state = {
				'received':False,
				'closed':False,
			}
			def websock_conn(handler):
				send_msg = guavacado.WebSocketMessage()
				send_msg.write(data)
				send_msg.end_message()
				handler.send_message(send_msg)
			def websock_recv(handler, msg):
				state['received'] = True
				msg_body = msg.read_all()
				self.helpers.assertEqual(msg_body, data)
				handler.close_connection()
			def websock_close(_handler):
				state['closed'] = True
				with closed:
					closed.notify_all()
			guavacado.Client.open_websocket_url(url, connected=websock_conn, received=websock_recv, closed=websock_close, TLS_check_cert=TLS_check_cert, follow_redir=follow_redir)
			def is_it_closed():
				return state['closed']
			with closed:
				closed.wait_for(is_it_closed)
			self.helpers.assertTrue(state['received'])
		test_websocket_echo_url('wss://localhost/websock_echo/', TLS_check_cert=False)
		test_websocket_echo_url('ws://localhost/websock_echo/', TLS_check_cert=False, follow_redir=True)
		test_websocket_echo_url('ws://localhost:88/websock_echo/')
		test_websocket_echo_url('ws://localhost:88/websock_echo/', TLS_check_cert=False, follow_redir=True, data=self.test_env.test_function_contents_1200)

if __name__=='__main__':
	test_env = GuavacadoTestEnvironment()
	test_env.start_test_server()
	guavacado.wait_for_keyboardinterrupt()
	test_env.stop_test_server()
