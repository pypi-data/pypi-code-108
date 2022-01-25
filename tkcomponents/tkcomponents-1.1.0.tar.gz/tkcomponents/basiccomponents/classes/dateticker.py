from datetime import datetime


class DateTicker:
    def __init__(self):
        self._date_reference = datetime.now().date()

    @property
    def is_tomorrow(self):
        new_date = datetime.now().date()

        if new_date != self._date_reference:
            self._date_reference = new_date
            return True
