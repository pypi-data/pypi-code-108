import datetime


def date_time(text: str) -> datetime.datetime:
    return datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
