#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel TARS model to generate charge by ionization."""

import logging
import math
import typing as t  # noqa: F401
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from typing_extensions import Literal

from pyxel.detectors import Detector
from pyxel.models.charge_generation.cosmix.plotting import PlottingCosmix
from pyxel.models.charge_generation.cosmix.simulation import Simulation
from pyxel.models.charge_generation.cosmix.util import (  # , load_histogram_data
    interpolate_data,
    read_data,
)
from pyxel.util import temporary_random_state

# from astropy import units as u
# TODO: write basic test to check inputs, private function, documentation


# @validators.validate
# @config.argument(name='', label='', units='', validate=)
@temporary_random_state
def run_tars(
    detector: Detector,
    simulation_mode: t.Optional[
        Literal["cosmic_ray", "cosmics", "radioactive_decay", "snowflakes"]
    ] = None,
    running_mode: t.Optional[
        Literal["stopping", "stepsize", "geant4", "plotting"]
    ] = None,
    particle_type: t.Optional[Literal["proton", "alpha", "ion"]] = None,
    initial_energy: t.Optional[t.Union[int, float, Literal["random"]]] = None,
    particle_number: t.Optional[int] = None,
    incident_angles: t.Optional[t.Tuple[str, str]] = None,
    starting_position: t.Optional[t.Tuple[str, str, str]] = None,
    # step_size_file: str = None,
    # stopping_file: str = None,
    spectrum_file: t.Optional[str] = None,
    seed: t.Optional[int] = None,
    ionization_energy: float = 3.6,
    progressbar: bool = True,
) -> None:
    """TARS model.

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    simulation_mode: literal
        Simulation mode: ``cosmic_rays``, ``radioactive_decay``.
    running_mode: literal
        Mode: ``stopping``, ``stepsize``, ``geant4``, ``plotting``.
    particle_type:
        Type of particle: ``proton``, ``alpha``, ``ion``.
    initial_energy: int or float or literal
        Kinetic energy of particle, set `random` for random.
    particle_number: int
        Number of particles.
    incident_angles: tuple of str
        Incident angles: ``(α, β)``.
    starting_position: tuple of str
        Starting position: ``(x, y, z)``.
    spectrum_file: str
        Path to input spectrum
    seed: int, optional
        Random seed.
    ionization_energy: float
        Mean ionization energy of the semiconductor lattice.
    progressbar: bool
        Progressbar.
    """
    if simulation_mode is None:
        raise ValueError("TARS: Simulation mode is not defined")
    if running_mode is None:
        raise ValueError("TARS: Running mode is not defined")
    if particle_type is None:
        raise ValueError("TARS: Particle type is not defined")
    if particle_number is None:
        raise ValueError("TARS: Particle number is not defined")
    if spectrum_file is None:
        raise ValueError("TARS: Spectrum is not defined")

    if initial_energy is None:
        initial_energy = "random"  # TODO

    if incident_angles is None:
        incident_angle_alpha, incident_angle_beta = ("random", "random")
    else:
        incident_angle_alpha, incident_angle_beta = incident_angles

    if starting_position is None:
        start_pos_ver, start_pos_hor, start_pos_z = ("random", "random", "random")
    else:
        start_pos_ver, start_pos_hor, start_pos_z = starting_position

    tars = TARS(
        detector=detector,
        simulation_mode=simulation_mode,
        particle_type=particle_type,
        initial_energy=initial_energy,
        particle_number=particle_number,
        incident_angle_alpha=incident_angle_alpha,
        incident_angle_beta=incident_angle_beta,
        start_pos_ver=start_pos_ver,
        start_pos_hor=start_pos_hor,
        start_pos_z=start_pos_z,
        ionization_energy=ionization_energy,
        progressbar=progressbar,
    )

    # tars.set_simulation_mode(simulation_mode)
    # tars.set_particle_type(particle_type)                # MeV
    # tars.set_initial_energy(initial_energy)              # MeV
    # tars.set_particle_number(particle_number)            # -
    # tars.set_incident_angles(incident_angles)            # rad
    # tars.set_starting_position(starting_position)        # um
    tars.set_particle_spectrum(Path(spectrum_file))

    if running_mode == "stopping":
        # tars.run_mod()          ########
        raise NotImplementedError
        # tars.set_stopping_power(stopping_file)
        # tars.run()
    elif running_mode == "stepsize":
        tars.set_stepsize()
        tars.run()
    elif running_mode == "geant4":
        tars.set_geant4()
        tars.run()
    elif running_mode == "plotting":

        plot_obj = PlottingCosmix(tars, save_plots=True, draw_plots=True)

        # # # plot_obj.plot_flux_spectrum()

        #
        # # plot_obj.plot_step_dist()
        # # plot_obj.plot_step_cdf()

        # plot_obj.plot_tertiary_number_cdf()
        # plot_obj.plot_tertiary_number_dist()

        # plot_obj.plot_step_size_histograms(normalize=True)
        # plot_obj.plot_secondary_spectra(normalize=True)
        #
        # # plot_obj.plot_edep_per_step()
        # # plot_obj.plot_edep_per_particle()

        # plot_obj.plot_charges_3d()

        plot_obj.plot_flux_spectrum()

        # plot_obj.plot_gaia_bam_vs_sm_electron_hist(normalize=True)
        # plot_obj.plot_old_tars_hist(normalize=True)

        plot_obj.plot_gaia_vs_gras_hist(normalize=True)

        # plot_obj.plot_track_histogram(tars.sim_obj.track_length_list)
        # plot_obj.plot_track_histogram(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-track_length_lst_per_event.npy',
        #     normalize=True)

        # plot_obj.plot_electron_hist(tars.sim_obj.e_num_lst_per_event, normalize=True)

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_2\tars-e_num_lst_per_step.npy',
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_2\tars-p_energy_lst_per_event.npy',

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-e_num_lst_per_event.npy',
        #                             title='all e per event', hist_bins=500, hist_range=(0, 15000))

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-sec_lst_per_event.npy',
        #                             title='secondary e per event', hist_bins=500, hist_range=(0, 15000))
        #
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-ter_lst_per_event.npy',
        #                             title='tertiary e per event', hist_bins=500, hist_range=(0, 15000))

        # plot_obj.plot_spectrum_hist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_6\tars-p_energy_lst_per_event.npy')
        # plot_obj.plot_spectrum_hist(r'C:\dev\work\pyxel\tars-p_energy_lst_per_event.npy')

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-e_num_lst_per_event.npy',
        #                             title='all e per event', hist_bins=500, hist_range=(0, 15000))
        #
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-sec_lst_per_event.npy',
        #                             title='secondary e per event', hist_bins=400, hist_range=(0, 2000))
        #
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-ter_lst_per_event.npy',
        #                             title='tertiary e per event', hist_bins=500, hist_range=(0, 5000))

        # plot_obj.plot_spectrum_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-p_energy_lst_per_event.npy')

        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_6\tars-alpha_lst_per_event.npy')
        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\tars-alpha_lst_per_event.npy')

        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_6\tars-beta_lst_per_event.npy')

        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\tars-beta_lst_per_event.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)\Raw data\alpha.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)\Raw data\beta.npy')

        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)(17-08-2016_13h51)\Raw data\alpha.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)(17-08-2016_13h51)\Raw data\beta.npy')

        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel/models/charge_generation/tars/data/validation/Results-20180404T121902Z-001/
        # Results/10000 events from random protons CREME96 (step=0.5)(16-08-2016_15h56)\Raw data\alpha.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\10000 events from random protons CREME96 (step=0.5)(16-08-2016_15h56)\Raw data\beta.npy')

        # todo: not implemented yet:
        # file_path = Path(__file__).parent.joinpath('data', 'inputs', 'all_elec_num_proton.ascii')
        # g4_all_e_num_hist = load_histogram_data(file_path, hist_type='electron', skip_rows=4, read_rows=1000)
        # plot_obj.plot_electron_hist(tars.sim_obj.e_num_lst_per_event, g4_all_e_num_hist, normalize=True)

        # plot_obj.plot_electron_hist(tars.sim_obj.e_num_lst_per_event,
        #                             tars.sim_obj.sec_lst_per_event,
        #                             tars.sim_obj.ter_lst_per_event, normalize=True)

        plot_obj.show()
    else:
        raise ValueError
    #
    # np.save('tars-e_num_lst_per_event.npy', tars.sim_obj.e_num_lst_per_event)
    # np.save('tars-sec_lst_per_event.npy', tars.sim_obj.sec_lst_per_event)
    # np.save('tars-ter_lst_per_event.npy', tars.sim_obj.ter_lst_per_event)
    # np.save('tars-track_length_lst_per_event.npy', tars.sim_obj.track_length_lst_per_event)
    # np.save('tars-p_energy_lst_per_event.npy', tars.sim_obj.p_energy_lst_per_event)
    # np.save('tars-alpha_lst_per_event.npy', tars.sim_obj.alpha_lst_per_event)
    # np.save('tars-beta_lst_per_event.npy', tars.sim_obj.beta_lst_per_event)
    # np.save('tars-e_num_lst_per_step.npy', tars.sim_obj.e_num_lst_per_step)

    # plot_obj = PlottingTARS(tars, save_plots=True, draw_plots=True)
    # plot_obj.plot_charges_3d()
    # plot_obj.show()


class TARS:
    """TBW."""

    def __init__(
        self,
        detector: Detector,
        simulation_mode: Literal[
            "cosmic_ray", "cosmics", "radioactive_decay", "snowflakes"
        ],
        particle_type: Literal[
            "proton", "ion", "alpha", "beta", "electron", "gamma", "x-ray"
        ],
        initial_energy: t.Union[int, float, Literal["random"]],
        particle_number: int,
        incident_angle_alpha: str,
        incident_angle_beta: str,
        start_pos_ver: str,
        start_pos_hor: str,
        start_pos_z: str,
        ionization_energy: float = 3.6,
        progressbar: bool = True,
    ):
        self.simulation_mode = simulation_mode
        self.part_type = particle_type
        self.init_energy = initial_energy
        self.particle_number = particle_number
        self.angle_alpha = incident_angle_alpha
        self.angle_beta = incident_angle_beta
        self.position_ver = start_pos_ver
        self.position_hor = start_pos_hor
        self.position_z = start_pos_z
        self.ionization_energy = ionization_energy
        self._progressbar = progressbar

        self.sim_obj = Simulation(detector)
        self.charge_obj = detector.charge
        self._log = logging.getLogger(__name__)

    # TODO: Is it still used ?
    def set_simulation_mode(
        self,
        sim_mode: Literal["cosmic_ray", "cosmics", "radioactive_decay", "snowflakes"],
    ) -> None:
        """TBW.

        :param sim_mode:
        """
        self.simulation_mode = sim_mode

    # TODO: Is it still used ?
    def set_particle_type(
        self,
        particle_type: Literal[
            "proton", "ion", "alpha", "beta", "electron", "gamma", "x-ray"
        ],
    ) -> None:
        """TBW.

        :param particle_type:
        """
        self.part_type = particle_type

    # TODO: Is it still used ?
    def set_initial_energy(
        self, energy: t.Union[int, float, Literal["random"]]
    ) -> None:
        """TBW.

        :param energy:
        """
        self.init_energy = energy

    # TODO: Is it still used ?
    def set_particle_number(self, number: int) -> None:
        """TBW.

        :param number:
        """
        self.particle_number = number

    # TODO: Is it still used ?
    def set_incident_angles(self, angles: t.Tuple[str, str]) -> None:
        """TBW.

        :param angles:
        """
        alpha, beta = angles
        self.angle_alpha = alpha
        self.angle_beta = beta

    # TODO: Is it still used ?
    def set_starting_position(self, start_position: t.Tuple[str, str, str]) -> None:
        """TBW.

        :param start_position:
        """
        position_vertical, position_horizontal, position_z = start_position
        self.position_ver = position_vertical
        self.position_hor = position_horizontal
        self.position_z = position_z

    def set_particle_spectrum(self, file_name: Path) -> None:
        """Set up the particle specs according to a spectrum.

        :param string file_name: path of the file containing the spectrum
        """
        spectrum = read_data(file_name)  # nuc/m2*s*sr*MeV
        geo = self.sim_obj.detector.geometry
        detector_area = geo.vert_dimension * geo.horz_dimension * 1.0e-8  # cm2

        spectrum[:, 1] *= 4 * math.pi * 1.0e-4 * detector_area  # nuc/s*MeV

        spectrum_function = interpolate_data(spectrum)

        lin_energy_range = np.arange(
            np.min(spectrum[:, 0]), np.max(spectrum[:, 0]), 0.01
        )
        self.sim_obj.flux_dist = spectrum_function(lin_energy_range)

        cum_sum = np.cumsum(self.sim_obj.flux_dist)
        cum_sum /= np.max(cum_sum)
        self.sim_obj.spectrum_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

    def set_stopping_power(self, stopping_file: Path) -> None:
        """TBW.

        :param stopping_file:
        """
        self.sim_obj.energy_loss_data = "stopping"
        self.sim_obj.stopping_power = read_data(stopping_file)

    def set_stepsize(self) -> None:
        """TBW."""
        self.sim_obj.energy_loss_data = "stepsize"
        self.create_data_library()

    def set_geant4(self) -> None:
        """TBW."""
        self.sim_obj.energy_loss_data = "geant4"

    def create_data_library(self) -> None:
        """TBW."""
        self.sim_obj.data_library = pd.DataFrame(
            columns=["type", "energy", "thickness", "path"]
        )

        # mat_list = ['Si']

        type_list = [
            "proton"
        ]  # , 'ion', 'alpha', 'beta', 'electron', 'gamma', 'x-ray']
        energy_list = [100.0]  # MeV
        thick_list = [40.0, 50.0, 60.0, 70.0, 100.0]  # um

        # TODO: Fix this. See issue #152
        path = Path(__file__).parent.joinpath("data", "inputs")
        filename_list = [
            "stepsize_proton_100MeV_40um_Si_10k.ascii",
            "stepsize_proton_100MeV_50um_Si_10k.ascii",
            "stepsize_proton_100MeV_60um_Si_10k.ascii",
            "stepsize_proton_100MeV_70um_Si_10k.ascii",
            "stepsize_proton_100MeV_100um_Si_10k.ascii",
        ]

        i = 0
        for pt in type_list:
            for en in energy_list:
                for th in thick_list:
                    data_dict = {
                        "type": pt,
                        "energy": en,
                        "thickness": th,
                        "path": str(Path(path, filename_list[i])),
                    }
                    new_df = pd.DataFrame(data_dict, index=[0])
                    self.sim_obj.data_library = pd.concat(
                        [self.sim_obj.data_library, new_df], ignore_index=True
                    )
                    i += 1

    def run(self) -> None:
        """TBW."""
        # print("TARS - simulation processing...\n")

        self.sim_obj.parameters(
            sim_mode=self.simulation_mode,
            part_type=self.part_type,
            init_energy=self.init_energy,
            pos_ver=self.position_ver,
            pos_hor=self.position_hor,
            pos_z=self.position_z,
            alpha=self.angle_alpha,
            beta=self.angle_beta,
            ionization_energy=self.ionization_energy,
        )

        # Get output folder and create it (if needed)
        out_path = Path("data").resolve()
        out_path.mkdir(parents=True, exist_ok=True)

        self._log.info("Save data in folder '%s'", out_path)

        for k in tqdm(
            range(self.particle_number),
            desc="TARS",
            unit=" particle",
            disable=(not self._progressbar),
        ):
            # for k in range(0, self.particle_number):
            err = None  # type: t.Optional[bool]
            if self.sim_obj.energy_loss_data == "stepsize":  # TODO
                err = self.sim_obj.event_generation()
            elif self.sim_obj.energy_loss_data == "geant4":
                err = self.sim_obj.event_generation_geant4()
            if k % 10 == 0:
                np.save(
                    f"{out_path}/tars-e_num_lst_per_event.npy",
                    self.sim_obj.e_num_lst_per_event,
                )
                np.save(
                    f"{out_path}/tars-sec_lst_per_event.npy",
                    self.sim_obj.sec_lst_per_event,
                )
                np.save(
                    f"{out_path}/tars-ter_lst_per_event.npy",
                    self.sim_obj.ter_lst_per_event,
                )
                np.save(
                    f"{out_path}/tars-track_length_lst_per_event.npy",
                    self.sim_obj.track_length_lst_per_event,
                )
                np.save(
                    f"{out_path}/tars-p_energy_lst_per_event.npy",
                    self.sim_obj.p_energy_lst_per_event,
                )
                np.save(
                    f"{out_path}/tars-alpha_lst_per_event.npy",
                    self.sim_obj.alpha_lst_per_event,
                )
                np.save(
                    f"{out_path}/tars-beta_lst_per_event.npy",
                    self.sim_obj.beta_lst_per_event,
                )

                np.save(
                    f"{out_path}/tars-e_num_lst_per_step.npy",
                    self.sim_obj.e_num_lst_per_step,
                )
                np.save(f"{out_path}/tars-e_pos0_lst.npy", self.sim_obj.e_pos0_lst)
                np.save(f"{out_path}/tars-e_pos1_lst.npy", self.sim_obj.e_pos1_lst)
                np.save(f"{out_path}/tars-e_pos2_lst.npy", self.sim_obj.e_pos2_lst)

                np.save(
                    f"{out_path}/tars-all_e_from_eloss.npy",
                    self.sim_obj.electron_number_from_eloss,
                )
                np.save(
                    f"{out_path}/tars-sec_e_from_eloss.npy",
                    self.sim_obj.secondaries_from_eloss,
                )
                np.save(
                    f"{out_path}/tars-ter_e_from_eloss.npy",
                    self.sim_obj.tertiaries_from_eloss,
                )
            if err:
                k -= 1

        size = len(self.sim_obj.e_num_lst_per_step)

        self.sim_obj.e_vel0_lst = np.zeros(size)
        self.sim_obj.e_vel1_lst = np.zeros(size)
        self.sim_obj.e_vel2_lst = np.zeros(size)

        self.charge_obj.add_charge(
            particle_type="e",
            particles_per_cluster=np.asarray(self.sim_obj.e_num_lst_per_step),
            init_energy=np.asarray(self.sim_obj.e_energy_lst),
            init_ver_position=np.asarray(self.sim_obj.e_pos0_lst),
            init_hor_position=np.asarray(self.sim_obj.e_pos1_lst),
            init_z_position=np.asarray(self.sim_obj.e_pos2_lst),
            init_ver_velocity=self.sim_obj.e_vel0_lst,
            init_hor_velocity=self.sim_obj.e_vel1_lst,
            init_z_velocity=self.sim_obj.e_vel2_lst,
        )

    def run_mod(self) -> None:
        """TBW."""
        # TODO: Use `logging`
        print("TARS - adding previous cosmic ray signals to image ...\n")

        # TODO: Use `pathlib.Path`
        out_path = "data/"
        e_num_lst_per_step = np.load(out_path + "tars-e_num_lst_per_step.npy")
        e_pos0_lst = np.load(out_path + "tars-e_pos0_lst.npy")
        e_pos1_lst = np.load(out_path + "tars-e_pos1_lst.npy")
        e_pos2_lst = np.load(out_path + "tars-e_pos2_lst.npy")

        size = len(e_num_lst_per_step)
        e_energy_lst = np.zeros(size)
        e_vel0_lst = np.zeros(size)
        e_vel1_lst = np.zeros(size)
        e_vel2_lst = np.zeros(size)

        self.charge_obj.add_charge(
            particle_type="e",
            particles_per_cluster=e_num_lst_per_step,
            init_energy=e_energy_lst,
            init_ver_position=e_pos0_lst,
            init_hor_position=e_pos1_lst,
            init_z_position=e_pos2_lst,
            init_ver_velocity=e_vel0_lst,
            init_hor_velocity=e_vel1_lst,
            init_z_velocity=e_vel2_lst,
        )
