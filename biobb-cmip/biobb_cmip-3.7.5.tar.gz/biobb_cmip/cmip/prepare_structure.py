#!/usr/bin/env python3

"""Module containing the PrepareStructure class and the command line interface."""
import os
import argparse
import shutil
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
# Write the CMIP PDB
from biobb_cmip.cmip.common import write_cmip_pdb
# Dani's methods using a topology and a PDB file
from biobb_cmip.cmip.common import get_topology_cmip_elements_canonical
from biobb_cmip.cmip.common import get_topology_charges
# JLG methods using just the PDB file
from biobb_cmip.cmip.common import get_pdb_charges
from biobb_cmip.cmip.common import get_pdb_cmip_elements_canonical


class PrepareStructure(BiobbObject):
    """
    | biobb_cmip PrepareStructure
    | Generate a CMIP suitable PDB input.
    | Generate a CMIP suitable PDB input from a common PDB file or a Topology + PDB file.

    Args:
        input_pdb_path (str): Path to the input PDB file. File type: input. `Sample file <TODO>`_. Accepted formats: pdb (edam:format_1476).
        input_topology_path (str) (Optional): Path to the input topology path. File type: input. `Sample file <TODO>`_. Accepted formats: zip (edam:format_3987), top (edam:format_3880), psf (edam:format_3882), prmtop (edam:format_3881).
        output_pdb_path (str): Path to the output PDB file. File type: output. `Sample file <TODO>`_. Accepted formats: pdb (edam:format_1476).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - ("cmip/cmip:latest") Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_working_dir** (*str*) - (None) Path to the internal CWD in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the container shell.


    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_cmip.cmip.prepare_structure import prepare_structure
            prop = { }
            prepare_structure(input_pdb_path='/path/to/myStructure.pdb',
                              output_pdb_path='/path/to/newStructure.pdb',
                              properties=prop)

    Info:
        * wrapped_software:
            * name: CMIP cmip
            * version: 2.7.0
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_pdb_path: str, output_pdb_path: str, input_topology_path: str = None, properties: dict = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)

        # Input/Output files
        self.io_dict = {
            "in": {"input_pdb_path": input_pdb_path, "input_topology_path": input_topology_path},
            "out": {"output_pdb_path": output_pdb_path}
        }


        # Check the properties
        self.check_properties(properties)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Cmip <cmip.cmip.PrepareStructure>` object."""
        # Setup Biobb
        if self.check_restart(): return 0

        #######################################

        # Dani's method
        if self.io_dict['in']['input_topology_path']:
            top_file = self.io_dict['in']['input_topology_path']
            if self.io_dict['in']['input_topology_path'].lower().endswith(".zip"):
                # Unzip topology to topology_out
                top_file = fu.unzip_top(zip_file=self.io_dict['in']['input_topology_path'], out_log=self.out_log)
                top_dir = str(Path(top_file).parent)

            charges_list = get_topology_charges(top_file)
            elements_list = get_topology_cmip_elements_canonical(top_file)

        # JLG's method
        else:
            charges_list = get_pdb_charges(self.io_dict['in']['input_pdb_path'])
            elements_list = get_pdb_cmip_elements_canonical(self.io_dict['in']['input_pdb_path'])

        write_cmip_pdb(self.io_dict['in']['input_pdb_path'],
                       self.io_dict['out']['output_pdb_path'],
                       charges_list,
                       elements_list)

        ###################################
        # Remove temporal files
        self.remove_tmp_files()

        return 0


def prepare_structure(input_pdb_path: str, output_pdb_path: str, input_topology_path: str = None,
                      properties: dict = None, **kwargs) -> int:
    """Create :class:`Cmip <cmip.cmip.PrepareStructure>` class and
    execute the :meth:`launch() <cmip.cmip.PrepareStructure.launch>` method."""

    return PrepareStructure(input_pdb_path=input_pdb_path, output_pdb_path=output_pdb_path,
                            input_topology_path=input_topology_path, properties=properties,
                            **kwargs).launch()


def main():
    parser = argparse.ArgumentParser(description="Wrapper of the cmip prepare_structure module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pdb_path', required=True)
    required_args.add_argument('--output_pdb_path', required=True)
    parser.add_argument('--input_topology_path', required=False)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    prepare_structure(input_pdb_path=args.input_pdb_path, output_pdb_path=args.output_pdb_path,
                      input_topology_path=args.input_topology_path, properties=properties)


if __name__ == '__main__':
    main()
