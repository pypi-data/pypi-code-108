import os
import re

from collections import defaultdict, namedtuple
from junit_xml import TestSuite, TestCase

module_dir = os.path.abspath(os.path.dirname(__file__))

Suite = namedtuple('Suite', 'name tests msgs fails times lines')

class GUnit:
    def __init__(self, build_dir='.', executable='gdb'):
        self.build_dir = os.path.abspath(os.path.join(build_dir, 'gunit'))

        # Create output directory
        os.makedirs(self.build_dir, exist_ok=True)

        self.logging_file = os.path.join(self.build_dir, 'gdblog')
        self.report_file = os.path.join(self.build_dir, 'report.xml')

        self.log = f'-ex "set logging file {self.logging_file}"'
        self.remote = ''
        self.load = ''

        self.gdb = executable

    # Runs automatic testing on given binary/test suite
    def test(self, path=None):
        # Get scripts
        setup_path = os.path.join(module_dir, 'setup.gdb')
        execute_path = os.path.join(module_dir, 'execute.gdb')

        # Activate GDB and connect to server
        command = f'{self.gdb} -batch-silent {self.log} -x {setup_path} '

        if path is not None:
            command += f'-ex "file {path}" '

        command += f' {self.remote} {self.load} -x {execute_path}'

        os.system(command)

    def junit(self):
        suites = []

        with open(self.logging_file, "r") as gdblog:
            lines = gdblog.readlines()

            suites_raw = []
            for line in lines:
                if line[0] == '$':
                    suites_raw += [line]

            data = [None] * 6
            data_i = 0
            for sr in suites_raw:
                data[data_i] = sr.split(" = ")[1][0:-1]
                if data_i != 0:
                    data[data_i] = data[data_i][1:-1]

                if data_i == 5:
                    suite_name = data[0][1:-1]
                    suite_tests = re.sub(r'("| *)', '', data[1]).split(',')
                    suite_messages = re.sub(r'"', '', data[2]).split(',')
                    suite_fails = re.sub(r'("| *)', '', data[3]).split(',')
                    suite_elapsed = re.sub(r' *', '', data[4]).split(',')
                    suite_lines = re.sub(r' *', '', data[5]).split(',')

                    suites += [Suite(suite_name, suite_tests, suite_messages, suite_fails, suite_elapsed, suite_lines)]

                    data_i = 0

                data_i += 1

        test_suites = []
        for suitei, suite in enumerate(suites):
            suite_name = suite.name

            # Get the number of test cases in the suite
            testn = len(suite.tests)

            # Create a test case for each test
            cases = []
            for testi in range(testn):
                name = suite.tests[testi]
                message = suite.msgs[testi]
                fail = suite.fails[testi] == 'true'
                elapsed = suite.times[testi]
                fline = suite.lines[testi]

                tc = TestCase(name, suite_name, float(elapsed), "", "", allow_multiple_subelements=True)

                if fail:
                    tc.add_failure_info(f"Affirmation failed at {suite_name}:{fline} with the following message: {message}")

                cases += [tc]

            test_suites += [TestSuite(suite_name, cases)]

        with open(self.report_file, "w") as outxml:
            outxml.write(TestSuite.to_xml_string(test_suites))

    #### STATIC FUNCTIONS ####

    # Generate GUnit.h
    def get_header(build_dir='.'):
        source_path = os.path.join(module_dir, 'GUnit.hpp')
        destination_path = os.path.abspath(os.path.join(build_dir, 'GUnit.hpp'))

        with open(source_path, "r") as src, open(destination_path, "w") as dst:
            dst.write(src.read())

    # Configure GUnit for OpenOCD server
    def openOCD(gdb_uri, build_dir='.', executable='gdb'):
        target = GUnit(build_dir, executable)

        target.remote = f'-ex "target extended-remote {gdb_uri}"'
        target.load = '-ex load -ex "monitor reset init"'

        return target

    # Configure GUnit for regular GDB server
    def gdbserver(gdb_uri, build_dir='.'):
        target = GUnit(build_dir)

        target.remote = f'-ex "target extended-remote {gdb_uri}"'

        return target
