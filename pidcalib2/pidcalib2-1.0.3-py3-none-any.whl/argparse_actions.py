###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import argparse

from logzero import logger as log

from . import markdown_table, pid_data


class ListValidAction(argparse.Action):
    """Class that overrides required parameters and prints valid configs."""

    def __call__(self, parser, namespace, values, option_string=None):

        if values == "configs" or values.endswith(".json"):
            header = ["Sample", "Magnet", "Particle"]
            table = markdown_table.MarkdownTable(header)

            # Print configs from the default samples.json if no file specified
            if values == "configs":
                values = None

            for entry in pid_data.get_calibration_samples(values).keys():
                try:
                    sample, magnet, particle = entry.split("-")
                    magnet = magnet[3:].lower()
                    table.add_row([sample, magnet, particle])
                except ValueError:
                    # Skip group entries like "Turbo18-MagUp"
                    pass

            table.print()

        elif values == "aliases":
            table_pid = markdown_table.MarkdownTable(["Alias", "Variable"])
            for alias, var in pid_data.aliases.items():
                table_pid.add_row([alias, var])
            table_pid.print()
        else:
            log.error(f"'{values}' is not a known keyword for list-valid")
            raise KeyError

        parser.exit()
