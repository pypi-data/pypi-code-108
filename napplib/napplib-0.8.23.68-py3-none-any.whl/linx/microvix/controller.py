from typing import Optional, Union
import logging
from .models.authentication import MicrovixAuthentication
from datetime import datetime
from .models.base_controller import BaseController


class MicrovixController(BaseController):

	@classmethod
	def get_stocks(
		cls,
		authentication: MicrovixAuthentication,
		start_mov_date: Optional[Union[str, datetime]]= None,
		end_mov_date: Optional[Union[str, datetime]]=None
	):

		logging.info(f"Getting stocks info...")

		if start_mov_date and isinstance(start_mov_date, datetime):
			start_mov_date = start_mov_date.strftime('%Y-%m-%d')

		if end_mov_date and isinstance(end_mov_date, datetime):
			end_mov_date = end_mov_date.strftime('%Y-%m-%d')

		authentication = authentication.copy()
		authentication.setCommandName('LinxProdutosDetalhes')

		authentication['data_mov_ini'] = start_mov_date
		authentication['data_mov_fim'] = end_mov_date

		return cls._post(authentication)


	@classmethod
	def get_product_attributes(
		cls,
		authentication: MicrovixAuthentication,
		start_mov_date: Optional[Union[str, datetime]]= None,
		end_mov_date: Optional[Union[str, datetime]]=None,
		product_code: Optional[str]=None
	):

		logging.info(f"Getting  info...")

		if start_mov_date and isinstance(start_mov_date, datetime):
			start_mov_date = start_mov_date.strftime('%Y-%m-%d')

		if end_mov_date and isinstance(end_mov_date, datetime):
			end_mov_date = end_mov_date.strftime('%Y-%m-%d')

		authentication = authentication.copy()
		authentication.setCommandName('LinxProdutosCamposAdicionais')

		authentication['data_mov_ini'] = start_mov_date
		authentication['data_mov_fim'] = end_mov_date
		authentication['cod_produto'] = product_code

		return cls._post(authentication)


	@classmethod
	def get_products(
		cls,
		authentication: MicrovixAuthentication,
		start_update_date: Optional[Union[str, datetime]]=None,
		end_update_date: Optional[Union[str, datetime]]=None,
		product_code: Optional[str]=None
	):

		logging.info(f"Getting products...")

		if start_update_date and isinstance(start_update_date, datetime):
			start_update_date = start_update_date.strftime('%Y-%m-%d')

		if end_update_date and isinstance(end_update_date, datetime):
			end_update_date = end_update_date.strftime('%Y-%m-%d')

		authentication = authentication.copy()
		authentication.setCommandName('LinxProdutos')

		authentication['dt_update_inicio'] = start_update_date
		authentication['dt_update_fim'] = end_update_date
		authentication['cod_produto'] = product_code

		return cls._post(authentication)
