from upyog.imports import *
from upyog.os.read_files import *
from upyog.utils import *
from upyog.cli import Param as P, call_parse


__all__ = ["move_files", "cleanup_duplicates"]


@call_parse
def move_files(
    i: P("Input folders to move the files from", str, nargs="+", metavar="INP") = None,
    o: P("Path to the output folders", str) = None,
    move: P("Move files (desctructively)", action="store_true") = False,
):
    """
            --------- FILE MOVER ---------

    Move files from an arbitrary number of input folders to a _single_ output folder.

    The input folders are scanned recursively.
    If the output folder doesn't exist, it is created
    """
    recurse = True
    files = flatten([get_files(p, recurse=recurse) for p in i])
    out_dir = Path(o)
    if not out_dir.exists():
        rich.print(f"Creating output folder: {out_dir}")
        out_dir.mkdir(exist_ok=True, parents=True)

    mover = shutil.move if move else shutil.copy

    for file in track(files, "Moving Files..."):
        mover(str(file), str(out_dir))


@call_parse
def cleanup_duplicates(
    i: P("Single input folder that is to be cleaned up", str) = None,
    t: P(
        "An arbitrary number of target folders that contain duplicate files that are to be removed from the input folder `--i`",
        str,
        nargs="+",
    ) = None,
):
    """
            --------- DUPLICATE REMOVER ---------

    This program scans the _names_ of the files in the input and target folders
    recursively, and removes all the files from the `input` folder that exist in
    `target` folders

    If input folder has the following files:
    ├── input-folder
    │   ├── file1.jpg
    │   ├── file2.jpg
    │   └── file3.jpg

    And the target folder(s) have the following files:
    ├── target-folder-1
    │   ├── file1.jpg
    │   ├── other-random-file-1.jpg

    ├── target-folder-2
    │   ├── file2.jpg
    │   ├── other-random-file-2.jpg

    Using this program would remove `file1.jpg` and `file2.jpg` from the input folders

    Usage:
    ------

    remove-duplicates-from-folder
        --i input-folder
        --t target-folder-1   target-folder-2   ...
    """
    cleanup_path = Path(i)
    target_paths = [Path(p) for p in t]

    target_fnames = flatten([get_image_files(path) for path in target_paths])
    target_fnames = [f.stem for f in target_fnames]

    cleanup_files = get_image_files(cleanup_path)
    cleanup_fnames = [f.stem for f in cleanup_files]

    fnames_to_delete = set.intersection(set(cleanup_fnames), set(target_fnames))

    counter = 0
    for f in track(cleanup_files, "Scanning Files..."):
        if f.stem in fnames_to_delete:
            print(f"Deleting {f.name}")
            counter += 1
            f.unlink()

    print(f"Deleted {counter} files")
