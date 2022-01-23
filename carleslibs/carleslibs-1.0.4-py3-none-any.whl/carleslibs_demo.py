from datetimeutils import DateTimeUtils
from keyboardutils import KeyboardUtils
from menuutils import MenuUtils
from fileutils import FileUtils
from pythonutils import PythonUtils
from stringutils import StringUtils
from subprocessutils import SubProcessUtils


class CarlesLibsDemo:
    """
    A demo apllication for carleslibs from Carles Mateo
    https://blog.carlesmateo.com/carleslibs
    """

    def __init__(self, o_datetime, o_keyboard, o_menu, o_python, o_file):
        self.o_datetime = o_datetime
        self.o_keyboard = o_keyboard
        self.o_menu = o_menu
        self.o_python = o_python
        self.o_file = o_file

    def main(self):
        s_version, i_major, i_minor, i_micro, s_releaselevel = self.o_python.get_python_version()
        print("Python Version:", s_version)
        if self.o_python.is_python_2() is True:
            print("Warning! Python 2 reached End of Life")
        print()

        a_menu = [("See all the files in the local directory", False, self, "list_files"),
                  ("See files with a specific mask", False, self, "list_files_asking"),
                  ("Print current time", False, self, "print_current_time")]

        self.o_menu.run_menu(s_title="Carleslibs Demo Main Menu", a_menu=a_menu, b_admin_user=False, s_msg_select="Select menu option:", s_msg_return="Return (or CTRL + C to exit the program)")

    def print_current_time(self):
        print("Current time:", self.o_datetime.get_datetime(), "-", self.o_datetime.get_unix_epoch())

    def list_files_asking(self):

        s_mask = self.o_keyboard.ask_for_string("Mask (Ie: *.py):", i_min_length=0, i_max_length=100, b_allow_spaces=False, b_allow_underscores=True)
        if s_mask == "":
            print("No mask selected.")
            return

        self.list_files(s_mask)

    def list_files(self, s_mask="*"):
        b_success, a_files = self.o_file.get_all_files_or_directories_with_mask(s_mask)

        if b_success is False:
            print("There has been an error")
            return

        print(self.o_menu.get_nice_title("Files with mask " + s_mask, s_underline_char="-"))
        print()

        print("Total files:", len(a_files))
        print()

        if len(a_files) > 0:
            for s_file in a_files:
                print(s_file)

            print()


if __name__ == "__main__":
    o_datetime = DateTimeUtils()
    o_keyboard = KeyboardUtils()
    o_menu = MenuUtils()
    o_python = PythonUtils()
    o_file = FileUtils(o_pythonutils=o_python)

    o_demo = CarlesLibsDemo(o_datetime, o_keyboard, o_menu, o_python, o_file)
    try:
        o_demo.main()
    except KeyboardInterrupt:
        print("CTRL + C captured. Exitting")
