import sys
import os
PYTHON_PATH = sys.executable
file_path = sys.path[-1] + '/server/server.py'
os.system(f'{PYTHON_PATH} {file_path}')