
import os
import sys


def project_root_path(project_name=None):
    """
    a
    """

    global root_path
    PROJECT_NAME = 'TMT_QA_UI_Test' if project_name is None else project_name
    project_path = os.path.abspath(os.path.dirname(__file__))
    if sys.platform == "darwin":
        root_path = project_path.split(PROJECT_NAME)[0] + '/' + PROJECT_NAME
    if sys.platform == "win32":
        root_path = project_path.split(PROJECT_NAME)[0] + PROJECT_NAME
    if sys.platform == 'linux':
        # root_path = project_path.split(PROJECT_NAME)[0] + '/' + PROJECT_NAME
        root_path = '/tmp/pycharm_project_593/'

    return root_path
