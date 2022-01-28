#
# jomiel
#
# Copyright
#  2019 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""


def dump_plugins():
    """Dumps plugin details to the stdout."""

    def foreach_plugin():
        """Repeat for each found plugin.

        Returns:
            a dict containing the plugin data

        """
        namespaces = {}
        for nspace in plugin_handlers:
            namespaces[nspace] = [
                handler.name for handler in plugin_handlers[nspace]
            ]
        return namespaces

    yaml = {"plugins": foreach_plugin()}

    from jomiel_kore.app import dump_as_yaml

    dump_as_yaml(yaml)


# vim: set ts=4 sw=4 tw=72 expandtab:
