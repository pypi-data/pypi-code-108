'''This module contains quick access to different hash functions'''

import base64
import hashlib

from blake3 import blake3
from retval import RetVal, ErrBadValue

def blake2hash(data: bytes) -> str:
	'''Returns a CryptoString-formatted BLAKE2B-256 hash string of the passed data'''
	if data is None or data == '':
		return ''
	
	hasher=hashlib.blake2b(digest_size=32)
	hasher.update(data)
	return "BLAKE2B-256:" + base64.b85encode(hasher.digest()).decode()


def blake3hash(data: bytes) -> str:
	'''Returns a CryptoString-formatted BLAKE3-256 hash string of the passed data'''
	if data is None or data == '':
		return ''
	
	hasher = blake3.blake3() # pylint: disable=c-extension-no-member
	hasher.update(data)
	return "BLAKE3-256:" + base64.b85encode(hasher.digest()).decode()


def sha256hash(data: bytes) -> str:
	'''Returns a CryptoString-formatted SHA-256 hash string of the passed data'''
	if data is None or data == '':
		return ''
	
	hasher=hashlib.sha256()
	hasher.update(data)
	return "SHA-256:" + base64.b85encode(hasher.digest()).decode()


def sha3_256hash(data: bytes) -> str:
	'''Returns a CryptoString-formatted SHA3-256 hash string of the passed data'''
	if data is None or data == '':
		return ''
	
	hasher=hashlib.sha3_256()
	hasher.update(data)
	return "SHA3-256:" + base64.b85encode(hasher.digest()).decode()


def hashfile(path: str, algorithm='BLAKE2B-256') -> RetVal:
	'''Returns a hash of the passed file in the 'hash' field.
	
	Parameters:
	path: path to the file to hash
	algorithm: The type of hash to return. Defaults to 'BLAKE2B-256', but also can be 'BLAKE3-256' 
	'SHA-256', or 'SHA3-256'.
	
	Returns:
	field 'hash': a CryptoString-formatted string of the hash of the file
	'''
	if not path:
		return RetVal(ErrBadValue, 'bad path')
	
	hasher = None
	if algorithm == 'BLAKE2B-256':
		hasher = hashlib.blake2b(digest_size=32)
	elif algorithm == 'BLAKE3-256':
		hasher = blake3.blake3() # pylint: disable=c-extension-no-member
	elif algorithm == 'SHA-256':
		hasher = hashlib.sha256()
	elif algorithm == 'SHA3-256':
		hasher = hashlib.sha3_256()
	else:
		return RetVal(ErrBadValue, 'bad algorithm')
	
	try:
		handle = open(path, 'rb')
	except Exception as e:
		return RetVal().wrap_exception(e)

	filedata = handle.read(8192)
	while filedata:
		hasher.update(filedata)
		filedata = handle.read(8192)
	
	handle.close()

	return RetVal().set_value('hash', f"{algorithm}:{base64.b85encode(hasher.digest()).decode()}")
