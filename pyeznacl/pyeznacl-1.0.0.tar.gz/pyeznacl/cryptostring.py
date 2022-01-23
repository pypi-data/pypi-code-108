import base64
import re

def encode85(b: bytes, pad=False) -> str:
	'''A string-oriented version of the b85encode function in the base64 module'''
	return base64.b85encode(b, pad).decode()

def decode85(s: str) -> bytes:
	'''A string-oriented version of the b85decode function in the base64 module'''
	return base64.b85decode(s.encode())

class CryptoString:
	'''This class encapsulates code for working with strings associated with an algorithm. This 
	includes hashes and encryption keys.'''

	def __init__(self, string='', data=None):
		'''Create a CryptoString object, optionally based on existing data.

		Parameters:
		string: If used by itself, this is expected to be a CryptoString-formatted string. If the 
		data parameter is used, this must contain only the CryptoString prefix for the data.
		data: Raw binary data. If used, the string parameter must contain the string prefix, e.g. 
		'BLAKE3-256'.

		Notes:
		The two different ways of using the CryptoString constructor affords great flexibility in 
		exchange for being a little confusing -- it can be used like set() or set_raw().
		'''
		self.prefix = ''
		self.data = ''
		
		if data and isinstance(data, bytes):
			self.set_raw(string, data)
		else:
			self.set(string)
	
	def set(self, data: str) -> bool:
		'''Initializes the instance from data passed to it.
		
		Parameters:
		data: A string in the format ALGORITHM:DATA, where DATA is assumed to be base85-encoded raw 
		byte data

		Returns:
		True if successfully set.
		'''

		if not data:
			self.prefix = ''
			self.data = ''
			return True

		if not is_cryptostring(data):
			return False

		self.prefix, self.data = data.split(':', 1)
		return True

	def set_raw(self, prefix: str, data: bytes) -> str:
		'''Initializes the instance to some raw data and a prefix.
		
		Parameters:
		prefix: The CryptoString prefix for the data
		data: Raw, unencoded binary data, such as the output from nacl.public.PrivateKey.generate().

		Returns:
		A CryptoString-formatted string representing the original data. This method returns an 
		empty string if an error has occurred.
		'''

		if not (prefix and data):
			return ''
		
		encoded = encode85(data)

		if not is_cryptostring(f"{prefix}:{encoded}"):
			return ''
		
		self.prefix = prefix
		self.data = encoded
		return f"{prefix}:{encoded}"

	def __str__(self):
		return f"{self.prefix}:{self.data}"
	
	def __eq__(self, b):
		return self.prefix == b.prefix and self.data == b.data

	def __ne__(self, b):
		return self.prefix != b.prefix or self.data != b.data

	def as_string(self):
		'''Returns the instance information as a string'''

		return f"{self.prefix}:{self.data}"
	
	def as_bytes(self) -> bytes:
		'''Returns the instance information as a byte string'''

		return b'%s:%s' % (self.prefix, self.data)
	
	def as_raw(self) -> bytes:
		'''Decodes the internal data and returns it as a byte string.'''

		return base64.b85decode(self.data)
	
	def is_valid(self) -> bool:
		'''Returns false if the prefix and/or the data is missing'''

		return self.prefix and self.data
	
	def make_empty(self):
		'''Makes the entry empty'''

		self.prefix = ''
		self.data = ''


def is_cryptostring(string: str) -> bool:
	'''Checks a string to see if it matches the CryptoString format'''
	
	m = re.match(r'^[A-Z0-9-]{1,24}:', string)
	if not m:
		return False

	parts = string.split(':', 1)
	if len(parts) != 2:
		return False

	try:
		base64.b85decode(parts[1])
	except ValueError:
		return False
	
	return True
	