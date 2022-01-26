import logging
from typing import List, Optional, Union
from ..models.authentication import MicrovixAuthentication
from datetime import datetime
from ..models.base_controller import BaseController




class MicrovixController(BaseController):

	"""
	Controller for B2C webservice from Linx Microvix.
	Documentation: https://share.linx.com.br/display/SHOPLINXMICRPUB/WebService+B2C
	"""

	@classmethod
	def get_products(
		cls,
		authentication: MicrovixAuthentication,
		start_register_date: Optional[Union[str, datetime]]=None,
		end_register_date: Optional[Union[str, datetime]]=None,
		product_code: Optional[str]=None
	):

		'''
		Method: B2CConsultaProdutos
		'''
		logging.info('getting products...')

		if end_register_date and isinstance(end_register_date, datetime):
			end_register_date = end_register_date.strftime('%Y-%m-%d')

		if start_register_date and isinstance(start_register_date, datetime):
			start_register_date = start_register_date.strftime('%Y-%m-%d')


		authentication = authentication.copy()
		authentication.setCommandName('B2CConsultaProdutos')

		authentication['dt_cadastro_inicial'] = start_register_date
		authentication['dt_cadastro_fim']     = end_register_date
		authentication['codigoproduto']       = product_code
		authentication['timestamp']           = 0

		return cls._post(authentication)


	@classmethod
	def get_product_stock_info(
		cls,
		authentication: MicrovixAuthentication,
		companies: Optional[Union[str, List[str]]] = None
	):
		'''
		Method: B2CConsultaProdutosDetalhes
		'''

		logging.info('getting stock info...')

		if isinstance(companies, list):
			companies = ','.join(companies)

		authentication = authentication.copy()
		authentication.setCommandName('B2CConsultaProdutosDetalhes')

		authentication['timestamp'] = 0
		authentication['empresas'] = companies

		return cls._post(authentication)


	@classmethod
	def get_product_price_info(
		cls,
		authentication: MicrovixAuthentication,
		product_code: Optional[int] = None,
	):
		'''
		Method: B2CConsultaProdutosCustos
		'''

		logging.info('getting price info...')

		authentication = authentication.copy()
		authentication.setCommandName('B2CConsultaProdutosCustos')

		authentication['codigoproduto'] = product_code
		authentication['timestamp']     = 0

		return cls._post(authentication)


	@classmethod
	def get_product_promotional_price_info(
		cls,
		authentication: MicrovixAuthentication,
		product_code: int,
		promotion_code: Optional[int] = None
	):
		'''
		Method: B2CConsultaProdutosPromocao
		'''

		logging.info('getting promotional price info...')

		authentication = authentication.copy()
		authentication.setCommandName('B2CConsultaProdutosPromocao')

		authentication['codigo_promocao'] = promotion_code
		authentication['codigoproduto']   = product_code
		authentication['timestamp']       = 0

		return cls._post(authentication)


	@classmethod
	def get_brand_info(
		cls,
		authentication: MicrovixAuthentication,
		brand_code: int,
	):
		'''
		Method: B2CConsultaMarcas
		'''

		logging.info('getting brand info...')

		authentication = authentication.copy()
		authentication.setCommandName('B2CConsultaMarcas')

		authentication['codigo_marca'] = brand_code
		authentication['timestamp']    = 0

		return cls._post(authentication)


	@classmethod
	def get_sector_info(
		cls,
		authentication: MicrovixAuthentication,
		sector_code: int,
	):
		'''
		Method: B2CConsultaSetores
		'''

		logging.info('getting sector info...')

		authentication = authentication.copy()
		authentication.setCommandName('B2CConsultaSetores')

		authentication['codigo_setor'] = sector_code
		authentication['timestamp']    = 0

		return cls._post(authentication)
