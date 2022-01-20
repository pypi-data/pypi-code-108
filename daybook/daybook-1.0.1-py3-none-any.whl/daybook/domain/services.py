from datetime import date


def get_valid_date(entry_date: date):
    if not entry_date:
        entry_date = date.today()
    return entry_date
