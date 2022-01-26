#! /usr/bin/env python
'''
Main class for the Guavacado server host
Instantiate `WebHost` then call `add_addr` for each port/IP address to listen on for hosting
Call `start_service` to start listening, then `stop_service` to stop listening
'''

from .WebDocs import WebDocs
from .ConnDispatcher import ConnDispatcher
from .misc import init_logger, set_loglevel, addr_rep

from .WebDispatcher import WebDispatcher
from .RedirectDispatcher import RedirectDispatcher
from .RawSocketDispatcher import RawSocketDispatcher

class WebHost(object):
	'''
	Main class for the Guavacado server host
	Instantiate `WebHost` then call `add_addr` for each port/IP address to listen on for hosting
	Call `start_service` to start listening, then `stop_service` to stop listening
	'''
	def __init__(self,timeout=10,loglevel='INFO', error_404_page_func=None):
		set_loglevel(loglevel)
		self.log_handler = init_logger(__name__)
		self.addr=[]
		self.timeout = timeout
		self.error_404_page_func = error_404_page_func
		self.specialized_dispatchers = {}
		self.dispatcher = ConnDispatcher()
		self.docs = WebDocs(self)
		self.docs.connect_funcs()

	def add_addr(self, addr=None, port=80, TLS=None, UDP=False, disp_type='web'):
		'''
		adds an address to the dispatcher for it to listen on
		- `addr` should be a hostname to listen on, or None to listen on all addresses
		- `port` should be a port number to listen on
		- `TLS` should be a tuple of two filenames to use for the certfile and keyfile for TLS, or None to use plain HTTP
		- `UDP` indicates to use UDP instead of TCP
		- `disp_type` should be one of the following:
			- `'web'` - HTTP(S) server
			- `('web', ident)` - HTTP(S) server with isolation from other HTTP(S) servers - `ident` can be any value, but any unique values will not share URLs
				- set `ident` to match the `web_dispatcher_ident` parameter of `WebInterface`, `WebFileInterface`, or `WebSocketInterface` for the resources from that interface to be available on this address
			- `('web', ident, auth)` - HTTP(S) server with authentication and isolation from other HTTP(S) servers
				- `ident` has the same usage as the previous example, but `auth` will only apply if it is the first call with the same `ident` value
				- `auth` is an instance of an authentication provider such as `BasicAuth`
					- required member variables:
						- `auth_type` - string of the authentication scheme to use in the [`WWW-Authenticate`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/WWW-Authenticate) header of error 401 (Unauthorized) responses
						- `realm` - string of the realm to use in the [`WWW-Authenticate`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/WWW-Authenticate) header of error 401 (Unauthorized) responses
						- `authenticate` - callable that determines whether the provided credentials are correct - should take 2 parameters `(auth_type, credentials)` and return a boolean of whether the client is authorized
							- `auth_type` is the authentication scheme from the [`Authorization`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization) header provided by the client
							- `credentials` is the remainder of the [`Authorization`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization) header provided by the client
			- `('redirect', target_domain)` - HTTP(S) server which responds with a redirect to the same path on `target_domain`
				- Ex: `('redirect', 'https://localhost/')`
			- `('raw_socket', callback)` - raw socket that listens for connections and calls `callback(socket, address, client_id)` every time a new client connects.
				- The callback parameters are:
					- `socket` - a [`socket`](https://docs.python.org/3/library/socket.html#socket-objects) object referring to the client connection
					- `address` - the address of the client of the connection (as the second part of the tuple returned by [`socket.accept()`](https://docs.python.org/3/library/socket.html#socket.socket.accept))
					- `client_id` - a unique ID number for the client connection - will not be reused until at least after the connection is closed
		'''
		# addr_tuple = ((addr,port),TLS)
		addr_dict = {'addr':addr, 'port':port, 'TLS':TLS, 'UDP':UDP}
		self.addr.append(addr_dict)
		self.dispatcher.add_conn_listener(addr_dict, self.get_specialized_dispatcher(disp_type).handle_connection, name='WebDispatch_'+addr_rep(addr_dict))

	def start_service(self):
		'''
		starts listening for incoming connections

		if `add_addr` has not been called previously, opens to port 80 and outputs a warning message
		'''
		if len(self.addr)==0:
			self.log_handler.warning('No port number specified! Defaulting to port 80!')
			self.add_addr()
		self.log_handler.info('Starting web server on {addr}'.format(addr=addr_rep(self.addr)))
		self.log_handler.debug("All Resources: {}".format(self.get_docs().GET_DOCS_JSON()))
		self.dispatcher.start_service()
	
	def stop_service(self):
		'''
		stops listening for incoming connections and shuts down the server
		'''
		self.log_handler.info('Stopping web server on {addr}'.format(addr=addr_rep(self.addr)))
		self.dispatcher.stop_service()
		self.log_handler.info('Web server stopped on {addr}'.format(addr=addr_rep(self.addr)))

	def get_dispatcher(self):
		'''
		returns reference to the `ConnDispatcher` instance for this host
		'''
		return self.dispatcher
	
	def get_specialized_dispatcher(self, disp_type):
		'''
		return a dispatcher for the specified `disp_type`

		either returns a pre-existing matching dispatcher or creates one if a matching one does not exist

		see docs for `add_addr` for more details about the `disp_type` parameter
		'''
		def setup_web_dispatcher(ident=None, auth=None):
			_ident = ident # suppresses linter warnings
			# ident argument is so this can instantiate multiple WebDispatcher instances by specifying this parameter
			return WebDispatcher(addr=self.addr, timeout=self.timeout, error_404_page_func=self.error_404_page_func, auth_handler=auth)
		def setup_redirect_dispatcher(target_domain):
			return RedirectDispatcher(timeout=self.timeout, target_domain=target_domain)
		def setup_raw_socket_dispatcher(callback):
			return RawSocketDispatcher(callback)
		dispatcher_setup_funcs = {
			'web':setup_web_dispatcher,
			'redirect':setup_redirect_dispatcher,
			'raw_socket':setup_raw_socket_dispatcher,
		}
		
		dict_key_ident = disp_type
		if type(dict_key_ident) in [tuple, list] and type(disp_type[0]) in [str]:
			if dict_key_ident[0]=='web':
				if len(dict_key_ident)>2:
					# remove the (non-hashable) auth information from the dictionary key
					dict_key_ident = dict_key_ident[:2]
		if dict_key_ident in self.specialized_dispatchers:
			return self.specialized_dispatchers[dict_key_ident]
		else:
			if type(disp_type) in [tuple, list] and type(disp_type[0]) in [str]:
				disp_type_string = disp_type[0]
				disp_args = disp_type[1:]
			else:
				disp_type_string = disp_type
				disp_args = ()
			if disp_type_string in dispatcher_setup_funcs:
				disp = dispatcher_setup_funcs[disp_type_string](*disp_args)
				self.specialized_dispatchers[dict_key_ident] = disp
				return disp
			else:
				raise NotImplementedError('Dispatcher type "{}" is not implemented!'.format(disp_type))

	def get_docs(self):
		'''
		return reference to the `WebDocs` instance that manages documentation for the REST API created by attached `WebDispatcher` instances
		'''
		return self.docs
	
	def get_addr(self):
		'''
		return list of address information for attached addresses created by calls to `add_addr`
		'''
		return self.addr
