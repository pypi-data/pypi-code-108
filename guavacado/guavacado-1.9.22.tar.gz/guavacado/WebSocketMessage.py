#! /usr/bin/env python
'''
Object controlling bufferring of data in a single message over a WebSocket
'''

import time
import threading

class WebSocketMessage(object):
	'''
	Object controlling bufferring of data in a single message over a WebSocket
	'''
	
	def __init__(self, complete=False, buf=b'', preserve_buf=True, text_or_bin='binary'):
		self.read_lock = threading.Lock()
		self.write_lock = threading.Lock()
		self.completion_lock = threading.Lock()
		self.complete = complete
		self.completion_callbacks = []
		self.buf = buf
		self.len_so_far = len(buf)
		self.read_pos = 0
		self.buf_offset = 0
		self.preserve_buf = preserve_buf
		self.text_or_bin = text_or_bin
	
	def write(self, data):
		'''writes the specified data into the buffer for the WebSocket message'''
		with self.write_lock:
			self.buf = self.buf + data
			self.len_so_far = self.len_so_far + len(data)
	
	def write_all(self, data):
		'''writes the specified data into the buffer for the WebSocket message then marks the end of the message'''
		self.write(data)
		self.end_message()
		
	def end_message(self):
		'''marks the end of the message and triggers any completion callbacks'''
		with self.completion_lock:
			self.complete = True
			for	callback in self.completion_callbacks:
				callback()

	def read(self, n=None):
		'''reads up to n bytes of the message - if n is not specified, reads all available bytes'''
		with self.read_lock:
			end_pos = self.len_so_far
			if n is not None:
				end_pos = min(self.len_so_far, self.buf_offset + self.read_pos + n)
			ret = self.buf[self.read_pos - self.buf_offset : end_pos - self.buf_offset]
			self.read_pos = end_pos
			if not self.preserve_buf:
				with self.write_lock:
					self.buf = self.buf[end_pos - self.buf_offset:]
					self.buf_offset = end_pos
			return ret
	
	def read_all(self):
		'''reads to the end of the message'''
		while not self.complete:
			time.sleep(0.005)
		return self.read()
		
	def readexactly(self, n):
		'''reads exactly n bytes from the message'''
		ret = b''
		while len(ret) < n:
			ret = ret + self.read(n-len(ret))
		return ret
	
	def get_full_buf(self):
		'''waits until message is marked as complete then returns the full buffer from the beginning of the message - only works if preserve_buf is True or no data is read yet'''
		if self.buf_offset==0:
			if self.complete:
				return self.buf
			else:
				while not self.complete:
					time.sleep(0.005)
				return self.buf
		else:
			raise Exception('Cannot get the complete buffer because some data has been disposed! Try setting the preserve_buf parameter to True on the message.')
	
	def is_complete(self):
		'''returns whether the message has been marked as complete'''
		return self.complete
	
	def is_all_read(self):
		'''returns whether all bytes have been read from the message'''
		return self.complete and self.read_pos==self.len_so_far
	
	def register_completion_callback(self, callback):
		'''registers callback function for when the message is completed'''
		with self.completion_lock:
			if self.complete:
				callback()
			else:
				self.completion_callbacks.append(callback)
	
	def set_text_or_bin(self, text_or_bin):
		'''marks whether the message is in text format or binary format'''
		self.text_or_bin = text_or_bin
	
	def get_text_or_bin(self):
		'''returns whether the message is marked as text format or binary format'''
		return self.text_or_bin
