import glob
import sys

from os.path import dirname, basename, isfile, join

sys.path.append(dirname(__file__))
sys.path.extend([file for file in glob.glob(join(dirname(__file__), "*.py")) if not file.endswith("__init__.py")])