import os
dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))

if os.path.exists(os.path.join(dir_path, "BASE_VERSION")):
    with open(os.path.join(dir_path, "BASE_VERSION")) as version_file:
        __version__ = version_file.readline()
elif os.path.exists(os.path.join(dir_path, "..", "..", "BASE_VERSION")):
    with open(os.path.join(dir_path, "..", "..", "BASE_VERSION")) as version_file:
        __version__ = version_file.readline()

else:
    __version__ = "unknown"