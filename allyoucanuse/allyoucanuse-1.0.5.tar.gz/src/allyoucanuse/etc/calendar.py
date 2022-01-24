from datetime import date, timedelta


def today_with_format(format:str="%Y-%m-%d")->str:
    return date.today().strftime(format)

def today_in_iso()->str:
    return str(date.today())

def yesterday_in_iso()->str:
    return str(date.today() - timedelta(days=1))

def firstday_previous_month():
    day = date.today()
    dd = day.replace(day=1)-timedelta(days=1)
    return str(dd.replace(day=1))