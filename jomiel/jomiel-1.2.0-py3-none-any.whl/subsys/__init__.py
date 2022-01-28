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
    """Initiates the application subsystems."""
    from jomiel.subsys import log, hypertext, plugin, broker

    log.init()
    plugin.init()
    hypertext.init()
    broker.init()

    from jomiel.log import lg

    lg().info("exit normally")


# vim: set ts=4 sw=4 tw=72 expandtab:
