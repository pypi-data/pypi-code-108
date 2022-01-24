import importlib
import subprocess
import sys


def attemptImport(packagePythonName, packagePip3Name):

    def importFunction():
        return importlib.import_module(name=packagePythonName)

    try:
        return importFunction()
    except (ImportError, ModuleNotFoundError):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', packagePip3Name], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    return importFunction()
