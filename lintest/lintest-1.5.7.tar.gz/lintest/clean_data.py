"""
module clean_data.py is used to:
1. clear all the __init__.py file which under tests package
2. remove all the .pyc files which under tests package

@author: Wang Lin
"""
import os
import time
import shutil
from .get_project_info import get_project_info


project_info = get_project_info()


# remove tests/android_temp if exists
def remove_android_temp(android_testcase_temp_package_name):
    tests_package_path = project_info.project_path + os.sep + project_info.testcase_package_name
    android_temp_package_path = tests_package_path + os.sep + android_testcase_temp_package_name

    while os.path.exists(android_temp_package_path):
        shutil.rmtree(android_temp_package_path)
        time.sleep(2)


# clear all the __init__.py file which under tests package
def clear_init_file():
    for directory_path, directory_names, file_names in os.walk(
                            project_info.project_path + os.sep + project_info.testcase_package_name, topdown=True):
        for file_name in file_names:
            if "__pycache__" in directory_path:
                continue

            if file_name == "__init__.py":
                with open(directory_path + os.sep + file_name, "w"):
                    print("clear file: %s" % (directory_path + os.sep + file_name))


def remove_pyc():
    # clear all the pyc file which under tests package
    for directory_path, directory_names, file_names in os.walk(
                            project_info.project_path + os.sep + project_info.testcase_package_name,
            topdown=True):
        for file_name in file_names:
            if file_name.endswith(".pyc"):
                file_path = directory_path + os.sep + file_name
                print("remove file: %s" % file_path)
                os.remove(file_path)
