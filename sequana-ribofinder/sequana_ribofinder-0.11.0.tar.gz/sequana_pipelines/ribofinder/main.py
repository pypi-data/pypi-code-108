# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
import sys
import os
import argparse
import shutil
import subprocess

from sequana_pipetools.options import *
from sequana_pipetools.options import before_pipeline
from sequana_pipetools.misc import Colors
from sequana_pipetools.info import sequana_epilog, sequana_prolog
from sequana_pipetools import SequanaManager
from sequana import logger

col = Colors()

NAME = "ribofinder"


class Options(argparse.ArgumentParser):
    def __init__(self, prog=NAME, epilog=None):
        usage = col.purple(sequana_prolog.format(**{"name": NAME}))
        super(Options, self).__init__(usage=usage, prog=prog, description="",
            epilog=epilog,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        # add a new group of options to the parser
        so = SlurmOptions()
        so.add_options(self)

        # add a snakemake group of options to the parser
        so = SnakemakeOptions(working_directory=NAME)
        so.add_options(self)

        so = InputOptions()
        so.add_options(self)

        so = GeneralOptions()
        so.add_options(self)

        pipeline_group = self.add_argument_group("pipeline_general")
        pipeline_group.add_argument("--aligner", dest="aligner",
            choices=['bowtie1'], default='bowtie1',
            help= "a mapper in bowtie")
        pipeline_group.add_argument("--rRNA-feature",
            default="rRNA",
            help="""Feature name corresponding to the rRNA to be identified for QCs""")
        pipeline_group.add_argument("--rRNA-file",
            default=None,
            help="""If you already have the rRNA file, just provide it""")
        pipeline_group.add_argument("--genbank-file",
            default=None,
            help="""genbank. if provided, do not provide gff""")
        pipeline_group.add_argument("--gff-file",
            default=None,
            help="""If provided, do not provide genbank""")
        pipeline_group.add_argument("--reference-file",
            default=None,
            help="""The required referenceto fetch features into""")


        self.add_argument("--run", default=False, action="store_true",
            help="execute the pipeline directly")

    def parse_args(self, *args):
        args_list = list(*args)
        if "--from-project" in args_list:
            if len(args_list)>2:
                msg = "WARNING [sequana]: With --from-project option, " + \
                        "pipeline and data-related options will be ignored."
                print(col.error(msg))
            for action in self._actions:
                if action.required is True:
                    action.required = False
        options = super(Options, self).parse_args(*args)
        return options


def main(args=None):

    if args is None:
        args = sys.argv

    # whatever needs to be called by all pipeline before the options parsing
    before_pipeline(NAME)

    # option parsing including common epilog
    options = Options(NAME, epilog=sequana_epilog).parse_args(args[1:])

    # the real stuff is here
    manager = SequanaManager(options, NAME)

    # create the beginning of the command and the working directory
    manager.setup()

    # fill the config file with input parameters
    if options.from_project is None:
        cfg = manager.config.config

        # --------------------------------------------------------- general
        cfg.general.aligner = options.aligner

        cfg.general.rRNA_feature = options.rRNA_feature
        if options.rRNA_file:
            cfg.general.rRNA_file = os.path.abspath(options.rRNA_file)
        if options.genbank_file:
            cfg.general.genbank_file = os.path.abspath(options.genbank_file)
        if options.gff_file:
            cfg.general.gff_file = os.path.abspath(options.gff_file)
        if options.reference_file:
            cfg.general.reference_file = os.path.abspath(options.reference_file)

        if options.reference_file is None and options.rRNA_file is None:
            logger.error("You must provide a rRNA file or a reference_file")
            sys.exit(1)

        if options.reference_file:
            logger.info("checking your input GFF file and rRNA feature if provided")
            if options.genbank_file:
                from sequana.genbank import GenBank
                gbk = GenBank(options.genbank_file)
            if options.genbank_file is None and options.gff_file is None:
                logger.error("Most probably you want to provide an annotation (genbank-file or gff-file)")
                sys.exit(0)

        # ----------------------------------------------------  others
        cfg.input_pattern = options.input_pattern
        cfg.input_directory = os.path.abspath(options.input_directory)
        cfg.input_readtag = options.input_readtag

        manager.exists(cfg.input_directory)
    # finalise the command and save it; copy the snakemake. update the config
    # file and save it.
    manager.teardown()

    if options.run:
        subprocess.Popen(["sh", '{}.sh'.format(NAME)], cwd=options.workdir)

if __name__ == "__main__":
    main()
