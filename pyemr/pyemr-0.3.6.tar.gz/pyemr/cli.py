# pylint: disable=R0201,C0413
"""Command Line Interface"""
import argparse
import sys

import fire

from pyemr import Cli as Cli2


print("sys.argv:")
print(sys.argv)


def _additional_site_packages_are_specifie():
    """Checks if additional_site_package_paths argument is specified"""
    print("_additional_site_packages_are_specifie")
    for arg in sys.argv:
        if "additional_site_package_paths" in str(arg):
            return True
    return False


def append_additional_site_packages():
    """Appends additional sub modules."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--additional_site_package_paths",
        type=str,
        help="Site packages to pass to pass to the enviroment.",
        default="",
    )
    args, unknown = parser.parse_known_args()
    site_packages = args.additional_site_package_paths.strip().split(",")
    for path in site_packages:
        if path not in sys.path:
            sys.path.append(path)


if _additional_site_packages_are_specifie():
    print("Appending additional site packages to sys path.")
    append_additional_site_packages()


cli = Cli2()


def main():
    """ """
    fire.Fire(cli)


if __name__ == "__main__":
    main()
