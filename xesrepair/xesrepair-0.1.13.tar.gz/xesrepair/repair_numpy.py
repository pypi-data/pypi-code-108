from xesrepair.common import PYTHONW_EXE, USER_LIB_PATH, create_python_process
def check():
    try:
        import numpy 
        print(numpy.__version__)
        return {"state": True}
    except Exception as e:
        print(e)
        return {"state": False, "reason": str(e)}

def repair():
    check_res = check()
    if not check_res["state"]:
        # 先卸载
        uninstall_args = [PYTHONW_EXE, "-m", "pip", "uninstall", "-y", "numpy"]
        create_python_process(uninstall_args)
        # 再安装
        install_args = [PYTHONW_EXE, "-m", "pip", "install",'--target', USER_LIB_PATH, 'numpy', '--no-cache-dir', '--no-warn-script-location', "--index-url", 'https://mirrors.aliyun.com/pypi/simple/', "--upgrade" ]
        create_python_process(install_args)
        check_res = check()
    return check_res
