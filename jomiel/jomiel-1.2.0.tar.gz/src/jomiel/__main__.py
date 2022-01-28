#
# jomiel
#
# Copyright
#  2019-2020 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""


def main():
    """main"""
    # from sys import path

    # [print(p) for p in path]

    from jomiel.app import App
    from jomiel import __version__

    pkg_name = "jomiel"
    data_dir = f"{pkg_name}.data"

    App(
        package_name=pkg_name,
        package_data_dir=data_dir,
        config_module=f"{pkg_name}.cache",
        version=__version__,
    ).run()


if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 tw=72 expandtab:
