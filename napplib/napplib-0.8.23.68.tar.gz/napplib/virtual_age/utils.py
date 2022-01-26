from datetime import datetime
import re
from typing import Union
import xml.dom.minidom
from bs4 import BeautifulSoup
import xmltodict


class VirtualAgeRequestWrapper:

	def __init__(self) -> None:
		self._items = {}

	def __setitem__(self, key, item):

		if not isinstance(item, dict):
			raise ValueError('Items must be a dict')

		item = { key: str(item) for key, item in item.items() }

		self._items[key] = item


	def __getitem__(self, key):
		return self._items[key]


	def envelope(self) -> bytes:
		'''Return the xml in bytes'''
		doc = xml.dom.minidom.Document()
		env = doc.createElement('soap:Envelope')
		env.setAttribute('xmlns:xsi'  , 'http://www.w3.org/2001/XMLSchema-instance')
		env.setAttribute('xmlns:xsd'  , 'http://www.w3.org/2001/XMLSchema')
		env.setAttribute('xmlns:soap' , 'http://schemas.xmlsoap.org/soap/envelope/')
		env.setAttribute('xmlns:urn'  , 'urn:udmDados-IdmDados')

		#requisicao
		requisicao = doc.createElement('requisicao')
		requisicao.setAttribute('in_schema', 'F')

		for key, item in self._items.items():

			element = doc.createElement(key)

			for attname, value in item.items():
				element.setAttribute(attname, value)

			requisicao.appendChild(element)

		#XML
		_xml = doc.createElement('XML')
		_xml.setAttribute('xsi:type', 'xsd:string')
		_xml.appendChild(requisicao)

		#urn
		urn = doc.createElement('urn:requisicao')
		urn.setAttribute('soap:encodingStyle', 'http://schemas.xmlsoap.org/soap/encoding/')
		urn.appendChild(_xml)

		#Body
		body = doc.createElement('soap:Body')
		body.appendChild(urn)

		env.appendChild(body)
		doc.appendChild(env)

		return doc.toxml('utf-8')


def xmlsoap_to_dict(soap_xml) -> Union[dict, None]:
	bs = BeautifulSoup(soap_xml, 'lxml', from_encoding='UTF-8')
	result = bs.find('return').text
	result = xmltodict.parse(result)
	fix_dict_encoding(result)
	return result


def fix_dict_encoding(item) -> None:

	if isinstance(item, list):
		for i in item:
			fix_dict_encoding(i)

	if isinstance(item, dict):
		for k, i in item.items():
			if isinstance(i, str):
				try:
					item[k] = i.encode('windows-1254').decode('UTF-8')
				except Exception:
					pass

			else:
				fix_dict_encoding(i)


def normalize_datetime(date: Union[datetime, str]) -> str:
	regex = r'^\d{4}(-\d{2}){2}$'

	if not isinstance(date, (str, datetime)):
		raise ValueError('"date" must be either datetime or str')

	if isinstance(date, str):

		result = re.search(regex,date)
		if not result:
			raise ValueError('Date pattern must follow this example: yyyy-mm-dd')

		date = datetime.strptime(date, '%Y-%m-%d')

	return date.strftime('%d/%m/%Y')
