import re
import datetime
from typing import Union, Tuple

def parse_datetime(date):

	regex = r'^\d{4}-\d{2}-\d{2}$'

	if isinstance(date, str):

		result = re.search(regex, date)

		if not result:

			raise ValueError(f'Invalid date format.\n\tExpected format 2001-01-01.\n\tString recieved: {date}')

		date = datetime.datetime.strptime(date, '%Y-%m-%d')

	return date

def parse_date_filter(name, param: Union[str, datetime.datetime, Tuple[str, str], Tuple[datetime.datetime, datetime.datetime]]):
	if not param:
		return ''
	if isinstance(param, (tuple, list)) and len(param) == 2:
		_from, to = param
		_from = parse_datetime(_from).strftime('%d/%m/%Y %H:%M:%S')
		to = parse_datetime(to).strftime('%d/%m/%Y %H:%M:%S')
	else:
		_from = parse_datetime(param).strftime('%d/%m/%Y %H:%M:%S')
		to = datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S')
	
	return f'{name}[{_from} TO {to}]'
