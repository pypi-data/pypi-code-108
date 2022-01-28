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


def load(ns_pkg):
    """Load all plugin packages from the given package dir.

    Args:
        ns_pkg (obj) - the imported package namespace to to search

    Returns:
        dict: Containing the imported plugin modules

    """

    def iter_namespace():
        return iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    from importlib import import_module
    from pkgutil import iter_modules

    return {
        name: import_module(name)
        for finder, name, ispkg in iter_namespace()
        if ispkg
    }


# vim: set ts=4 sw=4 tw=72 expandtab:
