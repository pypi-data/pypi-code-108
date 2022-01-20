import os
import sys
import zipfile

if ('LD_LIBRARY_PATH' not in os.environ or "ORACLE_HOME" not in os.environ):
    resourcesPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'DB', 'resources')
    if (sys.platform == "win32"):
        if ("instantclient_windows" not in os.listdir(resourcesPath)):
            with zipfile.ZipFile(os.path.join(resourcesPath, "instantclient_windows.zip")) as windowsZip:
                windowsZip.extractall(resourcesPath)
        os.environ["ORACLE_HOME"] = os.path.join(resourcesPath, "instantclient_linux")
        os.environ["LD_LIBRARY_PATH"] = os.path.join(os.environ.get("ORACLE_HOME"), "lib")
        os.environ["PATH"] = os.environ.get("PATH") + ":" + os.path.join(os.environ.get("ORACLE_HOME"), "lib")
    elif (sys.platform == "linux"):
        if ("instantclient_linux" not in os.listdir(resourcesPath)):
            with zipfile.ZipFile(os.path.join(resourcesPath, "instantclient_linux.zip")) as linuxZip:
                linuxZip.extractall(resourcesPath)
            os.symlink(os.path.join(resourcesPath, "instantclient_linux", "lib", "libclntsh.so.21.1"), os.path.join(resourcesPath, "instantclient_linux", "lib", "libclntsh.so"))
        os.environ["ORACLE_HOME"] = os.path.join(resourcesPath, "instantclient_linux")
        os.environ["LD_LIBRARY_PATH"] = os.path.join(os.environ.get("ORACLE_HOME"), "lib")
        os.environ["PATH"] = os.environ.get("PATH") + ":" + os.path.join(os.environ.get("ORACLE_HOME"), "lib")
    # if (sys.platform == 'win32'):
    #     os.environ["PATH"] = os.environ.get("PATH") + ";" + os.path.join(os.environ.get("ORACLE_HOME"), "lib")
    # else:
    #     os.environ["PATH"] = os.environ.get("PATH") + ":" + os.path.join(os.environ.get("ORACLE_HOME"), "lib")
    if ("--clean" in sys.argv):
        sys.argv.remove("--clean")
    elif ('-c' in sys.argv):
        sys.argv.remove("--clean")
    print(os.environ["ORACLE_HOME"])
    os.execv(sys.executable, ['python3'] + [os.path.abspath(sys.argv[0])] + sys.argv[1:])
