#
# String Utils
#
# Author: Carles Mateo
# Creation Date: 2014-01-01 15:29 IST
# Last Updated:  2021-08-24 20:35 Ireland.
# Description: Class to deal with Files and Directories
#

import os
import glob
import html


class StringUtils:

    def convert_string_to_integer(self, s_amount):
        """
        Convert a string to Integer, checking for errors.
        :param s_amount:
        :return: Boolean Success/False, Integer number if success or 0 otherwise

        """

        b_success = True
        i_value = 0

        if s_amount == "":
            i_value = 0
        else:
            try:
                i_value = int(s_amount)
            except:
                b_success = False
                i_value = 0

        return b_success, i_value

    def convert_to_gb_from_kb(self, s_amount, b_add_units=True):
        """
        Converts units in the format "10KB" or "123456789 KB" or "7000K" to GB with 2 decimal places
        Note: Dividing by 1024 not 1000
        :param s_amount:
        :param b_add_units:
        :return: boolean for success, String in GB with final "GB", float in GB
        """

        s_amount = s_amount.strip()
        f_amount = 0
        b_success = True

        if len(s_amount) < 2:
            if b_add_units is True:
                return False, "0GB", 0
            else:
                return False, "0", 0

        # We will accept "K" not only "KB"
        s_unit_1 = s_amount[-1:].upper()
        if s_unit_1 == "K":
            s_amount = s_amount + "B"

        s_unit = s_amount[-2:].upper()

        if s_unit == "KB":
            s_value = s_amount.replace(' ', '')
            # Remove "KB"
            s_value = s_value[0:-2]
            i_value = int(s_value)
            f_value_mb = i_value/1024.00
            f_value_gb = f_value_mb/1024.00
            #s_value = str(f_value_gb)[0:4]
            s_value = "%.2f" % f_value_gb
            if s_value[-3:] == ".00":
                s_value = s_value[0:-3]
            f_amount = float(s_value)

            if b_add_units is True:
                return b_success, s_value + "GB", f_amount
            else:
                return b_success, s_value, f_amount
        else:
            b_success = False

        # Unknown
        return b_success, s_amount, f_amount

    def convert_bytes_to_best_size(self, i_bytes):
        """
        Converts a number of bytes to the highest values, and adds the units
        :param i_bytes:
        :return: s_biggest_suggested
        """
        s_value_bytes, s_value_kb, s_value_mb, s_value_gb, s_value_tb, s_value_pb, s_biggest_suggested = self.convert_bytes_to_multiple_units(
            i_bytes)

        return s_biggest_suggested

    def convert_bytes_to_multiple_units(self, i_amount):
        s_value_bytes, s_value_kb, s_value_mb, s_value_gb, s_value_tb, s_value_pb, s_biggest_suggested = \
            self.convert_to_multiple_units(str(i_amount), b_add_units=True)

        return s_value_bytes, s_value_kb, s_value_mb, s_value_gb, s_value_tb, s_value_pb, s_biggest_suggested

    def convert_to_multiple_units(self, s_amount, b_add_units=False, i_decimals=2, b_remove_decimals_if_ge_1000=True):
        """
        Getting the bytes or Kbytes, we return multiple units.
        :param s_amount:
        :param b_add_units: If we suffix the units, like GiB
        :param i_decimals: Number of decimal positions
        :param b_remove_decimals_if_ge_1000: Will remove decimals part if the unit is greater or equal to 1000
        :return: String in Bytes, String in Kbytes, String in Mbytes, String in Gbytes, String in Tbytes,
                 str in Pbytes, biggest suggested unit
        """
        # @TODO: Finish this to support other units as input
        # Init values
        s_value_bytes = "0"
        i_value_bytes = 0
        s_value_kb = "0"
        i_value_kb = 0
        s_value_mb = "0"
        f_value_mb = 0
        s_value_gb = "0"
        f_value_gb = 0
        s_value_tb = "0"
        f_value_tb = 0
        s_value_pb = "0"
        f_value_pb = 0

        s_biggest_suggested = ""

        s_amount = s_amount.strip()

        s_mask = "{:." + str(i_decimals) + "f}"  # "{:.2f}"

        # Check if it has units, like 10KB
        if s_amount.isdigit() is not True:
            s_unit = s_amount[-2:].upper()
            s_unit1 = s_amount[-1:].upper()
            s_unit3 = s_amount[-3:].upper()

            if s_unit1 == "K" or s_unit == "KB" or s_unit3 == "KIB":
                s_value = s_amount.replace(' ', '')
                # Remove "KB"
                if s_unit == 'KB':
                    s_value = s_value[0:-2]
                elif s_unit3 == 'KIB':
                    s_value = s_value[0:-3]
                elif s_unit1 == "K":
                    s_value = s_value[0:-1]
                i_value = int(s_value)
                i_value_bytes = i_value * 1024
                # Convert to Bytes
                s_amount = str(i_value_bytes)

        if s_amount.isdigit() is True:
            # Is Bytes
            i_value = int(s_amount)
            i_value_bytes = i_value
            s_value_bytes = str(i_value_bytes)
            i_value_kb = i_value_bytes / 1024.00
            s_value_kb = s_mask.format(i_value_kb)
            f_value_mb = i_value_bytes / 1024 / 1024.00
            s_value_mb = s_mask.format(f_value_mb)
            f_value_gb = i_value_bytes / 1024 / 1024 / 1024.00
            s_value_gb = s_mask.format(f_value_gb)
            f_value_tb = i_value_bytes / 1024 / 1024 / 1024 / 1024.00
            s_value_tb = s_mask.format(f_value_tb)
            f_value_pb = i_value_bytes / 1024 / 1024 / 1024 / 1024 / 1024.00
            s_value_pb = s_mask.format(f_value_pb)

        if b_remove_decimals_if_ge_1000 is True:
            if i_value_kb >= 1000:
                i_value_kb = int(i_value_kb)
                s_value_kb = str(i_value_kb)
            if f_value_mb >= 1000:
                f_value_mb = int(f_value_mb)
                s_value_mb = str(f_value_mb)
            if f_value_gb >= 1000:
                f_value_gb = int(f_value_gb)
                s_value_gb = str(f_value_gb)
            if f_value_tb >= 1000:
                f_value_tb = int(f_value_tb)
                s_value_tb = str(f_value_tb)
            if f_value_pb >= 1000:
                f_value_pb = int(f_value_pb)
                s_value_pb = str(f_value_pb)
        else:
            s_value_mb = s_mask.format(f_value_mb)
            s_value_gb = s_mask.format(f_value_gb)
            s_value_tb = s_mask.format(f_value_tb)
            s_value_pb = s_mask.format(f_value_pb)

        if b_add_units is True:
            if i_value_bytes > 1 or i_value_bytes == 0:
                s_value_bytes = s_value_bytes + "Bytes"
            elif i_value_bytes == 1:
                s_value_bytes = s_value_bytes + "Byte"

            s_value_kb = s_value_kb + "KB"
            s_value_mb = s_value_mb + "MB"
            s_value_gb = s_value_gb + "GB"
            s_value_tb = s_value_tb + "TB"
            s_value_pb = s_value_pb + "PB"

        if f_value_pb >= 1:
            s_biggest_suggested = s_value_pb
        elif f_value_tb >= 1:
            s_biggest_suggested = s_value_tb
        elif f_value_gb >= 1:
            s_biggest_suggested = s_value_gb
        elif f_value_mb >= 1:
            s_biggest_suggested = s_value_mb
        elif i_value_kb >= 1:
            s_biggest_suggested = s_value_kb
        else:
            s_biggest_suggested = s_value_bytes

        return s_value_bytes, s_value_kb, s_value_mb, s_value_gb, s_value_tb, s_value_pb, s_biggest_suggested

    def format_float_to_string(self, f_number, i_decimal_positions=2):
        s_format = "%." + str(i_decimal_positions) + "f"

        s_formatted = (s_format % f_number)

        return s_formatted

    def get_dict_value(self, s_key, d_dict, m_default=""):
        """
        Returns the value of the dictionary for key or default. Same as Dict.get
        :param s_key:
        :param d_dict:
        :param m_default:
        :return: Boolean found or not, value
        """
        if s_key in d_dict:
            return True, d_dict[s_key]

        return False, m_default

    def add_trailing_slash(self, s_path):
        """
        Adds / if not found at the end
        :param s_path:
        :return: String
        """

        if s_path == "":
            s_path = "/"

        if s_path[-1] != "/":
            s_path = s_path + "/"

        return s_path

    def format_string_to_fixed_length(self, s_text, i_length=10, s_align_mode="L", b_truncate_excess=True):
        """
        Formats a string keeping the max characters and aligning
        :param b_truncate_excess:
        :param i_length:
        :param s_text:
        :param s_align_mode:
        :return: str
        """

        s_length = str(i_length)

        if b_truncate_excess is True:
            s_text = s_text[0:i_length]

        if s_align_mode == "L":
            s_format = '{0: <' + s_length + '}'
        else:
            # s_align_mode == "R":
            s_format = '{0: >' + s_length + '}'

        s_output = s_format.format(s_text)

        return s_output

    def replace_and_format_multiple_strings(self, s_original_text, a_h_s_to_render):
        """
        Replaces and formats multiple strings based on a_h_s_to_render.
        Example:
        a_h_s_format = [{"s_replace_from": "#DATA_SOURCE#",
                                 "s_replace_to": s_id_data_source,
                                 "i_length": i_length_field_datasource,
                                 "s_align_mode": "L",
                                 "b_truncate_excess": True
                        },
                        {"s_replace_from": "#ENABLED#",
                         "s_replace_to": "True",
                         "i_length": i_length_field_enabled,
                         "s_align_mode": "R",
                         "b_truncate_excess": True
                         }]
        :param s_original_text:
        :param a_h_s_to_render:
        :return:
        """

        s_output = s_original_text

        for h_s_to_render in a_h_s_to_render:
            s_replace_from = h_s_to_render["s_replace_from"]
            s_replace_to = h_s_to_render["s_replace_to"]
            i_length = h_s_to_render["i_length"]
            s_align_mode = h_s_to_render["s_align_mode"]
            b_truncate_excess = h_s_to_render["b_truncate_excess"]

            s_field_aligned = self.format_string_to_fixed_length(s_replace_to,
                                                                 i_length=i_length,
                                                                 s_align_mode=s_align_mode,
                                                                 b_truncate_excess=b_truncate_excess)

            s_output = s_output.replace(s_replace_from, s_field_aligned)

        return s_output

    def convert_integer_to_string_thousands(self, i_number, s_thousand_sep=","):
        """
        Puts thousand separator
        :param i_number:
        :param s_thousand_sep:
        :return: s_number_formatted
        """

        s_number = str(i_number)
        s_number_formatted = ""
        i_pos = 0
        for i_index in range(len(s_number)-1, -1, -1):
            i_pos = i_pos + 1
            if i_pos % 3 == 1 and i_pos > 1 and s_number[i_index] != "-":
                s_number_formatted = s_number[i_index] + s_thousand_sep + s_number_formatted
            else:
                s_number_formatted = s_number[i_index] + s_number_formatted

        return s_number_formatted

    def get_bytes_per_second(self, i_bytes, f_seconds):
        """
        Returns the speed in bytes/seconds
        :param i_bytes:
        :param f_seconds:
        :return: i_speed_bytes_per_second, s_biggest_suggested
        """

        i_speed_bytes_per_second = int(i_bytes / f_seconds)
        s_value_bytes, s_value_kb, s_value_mb, s_value_gb, s_value_tb, s_value_pb, s_biggest_suggested = \
            self.convert_bytes_to_multiple_units(i_speed_bytes_per_second)

        return i_speed_bytes_per_second, s_biggest_suggested

    def get_percent(self, i_partial, i_total, b_add_percent=True):
        """
        Gets the percent from two integers.
        Is designed to work with Python 3 and Python 2.
        """

        f_percent_free = (100.0 * i_partial) / i_total
        i_percent_free = int(f_percent_free)
        s_percent_no_decimals = str(i_percent_free)
        s_percent_decimals = str(round(f_percent_free, 2))
        if b_add_percent is True:
            s_percent_no_decimals = s_percent_no_decimals + "%"
            s_percent_decimals = s_percent_decimals + "%"

        return f_percent_free, i_percent_free, s_percent_decimals, s_percent_no_decimals

    def get_time_and_bytes_per_second(self, i_bytes, f_time_start, f_time_finish):
        """
        Calculates the time between start and end, and the bytes per second, and the best unit for it
        :param i_bytes:
        :param f_time_start:
        :param f_time_finish:
        :return: f_time, s_time, i_bytes_per_second, s_best_unit
        """

        f_time = f_time_finish - f_time_start
        s_time = str(round(f_time, 2))

        i_bytes_per_second, s_best_unit = self.get_bytes_per_second(i_bytes, f_time)

        return f_time, s_time, i_bytes_per_second, s_best_unit

    def html_escape(self, s_text, b_quote=True):
        """
        Returns HTML safe, with escaped characters like <> and &
        :param s_text: Text to escape-HTML from
        :return: String
        """

        s_result = html.escape(s_text, quote=b_quote)

        return s_result
