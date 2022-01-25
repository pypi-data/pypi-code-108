from datetime import datetime


def transfer_datetime_str_to_datetime(date_str: str) -> datetime:
	return datetime(year=int(date_str[:4]), month=int(date_str[4: 6]), day=int(date_str[6:]))

