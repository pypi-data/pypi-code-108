#! /usr/bin/env python

import struct
import threading
import time
import os
from .WebRequestHandler import WebRequestHandlingException
from .WebSocketMessage import WebSocketMessage

class WebSocketException(WebRequestHandlingException):
	'''base class for all exceptions related to web sockets'''

class WebSocketProtocolException(WebSocketException):
	'''indicates a protocol issue with web sockets'''

class WebSocketCloseTimeoutException(WebSocketProtocolException):
	'''timeout in waiting for the peer to close after attempting to close'''

class WebSocketPingDataException(WebSocketProtocolException):
	'''incorrect data returned from a pong'''

class InvalidWebSocketFrameOpCode(WebSocketProtocolException):
	'''indicates an invalid opcode from the websocket peer'''

class WebSocketHandler(object):
	"""
	Object controlling communication over a WebSocket after headers are complete
	"""

	def __init__(self, web_request_handler, message_callback, is_client = False):
		self.send_msg_lock = threading.Lock()
		self.ping_lock = threading.Lock()
		self.ping_signal = threading.Condition()
		self.last_pong_time = None
		self.last_pong_data = None
		self.web_request_handler = web_request_handler
		self.message_callback = message_callback
		self.is_client = is_client
		self.close_sent = False
		self.close_send_time = None
		self.close_received = False
		self.messages_to_handle = []
		self.messages_waiting = threading.Condition()
		self.end_message_handling = False

	def send_message(self, msg, msg_type='binary'):
		with self.send_msg_lock:
			masked = self.is_client
			max_fragment_size = 1 << 32
			first_frame = True
			while not msg.is_all_read():
				payload = msg.read(n=max_fragment_size)
				last_frame = msg.is_all_read()
				if len(payload)>0 or last_frame:
					if first_frame:
						if msg_type=='text':
							opcode = 0x01
						elif msg_type=='binary':
							opcode = 0x02
						elif msg_type=='close':
							self.close_sent = True
							if self.close_send_time is None:
								self.close_send_time = time.time()
							opcode = 0x08
						elif msg_type=='ping':
							opcode = 0x09
						elif msg_type=='pong':
							opcode = 0x0A
						else:
							# treat as binary for default
							opcode = 0x02
					else:
						opcode = 0x00
					if last_frame:
						fin_bit = 0x01
					else:
						fin_bit = 0x00
					first_byte = opcode ^ (fin_bit << 7)
					if masked:
						mask_bit = 0x01
					else:
						mask_bit = 0x00
					payload_len = len(payload)
					if payload_len < 126:
						payload_len_0 = payload_len
						payload_additional_bytes = b''
					elif payload_len < (1 << 16):
						payload_len_0 = 126
						# payload_additional_bytes = struct.pack('<H',payload_len)
						payload_additional_bytes = bytes([
							(payload_len & (0xff << 8)) >> 8, 
							payload_len & 0xff,
						])
					else:
						payload_len_0 = 127
						# payload_additional_bytes = struct.pack('<I',payload_len)
						payload_additional_bytes = bytes([
							(payload_len & (0xff << 56)) >> 56, 
							(payload_len & (0xff << 48)) >> 48, 
							(payload_len & (0xff << 40)) >> 40, 
							(payload_len & (0xff << 32)) >> 32, 
							(payload_len & (0xff << 24)) >> 24, 
							(payload_len & (0xff << 16)) >> 16, 
							(payload_len & (0xff << 8)) >> 8, 
							payload_len & 0xff,
						])
					second_byte = (payload_len_0 & 127) ^ (mask_bit << 7)
					if masked:
						masking_key = os.urandom(4)
						masked_payload = bytes([masking_key[i%4] ^ payload[i] for i in range(len(payload))])
					else:
						masking_key = b''
						masked_payload = payload
					packet = bytes([first_byte, second_byte]) + payload_additional_bytes + masking_key + masked_payload
					self._send_bytes(packet)
				else:
					time.sleep(0.1)
	
	def run(self):
		msg_thread = threading.Thread(target=self.handle_messages_continuous, name='WebSocket_message_processing__clientid_{client_id}'.format(client_id=self.web_request_handler.client_id))
		msg_thread.start()
		while not self.close_received:
			self._recv_message()
			if (not self.close_received) and self.close_sent and (self.close_send_time is not None) and (self.close_send_time - time.time() > 30):
				raise WebSocketCloseTimeoutException('No close frame received from peer within 30 seconds of sending!')
		self.end_message_handling = True
		with self.messages_waiting:
			self.messages_waiting.notify_all()
		msg_thread.join()
	
	def handle_messages_continuous(self):
		while not self.end_message_handling or len(self.messages_to_handle) > 0:
			while len(self.messages_to_handle) > 0:
				if self.message_callback is not None:
					self.message_callback(self.messages_to_handle[0])
				self.messages_to_handle = self.messages_to_handle[1:]
			if not self.end_message_handling:
				with self.messages_waiting:
					self.messages_waiting.wait()

	def _recv_message(self):
		msg = WebSocketMessage()
		first_frame = True
		last_frame = False
		first_opcode = None
		while not last_frame:
			first_byte = self._recv_bytes(1)[0]
			last_frame = (first_byte & 0x80)==0x80 # most significant bit
			_rsv1 = (first_byte & 0x40)==0x40 # 2nd bit
			_rsv2 = (first_byte & 0x20)==0x20 # 3rd bit
			_rsv3 = (first_byte & 0x10)==0x10 # 4th bit
			opcode = first_byte & 0x0f # 4 least significant bits
			second_byte = self._recv_bytes(1)[0]
			masked = (second_byte & 0x80)==0x80 # most significant bit
			payload_len_0 = second_byte & 0x7f # 7 least significant bits
			if payload_len_0==126:
				len_bytes = self._recv_bytes(2)
				# big-endian 16-bit number
				payload_len = (len_bytes[0] << 8) ^ len_bytes[1]
			elif payload_len_0==127:
				len_bytes = self._recv_bytes(8)
				# big-endian 64-bit number
				payload_len = (
					(len_bytes[0] << 56) ^ 
					(len_bytes[1] << 48) ^ 
					(len_bytes[2] << 40) ^ 
					(len_bytes[3] << 32) ^ 
					(len_bytes[4] << 24) ^ 
					(len_bytes[5] << 16) ^ 
					(len_bytes[6] << 8) ^ 
					len_bytes[7]
				)
			else:
				payload_len = payload_len_0
			if masked:
				masking_key = self._recv_bytes(4)
			else:
				masking_key = b''
			masked_payload = self._recv_bytes(payload_len)
			if masked:
				payload = bytes([masking_key[i%4] ^ masked_payload[i] for i in range(len(masked_payload))])
			else:
				payload = masked_payload
			if first_frame:
				first_frame = False
				first_opcode = opcode
				if opcode==0x00: # continuation frame - invalid in first fragment
					raise InvalidWebSocketFrameOpCode('Received continuation frame opcode on first fragment of message!')
				elif opcode in [0x01, 0x02]: # text/binary message
					if opcode==0x01: # text message
						msg.set_text_or_bin('text')
					else: # binary message
						msg.set_text_or_bin('binary')
					self.messages_to_handle.append(msg)
					with self.messages_waiting:
						self.messages_waiting.notify_all()
				elif opcode in [0x08, # connection close
								0x09, # ping
								0x0A]: # pong
					pass
				else:
					raise InvalidWebSocketFrameOpCode('Unrecognized opcode {opcode}!'.format(opcode=opcode))
				msg.write(payload)
			else:
				if opcode!=0x00:
					raise InvalidWebSocketFrameOpCode('Expected continuation frame but got opcode {opcode}!'.format(opcode=opcode))
				msg.write(payload)
		msg.end_message()
		if first_opcode==0x08: # connection close
			self.close_received = True
			if not self.close_sent:
				self.close_connection()
		elif first_opcode==0x09: # ping
			pong_msg = WebSocketMessage()
			pong_msg.write(msg.read_all())
			pong_msg.end_message()
			self.send_message(pong_msg, msg_type='pong')
		elif first_opcode==0x0A: # pong
			self.last_pong_time = time.time()
			self.last_pong_data = msg.read_all()
			self.ping_signal.notify_all()
	
	def _recv_bytes(self, num_bytes):
		return self.web_request_handler.recv_bytes(num_bytes)
	
	def _send_bytes(self, data):
		self.web_request_handler.clientsocket.sendall(data)
	
	def close_connection(self, code=1000, reason=''):
		'''
		Closes the connection, with the given status code and reason.
		`code` must be an integer less than 65536.  See https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1 for defined codes.
		'''
		self.close_sent = True
		close_msg = WebSocketMessage()
		close_msg.write(struct.pack('<H',code))
		close_msg.write(reason.encode('utf-8'))
		close_msg.end_message()
		self.close_send_time = time.time()
		self.send_message(close_msg, msg_type='close')
	
	def ping(self, ping_data=b''):
		def is_pong_stored():
			return self.last_pong_data is not None
		with self.ping_lock:
			start_time = time.time()
			ping_msg = WebSocketMessage()
			ping_msg.write(ping_data)
			ping_msg.end_message()
			self.send_message(ping_msg, msg_type='ping')
			self.ping_signal.wait_for(is_pong_stored, timeout=0.25)
			if self.last_pong_data!=ping_data:
				raise WebSocketPingDataException('The ping received different data than was sent!')
			return self.last_pong_time - start_time
