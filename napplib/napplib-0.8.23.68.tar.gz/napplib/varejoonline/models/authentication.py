from dataclasses import dataclass, InitVar
import json
@dataclass
class VarejoOnlineAuthentication:

	client_id     : str
	client_secret : str
	redirect_uri  : str
	code          : InitVar[str] = None
	refresh_token : InitVar[str] = None

	def __post_init__(self, code, refresh_token):

		if not code and not refresh_token:
			raise ValueError('"code" and "refresh_token" cannot be both None, only one must be set')

		if code:
			self.code = code
			self.grant_type = 'authorization_code'

		if refresh_token:
			self.refresh_token = refresh_token
			self.grant_type = 'refresh_token'

	def __str__(self):
		return json.dumps(self.__dict__)
