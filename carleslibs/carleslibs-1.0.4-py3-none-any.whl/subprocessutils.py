#
# Class to work with subprocesses
#
# Author: Carles Mateo
# Creation Date: 2014
#
# v.0.1.4 - 2020-10-04 - Carles Mateo
# v.0.1.5 - 2020-10-09 - Carles Mateo
# v.0.1.6 - 2020-10-11 - Carles Mateo
#

import subprocess


class SubProcessUtils:

    def execute_command_for_output(self, s_command, b_shell=True, b_convert_to_ascii=True, b_convert_to_utf8=False):
        """
        Executes Command and returns the Error Code, the Standard Output STDOUT and Standard Error STDERR
        """

        s_output = ""
        s_error = ""

        try:
            # Note: In Python3 this will return a binary
            process = subprocess.Popen([s_command],
                                       shell=b_shell,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            s_output, s_error = process.communicate()
            i_error_code = process.returncode

        except:
            i_error_code = 99

        try:
            if b_convert_to_ascii is True:
                s_output = s_output.decode('ascii')
                s_error = s_error.decode('ascii')
            if b_convert_to_utf8 is True:
                s_output = s_output.decode('utf8')
                s_error = s_error.decode('utf8')

        except:
            i_error_code = 128

        return i_error_code, s_output, s_error

    def execute_command_with_no_pipe_and_no_stderr(self, s_command, b_shell=True, b_convert_to_ascii=True, b_convert_to_utf8=False):
        """
        Execute without locking pipe and without stderr
        """

        # Using stderr = subprocess.STDOUT would provoke locking and expiring the timeout
        s_output = ""
        s_exception = ""
        try:
            s_output = subprocess.check_output([s_command], shell=b_shell)
            if b_convert_to_ascii is True:
                s_output = s_output.decode('ascii')
            if b_convert_to_utf8 is True:
                s_output = s_output.decode('utf8')

        except:
            s_output = ""

        return s_output
