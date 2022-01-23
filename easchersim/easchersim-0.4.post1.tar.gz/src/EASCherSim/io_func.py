# BSD 3-Clause License
#
# Copyright (c) 2021, Austin Cummings
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# TODO: make Showerfile actually configurable, requires calculation of X_0 and energy of shower file
# TODO: Re-write onfiguration parser

''' IO Functions

.. autosummary::
   :toctree:
   :recursive:

   CORSIKA_Shower_Reader
   average_CORSIKA_profile
   read_config

'''

from rich.console import Console
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

import configparser as cp
import numpy as np
import io

'''
root_found = True
try:
    from ROOT import TFile, TTree, TH1D, vector
except ImportError:
    print("The root application is not available! If you want to have root output please install.")
    root_found = False
'''
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files


class IO:
    """root IO class
    """
    def __init__(self, file_name='CherSim.root'):
        self.__vec_time = vector("TH1D")()
        self.__vec_ang = vector("TH1D")()
        self.create_root_file(file_name)

    def create_root_file(self, filename):
        self.__file = TFile(filename, 'recreate')
        self.__tcher_ph = TTree("cherPhProp", "Cherenkov Photon Properties")
        self.__tshower = TTree("showerProp", "Shower Properties")

        # create branches for tshower
        self.__eng = np.zeros(1, dtype=float)
        self.__zen = np.zeros(1, dtype=float)
        self.__startalt = np.zeros(1, dtype=float)

        self.__tshower.Branch("energy", self.__eng, 'eng/D')
        self.__tshower.Branch("zenith", self.__zen, 'zen/D')
        self.__tshower.Branch("startalt", self.__startalt, 'startalt/D')

        # define histograms
        histo_w = TH1D()
        histo_r = TH1D()
        histo_t_off = TH1D()
        histo_ang_off = TH1D()

        # set branch for histograms
        self.__tcher_ph.Branch("wavelength", 'TH1D', histo_w)
        self.__tcher_ph.Branch("distance", 'TH1D', histo_r)
        self.__tcher_ph.Branch("time_offset", 'TH1D', histo_t_off)
        self.__tcher_ph.Branch("angle_offset", 'TH1D', histo_ang_off)
        self.__tcher_ph.Branch("time_dist", self.__vec_time)
        self.__tcher_ph.Branch("angle_dist", self.__vec_ang)

    def write_shower_prop(self, energy, zenith, start):
        print("Write Shower Prop")

        # add shower properties
        self.__eng[0] = energy
        self.__zen[0] = zenith
        self.__startalt[0] = start
        self.__tshower.Fill()

    def write_cher_ph_prop(self, cher_ph):
        print("Write Photon Prop")

        num_wl_bin = len(cher_ph["w_grid"]) - 1
        num_dist_bin = len(cher_ph["r_bins"]) - 1
        num_time_bin = len(cher_ph["time_bins"]) - 1
        num_ang_bin = len(cher_ph["angle_bins"]) - 1

        # define histograms
        histo_w = TH1D("wl", "wavelength", num_wl_bin, cher_ph["w_grid"])
        histo_r = TH1D("r", "distance", num_dist_bin, cher_ph["r_bins"])
        histo_t_off = TH1D("t_off", "time offset",
                           num_dist_bin, cher_ph["r_bins"])
        histo_ang_off = TH1D("ang_off", "angle offset",
                             num_dist_bin, cher_ph["r_bins"])
        histo_t = [TH1D("t_dist_" + str(i), "time_dist_" + str(i),
                        num_time_bin, cher_ph["time_bins"]) for i in range(num_dist_bin)]
        histo_ang = [TH1D("ang_dist_" + str(i), "angle_dist_" + str(i),
                          num_ang_bin, cher_ph["angle_bins"]) for i in range(num_dist_bin)]

        # fill histograms
        for wl_bin, counts in enumerate(cher_ph["w_counts"]):
            histo_w.SetBinContent(wl_bin + 1, counts)
        for r_bin, counts in enumerate(cher_ph["r_counts"]):
            histo_r.SetBinContent(r_bin + 1, counts)
            histo_t_off.SetBinContent(r_bin + 1, cher_ph["lower_times"][r_bin])
            histo_ang_off.SetBinContent(r_bin + 1, cher_ph["lower_angles"][r_bin])
            for t_bin, counts_t in enumerate(cher_ph["time_counts"][r_bin]):
                histo_t[r_bin].SetBinContent(t_bin + 1, counts_t)
            for ang_bin, counts_ang in enumerate(cher_ph["angle_counts"][r_bin]):
                histo_ang[r_bin].SetBinContent(ang_bin + 1, counts_ang)

        self.__tcher_ph.SetBranchAddress("wavelength", histo_w)
        self.__tcher_ph.SetBranchAddress("distance", histo_r)
        self.__tcher_ph.SetBranchAddress("angle_offset", histo_ang_off)
        self.__tcher_ph.SetBranchAddress("time_offset", histo_t_off)
        self.__vec_time.assign(histo_t)
        self.__vec_ang.assign(histo_ang)
        self.__tcher_ph.Fill()

    def close_root(self):
        self.__tshower.Write("", TFile.kOverwrite)
        self.__tcher_ph.Write("", TFile.kOverwrite)
        self.__file.Close()


def is_float(s):
    """Determines if an input value is a float

    Parameters
    ----------
    s : str
        input string

    Returns
    -------
    Bollean
        True: if string is float, False otherwise
    """

    try:
        float(s)
        return True
    except ValueError:
        return False


def CORSIKA_Shower_Reader(filename):
    """Reads in longitudinal charged particle profiles (.long files) generated by CORSIKA simulations

    Parameters
    ----------
    filename : str
        CORSIKA .long file path

    Returns
    -------
    ArrayLike
        longitudial chaged particle profile of showers array of lists (depth, num electrons)
    """
    # Initialize an array to contain all the simulated showers and arrays to contain the depths (g/cm^2) and particle content for each shower
    showers = []
    depths, electrons = [], []

    with open(filename) as f:
        # Flag for whether to output the lines which follow, initialize as false
        readout_flag = False

        # Loop through the given file line by line
        for line in f:
            if readout_flag:

                # Split the line on the " " delimiter
                data = line.split()

                # If the first value is a float, can continue
                if is_float(data[0]):
                    # Append the depth to the depth array, and the sum of electrons and positrons to the electron array
                    # If other particle types are desired:
                    # [0]: depths, [1]: gammas, [2]: electrons, [3]: positrons, [4]: anti-muons, [5]: muons, [6]: hadrons, [7]: charged particles, [8]: nuclei
                    depths.append(float(data[0]))
                    electrons.append(float(data[2]) + float(data[3]))

            # Determine if charged particle info follows.
            # CORSIKA outputs charged particle profiles, followed by energy information, so flag must switch every instance of header
            if "ELECTRONS" in line:
                # Append shower info to container array
                if len(depths) > 0:
                    showers.append([depths, electrons])

                readout_flag = not readout_flag
                # Reinitialize arrays
                depths, electrons = [], []

    showers = np.array(showers)

    return showers


def average_CORSIKA_profile(showers):
    """Calculates the average charged particle longitudinal profile from the CORSIKA data

    Parameters
    ----------
    showers : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    average_shower = np.average(showers, axis=0)

    return average_shower


def getargs():
    """Read of command line arguments

    Returns
    -------
    Namespace
        returns commandline arguments
    """
    cli = argparse.ArgumentParser()
    cli.add_argument(
        "--config",
        type=str,
        help="File containing simulation configurations",
        required=True
    )

    args = cli.parse_args()
    return args


def read_config(cfg_file):
    """Read configuration file.

    Parameters
    ----------
    cfg_file : str
        name of User config file

    Returns
    -------
    ConfigParser
        Settings for simulation (defualt & user specified)
    """
    cfg = cp.ConfigParser(allow_no_value=True,
                          converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    cfg.optionxform = lambda option: option
    # read default settings
    default_cfg = files("EASCherSim.data")/"default_conf.ini"
    cfg.read(default_cfg)

    # read user settings (overwrittes defaults)
    cfg.read(cfg_file)

    return cfg


def create_config(user_args):
    """Creates example configuration file

    Values can be specified by user via command line all not specified parameter will be default

    Parameters
    ----------
    user_args : namespace
        User inputs parsed by argparse
    """
    cfg = cp.ConfigParser()
    cfg.optionxform = lambda option: option
    cfg['shower'] = {'energy': user_args.energy,
                     'angle': f"""{user_args.angle[0]}, {user_args.angle[1]}""",
                     'distFistInteraction': user_args.distFirstInt}
    cfg['detector'] = {'altitude': user_args.det_alt}
    cfg['atmosphere'] = {'scattering': user_args.atm_scatter}
    cfg['magField'] = {'useField': user_args.mag_field}
    cfg['runSettings'] = {'useGreisenParametrization': user_args.useGreisen}
    cfg['output'] = {'name': user_args.output_name}
    cfg['output'] = {'plots': user_args.plots}

    with open(user_args.filename, 'w') as cfg_file:
        cfg.write(cfg_file)


def dump_default_conf():
    """Print default configuration to screen
    """
    cfg = cp.ConfigParser()
    # read default settings
    default_cfg = files("EASCherSim.data")/"default_conf.ini"
    cfg.read(default_cfg)
    with io.StringIO() as str_stream:
        cfg.write(str_stream)
        print(str_stream.getvalue())


def get_console(**kargs):
    if len(kargs) != 0:
        console = Console(**kargs, width=100)
    else:
        console = Console(width=100, log_path=False)
    return console


def flog(*args):
    get_console().log(*args)


def get_progress():
    text_col = TextColumn("[bold red]{task.description}", table_column=Column(ratio=1))
    bar_col = BarColumn(bar_width=40, table_column=Column(ratio=4))

    progress = Progress(text_col, bar_col, "[progress.percentage]{task.percentage:>3.0f}%",
                        TimeElapsedColumn(), console=get_console(),)
    return progress
