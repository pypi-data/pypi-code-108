import re

from release_mgr.version_files.version_file import VersionFile


class SetupPy(VersionFile):
    filename = "setup.py"
    pattern = re.compile(r'(version=)[\'"][0-9]*.[0-9]*.[0-9]*[\'"]')
    replace_pattern = r'\1"{new_version}"'
