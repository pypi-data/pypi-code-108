"""
Core post install script. 

setup.py likes to change the shebang in commandline scripts it installs. It replaces it with an
explicit path to the python that ran setup. This can be a problem if it was set with a python that
has since been removed. Therefore, we will reset it to #!/usr/bin/env.

https://stackoverflow.com/questions/50557963/why-does-pip-install-seem-to-change-the-interpreter-line-on-some-machines
"""
import os
import sys

CIO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH_EXECUTABLE = os.path.join(CIO_DIR, "bin", "conductor")
PLATFORM = sys.platform

def main():
    if not PLATFORM.startswith(("darwin", "linux")):
        sys.exit(0)

    with open(SH_EXECUTABLE) as f:
        lines = ["#!/usr/bin/env python3\n"] + [line for line in f.readlines() if not line.strip().startswith("#!") ]

    with open(SH_EXECUTABLE, "w") as f:
        f.writelines(lines)

    sys.stdout.write("Completed Core post install.\n")

if __name__ == "__main__":
    main()
