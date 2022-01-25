# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).


"""Holds the logic for installing bamboolib's lab-/nbextensions."""


from bamboolib.setup._extensions import (
    install_extensions,
    install_nbextensions,
    install_labextensions,
)


USAGE = """Usage: python -m bamboolib COMMAND
Command options:
  install_extensions      installs both notebook and lab extensions (if possible)
  install_nbextensions    installs Jupyter Notebook extensions only
  install_labextensions   installs JupyterLab extensions only
"""

VALID_COMMANDS = ["install_extensions", "install_nbextensions", "install_labextensions"]


if __name__ == "__main__":
    import sys

    # python -m bamboolib install_extensions => sys.argv = ['path/to/bamboolib/__main__.py', 'install_extensions']
    if not (len(sys.argv) == 2 and sys.argv[1] in VALID_COMMANDS):
        print(USAGE)
        sys.exit(-1)

    command = sys.argv[1]
    if command == "install_extensions":
        install_extensions()
    elif command == "install_nbextensions":
        install_nbextensions()
    else:
        install_labextensions()
