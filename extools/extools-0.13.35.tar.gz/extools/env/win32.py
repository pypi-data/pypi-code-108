import sys
import os
from pathlib import Path

def setup_win32api_env():
    site_packages = Path(__file__).parent / ".." / ".."
    sys.path += [
        str(site_packages / 'win32'),
        str(site_packages / 'win32' / 'lib'),
        str(site_packages / 'Pythonwin'), ]
    os.add_dll_directory(str(site_packages / 'pywin32_system32'))
    return True

def send_to_printer(filename, printer=None):
    if not setup_win32api_env():
        return False

    try:
        import win32api
    except ImportError as e:
        return False

    win32api.ShellExecute(
        0,
        "print",
        str(filename),
        #
        # If this is None, the default printer will
        # be used anyway.
        #
        # '/d:"Microsoft Print to PDF"',
        '/d:"{}"'.format(printer),
        ".",
        0)

    return True
