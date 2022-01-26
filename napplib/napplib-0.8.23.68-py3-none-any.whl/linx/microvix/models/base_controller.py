import requests
from ..utils import xml_to_dict_array
from .authentication import MicrovixAuthentication
from torrequest import TorRequest
from abc import ABC

class BaseController(ABC):

	url = 'http://webapi.microvix.com.br/1.0/api/integracao'
	session=TorRequest()
	session.reset_identity() #Reset Tor
	
	@classmethod
	def _post(cls, authentication: MicrovixAuthentication):

		payload = str(authentication)

		headers = { 'Content-Type': 'application/xml' }

		response = cls.session.post(cls.url, headers=headers, data=payload)

		if response is None:
			raise Exception('Request returned nothing', authentication)

		return xml_to_dict_array(response.content)
