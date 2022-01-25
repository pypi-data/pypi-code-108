import os
import sys
from shutil import copy2
 
CIO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILENAME = "clarisse.env"
PLATFORM = sys.platform

def main():
    sys.stdout.write("Running Clarisse post install script\n")

    if not PLATFORM in ["darwin", "win32", "linux"]:
        sys.stderr.write("Unsupported platform: {}".format(PLATFORM))
        sys.exit(1)
    transform_env_files()
    sys.stdout.write("Completed Clarisse post install script\n")

    sys.exit(0)


def transform_env_files():
    """Find env files below the Clarisse dir and add a Conductor location variable."""
    if PLATFORM == "darwin":
        root = os.path.expanduser(os.path.join("~","Library","Preferences","Isotropix","Clarisse"))
    elif PLATFORM == "linux":
        root = os.path.expanduser(os.path.join("~",".isotropix","clarisse"))
    else:  # windows
        root =  os.path.expanduser(os.path.join("~","AppData", "Roaming", "Isotropix", "Clarisse"))
    sys.stdout.write("Found Clarisse preferences folder: {}\n".format(root))
    transform_tree(root)


def transform_tree(root):
    """Walk the filesystem and transform env files."""
    root, dirs, filenames = next(os.walk(root), (None,[], []))
    for fn in filenames:
        if fn == CONFIG_FILENAME:
            transform_env_file(os.path.join(root, fn))
    if dirs:
        for dr in dirs:
            transform_tree(os.path.join(root, dr))

def transform_env_file(env_file):
    sys.stdout.write("Write CIO additions to file: {}\n".format(env_file))
    lines = []
    real_env_file = os.path.realpath(env_file)
    bak = "{}.bak".format(real_env_file)

    with open(real_env_file) as fn:
        for line in fn:
            if not line.startswith("CIO_DIR"):
                lines.append(line.rstrip())

    cio_line =  "CIO_DIR={}".format(CIO_DIR) 
    lines.append(cio_line)

    msg = "Couldn't backup this Clarisse env file. '{}'\n".format(real_env_file)
    msg += "Please paste in the following line manually.\n"
    msg += "{}\n".format(cio_line)
    msg += "#" * 30
    msg += "\n"


    sys.stdout.write("Attempt to backup env file: {}\n".format(real_env_file))
    try:
        os.remove(bak)
    except OSError:
        pass

    try:
        os.rename(real_env_file, bak)
    except OSError:
        sys.stdout.write(msg)
        return
        
    try:
        with open(real_env_file, "w") as fn:
            for line in lines:
                fn.write("{}\n".format(line))
    except OSError:
        sys.stdout.write(msg)
        os.rename(bak, real_env_file)
        return
        
    sys.stdout.write("Wrote Conductor additions to : {}\n".format(env_file))

if __name__ == '__main__':
    main()
