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
    """Initiates the logging subsystem."""
    from jomiel.cache import logger_paths, opts
    from jomiel_kore.log import log_init

    (logger_file, idents) = log_init(
        logger_paths,
        ident_must_exist=opts.logger_ident,
    )

    from jomiel.log import lg

    lg().debug(
        "subsys/log: configuration file loaded from '%s'",
        logger_file,
    )

    if opts.logger_idents:
        from jomiel_kore.app import dump_logger_identities

        dump_logger_identities(
            idents,
            opts.logger_idents_verbose,
        )

    if opts.plugin_list:
        # Prevent INFO lines from being printed to the output with
        # --plugin-list.
        from logging import WARNING

        lg().level = WARNING

    lg().info("log subsystem initiated")


# vim: set ts=4 sw=4 tw=72 expandtab:
