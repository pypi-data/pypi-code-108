"""Main entry point"""
import os
import sys


if sys.argv[0].endswith("__main__.py"):
    import os.path
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + "-m HTest"


if len(sys.argv) < 2:
    print("\n" + "----------------------------------------------------------------------" + "\n" +
          "Ran 0 test in 0.000s\n" + "\n" + "OK")

else:
    file_suffix = os.path.splitext(sys.argv[1])[1].lower()  # 获取文件后缀名
    file = os.path.join(os.getcwd(), sys.argv[1])  # 获取执行文件
    print(file)
    if file_suffix in ['.yaml', '.yml']:
        if os.path.isfile(sys.argv[1]):
            from testcase import get_data
            get_data(file)
            from run_yaml import test_yaml
            test_yaml()
        else:
            print("E" + "\n" + "======================================================================" + "\n" +
                  "ERROR: " + sys.argv[1] + "\n" + "FileNotFoundError: No file named %s" % sys.argv[1].split("/")[-1])
            print("\n" + "----------------------------------------------------------------------" + "\n" +
                  "Ran 1 test in 0.000s\n" + "\n" + "FAILED (errors=1)")
    elif file_suffix == '.py':
        from unittest.main import main
        main(module=None)
    else:
        print("ModuleNotFoundError: No module named %s" % sys.argv[1])
