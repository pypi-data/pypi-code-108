import datetime
import sys
import helpers as hlp
#from src.uscalendar import helpers as hlp

"""

Federal Holidays:

X New Years Day
X MLK
x Inauguration Day (Jan 20th)
X Washington's Birthday (aka Presidents Day)
X Memorial Day
x Juneteenth
x Independence Day
x Labor Day
x Columbus Day
x Veterans Day
X Thanksgiving Day
x Christmas Day

per: https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/#url=2022

*If a holiday falls on a Saturday, for most Federal employees, the preceding Friday will be treated as a holiday for pay
and leave purposes. (See 5 U.S.C. 6103(b).) If a holiday falls on a Sunday, for most Federal employees, 
the following Monday will be treated as a holiday for pay and leave purposes. (See Section 3(a) of Executive Order 
11582, February 11, 1971.) See also our Federal Holidays – "In Lieu Of" Determination Fact Sheet at 
https://www.opm.gov/policy-data-oversight/pay-leave/work-schedules/fact-sheets/Federal-Holidays-In-Lieu-Of-Determination.

**This holiday is designated as "Washington’s Birthday" in section 6103(a) of title 5 of the United States Code, which 
is the law that specifies holidays for Federal employees. Though other institutions such as state and local governments 
and private businesses may use other names, it is our policy to always refer to holidays by the names designated in the 
law.

"""


def holiday_name(date):
    """ returns name of holiday given a date, None if there is no holiday """
    date = hlp.strip_date(date)
    return FederalHoliday(date).holiday


def is_federal_holiday(date):
    """ returns True if day is a federal holiday """
    date = hlp.strip_date(date)
    return FederalHoliday(date).federal_holiday


def is_weekend(date):
    """ returns True if day is on a weekend """
    date = hlp.strip_date(date)
    return FederalHoliday(date).weekend


def is_weekday(date):
    """ returns True if day is on a weekday """
    date = hlp.strip_date(date)
    return not FederalHoliday(date).weekend


def is_working_day(date):
    """" returns True if it's a working day for federal employees """
    date = hlp.strip_date(date)
    return (not FederalHoliday(date).federal_holiday) and (not FederalHoliday(date).weekend)


def is_off_day(date):
    """ returns True if it's an off day for federal employees"""
    date = hlp.strip_date(date)
    return FederalHoliday(date).federal_holiday or FederalHoliday(date).weekend


class FederalHoliday:
    # class that, given an input date, will return if holiday with the method .federal_holiday()
    def __init__(self, input_date):
        # get input date without anything else
        self.input_date = datetime.datetime.strptime(str(input_date), '%Y-%m-%d')
        self.month_day = str(self.input_date.month) + '-' + str(self.input_date.day)  # get day and month
        self.year = self.input_date.year
        self.weekday = self.input_date.weekday()  # get weekday
        self.holiday = "None"  # initialize holiday name as none, assign if it is
        self.federal_holiday = False
        self.weekend = False
        self.is_weekend()

        function_list = ['is_new_years', 'is_mlk', 'is_presidents_day', 'is_memorial_day', 'is_juneteenth',
                         'is_independence_day', 'is_labor_day', 'is_columbus_day', 'is_veterans_day',
                         'is_thanksgiving', 'is_christmas']

        for func in function_list:  # run each function to check if the stock exchange is open
            eval('self.' + func + '()')

        if self.year % 4 == 1:  # if inauguration year
            eval('self.is_inauguration_day' + '()')

    def is_weekend(self):
        if self.weekday in [5, 6]:
            self.federal_holiday = False
            self.weekend = True

    def is_christmas(self):
        xmas_holiday_name = 'Christmas Day'
        if self.month_day == '12-25' and not self.weekend:
            self.federal_holiday = True  # Christmas day get some presents
            self.holiday = xmas_holiday_name
        elif (self.weekday == 0) & (self.month_day == '12-26'):  # Monday the 26th of January
            self.federal_holiday = True
            self.holiday = xmas_holiday_name
        elif (self.weekday == 4) & (self.month_day == '12-24'):  # Friday the 24th of December
            self.federal_holiday = True
            self.holiday = xmas_holiday_name

    def is_columbus_day(self):
        cday_holiday_name = 'Columbus Day'
        dt = datetime.datetime(self.input_date.year, 10, 1)
        if dt.weekday() == 0:
            delta_time = datetime.timedelta(days=7)  # if the first is a Monday, add a week
        else:
            delta_time = datetime.timedelta(days=(14 - dt.weekday()))
        columbus_day = dt + delta_time  # get the second Monday of October

        if self.input_date == columbus_day:
            self.federal_holiday = True
            self.holiday = cday_holiday_name

    def is_labor_day(self):
        lday_holiday_name = 'Labor Day'
        dt = datetime.datetime(self.input_date.year, 9, 1)
        if dt.weekday() == 0:
            delta_time = datetime.timedelta(days=(0 - dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=(7 - dt.weekday()))
        labor_day = dt + delta_time  # get the first Monday of September

        if self.input_date == labor_day:
            self.federal_holiday = True
            self.holiday = lday_holiday_name

    def is_juneteenth(self):
        jt_holiday_name = 'Juneteenth'
        if self.month_day == '6-19' and not self.weekend:
            self.federal_holiday = True  # Juneteenth is typically the 19th of June not on a weekend
            self.holiday = jt_holiday_name
        elif (self.weekday == 0) & (self.month_day == '6-20'):  # The next Monday if Juneteeth is on a Sunday
            self.federal_holiday = True
            self.holiday = jt_holiday_name
        elif (self.weekday == 4) & (self.month_day == '6-18'):  # Friday the 18th if Juneteenth is on a Saturday
            self.federal_holiday = True
            self.holiday = jt_holiday_name

    def is_mlk(self):
        dt = datetime.datetime(self.input_date.year, 1, 1)
        if dt.weekday() == 0:
            delta_time = datetime.timedelta(days=(0 - dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=(7 - dt.weekday()))
        dt = dt + delta_time  # get the first Monday of January
        mlk = dt + datetime.timedelta(days=14)  # get the third Monday of January

        if self.input_date == mlk:
            self.federal_holiday = True
            self.holiday = "Martin Luther King Day"

    def is_inauguration_day(self):
        """ if it's on a weekend, no day off """

        ianug_holiday_name = 'Inauguration Day'
        if self.month_day == '1-20' and not self.weekend:
            self.federal_holiday = True
            if self.holiday == 'Martin Luther King Day':
                self.holiday = 'Martin Luther King Day and ' + ianug_holiday_name
            else:
                self.holiday = ianug_holiday_name

    def is_independence_day(self):
        inde_holiday_name = 'Independence Day'
        if self.month_day == '7-4' and not self.weekend:
            self.federal_holiday = True  # July 4 not on a weekend, kick out the british
            self.holiday = inde_holiday_name
        elif (self.weekday == 0) & (self.month_day == '7-5'):  # Monday the 5th of July
            self.federal_holiday = True
            self.holiday = inde_holiday_name
        elif (self.weekday == 4) & (self.month_day == '7-3'):  # Friday the third of July
            self.federal_holiday = True
            self.holiday = inde_holiday_name

    def is_memorial_day(self):
        # the last Monday in May
        dt = datetime.datetime(self.input_date.year, 6, 1)
        if dt.weekday() != 0:
            delta_time = datetime.timedelta(days=(dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=7)
        memorial_day = dt - delta_time
        if self.input_date == memorial_day:
            self.federal_holiday = True
            self.holiday = "Memorial Day"

    def is_new_years(self):
        nyd_holiday_name = 'New Years Day'
        if self.month_day == '1-1' and not self.weekend:
            self.federal_holiday = True  # new years day
            self.holiday = nyd_holiday_name
        elif (self.weekday == 0) & (self.month_day == '1-2'):  # Monday the 2nd of January
            self.federal_holiday = True
            self.holiday = nyd_holiday_name
        elif (self.weekday == 4) & (self.month_day == '12-31'):  # Friday the 31st of December
            self.federal_holiday = True
            self.holiday = nyd_holiday_name

    def is_presidents_day(self):
        dt = datetime.datetime(self.input_date.year, 2, 1)
        if dt.weekday() == 0:
            delta_time = datetime.timedelta(days=(0 - dt.weekday()))
        else:
            delta_time = datetime.timedelta(days=(7 - dt.weekday()))

        presidents_day = dt + delta_time + datetime.timedelta(days=14)  # get the 3rd Monday of February

        if self.input_date == presidents_day:
            self.federal_holiday = True
            self.holiday = "President's Day"

    def is_thanksgiving(self):
        dt = datetime.datetime(self.input_date.year, 11, 1)

        if dt.weekday() >= 4:
            delta_time = datetime.timedelta(days=(10-dt.weekday()))  # go back to the first thursday
        else:
            delta_time = datetime.timedelta(days=(3 - dt.weekday()))

        thanksgiving = dt + delta_time + datetime.timedelta(days=21)  # get the fourth Thursday of November

        if self.input_date == thanksgiving:
            self.federal_holiday = True
            self.holiday = 'Thanksgiving Day'

    def is_veterans_day(self):
        vday_holiday_name = 'Veterans Day'
        if self.month_day == '11-11' and not self.weekend:  # eleventh hour of the eleventh day
            self.federal_holiday = True  # Veterans Day
            self.holiday = vday_holiday_name
        elif (self.weekday == 0) & (self.month_day == '11-12'):  # Monday the 12th if it falls on a Sunday
            self.federal_holiday = True
            self.holiday = vday_holiday_name
        elif (self.weekday == 4) & (self.month_day == '11-10'):  # Friday the 10th if it falls on a Saturday
            self.federal_holiday = True
            self.holiday = vday_holiday_name

    def federal_holiday(self):
        return self.federal_holiday


if __name__ == '__main__':
    sys.stdout.write(str(is_federal_holiday(sys.argv[1])))
