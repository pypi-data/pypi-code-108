#! /usr/bin/env python

import threading

from .misc import init_logger, addr_rep
from .ConnListener import ConnListener

class ConnDispatcher(object):
	'''handles dispatching connections from multiple ConnListener instances to the proper callback functions'''
	def __init__(self):
		self.log_handler = init_logger(__name__)
		self.conn_listeners = {}
	
	def get_conn_listener(self, name):
		return self.conn_listeners[name]
	
	def add_conn_listener(self, addr, conn_handler, name=None):
		if name is None:
			name = "gen_conn_listener_"+str(addr)
		def handle_callback(clientsocket, address, client_id, name=name):
			self.conn_listeners[name]['handler'](clientsocket, address, client_id)
		self.conn_listeners[name] = {'listener':ConnListener(handle_callback, addr=addr), 'handler':conn_handler, 'addr':addr}
		return name
	
	def start_service(self):
		for _listener_name, listener in self.conn_listeners.items():
			self.log_handler.debug('Starting connection listener for {addr}'.format(addr=addr_rep(listener['addr'])))
			listener['thread'] = threading.Thread(target=listener['listener'].run, name='conn_listener_{addr}'.format(addr=addr_rep(listener['addr'])))
			listener['thread'].daemon = True
			listener['thread'].start()
	
	def stop_service(self):
		for _listener_name, listener in self.conn_listeners.items():
			self.log_handler.debug('Stopping connection listener for {addr}'.format(addr=addr_rep(listener['addr'])))
			listener['listener'].stop()
			listener['thread'].join(60)
			if listener['thread'].is_alive():
				self.log_handler.warning('Continuing without closing connection listener thread for {addr} because it did not close!'.format(addr=addr_rep(listener['addr'])))
			else:
				self.log_handler.debug('Stopped connection listener for {addr}'.format(addr=addr_rep(listener['addr'])))
