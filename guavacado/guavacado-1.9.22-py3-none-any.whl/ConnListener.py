#! /usr/bin/env python

'''
opens a socket listening for a connection from a client
calls conn_callback in a new thread with a socket when a connection is established
'''

import socket
import ssl
import threading
import traceback

from .misc import init_logger, addr_rep

class ConnListener(object):
	'''
	opens a socket listening for a connection from a client
	calls conn_callback in a new thread with a socket when a connection is established
	'''
	def __init__(self, conn_callback, addr=None):
		self.log_handler = init_logger(__name__)
		self.conn_callback = conn_callback
		if addr is None:
			self.addr = ('',80)
			self.tls = None
			self.udp = False
		elif isinstance(addr, tuple):
			if addr[0] is None:
				self.addr = ('',80)
				self.tls = addr[1]
				self.udp = False
			else:
				if addr[0][0] is None:
					self.addr = ('',addr[0][1])
					self.tls = addr[1]
					self.udp = False
				else:
					self.addr = addr[0]
					self.tls = addr[1]
					self.udp = False
		else:
			ip = addr.get('addr')
			port = addr.get('port')
			if ip is None:
				ip = ''
			self.addr = (ip, port)
			self.tls = addr.get('TLS')
			self.udp = addr.get('UDP',False)
		if self.tls is None:
			self.use_tls = False
		else:
			self.use_tls = True
		self.active_client_ids = []
		self.recent_client_ids = []
		self.client_ids_lock = threading.Lock()
		self.client_info = {}
		self.stop_event = threading.Event()
		self.create_server_socket()
	
	def create_server_socket(self):
		'''creates a socket object listening for connections and saves it to the variable self.sock'''
		self.log_handler.debug('Starting listening on {addr} for connections.'.format(addr=addr_rep(self.addr)))
		if not self.udp:
			# create an INET, STREAMing (TCP) socket
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		else:
			# create an INET, DATAGRAM (UDP) socket
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# bind the socket to a public host, and a well-known port
		self.sock.bind(self.addr)
		if not self.udp:
			# become a server socket
			self.sock.listen(5) # 5 is the number of queued connections to allow before refusing connections from new clients - 5 is typically the maximum for the OS
		if self.use_tls:
			self.tls_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
			self.tls_context.load_cert_chain(certfile=self.tls[0], keyfile=self.tls[1])

	def gen_client_id(self):
		'''generate an id number to identify a client'''
		with self.client_ids_lock:
			if len(self.active_client_ids+self.recent_client_ids)==0:
				ret = 0
			else:
				lv = min(self.active_client_ids+self.recent_client_ids)
				uv = max(self.active_client_ids+self.recent_client_ids)
				if lv<=0:
					ret = uv+1
				else:
					ret = lv-1
			self.active_client_ids.append(ret)
			self.recent_client_ids.append(ret)
			self.recent_client_ids = self.recent_client_ids[-49:]
		return ret

	def free_client_id(self, client_id):
		'''remove a specified client id from the list of active ids so it can be used again'''
		with self.client_ids_lock:
			if client_id in self.active_client_ids:
				self.active_client_ids.remove(client_id)

	def spawn_client_thread(self, clientsocket, address, sync=False):
		'''
		spawn a thread to handle the client socket
		keep track of the client thread and socket in a dictionary to be used for shutdown
		'''
		client_id = self.gen_client_id()
		self.log_handler.debug('{addr} [id {id}] Connection established'.format(addr=addr_rep(address),id=client_id))
		client_thread = threading.Thread(
			target=self.handle_client, 
			args=(clientsocket, address, client_id), 
			name='clienthandler_{}'.format(client_id), 
		)
		client_thread.daemon=True # separated from Thread constructor for python2 compatibility
		self.client_info[client_id] = {
			'socket':clientsocket,
			'address':address,
			'thread':client_thread,
		}
		if not sync:
			client_thread.start()
			self.log_handler.debug('Thread number {ident} started for connection id {id}'.format(ident=client_thread.ident,id=client_id))
		else:
			self.log_handler.debug('Running connection id {id} synchronously'.format(id=client_id))
			client_thread.run()
	
	def handle_client(self, clientsocket, address, client_id):
		'''
		handle the connection to the client
		should be running in separate thread (unless synchronous)
		'''
		self.conn_callback(clientsocket, address, client_id)
		try:
			self.log_handler.debug('{addr} [id {id}] Shutting down connection'.format(addr=addr_rep(address),id=client_id))
			clientsocket.shutdown(socket.SHUT_RDWR)
			self.log_handler.debug('{addr} [id {id}] Closing connection'.format(addr=addr_rep(address),id=client_id))
			clientsocket.close()
			self.log_handler.debug('{addr} [id {id}] Closed connection'.format(addr=addr_rep(address),id=client_id))
		except OSError:
			self.log_handler.warning('{addr} [id {id}] Could not shut down connection because it is not open!'.format(addr=addr_rep(address),id=client_id))
		# remove references to this client before closing the thread
		if client_id in self.client_info:
			del self.client_info[client_id]
		self.free_client_id(client_id)

	def run(self):
		'''accept connections from clients and spawn threads for them'''
		self.log_handler.debug('Starting accepting connections on {addr}'.format(addr=addr_rep(self.addr)))
		if self.use_tls:
			# wrap listening socket in TLS context
			self.raw_socket = self.sock
			self.sock = self.tls_context.wrap_socket(self.raw_socket, server_side=True)
		while not self.stop_event.is_set():
			# accept connections from outside
			try:
				if not self.udp:
					(clientsocket, address) = self.sock.accept()
				else:
					clientsocket = self.sock
					address = None
				if not self.stop_event.is_set():
					if not self.udp:
						# spawn thread using the new socket
						self.spawn_client_thread(clientsocket, address)
					else:
						# run synchronously using the new socket
						self.spawn_client_thread(clientsocket, address, sync=True)
						self.stop_event.set()
			except ssl.SSLError as e:
				if e.reason in ['SSLV3_ALERT_CERTIFICATE_UNKNOWN', 'TLSV1_ALERT_UNKNOWN_CA']:
					self.log_handler.warning("The incoming client refused to connect due to an invalid certificate!")
				else:
					self.log_handler.error("An error was encountered trying to set up a TLS connection!")
					self.log_handler.error(traceback.format_exc())
			except OSError:
				if not self.stop_event.is_set():
					self.log_handler.error("An error was encountered trying to accept a new socket connection!")
					self.log_handler.error(traceback.format_exc())
	
	def stop(self):
		'''stop accepting connections and shut down all sockets'''
		self.log_handler.debug('Stopping server socket.')
		self.stop_event.set()
		if not self.udp:
			# connect as fake client to stop the looping thread
			if self.tls:
				tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				tls_context.check_hostname = False
				tls_context.verify_mode = ssl.CERT_NONE
				tls_context.load_default_certs()
				raw_sock = socket.socket(socket.AF_INET)
				s = tls_context.wrap_socket(raw_sock, server_hostname='localhost')
			else:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect(('localhost', self.addr[1]))
			s.shutdown(socket.SHUT_RDWR)
			s.close()
		try:
			# self.sock.shutdown(socket.SHUT_RDWR)
			self.sock.close()
		except OSError:
			self.log_handler.warning('Not shutting down server socket because it is not connected.')
		self.log_handler.debug('Stopping client socket connections.')
		client_ids = list(self.client_info.keys())
		for client_id in client_ids:
			if client_id in self.client_info:
				client_dat = self.client_info[client_id]
				self.log_handler.debug('{addr} [id {id}] Stopping connection'.format(addr=addr_rep(client_dat['address']),id=client_id))
				try:
					client_dat['socket'].shutdown(socket.SHUT_RDWR)
				except OSError:
					pass
				try:
					client_dat['socket'].close()
				except OSError:
					pass
				self.log_handler.debug('Waiting for thread id {ident} to close'.format(ident=client_dat['thread'].ident))
				if client_dat['thread'].is_alive():
					client_dat['thread'].join(timeout=5)
				if client_dat['thread'].is_alive():
					self.log_handler.warning('Thread id {ident} ({addr} [id {id}]) did not close after 5 seconds! Continuing anyways...'.format(ident=client_dat['thread'].ident,addr=addr_rep(client_dat['address']),id=client_id))
		self.log_handler.debug('All client socket connections stopped.')
