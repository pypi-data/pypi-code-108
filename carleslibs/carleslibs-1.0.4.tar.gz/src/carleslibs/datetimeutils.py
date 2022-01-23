#
# Date time methods
#
# Author: Carles Mateo
# Creation Date: 2014 Barcelona
# Last Update: 2021-07-01 11:10 Ireland. Added remove_colons
# Description: Class to return Date, datetime, Unix EPOCH timestamp
#

import datetime
import time


class DateTimeUtils:

    def get_unix_epoch(self):
        """
        Will return the EPOCH Time. For convenience is returned as String
        :return: s_now_epoch
        """
        s_now_epoch = str(int(time.time()))

        return s_now_epoch

    def get_unix_epoch_as_float(self):
        """
        Will return the EPOCH Time in float with all the decimals.
        :return: f_now_epoch
        """
        f_now_epoch = time.time()

        return f_now_epoch

    def get_datetime(self, b_milliseconds=False, b_remove_spaces_and_colons=False, b_remove_dashes=False):
        """
        Return the datetime with milliseconds in format YYYY-MM-DD HH:MM:SS.xxxxx
        or without milliseconds as YYYY-MM-DD HH:MM:SS"""
        if b_milliseconds is True:
            s_now = str(datetime.datetime.now())
        else:
            s_now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if b_remove_spaces_and_colons is True:
            s_now = s_now.replace(" ", "-")
            s_now = s_now.replace(":", "")

        if b_remove_dashes is True:
            s_now = s_now.replace("-", "")

        return s_now

    def get_datetime_as_14_string(self):
        """
        Returns the datetime in format 202107011444
        :return:
        """

        return self.get_datetime(b_milliseconds=False, b_remove_spaces_and_colons=True, b_remove_dashes=True)
