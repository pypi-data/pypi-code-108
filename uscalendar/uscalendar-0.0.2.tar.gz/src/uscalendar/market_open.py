import datetime
import sys
from src.uscalendar import helpers as hlp

"""
Package that returns if it's a trading day on the US Stock market.

Stock Market Holidays:

  New Years
  Martin Luther King Day
  Presidents Day
  Good Friday (not af Federal Holiday surprisingly)
  Memorial Day
  Independence Day
  Labor Day
  Thanksgiving
  Christmas

The market is open if the holiday falls on a Friday, but off the following Monday if it falls on a Sunday. Strange

"""


def market_open(date):
    date = hlp.strip_date(date)
    return MarketOpen(date).market_open


def is_weekend(date):
    """ returns True if day is on a weekend """
    date = hlp.strip_date(date)
    return MarketOpen(date).weekend


def is_weekday(date):
    """ returns True if day is on a weekday """
    date = hlp.strip_date(date)
    return not MarketOpen(date).weekend


def next_market_open_date(date):
    """ function that, given a date, returns the next date the market is open """
    date = hlp.to_datetime_date(date)
    next_day = date + datetime.timedelta(days=1)

    while not market_open(next_day):
        next_day = next_day + datetime.timedelta(days=1)

    next_day = hlp.to_string_date(next_day)
    return next_day


class MarketOpen:
    # class that, given an input date, will return if holiday with the method .market_open()
    def __init__(self, input_date):
        # get input date without anything else
        self.input_date = datetime.datetime.strptime(str(input_date), '%Y-%m-%d')
        self.month_day = str(self.input_date.month) + '-' + str(self.input_date.day)  # get day and month
        self.weekday = self.input_date.weekday()  # get weekday
        self.market_open = True  # set market to open and set to false if exception occurs
        self.weekend = False
        self.is_weekend()

        function_list = ['is_weekend', 'is_not_new_years', 'is_not_mlk', 'is_not_presidents_day', 'is_not_good_friday',
                         'is_not_memorial_day', 'is_not_independence_day', 'is_not_labor_day', 'is_not_thanksgiving',
                         'is_not_christmas']

        for func in function_list:  # run each function to check if the stock exchange is open
            eval('self.' + func + '()')

    def is_weekend(self):
        if self.weekday in [5, 6]:
            self.market_open = False
            self.weekend = True

    def is_not_christmas(self):
        if self.month_day == '12-25':
            self.market_open = False  # christmas day get some presents
        elif (self.weekday == 0) & (self.month_day == '12-26'):  # Monday the 26th of January
            self.market_open = False
        elif (self.weekday == 4) & (self.month_day == '12-24'):  # Friday the 24th of December
            self.market_open = False

    def is_not_labor_day(self):
        dt = datetime.datetime(self.input_date.year, 9, 1)
        if dt.weekday() == 0:
            delta_time = datetime.timedelta(days=(0 - dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=(7 - dt.weekday()))
        labor_day = dt + delta_time  # get the first Monday of September

        if self.input_date == labor_day:
            self.market_open = False

    def is_not_mlk(self):
        dt = datetime.datetime(self.input_date.year, 1, 1)
        if dt.weekday() == 0:
            delta_time = datetime.timedelta(days=(0 - dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=(7 - dt.weekday()))
        dt = dt + delta_time  # get the first Monday of January
        mlk = dt + datetime.timedelta(days=14)  # get the third Monday of January

        if self.input_date == mlk:
            self.market_open = False

    def is_not_good_friday(self):
        # boo lunar calendars
        good_friday_dates = ['2021-4-2', '2022-4-15', '2023-4-7', '2024-3-29', '2025-4-18', '2026-4-03',
                             '2027-3-26', '2028-4-14', '2029-3-30', '2030-4-19']

        day = str(self.input_date.year) + '-' + str(self.input_date.month) + '-' + str(self.input_date.day)

        if any(day in dates for dates in good_friday_dates):
            self.market_open = False

    def is_not_independence_day(self):
        if self.month_day == '7-4':
            self.market_open = False  # new independence day
        elif (self.weekday == 0) & (self.month_day == '7-5'):  # Monday the 5th of July
            self.market_open = False

    def is_not_memorial_day(self):
        # the last Monday in May
        dt = datetime.datetime(self.input_date.year, 6, 1)
        if dt.weekday() != 0:
            delta_time = datetime.timedelta(days=(dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=7)
        memorial_day = dt - delta_time
        if self.input_date == memorial_day:
            self.market_open = False

    def is_not_new_years(self):
        if self.month_day == '1-1':
            self.market_open = False  # new years day
        elif (self.weekday == 0) & (self.month_day == '1-2'):  # Monday the 2nd of January
            self.market_open = False
        # Surprisingly if New Years is on a Saturday, there is no holiday at all

    def is_not_presidents_day(self):
        dt = datetime.datetime(self.input_date.year, 2, 1)
        if dt.weekday() == 0:
            delta_time = datetime.timedelta(days=(0 - dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=(7 - dt.weekday()))

        presidents_day = dt + delta_time + datetime.timedelta(days=14)  # get the 3rd Monday of February

        if self.input_date == presidents_day:
            self.market_open = False

    def is_not_thanksgiving(self):
        dt = datetime.datetime(self.input_date.year, 11, 1)

        if dt.weekday() >= 4:
            delta_time = datetime.timedelta(days=(10 - dt.weekday()))  # go back to the first thursday
        else:
            delta_time = datetime.timedelta(days=(3 - dt.weekday()))

        thanksgiving = dt + delta_time + datetime.timedelta(days=21)  # get the fourth Thursday of November

        if self.input_date == thanksgiving:
            self.market_open = False

    def market_open(self):
        return self.market_open


if __name__ == '__main__':
    sys.stdout.write(str(market_open(sys.argv[1])))
