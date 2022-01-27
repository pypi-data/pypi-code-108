"""
get_project_info.py module is used to:
    1. define the TESTCASE_PACKAGE_NAME, TAG_TESTCASE_PACKAGE_NAME and LIN_TEST_PROJECT_PATH
    2. set the project_path into sys.path
    3. return project_info

@author: Wang lin
"""

import os
import shutil
import sys
import time
import platform
import traceback
from time import strftime

TESTCASE_PACKAGE_NAME = "tests"
TAG_TESTCASE_PACKAGE_NAME = "tag_testcases"
FRAMEWORK_PACKAGE_NAME = os.path.dirname(os.path.abspath(__file__)).split(os.sep)[-1]


class ProjectInfo(object):
    project_info_obj = None

    def __init__(self, project_path, testcase_package_name, tag_testcase_package_name, framework_package_name,
                 project_name, output_folder):
        self.project_path = project_path
        self.testcase_package_name = testcase_package_name
        self.tag_testcase_package_name = tag_testcase_package_name
        self.framework_package_name = framework_package_name
        self.project_name = project_name
        self.output_folder = output_folder


def get_project_info():
    if ProjectInfo.project_info_obj is None:
        project_path = os.getenv("LIN_TEST_PROJECT_PATH")
        project_name = project_path.split(os.sep)[-1]

        if project_path is None:
            project_path = os.path.dirname(os.path.abspath(__file__)).split(os.sep + FRAMEWORK_PACKAGE_NAME)[0]

        sys.path.insert(0, project_path)

        if not hasattr(ProjectInfo, "start_time_for_output"):
            current_time = strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            import random
            current_time += "-" + str(random.randint(100000, 999999))
            ProjectInfo.start_time_for_output = current_time

            # When a jenkins job executes, it sets some environment variables that you may use in your shell script, batch
            # command, Ant script or Maven POM.
            # reference:
            # https://wiki.jenkins-ci.org/display/JENKINS/Building+a+software+project#Buildingasoftwareproject-JenkinsSetEnvironmentVariables
            if "JENKINS_URL" in os.environ.keys():
                output_folder = project_path + os.sep + "output"
            else:
                import random
                output_folder = project_path + os.sep + "output" + os.sep + current_time

            if os.path.exists(output_folder):
                shutil.rmtree(output_folder)

            os.makedirs(output_folder)

            if platform.system() != "Windows":
                try:
                    os.chdir(project_path + os.sep + "output")

                    if os.path.islink('latest') == True:
                        os.unlink('latest')

                    os.symlink(current_time, 'latest')
                except BaseException:
                    traceback.print_exc()

        project_info_obj = ProjectInfo(project_path, TESTCASE_PACKAGE_NAME, TAG_TESTCASE_PACKAGE_NAME, FRAMEWORK_PACKAGE_NAME,
                           project_name, output_folder)

        ProjectInfo.project_info_obj = project_info_obj

    return ProjectInfo.project_info_obj


if __name__ == "__main__":
    project_info = get_project_info()
