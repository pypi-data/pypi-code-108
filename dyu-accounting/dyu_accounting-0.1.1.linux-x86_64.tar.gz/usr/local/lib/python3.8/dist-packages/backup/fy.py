import datetime


def get_fy(date):
    entry_year = date.year
    entry_month = date.month
    fy = entry_year-1 if entry_month < 4 else entry_year
    return fy


def get_year_end(date):
    entry_year = date.year
    entry_month = date.month
    fy = entry_year-1 if entry_month < 4 else entry_year

    return datetime.date(fy+1, 3, 31)


def get_quarter(date):
    entry_quarter = date.month//3
    entry_quarter = 'q4' if entry_quarter == 0 else 'q' + str(entry_quarter)
    return entry_quarter
