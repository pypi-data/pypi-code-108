from datetime import datetime
import calendar

def get_form_name():
    current_day = datetime.now().day
    month = datetime.now().month
    current_year = datetime.now().year

    if current_day < 15:
        month -= 1

    if month == 0:
        current_year -= 1
        month = 12

    month_name = calendar.month_name[month]
    form_name = f"Form {month_name} {current_year}"

    return form_name