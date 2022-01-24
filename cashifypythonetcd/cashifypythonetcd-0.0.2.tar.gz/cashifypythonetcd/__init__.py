import etcd
import requests

# Can also use python cache if we want to use it as generic
# Currently using this for Django as use case
from django.core.cache import cache


class CashifyETCD(object):

	"""
	Base class for initalizing
	"""

	etcd_client = None
	app_name = None
	proxy = None
	headers = None

	def __init__(self, host, protocol, port, app_name, proxy=None, headers=None):

		""" Get ETCD client"""

		if not proxy:
			self.etcd_client = etcd.Client(host=host, protocol=protocol, port=port)
			self.app_name = app_name
		else:
			self.proxy = proxy
			self.headers = headers
			self.app_name = app_name

	def get_property_value(self, key, default):
		"""
		Get property value from ETCD if not found return default
		"""
		try:
			required_key = self.app_name + '/' + self.app_name + '.' + key
			value = self.get_value_cache(required_key)
			if value:
				return value
			if not self.proxy:
				value = self.etcd_client.read(required_key).value
			else:
				required_key = '/' + required_key
				values = requests.get(url=self.proxy, headers=self.headers).json()
				for _value in values.get('node').get('nodes'):
					if _value.get('key') == required_key:
						value = _value.get('value')
						break
				self.set_value_cache(required_key, value)
			return value
		except Exception as e:
			return default

	def get_value_cache(self, key):
		"""
		Get value from cache
		"""
		return cache.get(key)

	def set_value_cache(self, key, value):
		"""
		Set value in cache for 5 minutes
		"""
		cache.set(key, value, 300)
