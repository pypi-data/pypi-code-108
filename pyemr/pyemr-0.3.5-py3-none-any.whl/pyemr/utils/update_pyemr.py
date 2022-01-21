""""""
import os
import sys
from pathlib import Path


LATEST_PYEMR_PATH = "/pyemr"


def py_files(in_dir):
    """

    Args:
      in_dir:

    Returns:

    """
    for file_type in ["py", "sh", "Dockerfile", "txt"]:
        for path in Path(in_dir).rglob(f"*.{file_type}"):
            path = path.relative_to(in_dir)
            yield path


def copy_py_files(in_dir, out_dir):
    """

    Args:
      in_dir:
      out_dir:

    Returns:

    """
    for path in py_files(in_dir):
        in_path = f"{in_dir}/{path}"
        out_path = f"{out_dir}/{path}"
        Path(f"{out_dir}/{path.parent}").mkdir(parents=True, exist_ok=True)
        os.system(f"cp -rf {in_path} {out_path}")


def get_installed_pyemr():
    """Get the site package path of the current pyemr instillation."""
    for path in sys.path:
        if path.endswith("site-packages"):
            if os.path.isdir(f"{path}/pyemr"):
                yield f"{path}/pyemr"


def copy_self_into_site_package():
    """Copy the latest pyemr version into the instilation path."""
    for old_path in get_installed_pyemr():
        os.system(f"rm -r {old_path}")
        copy_py_files(LATEST_PYEMR_PATH, old_path)


copy_self_into_site_package()
