import errno
import pathlib

def check_dump_folder():
    dumpPath = pathlib.PosixPath("~/mikrotik_html_dumps")
    dumpPath = dumpPath.expanduser()
    try:
        pathlib.Path.mkdir(
            dumpPath,
            parents=True,
            exist_ok=True
        )
    except OSError as e:
        if e.errno == errno.EEXIST:
            print("Directory exists! - Continuing!")
        else:
            raise
    #change to directory
    return dumpPath