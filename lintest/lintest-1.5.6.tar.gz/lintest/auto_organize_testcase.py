"""
This module is to organize all the testcases into different groups(such as: "smoke", "nightly", "ignore" and "regression")

Testcase Demo: (below testcase will be added into smoke and nightly group)

class TestBackend1(BackendTestCase):
    execute_tag = "smoke, nightly"

    def run_test(self):
        self.test_case_id = "BackendTC-1"
        self.logger.debug("start to run backend test case 1")

@author: Wang Lin
"""

import os
import traceback

try:
    from tests import tests_testcases
except ImportError:
    traceback.print_exc()


def generate_testcase_list(testcase_dict):
    for key in testcase_dict.keys():
        if key == "regression":
            continue

        values = testcase_dict.get(key)
        with open((".." + os.path.sep + "tests" + os.path.sep + "%s.py") % key, "w") as file_obj:
            file_obj.write("import tests")
            file_obj.write(os.linesep)
            file_obj.write(os.linesep)

            file_obj.write("%s_run_testcase_list = [%s" % (key, os.linesep))

            for value in values:
                file_obj.write("    " + value.__module__ + "." + value.__name__)
                file_obj.write("," + os.linesep)

            file_obj.write("]")


def auto_organize_testcase(testcase_list):
    tag_list = []
    testcase_dict = {}

    for testcase in testcase_list:
        if hasattr(testcase, "tag"):
            tags = testcase.tag.lower().split(",")
            for tag in tags:
                if tag.strip() not in tag_list:
                    tag_list.append(tag.strip())

    for tag in tag_list:
        testcase_dict[tag] = []

    for testcase in testcase_list:
        if hasattr(testcase, "tag"):
            testcase_tags = testcase.tag.lower().split(",")
            for tag in testcase_tags:
                testcase_dict[tag.strip()].append(testcase)

    generate_testcase_list(testcase_dict)

    return testcase_dict


if __name__ == "__main__":
    testcase_dict = auto_organize_testcase(tests_testcases)

    for key in testcase_dict.keys():
        if key != "regression":
            print
            key, " : ", testcase_dict[key]
