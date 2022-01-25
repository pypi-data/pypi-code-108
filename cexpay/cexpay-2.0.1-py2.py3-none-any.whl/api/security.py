from base64 import b64decode, b64encode
import hashlib
import hmac

class SignatureCalculator:
	def __init__(self, secret: str) -> None:
		assert isinstance(secret, str)

		self._secret = b64decode(secret)

	def sing(self, timestamp: str, http_method: str,  url_path: str, body_raw: bytes = None) -> str:
		assert isinstance(timestamp, str)
		assert isinstance(http_method, str)
		assert isinstance(url_path, str)

		prefix: str = timestamp + http_method + url_path
		prefix_raw: bytes = prefix.encode("UTF-8")

		sha256_hmac = hmac.new(self._secret, digestmod = hashlib.sha256)

		what: bytes = prefix_raw
		if body_raw is not None:
			assert isinstance(body_raw, bytes)
			what =  b''.join([prefix_raw, body_raw])

		sha256_hmac.update(what)
		signature = sha256_hmac.digest()

		return b64encode(signature).decode('ascii')
