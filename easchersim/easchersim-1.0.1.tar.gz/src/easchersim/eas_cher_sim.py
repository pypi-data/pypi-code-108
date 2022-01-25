
# The Clear BSD License
#
# Copyright (c) 2021 Austin Cummings
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted (subject to the limitations in the disclaimer
# below) provided that the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#      * Neither the name of the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

""" easchersim

.. autosummary::
   :toctree:
   :recursive:

   cli
   run

"""

import argparse
import sys
import os

import numpy as np

from . import io_func
from . import plot
from . import geometry as geo
from . import constants as const
from . import spatial_cherenkov_profile as sp_cher_prof


def cli():
    """Command line interface

    Returns
    -------
    parser Obj
        command line arguments
    """
    parser = argparse.ArgumentParser(prog='easchersim', usage='%(prog)s [OPTIONS] COMMAND [ARGS]')
    parser._optionals.title = "OPTIONS"
    subparsers = parser.add_subparsers(title='COMMANDS', dest='COMMAND', required=True)
    # run commad
    run_par = subparsers.add_parser('run',
                                    help='run easchersim for settings from configuration file',
                                    prog='easchersim run',
                                    usage='%(prog)s [OPTIONS] CONFIGFILE'
                                    )
    run_par._optionals.title = "OPTIONS"
    run_par.add_argument('filename',
                         help=argparse.SUPPRESS
                         )
    run_par.add_argument('-e', '--energy',
                         type=float,
                         dest='eng',
                         help='Set shower energy in eV'
                         )
    run_par.add_argument('-a', '--angle',
                         nargs=2,
                         metavar=("ANGLE", "GEOMETRY-DEF"),
                         dest='angle',
                         help='Set shower angle and geometry definition (viewing/emergence)'
                         )
    run_par.add_argument('-d', '--dist-first-int',
                         type=float,
                         dest='distFirstInt',
                         help='Set distance to first interaction'
                         )
    run_par.add_argument('--save-plots',
                          dest='savefig',
                          action='store_true',
                          help='Set the type of plots to be created'
                          )
    run_par.set_defaults(func=run)

    # create the configuration file
    make_cfg = subparsers.add_parser('make-config',
                                     help='Produce configuration file from default \
                                     and/or given parameters.',
                                     prog='easchersim make-config',
                                     usage='%(prog)s [OPTIONS] CONFIGFILE')
    make_cfg._optionals.title = "OPTIONS"
    make_cfg.add_argument("filename",
                          default="easchersim.cfg",
                          help=argparse.SUPPRESS)

    make_cfg.add_argument('--det-alt',
                          type=float,
                          default=33,
                          dest='det_alt',
                          help='Set detection plane altitude in km'
                          )
    make_cfg.add_argument('-e', '--energy',
                          type=float,
                          default=1.e17,
                          dest='eng',
                          help='Set shower energy in eV'
                          )
    make_cfg.add_argument('-a', '--angle',
                          nargs=2,
                          default=[0., 'viewing'],
                          metavar=("ANGLE", "GEOMETRY-DEF"),
                          dest='angle',
                          help='Set shower angle and geometry definition (viewing/emergence)'
                          )
    make_cfg.add_argument('-d', '--dist-first-int',
                          type=float,
                          default=0,
                          dest='distFirstInt',
                          help='Set distance to first interaction'
                          )
    make_cfg.add_argument('-s', '--scattering',
                          type=str,
                          choices=('yes', 'no', 'on', 'off'),
                          default='yes',
                          dest='atm_scatter',
                          help='Turn atmospheric scattering on/off'
                          )
    make_cfg.add_argument('-m', '--use-mag-field',
                          type=str,
                          choices=('yes', 'no', 'on', 'off'),
                          default='on',
                          dest='mag_field',
                          help='Turn magnetic field on/off'
                          )
    make_cfg.add_argument('-g', '--use-greisen',
                          type=str,
                          choices=('yes', 'no', 'on', 'off'),
                          default='no',
                          dest='useGreisen',
                          help='Use Greisen parametrization for longitudianal profile \
                                instead of CORSIKA file'
                          )
    make_cfg.add_argument('-o', '--output',
                          type=str,
                          default='',
                          dest='output_name',
                          help='Name of the output file. Supported formats are root, npz'
                          )
    make_cfg.add_argument('-p', '--plots',
                          type=str,
                          choices=('none', 'basic', 'general', 'all'),
                          default='general',
                          dest='plots',
                          help='Set the type of plots to be created'
                          )
    make_cfg.add_argument('--save-plots',
                          dest='savefig',
                          action='store_true',
                          help='Set the type of plots to be created'
                          )
    make_cfg.set_defaults(func=io_func.create_config)
    return parser.parse_args()


def run(user_args):
    """Perform easchersim simulation

    Main application of easchersim, performs the simulation based on settings given config file

    Parameters
    ----------
    user_args : argparse Obj
        command line arguments

    Examples
    --------
    Command line usage of the run command:
    `easchersim run my_config_file.ini`
    """
    cfg = io_func.read_config(user_args.filename)

    # Check provided configuration
    detector_altitude = cfg.getfloat('detector', 'altitude')
    if user_args.angle is None:
        geo_view = cfg.getlist('shower', 'angle')[1]
        theta = float(cfg.getlist('shower', 'angle')[0])
    else:
        geo_view = user_args.angle[1]
        theta = float(user_args.angle[0])

    if geo_view == "emergence":
        theta_D = geo.theta_D_from_theta_EE(detector_altitude, theta)
    elif geo_view == "viewing":
        theta_D = theta
    else:
        io_func.flog(f'''[bold blue]WARN:[/] You entered an unkown shower geometry ({geo_view})! \n'''
                     '''Allowed options are\n'''
                     '''   - emergence for emergence angle shower definition\n'''
                     '''   - viewing for detector viewing angle shower definition\n'''
                     '''Please change your configuration accordingly.\n''')
        sys.exit(-1)

    if user_args.distFirstInt is None:
        L_particle = cfg.getfloat('shower', 'distFistInteraction')
    else:
        L_particle = float(user_args.distFirstInt)
    ## Calculating the path lengths to the detector and the top of the atmosphere
    [L_detector, L_atmosphere] = [geo.L_from_z(z, theta_D, detector_altitude)
                                  for z in [detector_altitude, const.z_max]]

    ## Disallowing for unobservable trajectories
    if np.isnan(L_detector) or np.isnan(L_atmosphere) or L_particle > min([L_detector, L_atmosphere]):
        io_func.flog('''[bold red] ERROR: [/]EAS begins past either the detector or the atmosphere and is unobservable.''')
        # change to try next shower in the future
        sys.exit(-1)
    if user_args.eng is None:
        energy = cfg.getfloat('shower', 'energy')
    else:
        energy = float(user_args.eng)
    
    # save or not to save fig
    if user_args.savefig or cfg.getboolean('output', 'saveFigures'):
        savefig = True
    else:
        savefig = False

    # set up output file
    out_file = cfg.get('output', 'name')
    if ".root" in out_file and io_func.root_found or ".npz" in out_file:
        output = io_func.IO(out_file)
    elif".root" in out_file:
        io_func.flog('''[bold red] ERROR: [/]Output format root requested but no root install found!\n'''
                     '''Please make sure root is installed and sourced.\n'''
                     '''ROOT can be installed via cond *conda install -c conda-forge root*'''
                     )
        sys.exit(-1)
    elif out_file != '':
        io_func.flog(f'''[bold red]ERROR: {cfg.get('output', 'name')} is an unknown format.\n'''
                     '''       Please change to one of the supported formats: root, npz'''
                     )
        sys.exit(-1)
    elif out_file == '':
        io_func.flog('''[bold blue]WARN:[/] No output file will be created. \n''')
    else:
        io_func.flog(f'''Simulation result will be written to {cfg.get('output', 'name')} \n''')

    # create plot folder
    if savefig:
        i = 1
        while os.path.exists(plot.plot_out_dir):
            plot.plot_out_dir = f"plots({i})/"
            i += 1
        io_func.flog(f'''Plots will be saved in {plot.plot_out_dir[:-1]}.''')
        os.mkdir(plot.plot_out_dir)

    sim_result = sp_cher_prof.cherenkov_from_particle_profile(detector_altitude,
                                                              energy, theta_D,
                                                              L_particle, L_detector, L_atmosphere,
                                                              cfg['atmosphere'], cfg['magField'],
                                                              cfg['runSettings'],
                                                              cfg.get('output', 'plots'),
                                                              savefig
                                                              )
    if "output" in locals():
        # write shower prop
        output.write_shower_prop(energy, float(theta_D), L_particle)
        # write cher ph prop
        output.write_cher_ph_prop(sim_result)

    # new check here as previous part needs to move to loop for multiple showers
    if "output" in locals():
        output.close()


def main():
    io_func.get_console(log_time=False, log_path=False).rule("[bold blue]EASCherSim")
    args = cli()
    args.func(args)


if __name__ == "__main__":
    main()
