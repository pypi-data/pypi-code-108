#!/usr/bin/env python3

"""Module containing the Cmip class and the command line interface."""
import os
import argparse
import shutil
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_cmip.cmip.common import create_params_file
from biobb_cmip.cmip.common import params_preset


class Cmip(BiobbObject):
    """
    | biobb_cmip Titration
    | Wrapper class for the CMIP cmip module.
    | The CMIP cmip module. CMIP cmip module compute classical molecular interaction potentials.

    Args:
        input_pdb_path (str): Path to the input PDB file. File type: input. `Sample file <https://raw.githubusercontent.com/bioexcel/biobb_cmip/master/biobb_cmip/test/data/cmip/1kim_h.pdb>`_. Accepted formats: pdb (edam:format_1476).
        input_probe_pdb_path (str) (Optional): Path to the input probe file in PDB format. File type: input. Accepted formats: pdb (edam:format_1476).
        output_pdb_path (str) (Optional): Path to the output PDB file. File type: output. `Sample file <https://raw.githubusercontent.com/bioexcel/biobb_cmip/master/biobb_cmip/test/reference/cmip/1kim_neutral.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_grd_path (str) (Optional): Path to the output grid file in GRD format. File type: output. Accepted formats: grd (edam:format_2330).
        output_cube_path (str) (Optional): Path to the output grid file in cube format. File type: output. Accepted formats: cube (edam:format_2330).
        output_rst_path (str) (Optional): Path to the output restart file. File type: output. Accepted formats: txt (edam:format_2330).
        output_byat_path (str) (Optional): Path to the output atom by atom energy file. File type: output. Accepted formats: txt (edam:format_2330).
        output_log_path (str): Path to the output CMIP log file LOG. File type: output. `Sample file <https://github.com/bioexcel/biobb_cmip/raw/master/biobb_cmip/test/reference/cmip/ref_cmip.log>`_. Accepted formats: log (edam:format_2330).
        input_vdw_params_path (str) (Optional): Path to the CMIP input Van der Waals force parameters, if not provided the CMIP conda installation one is used ("$CONDA_PREFIX/share/cmip/dat/vdwprm"). File type: input. Accepted formats: txt (edam:format_2330).
        input_params_path (str) (Optional): Path to the CMIP input parameters file. File type: input. Accepted formats: txt (edam:format_2330).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **execution_type** (*str*) - ("mip_pos") Default options for the params file, each one creates a different params file. Values: mip_pos (MIP O+  Mehler Solmajer dielectric), mip_neg (MIP O-  Mehler Solmajer dielectric), mip_neu (MIP Oxygen Mehler Solmajer dielectric), solvation (Solvation & MEP), energy (Docking Interaction energy calculation. PB electrostatics), docking (Docking Mehler Solmajer dielectric), docking_rst (Docking from restart file).
            * **params** (*dict*) - ({}) CMIP options specification.
            * **cmip_path** (*str*) - ("cmip") Path to the CMIP cmip executable binary.
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

            from biobb_cmip.cmip.cmip import cmip
            prop = { 'cmip_path': 'cmip' }
            cmip(input_pdb_path='/path/to/myStructure.pdb',
                      output_pdb_path='/path/to/newStructure.pdb',
                      output_log_path='/path/to/newStructureLog.log',
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

    def __init__(self, input_pdb_path: str, input_probe_pdb_path: str = None, output_pdb_path: str = None,
                 output_grd_path: str = None, output_cube_path: str = None, output_rst_path: str = None,
                 output_byat_path: str = None, output_log_path: str = None, input_vdw_params_path: str = None,
                 input_params_path: str = None, properties: dict = None, **kwargs) -> None:

        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)

        self.combined_params_path = properties.get('combined_params_path', 'params')

        # Input/Output files
        self.io_dict = {
            "in": {"input_pdb_path": input_pdb_path, "input_probe_pdb_path": input_probe_pdb_path,
                   "input_vdw_params_path": input_vdw_params_path, "input_params_path": input_params_path},
            "out": {"output_pdb_path": output_pdb_path, "output_grd_path": output_grd_path,
                    "output_cube_path": output_cube_path, "output_rst_path": output_rst_path,
                    "output_byat_path": output_byat_path, "output_log_path": output_log_path}
        }

        # Properties specific for BB
        self.cmip_path = properties.get('cmip_path', 'cmip')
        self.execution_type = properties.get('execution_type', 'mip_pos')
        self.params = {k: str(v) for k, v in properties.get('params', dict()).items()}

        if not self.io_dict['in'].get('input_vdw_params_path'):
            self.io_dict['in']['input_vdw_params_path'] = f"{os.environ.get('CONDA_PREFIX')}/share/cmip/dat/vdwprm"
        self.io_dict['in']['combined_params_path'] = properties.get('combined_params_path', 'params')

        # Check the properties
        self.check_properties(properties)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Cmip <cmip.cmip.Cmip>` object."""
        tmp_files = []

        # Setup Biobb
        if self.check_restart(): return 0

        # Check if output_pdb_path ends with ".pdb" and does not contain underscores
        if self.io_dict['out']['output_pdb_path']:
            if (not self.io_dict['out']['output_pdb_path'].endswith('.pdb')) or ("_" in str(Path(self.io_dict['out']['output_pdb_path']).name)):
                fu.log(f"ERROR: output_pdb_path ({self.io_dict['out']['output_pdb_path']}) name must end in .pdb and not contain underscores", out_log, self.global_log)
                raise ValueError(f"ERROR: output_pdb_path ({self.io_dict['out']['output_pdb_path']}) name must end in .pdb and not contain underscores")

        combined_params_dir = fu.create_unique_dir()
        self.io_dict['in']['combined_params_path'] = create_params_file(
            output_params_path=str(Path(combined_params_dir).joinpath(self.io_dict['in']['combined_params_path'])),
            input_params_path=self.io_dict['in'].get('input_params_path'),
            params_preset_dict=params_preset(execution_type=self.execution_type),
            params_properties_dict=self.params)

        self.stage_files()


        self.cmd = [self.cmip_path,
               '-i', self.stage_io_dict['in']['combined_params_path'],
               '-vdw', self.stage_io_dict['in']['input_vdw_params_path'],
               '-hs', self.stage_io_dict['in']['input_pdb_path']]

        if self.stage_io_dict["in"].get("input_probe_pdb_path") and Path(
                self.io_dict["in"].get("input_probe_pdb_path")).exists():
            self.cmd.append('-pr')
            self.cmd.append(self.stage_io_dict["in"].get("input_probe_pdb_path"))

        if self.stage_io_dict["out"].get("output_pdb_path"):
            self.cmd.append('-outpdb')
            self.cmd.append(self.stage_io_dict['out']['output_pdb_path'])

        if self.stage_io_dict["out"].get("output_grd_path"):
            self.cmd.append('-grdout')
            self.cmd.append(self.stage_io_dict["out"]["output_grd_path"])

        if self.stage_io_dict["out"].get("output_cube_path"):
            self.cmd.append('-cube')
            self.cmd.append(self.stage_io_dict["out"]["output_cube_path"])

        if self.stage_io_dict["out"].get("output_rst_path"):
            self.cmd.append('-rst')
            self.cmd.append(self.stage_io_dict["out"]["output_rst_path"])

        if self.stage_io_dict["out"].get("output_byat_path"):
            self.cmd.append('-byat')
            self.cmd.append(self.stage_io_dict["out"]["output_byat_path"])

        if self.stage_io_dict["out"].get("output_log_path"):
            self.cmd.append('-o')
            self.cmd.append(self.stage_io_dict["out"]["output_log_path"])


        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # CMIP removes or adds a .pdb extension from pdb output name
        if self.io_dict['out'].get('output_pdb_path'):
            output_pdb_path = self.io_dict['out'].get('output_pdb_path')
            if self.container_path:
                output_pdb_path = str(Path(self.stage_io_dict["unique_dir"]).joinpath(Path(self.io_dict['out'].get('output_pdb_path')).name))

            if Path(output_pdb_path[:-4]).exists():
                shutil.move(output_pdb_path[:-4], self.io_dict['out'].get('output_pdb_path'))
            elif Path(output_pdb_path + ".pdb").exists():
                shutil.move(output_pdb_path + ".pdb", self.io_dict['out'].get('output_pdb_path'))


        # Replace "ATOMTM" tag for "ATOM  "
        output_pdb_path = self.io_dict['out'].get('output_pdb_path')
        if output_pdb_path:
            with open(output_pdb_path) as pdb_file:
                list_pdb_lines = pdb_file.readlines()
            with open(output_pdb_path, 'w') as pdb_file:
                for line in list_pdb_lines:
                    pdb_file.write(line.replace('ATOMTM', 'ATOM  '))



        # Remove temporal files
        self.tmp_files.extend([combined_params_dir])
        self.remove_tmp_files()

        return self.return_code


def cmip(input_pdb_path: str, input_probe_pdb_path: str = None, output_pdb_path: str = None,
         output_grd_path: str = None, output_cube_path: str = None, output_rst_path: str = None,
         output_byat_path: str = None, output_log_path: str = None,
         input_vdw_params_path: str = None, input_params_path: str = None,
         properties: dict = None, **kwargs) -> int:
    """Create :class:`Cmip <cmip.cmip.Cmip>` class and
    execute the :meth:`launch() <cmip.cmip.Cmip.launch>` method."""

    return Cmip(input_pdb_path=input_pdb_path, input_probe_pdb_path=input_probe_pdb_path, output_pdb_path=output_pdb_path,
                output_grd_path=output_grd_path, output_cube_path=output_cube_path, output_rst_path=output_rst_path,
                output_byat_path=output_byat_path, output_log_path=output_log_path,
                input_vdw_params_path=input_vdw_params_path, input_params_path=input_params_path,
                properties=properties, **kwargs).launch()


def main():
    parser = argparse.ArgumentParser(description="Wrapper of the CMIP cmip module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pdb_path', required=True)
    parser.add_argument('--input_probe_pdb_path', required=False)
    parser.add_argument('--output_pdb_path', required=False)
    parser.add_argument('--output_grd_path', required=False)
    parser.add_argument('--output_cube_path', required=False)
    parser.add_argument('--output_rst_path', required=False)
    parser.add_argument('--output_byat_path', required=False)
    parser.add_argument('--output_log_path', required=False)
    parser.add_argument('--input_vdw_params_path', required=False)
    parser.add_argument('--input_params_path', required=False)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    cmip(input_pdb_path=args.input_pdb_path, input_probe_pdb_path=args.input_probe_pdb_path, output_pdb_path=args.output_pdb_path,
         output_grd_path=args.output_grd_path, output_cube_path=args.output_cube_path, output_rst_path=args.output_rst_path,
         output_byat_path=args.output_byat_path, output_log_path=output_log_path,
         input_vdw_params_path=args.input_vdw_params_path, input_params_path=args.input_params_path,
         properties=properties)


if __name__ == '__main__':
    main()
