from keyboardutils import KeyboardUtils


class MenuUtils:

    def __init__(self):

        self.o_keyboard = KeyboardUtils()

    def run_menu(self, s_title, a_menu, b_admin_user=False, s_msg_select="Select menu option:", s_msg_return="Return (or CTRL + C to exit the program)"):
        """
        Prints a menu and offers a selection, then executes the class and method indicated in 3th and 4th positions of the tuple
        for that line.
        :param s_title: Title for the menu
        :param a_menu: Menu as an array of tuples, with tuples like ("Line in the menu", b_is_visible_for_admin_only, o_class, "method_name_in_object_o_class")
        :param b_admin_user: If the user for who we are rendering the menu is admin (so it can see the options with b_is_visible_for_admin_only set to True)
        :param s_msg_select:
        :param s_msg_return:
        :return: None
        """

        # This will loop until 0 - Return is selected
        while True:
            a_menu_mapping = []
            i_menu_index = 0
            # Map the function to the index of the menu
            # 0 will be always go back
            a_menu_mapping.append("")

            print(s_title)
            print("=" * len(s_title))
            print()

            for t_menu_item in a_menu:
                s_title = t_menu_item[0]
                b_admin = t_menu_item[1]
                o_object = t_menu_item[2]
                s_method = t_menu_item[3]
                if (b_admin is True and b_admin_user is True) or (b_admin is False):
                    i_menu_index += 1
                    a_menu_mapping.append((o_object, s_method))
                    print(str(i_menu_index) + ". " + s_title)

            print("0. " + s_msg_return)

            i_option = self.o_keyboard.ask_for_valid_integer(s_msg_select, 0, i_menu_index)
            # Execute the command
            if i_option > 0:
                o_object = a_menu_mapping[i_option][0]
                s_method = a_menu_mapping[i_option][1]
                result = getattr(o_object, s_method)()

            if i_option == 0:
                return

    def run_menu_for_selection(self, a_menu, s_msg_return="Return (or CTRL + C to exit the program)"):
        """
        Print the menu, offer selection, return the string associated to the index
        :param a_menu:
        :return: String, String: Data of first selection, Data optional
        """

        i_justify_spaces = 1
        if len(a_menu) > 99:
            i_justify_spaces = 3
        elif len(a_menu) > 9:
            i_justify_spaces = 2

        i_menu_index = 0
        while True:
            for t_menu_item in a_menu:
                s_title = t_menu_item[0]
                s_value = t_menu_item[1]
                i_menu_index += 1
                # We reserve spaces as we can have up to 20 VMs running and many more stopped
                # We want to keep the alignment
                print(str(i_menu_index).rjust(i_justify_spaces) + ". " + s_title)

            print(s_msg_return)

            i_option = self.o_keyboard.ask_for_valid_integer("Select:", i_min=0, i_max=i_menu_index)
            # Execute the command
            if i_option > 0:
                s_value = a_menu[i_option-1][1]
                s_value_optional = ""
                if len(a_menu[i_option-1]) > 2:
                    s_value_optional = a_menu[i_option-1][2]
                return s_value, s_value_optional

            if i_option == 0:
                return "", ""

    def get_nice_title(self, s_text, s_underline_char="="):
        """
        Will return the s_text with underline and a blank line
        :param s_text:
        :param s_underline_char:
        :return: string: s_text_formatted
        """

        s_text_formatted = "\n"
        s_text_formatted += s_text + "\n" + s_underline_char * len(s_text) + "\n"

        s_text_formatted += "\n"

        return s_text_formatted
