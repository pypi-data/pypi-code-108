# Copyright 2019-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# 20210501 Not yet used. WIP for migrating from argh to click.

# """The main entry point for the :command:`atelier` command.
# """
#
# import click
#
# from atelier.setup_info import SETUP_INFO
#
# from .foreach import foreach
# from .listapps import listapps
#
# @click.group(help="""
# {}
# See https://atelier.lino-framework.org for more information.
#
# This is atelier version {}.
# """.format(SETUP_INFO['description'], SETUP_INFO['version']))
# def main():
#     pass
#
# main.add_command(foreach)
# main.add_command(listapps)
#
# if __name__ == '__main__':
#     main()
