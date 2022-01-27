# '''
# auto generate a Suite.txt file which according to the Robot Framework Require format.
#
# mainly include three steps
#     step1: collect all the test cases which should be executed
#     step2: fetch the related Library for each test case and generate the Suite.txt file
#     step3: execute command "pybot Suite.txt"
#
# @author: Wang Lin
# '''
# import os
# import time
# import datetime
# from tests import tests_testcases
#
# def generate_suite(testcase_list, suite_name, suit_directory):
#     file_obj = open("%s\%s" % (suit_directory, suite_name), "w")
#     suite_header = '''*** Settings ***
# Test Template'''
#     file_obj.write(suite_header)
#
#     # add all testcase's related Libraries
#     for testcase in testcase_list:
#         testcase_module = testcase.__module__
#         testcase_module_name = testcase_module.split(".")[-1]
#         new_testcase_module = testcase_module.replace(".", "\\")
#         testcase_related_lib = new_testcase_module + ".py"
#         testcase_related_lib = testcase_related_lib.replace("\\", "/")
#         testcase_name = testcase.__name__
#         all_text = '''
# Library           %s
# Library           %s.%s''' % (testcase_related_lib, testcase_module_name, testcase_name)
#         file_obj.write(all_text)
#     file_obj.write("\n\n*** Test Cases ***")
#
#     # add all test cases
#     for testcase in testcase_list:
#         testcase_module = testcase.__module__
#         module_items = testcase_module.split(".")
#         testcase_module_name = module_items[-1]
#         position = len(module_items) - 2
#         feature = module_items[position]
#         testcase_name = testcase.__name__
#         all_text = '''
# %s
#     [Tags]     %s
#     [Setup]    %s.%s.create browser driver
#     %s.%s.runTest
#     [Teardown]    %s.%s.close browser
#     ''' % (
#         testcase_name, feature, testcase_module_name, testcase_name, testcase_module_name, testcase_name, testcase_module_name, testcase_name)
#         file_obj.write(all_text)
#
#     file_obj.close()
#
#     # sleep 2 seconds make sure the Suite.txt have been generated completed
#     time.sleep(2)
#     cmd = r'''pybot '''
#     cmd = cmd + ''' %s\%s''' % ("robot_test_suite", suite_name)
#     print cmd
#
# if __name__ == "__main__":
#     testcase_list = tests_testcases
#     suite_name = "Suite.txt"
#     suite_directory = "..\\robot_test_suite"
#
#     begin_time = datetime.datetime.now()
#     print("execution begin at time: %s" % (begin_time))
#
#     path = os.path.dirname(os.path.abspath(__file__))
#
#     generate_suite(testcase_list, suite_name, suite_directory)
