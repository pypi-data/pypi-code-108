# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import shutil
import sys
import argparse

import coveriteam.util as util
from coveriteam.interpreter.python_code_generator import generate_python_code
import logging
import coveriteam
from pathlib import Path
from coveriteam.remote_client import exec_remotely


class CoVeriTeam:
    def start(self, argv):
        self.config = self.create_argument_parser().parse_args(argv)
        str_to_prepend = ""

        if self.config.debug:
            FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
            logging.basicConfig(level=util.CVT_DEBUG_LEVEL, format=FORMAT)

        if self.config.debug_deep:
            FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
            logging.basicConfig(level=logging.DEBUG, format=FORMAT)

        if self.config.cache_dir:
            util.set_cache_directories(Path(self.config.cache_dir).resolve())
        else:
            util.set_cache_directories()

        if self.config.no_cache_update:
            util.set_cache_update(False)
        else:
            util.set_cache_update(True)

        util.set_python_processes_flag(self.config.use_python_processes)

        if self.config.clean:
            # Remove both the archive and unzip directory
            shutil.rmtree(util.INSTALL_DIR)
            shutil.rmtree(util.ARCHIVE_DOWNLOAD_PATH)
            shutil.rmtree(util.TOOL_INFO_DOWNLOAD_PATH)
            util.create_cache_directories()

        if self.config.testtool:
            from coveriteam.language.atomicactor import AtomicActor

            a = AtomicActor(self.config.input_file)
            a.print_version()
            return

        if self.config.gettool:
            from coveriteam.language.atomicactor import AtomicActor

            a = AtomicActor(self.config.input_file)
            return

        if self.config.inputs:
            d = {}
            for k, v in self.config.inputs:
                if k in d:
                    # It should be either a string or a list of strings.
                    d[k] = [d[k]] + [v] if isinstance(d[k], str) else d[k] + [v]
                else:
                    d[k] = v
            for k in d:
                str_to_prepend += k + " = " + repr(d[k]) + "\n"

            str_to_prepend += "from coveriteam.language.actor import Actor\n"
            data_model = (
                f'"{self.config.data_model}"' if self.config.data_model else "None"
            )
            str_to_prepend += "Actor.data_model = " + data_model + "\n"

            trusted = (
                f'"{self.config.trust_tool_info}"'
                if self.config.trust_tool_info
                else "False"
            )
            str_to_prepend += "Actor.trust_tool_info = " + trusted + "\n"

        if self.config.input_file:
            if self.config.remote:
                exec_remotely(self.config)
                return
            """"CVL file is provided."""
            generated_code = str_to_prepend + generate_python_code(
                self.config.input_file
            )
            if self.config.generate_code:
                print(generated_code)
            else:
                exec(generated_code, globals())  # noqa S102

    def create_argument_parser(self):
        """
        Create a parser for the command-line options.
        @return: an argparse.ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            prog="coveriteam",
            fromfile_prefix_chars="@",
            description="""Execute a program written in CoVeriLang.
               Command-line parameters can additionally be read from a file if file name prefixed with '@' is given as argument.
               """,
        )
        parser.add_argument(
            "--version", action="version", version=f"{coveriteam.__version__}"
        )

        parser.add_argument(
            "--get-tool",
            dest="gettool",
            action="store_true",
            default=False,
            help="Download the tool archive and initialize an atomic actor for the given YML file configuration.",
        )

        parser.add_argument(
            "--tool-info",
            dest="testtool",
            action="store_true",
            default=False,
            help="Test the given YML file configuration by executing the tool for version.",
        )

        parser.add_argument(
            "input_file",
            metavar="INPUT_FILE",
            help="The program written in CoVeriLang or a YML configuration if testing a tool.",
        )
        parser.add_argument(
            "--input",
            action="append",
            type=lambda kv: kv.split("="),
            dest="inputs",
            help="Inputs to the CoVeriLang program provided in the form of key=val.",
        )

        parser.add_argument(
            "--gen-code",
            dest="generate_code",
            action="store_true",
            default=False,
            help="Flag to generate python code from the cvl file.",
        )

        parser.add_argument(
            "--clean",
            dest="clean",
            action="store_true",
            default=False,
            help="Clean the tmp directory, which contains the extracted archives of the atomic actors.",
        )

        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            default=False,
            help="Set the logging to debug for CoVeriTeam. Only logs debug (and higher) messages from CoVeriTeam",
        )

        parser.add_argument(
            "--debug-deep",
            dest="debug_deep",
            action="store_true",
            default=False,
            help="Set the logging to debug globally. Also logs debug (and higher) messages from BenchExec.",
        )

        parser.add_argument(
            "--cache-dir", metavar="CACHE_DIR", help="Path to the cache."
        )

        parser.add_argument(
            "--remote",
            dest="remote",
            action="store_true",
            default=False,
            help="Execute CoVeriTeam remotely.",
        )

        parser.add_argument(
            "--verbose",
            dest="verbose",
            action="store_true",
            default=False,
            help="Flag to print verbose output. At the moment supported only for remote execution.",
        )

        parser.add_argument(
            "--data-model",
            metavar="DATA_MODEL",
            help="Data model of the program under analysis."
            "Please choose ILP32 for 32 bit architecture, and LP64 for 64 bit."
            "Default value is ILP32.",
            type=str,
            choices={"ILP32", "LP64"},
        )

        parser.add_argument(
            "--trust-tool-info",
            dest="trust_tool_info",
            action="store_true",
            default=False,
            help="Trust the tool info modules. This will load them without a container.",
        )

        parser.add_argument(
            "--no-cache-update",
            dest="no_cache_update",
            action="store_true",
            default=False,
            help="Do not update the cache. Only use tools available in the cache. If tools are not available, then CoVeriTeam simply fails.",
        )

        parser.add_argument(
            "--use-python-processes",
            dest="use_python_processes",
            action="store_true",
            default=False,
            help="Execute portfolio using python processes instead of using MPI (even if MPI is available). Relevant if executing portfolio using only one machine.",
        )
        return parser


def main(argv=None):
    args = argv or sys.argv
    CoVeriTeam().start(args[1:])


if __name__ == "__main__":
    main()
