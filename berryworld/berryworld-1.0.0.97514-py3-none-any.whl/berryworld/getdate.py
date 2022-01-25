from datetime import datetime
import pandas as pd


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class GetDate:
    """ Prepare a date according to a specific date format """

    def get_now(self):
        """ Get the datetime in the instant the method is called
        :return: Now as string format
        """
        return self.strftime(datetime.utcnow())

    def get_today(self):
        """ Get the date in the instant the method is called
        :return: Today's date as string format
        """
        return self.strfdate(datetime.utcnow())

    @staticmethod
    def get_year():
        """ Get the year when the method is called
        :return: Today's year as integer
        """
        return datetime.utcnow().year

    @staticmethod
    def strfdate(input_date, dat_format=DATE_FORMAT):
        """ Convert a date into a string with a specific format
        :param input_date: Date to be converted into string
        :param dat_format: Date format to return
        :return: String representation of the input date in the correct formatting
        """
        return pd.Timestamp(input_date).strftime(dat_format)

    @staticmethod
    def strftime(input_datetime, dat_format=DATETIME_FORMAT):
        """ Converts a datetime into a string with a specific format
        :param input_datetime: datetime to be converted into string
        :param dat_format: Date format to return
        :return: String representation of the input datetime in the correct formatting
        """
        return pd.Timestamp(input_datetime).strftime(dat_format)
