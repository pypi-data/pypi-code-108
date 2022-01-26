import datetime
import re

def parse_datetime(date):

	regex = r'^\d{4}-\d{2}-\d{2}$'

	if isinstance(date, str):

		result = re.search(regex, date)

		if not result:
			raise ValueError(f'Invalid date format.\n\tExpected format 2001-01-01.\n\tString recieved: {date}')

		date = datetime.datetime.strptime(date, '%Y-%m-%d')

	return date.strftime('%d/%m/%Y')
