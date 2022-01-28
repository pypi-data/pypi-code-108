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
    from jomiel.keygen.app import App
    from jomiel import __version__

    pkg_name = "jomiel"  # shares the pkg_resources
    data_dir = "%s.data" % pkg_name

    App(
        package_name=pkg_name,
        package_data_dir=data_dir,
        config_module="%s.cache" % pkg_name,
        no_default_config_files=True,
        # no_version_long_option=True,
        no_print_config_option=True,
        no_config_file_option=True,
        no_logger_options=True,
        version=__version__,
    ).run()


if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 tw=72 expandtab:
