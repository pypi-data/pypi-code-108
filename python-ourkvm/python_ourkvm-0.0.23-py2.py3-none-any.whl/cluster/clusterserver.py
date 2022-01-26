import time
import socket
import json
import jwt
import logging
from typing import Optional, cast, Iterator, Union, Dict, Any, Type, Tuple, List

from ..storage import storage
from ..lib.networking import epoll, EPOLLIN, EPOLLHUP
from ..lib.helpers.dupedict import JSON
from ..lib.helpers.logger import log

class SimplifiedClientSocket:
	"""
	A wrapper around socket.socket() with some abstraction layers.
	Automatically detect the sending data and process it before sending.
	recv() will iterate over multiple or single transfers yielding result data.
	"""
	def __init__(self, addr :str, port :int) -> None:
		self.poller = epoll()
		self.addr = addr
		self.port = port
		self.socket :Optional[socket.socket] = None

		self._default_line_separator = b'\r\n'
		self._buffert = b''
		self._recv_len = 8192

	def connect(self) -> None:
		self.close()

		self.socket = socket.socket()
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.poller.register(self.socket.fileno(), EPOLLIN | EPOLLHUP)
		self.socket.connect((self.addr, self.port))

	def reconnect(self) -> None:
		self.connect()

	def close(self) -> None:
		self._buffert = b''
		if self.socket:
			self.poller.unregister(self.socket.fileno())
			self.socket.close()

	def send(self, data :Union[bytes, str, str], encoding :str = 'UTF-8', serializer :Optional[Union[Type[JSON], json.JSONEncoder]] = JSON) -> int:
		if not self.socket:
			try:
				self.connect()
			except ConnectionRefusedError:
				return -1

		if type(data) not in [str, bytes]:
			# We can safely assume it's an object
			# that needs JSON serialization before being
			# processed into bytes
			data = json.dumps(data, cls=cast(Type[json.JSONEncoder], serializer))

		if type(data) != bytes:
			data = bytes(cast(str, data), encoding)

		try:
			return cast(socket.socket, self.socket).send(data)
		except OSError:
			try:
				self.connect()
			except ConnectionRefusedError:
				return -1

			return cast(socket.socket, self.socket).send(data)

	def recv(self, line_by_line :bool = True, line_separator :Optional[bytes] = None) -> Iterator[bytes]:
		if not line_separator:
			line_separator = self._default_line_separator

		if next(self.poll(), None):
			# We can safely cast this to socket.socket because self.poller.poll()
			# Will never allow us to end up here unless we have an active socket connection.
			new_data = cast(socket.socket, self.socket).recv(self._recv_len)
			if not len(new_data):
				self.close()
			else:
				if line_by_line:
					for line in self._buffert[0:self._buffert.rfind(line_separator)].split(line_separator):
						if line:
							yield line + line_separator

					self._buffert = self._buffert[self._buffert.rfind(line_separator):]
				else:
					yield self._buffert
					self._buffert = b''

	def poll(self) -> Iterator[int]:
		for fileno, event in self.poller.poll():
			yield fileno


class SimplifiedServerSocket:
	"""
	A wrapper around socket.socket() with some abstraction layers.
	Automatically detect the sending data and process it before sending.
	recv() will iterate over multiple or single transfers yielding result data.
	"""
	def __init__(self, addr :str, port :int) -> None:
		self.poller = epoll()
		self.addr = addr
		self.port = port
		self.socket :Optional[socket.socket] = None

		self._default_line_separator = b'\r\n'
		self._recv_len = 8192
		self._sockets :Dict[int, Any] = {}

		self._attempts :Dict[str, Any] = {}
		self._blocks :Dict[str, Any] = {}
		self._attempt_limit_before_block = 3
		self._time_before_auto_unblock_in_sec = 30
		self._reset_block_time_on_new_attempts = True

	def listen(self) -> None:
		self.close()

		self.socket = socket.socket()
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.poller.register(self.socket.fileno(), EPOLLIN | EPOLLHUP)
		self.socket.bind((self.addr, self.port))
		self.socket.listen(4)

	def reconnect(self) -> None:
		self.listen()

	def is_blocked(self, addr :Optional[str] = None, fileno :Optional[int] = None) -> Union[float, bool]:
		if addr is None and fileno is None:
			raise ValueError(f"SimplifiedServerSocket().block() requires either an addr OR fileno, but not nothing.")

		if fileno:
			addr = self._sockets[fileno]['addr'][0]

		if blocked_time := self._blocks.get(cast(str, addr), False):
			if self._time_before_auto_unblock_in_sec:
				if time.time() - blocked_time > self._time_before_auto_unblock_in_sec:
					del(self._attempts[cast(str, addr)])
					del(self._blocks[cast(str, addr)])
					return False

				if self._reset_block_time_on_new_attempts:
					self._blocks[cast(str, addr)] = time.time()

			return float(blocked_time)

		return False

	def block_attempt(self, addr :Optional[str] = None, fileno :Optional[int] = None) -> bool:
		if addr is None and fileno is None:
			raise ValueError(f"SimplifiedServerSocket().block() requires either an addr OR fileno, but not nothing.")

		if fileno:
			addr = self._sockets[fileno]['addr'][0]

		if addr not in self._attempts:
			self._attempts[cast(str, addr)] = {
				'first_attempt' : time.time(),
				'attempts' : 0
			}

		self._attempts[cast(str, addr)]['attempts'] += 1
		
		if self._attempts[cast(str, addr)]['attempts'] >= self._attempt_limit_before_block:
			self._blocks[cast(str, addr)] = time.time()

		return True

	def close(self, fileno :Optional[int] = None) -> None:
		for socket_fileno in list(self._sockets.keys()):
			if fileno is None or (fileno and fileno == socket_fileno):
				self.poller.unregister(socket_fileno)
				self._sockets[socket_fileno]['socket'].close()
				del(self._sockets[socket_fileno])

		if not fileno:
			self._sockets = {}

		if self.socket and fileno is None:
			self.poller.unregister(self.socket.fileno())
			self.socket.close()

	def recv(self, fileno :Optional[int] = None, line_by_line :bool = True, line_separator :Optional[bytes] = None) -> Iterator[Tuple[int, bytes]]:
		if not line_separator:
			line_separator = self._default_line_separator

		for client_fileno in self.poll():
			if fileno and client_fileno != fileno:
				continue

			new_data = self._sockets[client_fileno]['socket'].recv(self._recv_len)
			if not len(new_data):
				self.close(client_fileno)
			else:
				self._sockets[client_fileno]['buffert'] += new_data
				if line_by_line:
					print()
					for line in self._sockets[client_fileno]['buffert'][0:self._sockets[client_fileno]['buffert'].rfind(line_separator)].split(line_separator):
						if line:
							yield client_fileno, line + line_separator

					self._sockets[client_fileno]['buffert'] = self._sockets[client_fileno]['buffert'][self._sockets[client_fileno]['buffert'].rfind(line_separator):]
				else:
					yield client_fileno, self._sockets[client_fileno]['buffert']
					self._sockets[client_fileno]['buffert'] = b''

	def poll(self, timeout :Union[float, int] = 0.25) -> Iterator[int]:
		for fileno, event in self.poller.poll(timeout):
			# Since self.poller.poll() protects us from ever reaching here
			# unless the socket is registered, we can safely cast this to socket.socket
			if fileno == cast(socket.socket, self.socket).fileno():
				new_client, client_addr = cast(socket.socket, self.socket).accept()
				if (block_time := self.is_blocked(client_addr[0])):
					blocked_fileno = new_client.fileno()
					new_client.close()
					log({
						"type": "networking.rejected",
						"message": "A potential cluster node was rejected due to being blocked",
						"data": {
							"addr": client_addr[0],
							"port": client_addr[1],
							"fileno": blocked_fileno,
							"time": block_time
						}
					}, level=logging.WARN, fg="yellow")
				else:
					log({
						"type": "networking.new_socket",
						"message": "new potential cluster node has connected",
						"data": {
							"addr": client_addr[0],
							"port": client_addr[1],
							"fileno": new_client.fileno()
						}
					}, level=logging.INFO)

					self._sockets[new_client.fileno()] = {
						'socket' : new_client,
						'addr' : client_addr,
						'buffert' : b''
					}
					self.poller.register(new_client.fileno(), EPOLLIN | EPOLLHUP)
			else:
				yield fileno

	def send(self, data :Union[bytes, str, str], fileno :Optional[int] = None, encoding :str = 'UTF-8', serializer :Optional[Union[Type[JSON], json.JSONEncoder]] = JSON) -> int:
		if not self.socket:
			try:
				self.listen()
			except ConnectionRefusedError:
				return -1

		if not fileno:
			# If no specific reciever was given we send
			# on all registered sockets as a broadcast
			sent_max = 0
			for fileno in self._sockets.keys():
				if (data_sent := self.send(data, fileno=fileno, encoding=encoding, serializer=serializer)) > sent_max:
					sent_max = data_sent

			return int(sent_max)
		else:
			if type(data) not in [str, bytes]:
				# We can safely assume it's an object
				# that needs JSON serialization before being
				# processed into bytes
				data = json.dumps(data, cls=cast(Type[json.JSONEncoder], serializer))

			if type(data) != bytes:
				data = bytes(str(data), encoding)

			try:
				return int(self._sockets[fileno]['socket'].send(data))
			except OSError:
				try:
					self.listen()
				except ConnectionRefusedError:
					return -1

				return int(self._sockets[fileno]['socket'].send(data))

class ClusterServer(SimplifiedServerSocket):
	"""
	TODO:
	Implementation of a cluster-share-service.
	This class listens for other nodes and can connect to other nodes.
	The purposes is to share states, machines, evacuate a node etc.
	"""
	def __init__(self) -> None:
		super(ClusterServer, self).__init__(storage['arguments'].cluster_addr, storage['arguments'].cluster_port)
		self._nodes :Dict[str, Any] = {}
		self._nodes_by_fileno :Dict[int, Any] = {}

	@property
	def interfaces(self) -> List[Dict[str, Any]]:
		from ..lib.networking import get_all_interfaces
		return get_all_interfaces()

	@property
	def harddrives(self) -> List[Dict[str, Any]]:
		from ..lib.qemu import get_harddrives
		return get_harddrives()

	def pre_process_jwt(self, fileno :int, data :bytes) -> Optional[Dict[str, Any]]:
		try:
			jwt_data = jwt.decode(data.decode(), "secret", algorithms=["HS256"])
		except jwt.exceptions.DecodeError:
			log({
				"type": "networking.invalid_data",
				"message": "Cluster sent invalid JWT data",
				"data": {
					"addr": self._sockets[fileno]['addr'][0],
					"port": self._sockets[fileno]['addr'][1],
					"fileno": fileno,
					"payload": data
				}
			}, level=logging.ERROR, fg="red")

			self.block_attempt(self._sockets[fileno]['addr'][0])

			return None

		log({
			"type": "networking.recieved_data",
			"message": "Cluster sent JWT data",
			"data": {
				"addr": self._sockets[fileno]['addr'][0],
				"port": self._sockets[fileno]['addr'][1],
				"fileno": fileno,
				"payload": jwt_data
			}
		}, level=logging.INFO)

		return {str(key): val for key, val in jwt_data.items()}

	def pre_process_json(self, fileno :int, data :bytes) -> Optional[Dict[str, Any]]:
		try:
			json_data = json.loads(data.decode())
		except json.decoder.JSONDecodeError:
			log({
				"type": "networking.broken_data",
				"message": "Cluster node sent invalid JSON data",
				"data": {
					"addr": self._sockets[fileno]['addr'][0],
					"port": self._sockets[fileno]['addr'][1],
					"fileno": fileno,
					"payload": data
				}
			}, level=logging.ERROR, fg="red")
			
			self.block_attempt(self._sockets[fileno]['addr'][0])

			return None

		log({
			"type": "networking.recieved_data",
			"message": "Cluster sent dictionary data",
			"data": {
				"addr": self._sockets[fileno]['addr'][0],
				"port": self._sockets[fileno]['addr'][1],
				"fileno": fileno,
				"payload": json_data
			}
		}, level=logging.INFO)

		return dict(json_data)

	def is_registered(self, fileno :int) -> bool:
		if fileno in self._nodes_by_fileno and self._nodes_by_fileno[fileno] in self._nodes:
			return True

		return False

	def process(self, fileno :int, data :bytes) -> None:
		if data.count(b'.') == 2 and data[:1] != b'{':
			if processed_data := self.pre_process_jwt(fileno, data):
				if processed_data.get('event') == 'register' and processed_data.get('node_id'):
					self.register_agent(fileno, processed_data['node_id'], processed_data)

				elif self.is_registered(fileno) and processed_data.get('event') == 'get_nodes':
					self.share_nodes(fileno, data)

				elif self.is_registered(fileno) and processed_data.get('event') == 'get_interfaces':
					self.share_interfaces(fileno, data)

				elif self.is_registered(fileno) and processed_data.get('event') == 'get_harddrives':
					self.share_harddrives(fileno, data)

				else:
					log({
						"type": "networking.invalid_data",
						"message": "Cluster node sent invalid data or data before registring",
						"data": {
							"addr": self._sockets[fileno]['addr'][0],
							"port": self._sockets[fileno]['addr'][1],
							"fileno": fileno,
							"payload": processed_data
						}
					}, level=logging.ERROR, fg="red")
					
					self.block_attempt(self._sockets[fileno]['addr'][0])
		else:
			processed_data = self.pre_process_json(fileno, data)

			# {"event": "register", "node_id": "sidekick"}, "secret", algorithm="HS256")
			# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJldmVudCI6InJlZ2lzdGVyIiwibm9kZV9pZCI6InNpZGVraWNrIn0.chZp2rljUsGkrp0krt3Izy5lHrdQySFbWrZTfDQjDdg

	def register_agent(self, fileno :int, node_id :str, data :Dict[str, Any] = {}) -> None:
		self._nodes[node_id] = {
			'last_seen': time.time(),
			'fileno' : fileno
		}
		self._nodes_by_fileno[fileno] = node_id
		log({
			"type": "networking.cluster.agent_register",
			"message": "Cluster node has registered itself",
			"data": {
				"addr": self._sockets[fileno]['addr'][0],
				"port": self._sockets[fileno]['addr'][1],
				"fileno": fileno,
				"payload": data
			}
		}, level=logging.INFO)

	def share_nodes(self, fileno :int, data :bytes) -> None:
		self.send(jwt.encode({"event": "update_nodes", "nodes" : self._nodes}, "secret", algorithm="HS256"), fileno)
		log({
			"type": "networking.cluster.node_sharing",
			"message": f"Sent our node-list to cluster node {self._nodes_by_fileno[fileno]}",
			"data": {
				"addr": self._sockets[fileno]['addr'][0],
				"port": self._sockets[fileno]['addr'][1],
				"fileno": fileno,
				"payload": data,
				"nodes": self._nodes
			}
		}, level=logging.INFO)

	def share_interfaces(self, fileno :int, data :bytes) -> None:
		self.send(jwt.encode({"event": "update_interfaces", "interfaces" : self.interfaces}, "secret", algorithm="HS256"), fileno)
		log({
			"type": "networking.cluster.node_sharing",
			"message": f"Sent our node-list to cluster node {self._nodes_by_fileno[fileno]}",
			"data": {
				"addr": self._sockets[fileno]['addr'][0],
				"port": self._sockets[fileno]['addr'][1],
				"fileno": fileno,
				"payload": data,
				"nodes": self._nodes
			}
		}, level=logging.INFO)

	def share_harddrives(self, fileno :int, data :bytes) -> None:
		self.send(jwt.encode({"event": "update_interfaces", "harddrives" : self.harddrives}, "secret", algorithm="HS256"), fileno)
		log({
			"type": "networking.cluster.node_sharing",
			"message": f"Sent our node-list to cluster node {self._nodes_by_fileno[fileno]}",
			"data": {
				"addr": self._sockets[fileno]['addr'][0],
				"port": self._sockets[fileno]['addr'][1],
				"fileno": fileno,
				"payload": data,
				"nodes": self._nodes
			}
		}, level=logging.INFO)