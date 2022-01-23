# Import package pyocean
import pathlib
import sys
import os

package_pyocean_path = str(pathlib.Path(__file__).parent.parent.parent.absolute())
pyocean_pkg = os.path.join(package_pyocean_path, "pyocean")
sys.path.append(package_pyocean_path)

from multirunnable.persistence.file.file import CsvFileFormatter
import importlib


CsvFileFormatter()

# spam_spec = importlib.util.find_module(
#     name="CsvFileFormatter",
#     package="pyocean.persistence.file.file")
# __package = importlib.import_module(name=".persistence.file.file", package="pyocean")
__package = importlib.import_module(name="pyocean", package=".persistence.file.file")
print(f"__package: {__package}")
__class = getattr(__package, "CsvFileFormatter")
print(f"__class: {__class}")

# print(f"Spam spec: {spam_spec}")


