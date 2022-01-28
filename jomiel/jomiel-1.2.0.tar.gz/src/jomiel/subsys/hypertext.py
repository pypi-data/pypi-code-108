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


def init():
    """Initiates the HTTP subsystem."""

    from jomiel.cache import opts
    from jomiel.log import lg

    if opts.http_debug:
        from jomiel.hypertext import be_verbose

        be_verbose()
        lg().debug("enable http logging")

    lg().info("http subsystem initiated")


# vim: set ts=4 sw=4 tw=72 expandtab:
