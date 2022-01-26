from dataclasses import dataclass
import base64

@dataclass
class MulticoisasAuthentication:
	email: str
	password: str

	def __str__(self):
		return 'Basic '+ base64.b64encode(f'{self.email}:{self.password}'.encode()).decode()
