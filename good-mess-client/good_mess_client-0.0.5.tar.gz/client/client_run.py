import sys
import os
PYTHON_PATH = sys.executable
file_path = sys.path[-1] + '/client/client.py'
os.system(f'{PYTHON_PATH} {file_path}')