import calendar
import datetime


def add_months(date_time, month):
    """
    according to the business logic, we need get the previous several months date.
    @author: Wang Lin
    """
    if month <= 0:
        if abs(month) <= 12:
            if date_time.month < abs(month):
                new_year = date_time.year - 1
                if abs(month) > 12:
                    new_year = date_time.year - (abs(month) % 12) - 1
                else:
                    new_year = date_time.year - 1
                new_month = date_time.month + 12 - abs(month)
                if new_month == 0:
                    new_month = 12
                    new_year -= 1
            else:
                new_year = date_time.year
                new_month = date_time.month - abs(month)
                if new_month == 0:
                    new_month = 12
                    new_year -= 1
        else:
            new_year = date_time.year - (abs(month) / 12)
            ex_m = abs(month) % 12
            if ex_m >= date_time.month:
                new_year -= 1
                new_month = date_time.month + 12 - ex_m
                if new_month == 0:
                    new_month = 12
                    new_year -= 1
            else:
                new_month = date_time.month - ex_m
                if new_month == 0:
                    new_month = 12
                    new_year -= 1
        if date_time.day > calendar.monthrange(new_year, new_month)[1]:
            new_day = calendar.monthrange(new_year, new_month)[1]
        else:
            new_day = date_time.day
        new_date_time = datetime.datetime(new_year, new_month, new_day)
        return new_date_time

    else:
        if date_time.month + month <= 12:
            new_month = date_time.month + month
            new_year = date_time.year
        else:
            new_year = date_time.year + (date_time.month + month) / 12
            new_month = (date_time.month + month) % 12
            if new_month == 0:
                new_month = 12
        if date_time.day > calendar.monthrange(new_year, new_month)[1]:
            new_day = calendar.monthrange(new_year, new_month)[1]
        else:
            new_day = date_time.day
        new_date_time = datetime.datetime(new_year, new_month, new_day)
        return new_date_time


if __name__ == "__main__":
    today = datetime.datetime.now()
    print(add_months(today, 3))
    print(add_months(today, -2))  # previous 2 months date
    print(add_months(today, 10))
