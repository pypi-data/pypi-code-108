import sys
import subprocess
import locale
import os

PYTHONW_EXE = sys.executable.replace(
    "xes_py_helper.exe", "pythonw.exe").replace("python.exe", "pythonw.exe")

def get_user_libs_path():
    '''
    :return 获取用户目录的学而思直播地址
    '''
    user_en = locale.getpreferredencoding()
    if user_en == "cp936":
        user_lib_path = os.path.expanduser(r"~\学而思直播\code\site-packages")
    else:
        user_lib_path = os.path.expanduser(r"~\xescode\site-packages")
    return user_lib_path

USER_LIB_PATH = get_user_libs_path()

def create_python_process(args):
    try:
        process_res = subprocess.check_output(args)
        return {
            "state": True,
            "output": process_res
        }
    except Exception as e: 
        print(e)
        return {
            "state": False,
            "output": str(e)
        }

