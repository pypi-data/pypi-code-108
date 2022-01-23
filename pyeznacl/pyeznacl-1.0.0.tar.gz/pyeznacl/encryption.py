'''Holds classes designed for working with encryption keys'''
import base64
import json
import os
import re
from typing import Union

import jsonschema
from nacl.exceptions import InvalidkeyError
import nacl.public
import nacl.pwhash
import nacl.secret
import nacl.signing
import nacl.utils
from retval import RetVal, ErrBadData, ErrBadValue, ErrBadType, ErrInternalError, ErrExists, \
	ErrNotFound

from pyeznacl.cryptostring import CryptoString
from pyeznacl.ezhash import blake2hash

VerificationError = 'VerificationError'
DecryptionFailure = 'DecryptionFailure'
ErrUnsupportedAlgorithm = 'ErrUnsupportedAlgorithm'

# JSON schemas used to validate keyfile data
__encryption_pair_schema = {
	'type' : 'object',
	'properties' : {
		'EncryptionKey' : { 'type' : 'string' },
		'DecryptionKey' : { 'type' : 'string' },
	}
}

__signing_pair_schema = {
	'type' : 'object',
	'properties' : {
		'VerificationKey' : { 'type' : 'string' },
		'SigningKey' : { 'type' : 'string' },
	}
}

__secret_key_schema = {
	'type' : 'object',
	'properties' : {
		'SecretKey' : { 'type' : 'string' }
	}
}

class CryptoKey:
	'''Defines a generic interface to a Mensago encryption key, which contains more
	information than just the key itself'''
	def __init__(self):
		self.pubhash = ''
		self.privhash = ''
		self.enctype = ''
		self.type = ''
	
	def get_encryption_type(self):
		'''Returns the name of the encryption used, such as rsa, aes256, etc.'''
		return self.enctype

	def get_type(self):
		'''Returns the type of key, such as asymmetric or symmetric'''
		return self.type


class PublicKey (CryptoKey):
	'''Represents a public encryption key'''

	def __init__(self, public: Union[CryptoString, str]):
		'''Creates a new PublicKey instance
		
		Parameters:
		public: the public half of an asymmetric key pair. It can be a CryptoString object or a 
		CryptoString-formatted string.

		Notes:
		After initializing this object, it is a good idea to check validity with is_valid().
		'''
		super().__init__()
		
		if public and isinstance(public, CryptoString):
			self.public = public
		else:
			cs = CryptoString()
			if cs.set(public):
				self.public = cs
			else:
				self.public = CryptoString()

		if self.public.is_valid():		
			self.pubhash = CryptoString(blake2hash(self.public.data.encode()))
		else:
			self.pubhash = CryptoString()
	
	def as_string(self):
		'''Returns the key as a CryptoString-formatted string'''
		return self.public.as_string()

	def encrypt(self, data : bytes) -> RetVal:
		'''Encrypt the passed data using the public key.
		
		Parameters:
		data: the data to encrypt
		
		Returns:
		field 'data': the Base85-encoded encrypted data 
		field 'prefix': the CryptoString prefix for the encrypted data'''
		if not isinstance(data, bytes):
			return RetVal(ErrBadType, 'bytes expected')
		
		try:
			sealedbox = nacl.public.SealedBox(nacl.public.PublicKey(self.public.as_raw()))
			encrypted_data = sealedbox.encrypt(data, Base85Encoder).decode()
		except Exception as e:
			return RetVal().wrap_exception(e)
		
		return RetVal().set_values({'prefix':self.public.prefix, 'data':encrypted_data})
	
	def is_valid(self) -> bool:
		'''Returns true if the object contains valid data'''
		if self.public and self.public.is_valid() and self.pubhash and self.pubhash.is_valid():
			return True
		
		return False


class EncryptionPair (CryptoKey):
	'''Represents an assymmetric encryption key pair'''

	def __init__(self, public=None, private=None):
		'''Creates a new EncryptionPair instance
		
		Parameters:
		public (optional): a CryptoString object or a CryptoString-formatted string containing the 
		public half of the key pair.
		
		private (optional): a CryptoString object or a CryptoString-formatted string containing the 
		private half of the key pair.

		Notes:
		Both the public and private keys are required if supplied. If either one (or both) is 
		missing a new keypair will be generated.
		'''
		super().__init__()

		self.public = CryptoString()
		self.private = CryptoString()
		self.pubhash = CryptoString()
		self.privhash = CryptoString()
		
		if not public or not private:
			self._generate()
			return
		
		if isinstance(public, CryptoString):
			pubadapter = public
		else:
			pubadapter = CryptoString(public)
		
		if not pubadapter.is_valid():
			self._generate()
			return
		
		if isinstance(private, CryptoString):
			privadapter = private
		else:
			privadapter = CryptoString(private)
		
		if not privadapter.is_valid():
			self._generate()
			return
		
		self.enctype = public.prefix
		self.public = pubadapter
		self.private = privadapter

		self.pubhash = CryptoString(blake2hash(self.public.data.encode()))
		self.privhash = CryptoString(blake2hash(self.private.data.encode()))

	def _generate(self):
		'''Resets the EncryptionKey instance to a new keypair'''

		key = nacl.public.PrivateKey.generate()
		self.enctype = 'CURVE25519'
		
		self.public = CryptoString('CURVE25519', key.public_key.encode())
		self.private = CryptoString('CURVE25519', key.encode())
		self.pubhash = CryptoString(blake2hash(self.public.data.encode()))
		self.privhash = CryptoString(blake2hash(self.private.data.encode()))

	def __str__(self):
		return self.as_string()

	def as_string(self) -> str:
		'''Returns the keypair as a string'''
		return ','.join([
			self.public.as_string(),
			self.private.as_string()
		])
	
	def as_dict(self) -> dict:
		'''Returns the keypair as a dictionary'''
		return {
			'EncryptionKey' : self.get_public_key(),
			'EncryptionHash' : self.get_public_hash(),
			'DecryptionKey' : self.get_private_key(),
			'DecryptionHash' : self.get_private_hash()
		}

	def get_public_key(self) -> str:
		'''Returns the public key as a CryptoString-formatted string'''
		return self.public.as_string()
	
	def get_public_hash(self) -> str:
		'''Returns the hash of the public key as a CryptoString-formatted string.
		
		Notes:
		The hash is generated from the encoded key, not the raw binary data.'''
		return self.pubhash.as_string()
	
	def get_private_key(self) -> str:
		'''Returns the private key as a CryptoString-formatted string'''
		return self.private.as_string()

	def get_private_hash(self) -> str:
		'''Returns the hash of the private key as a CryptoString-formatted string.
		
		Notes:
		The hash is generated from the encoded key, not the raw binary data.'''
		return self.privhash.as_string()
	
	def encrypt(self, data : bytes) -> RetVal:
		'''Encrypt the passed data using the public key.
		
		Parameters:
		data: the data to encrypt as a byte string
		
		Returns:
		field 'data': The Base85-encoded encrypted data.
		'''
		if not isinstance(data, bytes):
			return RetVal(ErrBadType, 'bytes expected')
		
		try:
			sealedbox = nacl.public.SealedBox(nacl.public.PublicKey(self.public.as_raw()))
			encrypted_data = sealedbox.encrypt(data, Base85Encoder).decode()
		except Exception as e:
			return RetVal().wrap_exception(e)
		
		return RetVal().set_values({'prefix':self.public.prefix, 'data':encrypted_data})

	def decrypt(self, data : str) -> RetVal:
		'''Decrypt the passed data using the private key
		
		Parameters:
		data: the Base85-encoded encrypted data
		
		Returns:
		field 'data': the decrypted data
		'''
		if not isinstance(data, str):
			return RetVal(ErrBadType, 'string expected')
		
		try:
			sealedbox = nacl.public.SealedBox(nacl.public.PrivateKey(self.private.as_raw()))
			decrypted_data = sealedbox.decrypt(data.encode(), Base85Encoder)
		except Exception as e:
			return RetVal().wrap_exception(e)
		
		return RetVal().set_value('data', decrypted_data.decode())

	def is_valid(self) -> bool:
		'''Returns true if the object contains valid data'''
		if self.public and self.public.is_valid() and self.pubhash and self.pubhash.is_valid() and \
			self.public.prefix == self.private.prefix:
			return True
		
		return False


def load_encryptionpair(path: str) -> RetVal:
	'''Instantiates a keypair from a file created with save_encryptionpair()

	Parameters:
	path: the path to the file

	Returns:
	field 'keypair': an EncryptionPair object
	'''

	if not path:
		return RetVal(ErrBadValue, 'path may not be empty')
	
	if not os.path.exists(path):
		return RetVal(ErrNotFound, f'{path} exists')
	
	indata = None
	try:
		with open(path, 'r', encoding='utf8') as fhandle:
			indata = json.load(fhandle)
	
	except Exception as e:
		return RetVal().wrap_exception(e)
	
	if not isinstance(indata, dict):
		return RetVal(ErrBadData, 'File does not contain an Mensago JSON keypair')

	try:
		jsonschema.validate(indata, __encryption_pair_schema)
	except jsonschema.ValidationError:
		return RetVal(ErrBadData, "file data does not validate")
	except jsonschema.SchemaError:
		return RetVal(ErrInternalError, "BUG: invalid EncryptionPair schema")

	public_key = CryptoString(indata['EncryptionKey'])
	private_key = CryptoString(indata['DecryptionKey'])
	if not public_key.is_valid() or not private_key.is_valid():
		return RetVal(ErrBadData, 'Failure to base85 decode key data')
	
	return RetVal().set_value('keypair', EncryptionPair(public_key, private_key))


def save_encryptionpair(key: EncryptionPair, path: str):
	'''Saves a keypair to a JSON-formatted file'''
	if not path:
		return RetVal(ErrBadValue, 'path may not be empty')
	
	if os.path.exists(path):
		return RetVal(ErrExists, f'{path} exists')

	try:
		with open(path, 'w', encoding='utf8') as fhandle:
			json.dump(key.as_dict(), fhandle, ensure_ascii=False, indent=1)
	
	except Exception as e:
		return RetVal().wrap_exception(e)

	return RetVal()


class VerificationKey (CryptoKey):
	'''Represents the public half of a signing keypair'''
	def __init__(self, public):
		'''Creates a new VerificationKey instance
		
		Parameters:
		public: the public half of an signing key pair. It can be a CryptoString object or a 
		CryptoString-formatted string.

		Notes:
		After initializing this object, it is a good idea to check validity with is_valid().
		'''
		super().__init__()
		
		if public and isinstance(public, CryptoString):
			self.public = public
		else:
			cs = CryptoString()
			if cs.set(public):
				self.public = cs
			else:
				self.public = CryptoString()

		if self.public.is_valid():		
			self.pubhash = CryptoString(blake2hash(self.public.data.encode()))
		else:
			self.pubhash = CryptoString()
	
	def as_string(self):
		'''Returns the key as a string'''
		return self.public.as_string()

	def verify(self, data: bytes, data_signature: CryptoString) -> RetVal:
		'''Verifies a signature with the passed data.
		
		Parameters:
		data: the data to verify against the signature
		data_signature: the signature to verify. Unlike most calls this parameter must be a
		CryptoString instance.

		Returns:
		Errors only. VerificationError is returned if the signature fails to verify the data 
		using this verification key.
		'''

		if not isinstance(data, bytes):
			return RetVal(ErrBadType, 'bytes expected for data')
		if not isinstance(data_signature, CryptoString):
			return RetVal(ErrBadType, 'signature parameter must be a CryptoString')
		
		key = nacl.signing.VerifyKey(self.public.as_raw())

		try:
			key.verify(data, data_signature.as_raw())
		except Exception as e:
			return RetVal(VerificationError, e)
		
		return RetVal()
	
	def is_valid(self) -> bool:
		'''Returns true if the object contains valid data'''
		if self.public and self.public.is_valid() and self.pubhash and self.pubhash.is_valid():
			return True
		
		return False


class SigningPair:
	'''Represents an asymmetric signing key pair'''
	def __init__(self, public=None, private=None):
		'''Creates a new SigningPair instance
		
		Parameters:
		public (optional): a CryptoString object or a CryptoString-formatted string containing the 
		public half of the key pair.
		
		private (optional): a CryptoString object or a CryptoString-formatted string containing the 
		private half of the key pair.

		Notes:
		Both the public and private keys are required if supplied. If either one (or both) is 
		missing a new keypair will be generated.
		'''
		super().__init__()

		self.public = CryptoString()
		self.private = CryptoString()
		self.pubhash = CryptoString()
		self.privhash = CryptoString()
		
		if not public or not private:
			self._generate()
			return
		
		if isinstance(public, CryptoString):
			pubadapter = public
		else:
			pubadapter = CryptoString(public)
		
		if not pubadapter.is_valid():
			self._generate()
			return
		
		if isinstance(private, CryptoString):
			privadapter = private
		else:
			privadapter = CryptoString(private)
		
		if not privadapter.is_valid():
			self._generate()
			return
		
		self.enctype = public.prefix
		self.public = pubadapter
		self.private = privadapter

		self.pubhash = CryptoString(blake2hash(self.public.data.encode()))
		self.privhash = CryptoString(blake2hash(self.private.data.encode()))
		
	def _generate(self):
		'''Resets the EncryptionKey instance to a new keypair'''

		key = nacl.public.PrivateKey.generate()
		self.enctype = 'CURVE25519'
		
		self.public = CryptoString('CURVE25519', key.public_key.encode())
		self.private = CryptoString('CURVE25519', key.encode())
		self.pubhash = CryptoString(blake2hash(self.public.data.encode()))
		self.privhash = CryptoString(blake2hash(self.private.data.encode()))

	def __str__(self):
		return self.as_string()

	def as_string(self) -> str:
		'''Returns the keypair as a string'''
		return ','.join([
			self.public.as_string(),
			self.private.as_string()
		])
	
	def as_dict(self) -> dict:
		'''Returns the keypair as a dictionary'''
		return {
			'VerificationKey' : self.get_public_key(),
			'VerificationHash' : self.get_public_hash(),
			'SigningKey' : self.get_private_key(),
			'SigningHash' : self.get_private_hash()
		}

	def get_public_key(self) -> str:
		'''Returns the public key as a CryptoString-formatted string'''
		return self.public.as_string()
	
	def get_public_hash(self) -> str:
		'''Returns the hash of the public key as a CryptoString-formatted string.
		
		Notes:
		The hash is generated from the encoded key, not the raw binary data.'''
		return self.pubhash.as_string()
	
	def get_private_key(self) -> str:
		'''Returns the private key as a CryptoString-formatted string'''
		return self.private.as_string()

	def get_private_hash(self) -> str:
		'''Returns the hash of the private key as a CryptoString-formatted string.
		
		Notes:
		The hash is generated from the encoded key, not the raw binary data.'''
		return self.privhash.as_string()
	
	def sign(self, data : bytes) -> RetVal:
		'''Generates a CryptoString-formatted string signature for the supplied data
		
		Returns:
		field 'signature': the generated signature
		'''
		if not isinstance(data, bytes):
			return RetVal(ErrBadType, 'bytes expected for data')
		
		key = nacl.signing.SigningKey(self.private.as_raw())

		try:
			signed = key.sign(data, Base85Encoder)
		except Exception as e:
			return RetVal().wrap_exception(e)
		
		return RetVal().set_value('signature', 'ED25519:' + signed.signature.decode())
	
	def verify(self, data : bytes, data_signature : CryptoString) -> RetVal:
		'''Verifies a signature
		
		Parameters:
		data: a byte string of data to verify
		data_signature: a CryptoString object containing the signature to verify

		Notes:
		If the signature does not verify the passed data with the verification key held by the 
		keypair, VerificationError is returned.
		'''
		
		if not isinstance(data, bytes):
			return RetVal(ErrBadType, 'bytes expected for data')
		if not isinstance(data_signature, CryptoString):
			return RetVal(ErrBadType, 'signature parameter must be a CryptoString')
		
		key = nacl.signing.VerifyKey(self.public.as_raw())

		try:
			key.verify(data, data_signature.as_raw())
		except Exception as e:
			return RetVal(VerificationError, e)
		
		return RetVal()

	def is_valid(self) -> bool:
		'''Returns true if the object contains valid data'''
		if self.public and self.public.is_valid() and self.pubhash and self.pubhash.is_valid() and \
			self.public.prefix == self.private.prefix:
			return True
		
		return False


def signingpair_from_string(keystr: str) -> SigningPair:
	'''Intantiates a SigningPair from a saved seed string that is used for the private key.
	
	Notes:
	The seed string must be Base85-encoded.'''
	
	key = nacl.signing.SigningKey(base64.b85decode(keystr))
	return SigningPair(
		CryptoString('ED25519', key.verify_key.encode()),
		CryptoString('ED25519', key.encode())
	)


def save_signingpair(key: SigningPair, path: str) -> RetVal:
	'''Saves a signing keypair to a JSON-formatted file'''
	if not path:
		return RetVal(ErrBadValue, 'path may not be empty')
	
	if os.path.exists(path):
		return RetVal(ErrExists, f'{path} exists')

	try:
		with open(path, 'w', encoding='utf8') as fhandle:
			json.dump(key.as_dict(), fhandle, ensure_ascii=False, indent=1)
	
	except Exception as e:
		return RetVal().wrap_exception(e)

	return RetVal()
	

def load_signingpair(path: str) -> RetVal:
	'''Instantiates a signing pair from a file saved with save_signingpair()
	
	Parameters:
	path: the path to the file

	Returns:
	field 'keypair': a SigningPair object
	'''
	if not path:
		return RetVal(ErrBadValue, 'path may not be empty')
	
	if not os.path.exists(path):
		return RetVal(ErrNotFound, f'{path} exists')
	
	indata = None
	try:
		with open(path, 'r', encoding='utf8') as fhandle:
			indata = json.load(fhandle)
	
	except Exception as e:
		return RetVal().wrap_exception(e)
	
	if not isinstance(indata, dict):
		return RetVal(ErrBadData, 'File does not contain an Mensago JSON signing pair')

	try:
		jsonschema.validate(indata, __signing_pair_schema)
	except jsonschema.ValidationError:
		return RetVal(ErrBadData, "file data does not validate")
	except jsonschema.SchemaError:
		return RetVal(ErrInternalError, "BUG: invalid SigningPair schema")

	public_key = CryptoString(indata['VerificationKey'])
	private_key = CryptoString(indata['SigningKey'])
	if not public_key.is_valid() or not private_key.is_valid():
		return RetVal(ErrBadData, 'Failure to base85 decode key data')
	
	return RetVal().set_value('keypair', SigningPair(public_key, private_key))


class SecretKey (CryptoKey):
	'''Represents a secret key used by symmetric encryption'''
	def __init__(self, key=None):
		'''Creates a new SecretKey instance
		
		Parameters:
		key (optional): a CryptoString instance or a CryptoString-formatted string containing the 
		secret key

		Notes:
		If the key parameter is not supplied or is invalid, a new secret key will be generated from 
		a cryptographically-secure source.
		'''
		super().__init__()

		if key and isinstance(key, CryptoString):
			self.key = key
		else:
			cs = CryptoString()
			if cs.set(key):
				self.key = cs
			else:
				self.key = CryptoString()

		if self.key.is_valid():
			self.enctype = self.key.prefix
		else:
			self.enctype = 'XSALSA20'
			self.key = CryptoString('XSALSA20', nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))

		# This silliness is just for CryptoKey compatibility		
		self.privhash = CryptoString(blake2hash(self.key.data.encode()))
		self.pubhash = self.privhash

	def __str__(self):
		return self.get_key()

	def is_valid(self):
		'''Returns true if the key is valid'''
		return self.key.is_valid() and self.pubhash.is_valid()

	def as_string(self) -> str:
		'''Returns the CryptoString-formatted key as a string'''
		return self.key.as_string()
	
	def as_dict(self) -> dict:
		'''Returns the key and hash as a dictionary'''
		
		return {
			'SecretKey': self.get_key(),
			'SecretHash': self.get_hash()
		}
	
	def get_key(self) -> str:
		'''Returns the CryptoString-formatted key as a string'''
		return self.key.as_string()
	
	def get_hash(self) -> str:
		'''Returns the CryptoString-formatted key as a string'''
		return self.pubhash.as_string()
	
	def decrypt(self, encdata : str) -> RetVal:
		'''Decrypts the Base85-encoded encrypted data and returns it as bytes. Returns None on 
		failure'''
		if encdata is None:
			return None
		
		if type(encdata).__name__ != 'str':
			raise TypeError

		secretbox = nacl.secret.SecretBox(self.key.as_raw())
		return RetVal().set_value('data', secretbox.decrypt(encdata, encoder=Base85Encoder))
	
	def encrypt(self, data : bytes) -> RetVal:
		'''Encrypts the passed data and returns it as a Base85-encoded string. Returns None on 
		failure'''
		if data is None:
			return None
		
		if type(data).__name__ != 'bytes':
			raise TypeError
		
		secretbox = nacl.secret.SecretBox(self.key.as_raw())
		mynonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
		return RetVal().set_values({ 'prefix':'XSALSA20',
			'data':secretbox.encrypt(data,nonce=mynonce, encoder=Base85Encoder).decode()})


def save_secretkey(key: SecretKey, path: str) -> RetVal:
	'''Saves the key to a JSON-formatted file'''
	if not path:
		return RetVal(ErrBadValue, 'path may not be empty')
	
	if os.path.exists(path):
		return RetVal(ErrExists, f'{path} exists')

	try:
		with open(path, 'w', encoding='utf8') as fhandle:
			json.dump(key.as_dict(), fhandle, ensure_ascii=False, indent=1)
	
	except Exception as e:
		return RetVal().wrap_exception(e)

	return RetVal()
	

def load_secretkey(path: str) -> RetVal:
	'''Instantiates a secret key from a file saved with SecretKey.save()

	Parameters:
	path: the path to the file

	Returns:
	field 'key': a SecretKey object
	'''
	if not path:
		return RetVal(ErrBadValue, 'path may not be empty')
	
	if not os.path.exists(path):
		return RetVal(ErrNotFound, f'{path} exists')
	
	indata = None
	try:
		with open(path, 'r', encoding='utf8') as fhandle:
			indata = json.load(fhandle)
	
	except Exception as e:
		return RetVal().wrap_exception(e)
	
	if not isinstance(indata, dict):
		return RetVal(ErrBadData, 'File does not contain an Mensago JSON secret key')

	try:
		jsonschema.validate(indata, __secret_key_schema)
	except jsonschema.ValidationError:
		return RetVal(ErrBadData, "file data does not validate")
	except jsonschema.SchemaError:
		return RetVal(ErrInternalError, "BUG: invalid SecretKey schema")

	key = CryptoString(indata['SecretKey'])
	if not key.is_valid():
		return RetVal(ErrBadData, 'Failure to base85 decode key data')
	
	return RetVal().set_value('key', SecretKey(key))


def check_password_complexity(indata: str) -> RetVal:
	'''Checks the requested string as meeting the needed security standards.
	
	Returns: RetVal
	field 'strength': string in [very weak', 'weak', 'medium', 'strong']

	Notes:
	If the strength of the password is too weak, it returns ErrBadValue with the 'strength' field 
	attached. Passwords are not limited to ASCII; UTF-8 characters are, in fact, encouraged. 
	Passwords are required to have at least 3 of the following: capital ASCII letters, lowercase 
	ASCII letters, numbers, symbols, and non-ASCII UTF-8 characters. They must also be a minimum of 
	8 characters. If 12 characters or greater, a password may have only 2 of the mentioned groups.
	'''
	if len(indata) < 8:
		return RetVal(ErrBadValue, 'Passphrase must be at least 8 characters.') \
			.set_value('strength', 'very weak')
	
	strength_score = 0
	strength_strings = [ 'error', 'very weak', 'weak', 'medium', 'strong', 'very strong']

	# Mensago *absolutely* permits UTF-8-encoded passwords. This greatly increases the
	# keyspace
	try:
		indata.encode().decode('ascii')
	except UnicodeDecodeError:
		strength_score = strength_score + 1
	
	if re.search(r"\d", indata):
		strength_score = strength_score + 1
	
	if re.search(r"[A-Z]", indata):
		strength_score = strength_score + 1
	
	if re.search(r"[a-z]", indata):
		strength_score = strength_score + 1

	if re.search(r"[~`!@#$%^&*()_={}/<>,.:;|'[\]\"\\\-\+\?]", indata):
		strength_score = strength_score + 1

	if (len(indata) < 12 and strength_score < 3) or strength_score < 2:
		# If the passphrase is less than 12 characters, require complexity
		status = RetVal(ErrBadValue, 'passphrase too weak')
		status.set_value('strength', strength_strings[strength_score])
		return status
	
	return RetVal().set_value('strength', strength_strings[strength_score])


class Password:
	'''Encapsulates hashed password interactions using the Argon2id hashing algorithm.'''
	def __init__(self, text=''):
		'''Instantiates a Password object.
		
		Parameters:
		text (optional): a plaintext password'''
		self.hashtype = 'argon2id'
		self.strength = ''
		self.hashstring = ''
		if text:
			self.set(text)

	def set(self, text) -> RetVal:
		'''
		Takes the given password text, checks strength, and generates a hash
		
		Returns:
		field 'strength': the strength of the password. Returned only on success.
		'''
		status = check_password_complexity(text)
		if status.error():
			return status
		self.strength = status['strength']
		self.hashstring = nacl.pwhash.argon2id.str(text.encode()).decode('ascii')
		
		return status
	
	def assign(self, pwhash: str) -> RetVal:
		'''Takes a PHC hash format string and assigns the password object to it.'''
		
		# TODO: Verify the PHC format
		
		self.hashstring = pwhash
		return RetVal()
	
	def check(self, text) -> bool:
		'''Checks the supplied plaintext password against the stored hash.

		Returns:
		True if the password matches the internal hash
		'''
		try:
			nacl.pwhash.verify(self.hashstring.encode(), text.encode())
		except InvalidkeyError:
			return False
		
		return True 
	
	def is_valid(self) -> bool:
		'''Returns true if the internal data is valid.
		
		Notes:
		A password may be weak and still valid.'''
		return self.strength and self.hashstring


class Base85Encoder:
	'''Base85 encoder for PyNaCl library'''
	@staticmethod
	def encode(data):
		'''Returns Base85 encoded data'''
		return base64.b85encode(data)
	
	@staticmethod
	def decode(data):
		'''Returns Base85 decoded data'''
		return base64.b85decode(data)
