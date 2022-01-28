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
    """Initiates the plugin subsystem."""

    from jomiel.plugin import load
    import jomiel.cache as cache
    from jomiel.log import lg

    def log(text):
        """Write a new (debug) entry to the logger."""
        lg().debug("subsystem/plugin: %s", text)

    cache.plugin_packages = {}
    cache.plugin_handlers = {}

    from importlib import import_module

    namespace_packages = [import_module("jomiel.plugin.media")]

    for ns_pkg in namespace_packages:
        ns_name = ns_pkg.__name__

        cache.plugin_packages[ns_pkg] = load(ns_pkg)
        cache.plugin_handlers[ns_name] = []

        for pkg_name in cache.plugin_packages[ns_pkg]:
            module = cache.plugin_packages[ns_pkg][pkg_name]
            handler = module.Handler()

            cache.plugin_handlers[ns_name].append(handler)
            log(f"<{pkg_name}> loaded {ns_pkg}")

        num_handlers = len(cache.plugin_handlers[ns_name])
        log("<%s> cached %d handler(s)" % (ns_name, num_handlers))

    no_packages = len(cache.plugin_packages)
    log("cached %d package(s)" % no_packages)

    lg().info("plugin subsystem initiated")

    from jomiel.cache import opts, dump_plugins

    if opts.plugin_list:
        dump_plugins()


# vim: set ts=4 sw=4 tw=72 expandtab:
