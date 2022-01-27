"""
This module is used to:
 1. start appium server
 2. check whether appium server is start success

@author: WangLin
"""
import os
import time
import subprocess
import traceback

import psutil
import platform

from . import android_testcase
from . import get_project_info

try:
    import settings
except ImportError:
    traceback.print_exc()


# from .selenium_helper import chromedriver_path_dict

project_info = get_project_info.get_project_info()

DEFAULT_SLEEP_TIME = 1
IS_APPIUM_RUNNING_TIMEOUT = 30
APPIUM_SERVER_DEFAULT_IP = getattr(settings, 'APPIUM_SERVER_DEFAULT_IP', "127.0.0.1")
APPIUM_SERVER_DEFAULT_PORT = int(getattr(settings, 'APPIUM_SERVER_DEFAULT_PORT', 4723))

# the default appium_server_port is start 4723,
# we assume that there are at most (20000 - 4723 = 15277) android testcases will be executed in one execution,
# for concurrently run android testcases, each testcase should have its own callback_port & bootstrap_port,
# here define the increment number for callback_port & bootstrap_port.
APPIUM_CALLBACK_PORT_INCREMENT = 20000
APPIUM_BOOTSTRAP_PORT_INCREMENT = 30000

process_id_list = []
process_id_testcase_dict = {}


def kill_process_by_name(process_name):
    try:
        if platform.system() == "Windows":
            subprocess.check_output("taskkill /f /im %s" % process_name, shell=True, stderr=subprocess.STDOUT)
        else:
            subprocess.check_output("killall '%s'" % process_name, shell=True, stderr=subprocess.STDOUT)

        print("kill process: %s" % process_name)

    except BaseException as e:
        pass


def get_process_id_by_process_name(name):
    process_id_list = []

    if platform.system() == "Windows":

        for proc in psutil.process_iter():
            process_name = str(proc.name)
            if process_name.__contains__(name):
                process_id = process_name.split("(pid=")[1].split(",")[0]
                if process_id not in process_id_list:
                    process_id_list.append(process_id)
    else:
        process_ids = subprocess.check_output("pgrep node", shell=True, universal_newlines=True)
        process_id_list = process_ids.split()

    return process_id_list


def start_appium(testcase=None, appium_log_path=None, appium_server_ip=None, appium_server_port=None):
    if appium_server_ip is None:
        appium_server_ip = getattr(settings, 'appium_server_default_ip', APPIUM_SERVER_DEFAULT_IP)

    if appium_server_port is None:
        appium_server_port = getattr(settings, 'appium_server_default_port', APPIUM_SERVER_DEFAULT_PORT)

    if appium_log_path is None:
        # if appium_log_path is None then save the appium's log into project_path/output/appium.log
        appium_log_path = project_info.project_path + os.sep + "output" + os.sep + "appium.log"
        if not os.path.exists(appium_log_path):
            with open(appium_log_path):
                pass

    if issubclass(testcase, android_testcase.AndroidTestCase):
        uuid = testcase.android_desired_capabilities["deviceName"]
        device_id = testcase.android_desired_capabilities["deviceName"]

        webview_version = get_webview_version(device_id=device_id)
        chromedriver_path = get_chromedriver_path_by_webview_version(webview_version)

        if chromedriver_path is None:
            # appium_start_cmd = "appium --log %s --log-level warn:debug --address %s --port %s  -cp %s  -bp %s -U %s &" % (
            appium_start_cmd = "appium --log %s --log-level warn:debug --address %s --port %s -bp %s -U %s " % (
                appium_log_path,
                appium_server_ip,
                appium_server_port,
                # str(int(appium_server_port) + APPIUM_CALLBACK_PORT_INCREMENT),
                str(int(appium_server_port) + APPIUM_BOOTSTRAP_PORT_INCREMENT),
                uuid
            )
        else:
            # appium_start_cmd = "appium --log %s --log-level warn:debug --address %s --port %s  -cp %s  -bp %s -U %s &" % (
            appium_start_cmd = "appium --log %s --log-level warn:debug --address %s --port %s -bp %s -U %s --chromedriver-executable %s " % (
                appium_log_path,
                appium_server_ip,
                appium_server_port,
                # str(int(appium_server_port) + APPIUM_CALLBACK_PORT_INCREMENT),
                str(int(appium_server_port) + APPIUM_BOOTSTRAP_PORT_INCREMENT),
                uuid,
                chromedriver_path
            )

        if hasattr(settings, "ANDROID_OPTION"):
            for opt in settings.ANDROID_OPTION:
                if type(opt) is str:
                    appium_start_cmd = appium_start_cmd + " " + opt + " "
                else:
                    raise Exception("settings.ANDROID_OPTION must be a string list!")

        appium_start_cmd += " &"
        print(appium_start_cmd)

    else:
        # todo: or 2. if got the port already be used, than change the port automaticlly ?
        try:
            os.system("kill -9 %s" % get_pid_by_port(APPIUM_SERVER_DEFAULT_PORT))
        except BaseException:
            pass

        appium_start_cmd = "appium --log %s --ipa %s --port %s --command-timeout 100 &" % (
            appium_log_path, appium_server_ip, appium_server_port)

    print("*********** try to start appium server: %s" % appium_start_cmd)
    process = subprocess.Popen(appium_start_cmd, shell=True)
    print(process.pid)  # this pid is not the node process's id. so here no-useful

    if not is_appium_running(appium_log_path, timeout=IS_APPIUM_RUNNING_TIMEOUT):
        raise Exception("start appium server failed after %s seconds" % IS_APPIUM_RUNNING_TIMEOUT)
    else:
        print(
            "appium server started successfully, you can check the appium log: %s" % appium_log_path)
        process_id_list = get_process_id_by_process_name("node")

        for process_id in process_id_list:
            if process_id not in process_id_testcase_dict.keys():
                testcase.node_process_pid = process_id
                process_id_testcase_dict[process_id] = testcase
                testcase.process_id_testcase_dict = process_id_testcase_dict
                return


def is_appium_log_generated(log_path):
    if os.path.exists(log_path):

        with open(log_path) as appium_log_file:
            for line in appium_log_file.readlines():
                if line.__contains__("[Appium] Appium REST http interface listener "):
                    return True
    return False


def is_appium_running(log_path, timeout=None):
    """
    check whether the appium server is running
    here check the information from the appium log

    Args:
        log_path: check the appium server info from log_path
        timeout: an integer for the max time to check, default value is None.

    Returns:
        False if not running
        True if running
    """

    if timeout is None:
        return is_appium_log_generated(log_path)

    elif isinstance(timeout, (int, float)):
        if timeout <= 0:
            raise ValueError("timeout should be a number and large than 0")
        else:
            process_running_flag = False
            index = 0

            while index < timeout and process_running_flag is False:
                index += 1
                time.sleep(DEFAULT_SLEEP_TIME)
                process_running_flag = is_appium_log_generated(log_path)

            return process_running_flag


def get_pid_by_port(port_num):
    try:
        system_info = subprocess.check_output("lsof -i:%s" % port_num, shell=True, universal_newlines=True)

        for info in system_info.splitlines():
            if info.endswith("(LISTEN)"):
                pid = info.split()[1]
                return pid
    except BaseException:
        pass


def get_android_webview_package(device_id):
    try:
        cmd_str = "adb -s {device_id} shell dumpsys package | grep webview | grep Package".format(device_id=device_id)
        # cmd_str = "adb -s {device_id} shell dumpsys package | grep chrome | grep Package".format(device_id=device_id)
        system_info = subprocess.check_output(cmd_str, shell=True, universal_newlines=True)
        print(system_info)

        for info in system_info.splitlines():
            if info.strip().startswith("Package ["):
                package_name = info.split("[")[1].split("]")[0]
                print("package name: %s  for device: %s " % (package_name, str(device_id)))
                return package_name
    except BaseException:
        pass


def get_webview_version(device_id):
    try:
        # todo: package name: should be com.android.chrome or com.google.android.webview ???
        package_webview_name = get_android_webview_package(device_id)
        package_webview_name = "com.android.chrome"

        cmd_str = "adb -s {device_id} shell dumpsys package {package_name} | grep versionName".format(
            device_id=device_id, package_name=package_webview_name)
        system_info = subprocess.check_output(cmd_str, shell=True, universal_newlines=True)
        print(system_info)

        for info in system_info.splitlines():
            if info.strip().startswith("versionName="):
                webview_version = info.split("versionName=")[1].split(".")[0]
                print("webveiw version: %s for device: %s" % (webview_version, device_id))
                return webview_version
    except BaseException:
        pass


def get_chromedriver_path_by_webview_version(webview_version):
    # todo refact
    pass
    # try:
    #     chromedriver_path = None
    #     print(project_info)
    #     chromedriver_path = project_info.project_path + os.sep + "chrome_drivers"
    #     if os.path.exists(chromedriver_path):
    #         webview_version_list = list(chromedriver_path_dict.keys())
    #
    #         if webview_version not in webview_version_list:
    #             print(
    #                 "webview_version: %s is not in chromedriver_path_dict.keys(), check the chrome/webview version on the Android device!" % webview_version)
    #             webview_version_list.sort()
    #             webview_version = webview_version_list[-1]
    #             chromedriver_path = chromedriver_path_dict[webview_version]
    #             print(
    #                 "now set chrome_version: %s to the llintest version number which defined in chromedriver_path_dict.keys()...." % webview_version)
    #         else:
    #             chromedriver_path = chromedriver_path_dict[webview_version]
    #     else:
    #         print("there are no chrome_drivers path found!")
    #         chromedriver_path = None
    # except BaseException:
    #     traceback.print_exc()
    # finally:
    #     return chromedriver_path


if __name__ == "__main__":
    get_pid_by_port(4723)
