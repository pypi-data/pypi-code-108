#
# Keyboard Utils
#
# Author: Carles Mateo
# Creation Date: 2021-12-07 01:10 Ireland
# Last Update: 2021-12-07 01:10 Ireland
# Description: Class to deal with Python 3 Input from Keyboard
#


class KeyboardUtils:

    def ask_for_string(self, s_text, i_min_length, i_max_length, b_allow_spaces=True, b_allow_underscores=True):
        """
        Ask for a string, and do not leave until criteria is matched.
        :param s_text:
        :param i_min_length:
        :param i_max_length:
        :param b_allow_spaces:
        :param b_allow_underscores:
        :return: String typed by the user
        """
        s_error_msg = "Please enter a text with length between " + str(i_min_length) + " and " + str(i_max_length)
        while True:
            s_answer = input(s_text)
            if b_allow_spaces is False:
                if " " in s_answer:
                    print("Please do not input spaces")
                    continue
            if b_allow_underscores is False:
                if "_" in s_answer:
                    print("Please do not input underscores")
                    continue
            if len(s_answer) < i_min_length or len(s_answer) > i_max_length:
                print(s_error_msg)
                continue

            break

        return s_answer

    def ask_for_valid_integer(self, s_text, i_min, i_max):
        """
        Ask for a Integer, and do not leave until criteria is matched.
        :param s_text:
        :param i_min:
        :param i_max:
        :return:
        """
        s_error_msg = "Please enter a valid value between " + str(i_min) + " and " + str(i_max)
        while True:
            s_answer = input(s_text)
            try:
                i_answer = int(s_answer)
            except ValueError:
                print(s_error_msg)
                continue

            if i_answer < i_min or i_answer > i_max:
                print(s_error_msg)
            else:
                break

        return i_answer
