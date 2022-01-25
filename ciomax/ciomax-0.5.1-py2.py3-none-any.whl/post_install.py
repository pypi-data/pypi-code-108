# from __future__ import unicode_literals


import os
import sys
import errno

# /users/me/Conductor/ciomax
PKG_DIR = os.path.dirname(os.path.abspath(__file__))
PKGNAME = os.path.basename(PKG_DIR)
PLATFORM = sys.platform
# LOCALAPPDATA = os.environ.get(  "LOCALAPPDATA", "%LOCALAPPDATA%")

LOCALAPPDATA =  os.path.expanduser(os.path.join("~","AppData", "Local"))

STUB_SCRIPT_FILENAME = "ciomax_stub.ms"

MENU_SCRIPT_PATH = os.path.join(PKG_DIR, "Conductor.ms").replace('\\', r'\\')


def main():

    content = """
-- Calls the Conductor 3DS Max plugin. Do not modify.
(
  include "{}"
)
""".format(MENU_SCRIPT_PATH)

    if not PLATFORM in ["win32"]:
        sys.stderr.write("Unsupported platform: {}\n".format(PLATFORM))
        manual_instructions(content)
        sys.exit(0)

    path = os.path.join(LOCALAPPDATA, "Autodesk", "3dsMax")
    if not os.path.exists(path):
        sys.stderr.write(
            "No 3ds startup directory in your local app data: {}\n".format(PLATFORM))
        manual_instructions(content)
        sys.exit(0)

    for folder in [f for f in os.listdir(path) if f.startswith("20")]:
        path = os.path.join(LOCALAPPDATA, "Autodesk", "3dsMax",
                            folder, "ENU", "scripts", "startup")

        ensure_directory(path)

        stub_file = os.path.join(path, STUB_SCRIPT_FILENAME)
        try:
            with open(stub_file, "w") as fn:
                fn.write(content)
        except BaseException:
            pass

def manual_instructions(content):
    msg = """MANUAL INSTRUCTIONS:
    If you are installing on a platform other than Windows, 
    or you haven't yet installed 3ds Max, then you'll need 
    to create a startup file manually so that 3ds Max can 
    find the Conductor menu script.

    The contents of the startup file should be something like:
    {}
    (You may need to adjust for Windows directory mapping.)

    The file should be placed here:
    {}
    """.format(content, os.path.join("%LOCALAPPDATA%", "Autodesk", "3dsMax", "<3ds-max-version>", "ENU", "scripts", "startup",STUB_SCRIPT_FILENAME))

    sys.stdout.write(msg)


def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise


if __name__ == '__main__':
    main()
