from aiohttp import ClientSession, ClientResponse, ClientError

from .utils import validate_auth_code
from .errors import InvalidFormat, UnknownAuthCode, ApiUnauthorized, ApiConnectionError

class LaundrifyAPI:
	"""Class to communicate with the laundrify API."""

	host = "https://api.laundrify.de"

	def __init__(self, access_token: str):
		"""Initialize the API and store the auth so we can make requests."""
		# raise_for_status: Raise an aiohttp.ClientResponseError if the response status is 400 or higher.
		self.client_session = ClientSession(self.host)
		self.access_token = access_token

	@classmethod
	async def exchange_auth_code(cls, auth_code: str):
		"""Exchange an Auth Code for an Access Token"""
		if not validate_auth_code(auth_code):
			raise InvalidFormat("The provided AuthCode ({auth_code}) doesn't match the expected pattern (xxx-xxx).")
		async with ClientSession(base_url=cls.host) as session:
			try:
				async with session.post('/auth/home-assistant/token', json={'authCode': auth_code}) as res:
					if (res.status == 404):
						raise UnknownAuthCode(f"The given AuthCode ({auth_code}) could not be found.")
					res.raise_for_status()
					data = await res.json()
					return data["token"]
			except ClientError as err:
				raise ApiConnectionError( str(err) )

	async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
		"""Make a request."""
		headers = kwargs.get("headers")

		if headers is None:
				headers = {}
		else:
				headers = dict(headers)

		headers["authorization"] = f"Bearer ha|{self.access_token}"

		try:
			res = await self.client_session.request(method, f"{path}", **kwargs, headers=headers)
			res.raise_for_status()
		except ClientError as err:
			raise ApiConnectionError(err)

		return res

	async def get_machines(self):
		"""Read all Machines from backend"""
		res = await self.request('get', '/api/machines')
		if (res.status == 401):
			raise ApiUnauthorized()
		machines = await res.json()
		return machines