#
# File Utils
#
# Author: Carles Mateo
# Creation Date: 2014-01-01 GMT+1
# Last Update  : 2021-04-11 07:21 Ireland by Carles Mateo
# Description: Class to deal with Files and Directories.
#              Please try to keep it lightweight and without other library dependencies.
#

import os
import glob
import csv
import platform
import sys

# ***********************************************************
# Adding to SysPath so Libraries will find there dependencies
# ***********************************************************
s_path_program = os.path.dirname(__file__)
sys.path.append(s_path_program)
# ***********************************************************

from pythonutils import PythonUtils


class FileUtils:

    o_pythonutils = None

    def test_helper(self):
        pass

    def __init__(self, o_pythonutils=PythonUtils()):
        self.o_pythonutils = o_pythonutils

    def append(self, s_file, s_text):
        """
        This method creates or appends to a file
        :return: boolean
        """
        b_success = True
        try:
            self.test_helper()

            fh = open(s_file, "a")
            fh.write(s_text)
            fh.close()

        except IOError:
            b_success = False

        return b_success

    # Type Hinting and Annotations disabled to have compatibility with Python 3.5.2.
    #     # def create_folder(self, s_folder: str) -> bool:
    def create_folder(self, s_folder):
        """
        Creates a folder
        :param s_folder: Folder to be created
        :return: boolean
        """

        # Commented for Compatibility with Python 2.x
        # b_success: bool = True
        b_success = True
        try:
            os.mkdir(s_folder)
        except IOError:
            b_success = False

        return b_success

    def delete(self, s_file):
        """
        This method deletes a given file
        :param s_file: The file path for the file to delete
        :type s_file: str
        :return: Indicate success of deletion
        :rtype boolean
        """

        b_success = True
        try:
            # This will help with Unit Testing by raisin IOError Exception
            self.test_helper()

            if os.path.exists(s_file):
                os.remove(s_file)
            else:
                b_success = False
        except IOError:
            b_success = False

        return b_success

    def delete_all_with_mask(self, s_mask):
        """
        This method deletes all files matching a given mask. Example mask: '/root/file*.txt'. This mask will delete any
        file in the root directory, starting with 'file' and ending with '.txt'.
        :param s_mask: The mask to use for deletion. Should contain entire file path.
        :type s_mask: str
        :return: Indicate success of deletion
        :rtype boolean
        :return: Number of files successfully deleted
        :rtype integer

        """
        b_success = True
        i_files_deleted = 0
        try:
            self.test_helper()

            for o_file in glob.glob(s_mask):
                os.remove(o_file)
                i_files_deleted = i_files_deleted + 1
        except IOError:
            b_success = False

        return b_success, i_files_deleted

    def get_all_files_or_directories_with_mask(self, s_mask="*"):
        """
        Get all files matching a given mask or the directories.
        Example mask: '/proc/[0-9]*/' will return the directories that start from a number.
        Example mask: '/root/file*.txt'. This mask will return any file in the root directory,
                      which name starts with 'file' and ends in '.txt'.
        :param s_mask: The mask to use for gathering the files. Should contain entire file path.
        :type s_mask: str
        :return: A boolean indicating success, An Array of files matching the mask
        :rtype boolean, list
        """
        a_files = []
        b_success = True
        try:
            self.test_helper()

            for s_filename in glob.glob(s_mask):
                a_files.append(s_filename)
        except IOError:
            b_success = False

        return b_success, a_files

    def get_file_size_in_bytes(self, s_file):

        b_success = False
        i_file_size = 0

        try:
            # This will help with Unit Testing by raisin IOError Exception
            self.test_helper()

            i_file_size = os.path.getsize(s_file)
            b_success = True
        except IOError:
            b_success = False

        return b_success, i_file_size

    def get_real_path(self, s_file):
        """
        Get the canonical path(removes symbolic links) for a specified file
        :param s_file: The file to get the path for
        :return: A boolean indicating success, A string of the real path
        """
        s_path = ""
        try:
            self.test_helper()

            s_path = os.path.realpath(s_file)
            if self.file_exists(s_file):
                b_success = True
            else:
                b_success = False
        except IOError:
            b_success = False

        return b_success, s_path

    def file_exists(self, s_file):
        """
        Check if a file exists
        :param s_file: The file to check
        :return: boolean indicating success
        """
        try:
            self.test_helper()

            b_exists = os.path.isfile(s_file)
        except IOError:
            b_exists = False

        return b_exists

    def folder_exists(self, s_folder):
        """
        Checks if a folder exists
        :param s_folder:
        :return: boolean
        """

        try:
            self.test_helper()

            b_exists = os.path.isdir(s_folder)
        except IOError:
            b_exists = False

        return b_exists

    def list_dir(self, s_dir):
        """
        Get the contents of a directory and return them as a list
        :param s_dir: The directory to list
        :return: A boolean indicating success, A list of the contents
        """
        b_success = True
        a_files = []
        try:
            a_files = os.listdir(s_dir)
        except IOError:
            b_success = False

        return b_success, a_files

    def path_exists(self, s_file_path):
        """
        Check if a file or folder path exists
        :param s_file_path: The file path to check
        :return: boolean indicating success
        """
        try:
            self.test_helper()

            b_exists = os.path.exists(s_file_path)
        except IOError:
            b_exists = False

        return b_exists

    def read_csv(self, s_file):
        """
        Read a CSV file.
        :param s_file:
        :return: boolean, Array
        """
        a_rows = []
        b_error = False

        try:
            with open(s_file, newline='') as o_csv_file:
                o_reader = csv.reader(o_csv_file, delimiter=',')
                for a_row in o_reader:
                    a_rows.append(a_row)
        except:
            b_error = True

        return b_error, a_rows

    def read_file_as_string(self, s_file, s_encoding='utf-8'):
        """
        This method reads the file in text ascii, utf-8 or other encodings.
        Note: Python3 will try to UTF-8 Decode binary and return "UnicodeDecodeError: 'utf-8' codec can't decode byte"
        :param s_file: The file path for the file to read
        :type s_file: str
        :return: b_result: Indicate success reading, s_result: The text of the file
        :rtype boolean, String
        """
        s_result = ""
        b_success = True

        try:
            fh = open(s_file, "r", encoding=s_encoding)
            s_result = fh.read()
            fh.close()

        except IOError:
            b_success = False

        return b_success, s_result

    def read_link_path(self, s_link_path):
        """
        Returns the path to the target gile, given a link
        :param s_link_path: Path to Link
        :return: b_result, s_file_path
        """

        b_success = False

        try:
            s_link_path = os.readlink(s_link_path)
            b_success = True
        except IOError:
            b_success = False
        except OSError:
            b_success = False
        except:
            b_success = False

        return b_success, s_link_path

    def get_only_config_values_from_list(self, a_s_lines):
        """
        Filters out anything that is not of the type key=value or key = value
        :param a_s_lines: the array containing the string lines
        :return: a_s_result
        """
        a_s_result = []

        for s_line in a_s_lines:
            if s_line[0] != "#":
                if "=" in s_line:
                    a_s_result.append(s_line)

        return a_s_result

    def read_config_file_values(self, s_file):
        """
        Reads a config file and returns a dict with key/value
        :param s_file: The file path for the file to read
        :type s_file: str
        :return: b_result, d_s_config_values
        """

        a_s_config = []
        d_s_config_values = {}

        b_success, a_s_result = self.read_file_as_lines(s_file)
        if b_success is True:
            a_s_config = self.get_only_config_values_from_list(a_s_result)

            for s_line in a_s_config:
                a_lines = s_line.split("=")
                s_key = a_lines[0]
                s_value = "=".join(a_lines[1:])
                if len(s_value) > 0 and s_value[-1] == "\n":
                    s_value = s_value[:-1]
                d_s_config_values[s_key] = s_value

        return b_success, d_s_config_values

    def read_file_as_lines(self, s_file, s_encoding='utf-8'):
        """
        This method reads the file in text with the encodinf specified: ascii, utf-8 format.
        Note: Python3 will try to UTF-8 Decode binary and return "UnicodeDecodeError: 'utf-8' codec can't decode byte"
        :param s_file: The file path for the file to read
        :type s_file: str
        :return: b_result: Indicate success reading, a_s_result: The text of the file as an Array of lines
        :rtype boolean, String
        """
        a_s_result = []
        b_success = True

        try:
            self.test_helper()

            with open(s_file, "r", encoding=s_encoding) as fp:
                for cnt, s_line in enumerate(fp):
                    a_s_result.append(s_line)

        except IOError:
            b_success = False

        return b_success, a_s_result

    def read_binary(self, s_file):
        """
        This method reads the file in binary format
        :param s_file: The file path for the file to read
        :type s_file: str
        :return: Indicate success reading
        :rtype boolean
        :return: by_result: byte
        :rtype byte
        """
        by_result = bytes()
        b_success = True

        try:
            self.test_helper()

            fh = open(s_file, "rb")
            by_result = fh.read()
            fh.close()

            # For python2
            by_result = bytearray(by_result)

        except IOError:
            by_result = bytes()
            b_success = False

        except:
            # May have crashed due to not more memory available
            by_result = bytes()
            b_success = False

        return b_success, by_result

    def read_file_with_readlines(self, s_file):
        """
        Read a file and return its contents as an array of lines by using readlines.
        This consideration is important for Memory purposes.
        :param s_file: The file to read
        :return: A list with each line of the file as strings
        """

        a_result = []
        b_success = True

        try:
            self.test_helper()

            fh = open(s_file, "r")
            a_result = fh.readlines()
            fh.close()

        except IOError:
            b_success = False
        except:
            # May have crashed due to not more memory available
            a_result = []
            b_success = False

        return b_success, a_result

    def remove_folder(self, s_folder):
        """
        Remove a folder
        :param s_folder: The folder to remove
        :return: A boolean indicating success
        """

        b_success = True
        try:
            os.rmdir(s_folder)
        except IOError:
            b_success = False

        return b_success

    def rename_file(self, s_old_file, s_new_file):
        """
        Rename a file to a new name
        :param s_old_file: The old file name
        :param s_new_file: The new file name
        :return: A boolean indicating success
        """

        try:
            self.test_helper()

            os.rename(s_old_file, s_new_file)
            b_success = self.file_exists(s_new_file)
        except IOError:
            b_success = False

        return b_success

    def strings(self, s_file):
        """
        This method reads the file as binary and returns only text. Like 'strings' Linux command in text ASCII format.
        :param s_file: The file path for the file to read
        :type s_file: str
        :return: b_result: Indicate success reading, s_result: The text of the file
        :rtype boolean, String
        """
        s_result = ""
        b_success = True

        try:
            self.test_helper()

            # fh = open(s_file, "rb")
            # a_i_result = fh.read()
            # fh.close()

            b_success_read_binary, by_contents = self.read_binary(s_file)

            if b_success_read_binary is False:
                b_success = False
                by_contents = bytes()
            else:
                #for i_ascii in a_i_result:
                for i_ascii in by_contents:
                    if i_ascii > 31 and i_ascii < 127:
                        s_result = s_result + chr(i_ascii)

        except IOError:
            b_success = False

        return b_success, s_result

    def write(self, s_file, s_text):
        """
        This method creates or overwrites a file
        :param s_file: The file path for the file to read
        :type s_file: str
        :param s_text: The text to write
        :type s_text: str
        :return: b_result: Indicate success reading, s_result: The text of the file
        :rtype bool, str
        """
        try:
            fh = open(s_file, "w")
            fh.write(s_text)
            fh.close()

        except IOError:
            return False

        return True

    def write_binary(self, s_file, by_content):
        """
        This method creates or overwrites a file
        :param s_file: The file path for the file to read
        :type s_file: str
        :param by_content: The text to write
        :type by_content: Binary
        :return: b_result: Indicate success reading, by_content: The binary content of the file
        :rtype bool, binary
        """
        try:
            fh = open(s_file, "wb")
            fh.write(by_content)
            fh.close()

        except IOError:
            return False

        return True

    def write_if_changed(self, s_file, s_text):
        """
        This method will check the current file contents against s_text and only write if its different or doesn't exist
        Use on text files, not binary.
        :param s_file: The file to write/update
        :param s_text: The text to write
        :return: boolean: If file was written, str: Error message
        :rtype: bool
        :rtype: str
        """
        # check if the file exists
        b_exists = self.file_exists(s_file)
        # if exists check if it the contents are different
        if b_exists is True:
            b_read_success, s_file_contents = self.read_file_as_string(s_file)
            if b_read_success is True:
                if s_file_contents == s_text:
                    return False, "The contents are the same."
            else:
                return False, "Unable to read File."

        b_write_success = self.write(s_file, s_text)
        if b_write_success is True:
            return True, ""
        else:
            return False, "Failed to write file."

    def get_file_creation_date(self, s_path_to_file):
        """
        Try to get the date that a file was created, falling back to when it was
        last modified if that isn't possible.
        See http://stackoverflow.com/a/39501288/1709587 for explanation.
        :param s_path_to_file: The file
        :return: boolean: If permission was retrieved
        :rtype: bool
        :rtype: int
        """

        i_unix_time = 0
        b_success = True

        if platform.system() == 'Windows':
            i_unix_time = os.path.getctime(s_path_to_file)
        else:
            o_stat = os.stat(s_path_to_file)
            try:
                i_unix_time = o_stat.st_birthtime
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                b_success = False
                i_unix_time = -1

        return b_success, i_unix_time

    def get_file_modification_date(self, s_path_to_file):
        """
        Try to get the date that a file was last modified
        :param s_path_to_file: The file
        :return: boolean: If permission was retrieved
        :rtype: bool
        :rtype: int
        """

        i_unix_time = 0
        b_success = True

        if platform.system() == 'Windows':
            i_unix_time = os.path.getmtime(s_path_to_file)
        else:
            o_stat = os.stat(s_path_to_file)
            try:
                i_unix_time = o_stat.st_mtime
            except AttributeError:
                b_success = False

        return b_success, i_unix_time

    def get_own_path(self):
        return os.path.dirname(os.path.abspath(__file__))
