# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import argparse

from sympathy.utils import log


class SympathyParserBuilder:
    def __init__(self, using_gui):
        self._using_gui = using_gui
        self.description = (
            f'run Sympathy in {"GUI" if using_gui else "CLI"} mode')

    def add_arguments(self, parser):
        # Filename is a positional argument.
        parser.add_argument(
            'filename', action='store', nargs='?', default=None,
            help='file containing workflow.')
        parser.add_argument(
            '--exit-after-exception',
            action='store', type=int,
            default=int(not self._using_gui),
            choices=[0, 1],
            help='exit after uncaught exception occurs in a signal handler')
        parser.add_argument(
            '-L', '--loglevel', nargs='+', action=log.LogLevelAction,
            metavar=('LOGGER', 'LEVEL'),
            default={},
            help='a logger configuration with a logger name and a level '
                 '(e.g. -L app.stats warning). This argument can be repeated.')
        parser.add_argument(
            '-N', '--node-loglevel',
            action=log.LogLevelAction, default="4",
            choices="012345", help=argparse.SUPPRESS)
        parser.add_argument(
            '--num-worker-processes',
            action='store', type=int, default=0,
            help='number of python worker processes\n'
                 '(0) use system number of CPUs')
        parser.add_argument(
            '-I', '--inifile', action='store', default=None,
            help='settings ini-file to use instead of the default')
        parser.add_argument(
            '--environment-credentials',
            metavar='PREFIX',
            action='store',
            help='read credential secrets from environment variables '
                 'starting with PREFIX that are encoded as json lists, '
                 'e.g, PREFIX["secret","foo"]={"secret":"bar"}.')

        if not self._using_gui:
            docs_group = parser.add_argument_group()

            docs_group.add_argument(
                '--generate-docs',
                action='store_true', default=None,
                help=argparse.SUPPRESS)

            docs_group.add_argument(
                '--docs-library-dir',
                help=argparse.SUPPRESS)

            docs_group.add_argument(
                '--docs-output-dir',
                help=argparse.SUPPRESS)

            docs_group.add_argument(
                '--docs-exclude-code-links',
                action='store_true',
                help=argparse.SUPPRESS)

        parser.add_argument(
            '--nocapture', action='store_true', default=False,
            help=('disable capturing of node output and send it directly '
                  'to stdout/stderr.'))


GuiParserDesc = SympathyParserBuilder(True)
CliParserDesc = SympathyParserBuilder(False)
