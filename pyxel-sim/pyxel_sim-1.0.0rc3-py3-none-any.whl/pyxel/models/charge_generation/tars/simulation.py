#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel TARS model to generate charge by ionization."""

import subprocess
import typing as t  # noqa: F401
from bisect import bisect
from pathlib import Path

import numpy as np
import pandas as pd
from typing_extensions import Literal

from pyxel.detectors import Detector
from pyxel.models.charge_generation.cosmix.particle import Particle
from pyxel.models.charge_generation.cosmix.util import (
    load_histogram_data,
    read_data,
    sampling_distribution,
)


class Simulation:
    """Main class of the program, Simulation contain all the methods to set and run a simulation."""

    def __init__(self, detector: Detector) -> None:
        """Initialize the simulation.

        :param Detector detector: Detector object(from CCD/CMSO library) containing all the simulated detector specs
        """
        self.detector = detector
        self.simulation_mode = (
            None
        )  # type: t.Optional[Literal["cosmic_ray", "cosmics","radioactive_decay", "snowflakes"]]

        self.flux_dist = None  # type: t.Optional[np.ndarray]
        self.spectrum_cdf = None  # type: t.Optional[np.ndarray]

        self.energy_loss_data = (
            None
        )  # type: t.Optional[Literal['stopping', 'stepsize', 'geant4']]

        self.elec_number_dist = pd.DataFrame()
        self.elec_number_cdf = np.zeros((1, 2))
        self.step_size_dist = pd.DataFrame()
        self.step_cdf = np.zeros((1, 2))
        self.kin_energy_dist = pd.DataFrame()
        self.kin_energy_cdf = np.zeros((1, 2))

        self.data_library = pd.DataFrame()

        self.stopping_power = None  # type: t.Optional[np.ndarray]

        self.particle = None  # type: t.Optional[Particle]

        self.particle_type = (
            None
        )  # type: t.Optional[Literal["proton", "ion", "alpha", "beta", "electron", "gamma", "x-ray"]]
        self.initial_energy = (
            None
        )  # type: t.Optional[t.Union[int, float, Literal['random']]]
        self.position_ver = None  # type: t.Optional[str]
        self.position_hor = None  # type: t.Optional[str]
        self.position_z = None  # type: t.Optional[str]
        self.angle_alpha = None  # type: t.Optional[str]
        self.angle_beta = None  # type: t.Optional[str]
        self.step_length = (
            1.0  # fix, all the other data/parameters should be adjusted to this
        )
        self.energy_cut = 1.0e-5  # MeV
        self.ionization_energy = 3.6

        self.e_num_lst_per_step = []  # type: t.List[int]
        self.e_energy_lst = []  # type: t.List[float]
        self.e_pos0_lst = []  # type: t.List[float]
        self.e_pos1_lst = []  # type: t.List[float]
        self.e_pos2_lst = []  # type: t.List[float]
        self.e_vel0_lst = np.array([])  # type: np.ndarray
        self.e_vel1_lst = np.array([])  # type: np.ndarray
        self.e_vel2_lst = np.array([])  # type: np.ndarray

        self.electron_number_from_eloss = []  # type: t.List[int]
        self.secondaries_from_eloss = []  # type: t.List[int]
        self.tertiaries_from_eloss = []  # type: t.List[int]

        self.track_length_lst_per_event = []  # type: t.List[float]
        self.e_num_lst_per_event = []  # type: t.List[int]
        self.sec_lst_per_event = []  # type: t.List[int]
        self.ter_lst_per_event = []  # type: t.List[int]
        self.edep_per_step = []  # type: t.List[float]
        self.total_edep_per_particle = []  # type: t.List[float]
        self.p_energy_lst_per_event = []  # type: t.List[float]
        self.alpha_lst_per_event = []  # type: t.List[float]
        self.beta_lst_per_event = []  # type: t.List[float]

    def parameters(
        self,
        sim_mode: Literal["cosmic_ray", "cosmics", "radioactive_decay", "snowflakes"],
        part_type: Literal[
            "proton", "ion", "alpha", "beta", "electron", "gamma", "x-ray"
        ],
        init_energy: t.Union[int, float, Literal["random"]],
        pos_ver: str,
        pos_hor: str,
        pos_z: str,
        alpha: str,
        beta: str,
        ionization_energy: float = 3.6,
    ) -> None:
        """TBW.

        Parameters
        ----------
        sim_mode
        part_type
        init_energy
        pos_ver
        pos_hor
        pos_z
        alpha
        beta
        ionization_energy
        """
        self.simulation_mode = sim_mode
        self.particle_type = part_type
        self.initial_energy = init_energy
        self.position_ver = pos_ver
        self.position_hor = pos_hor
        self.position_z = pos_z
        self.angle_alpha = alpha
        self.angle_beta = beta
        self.ionization_energy = ionization_energy

    def find_smaller_neighbor(self, column: str, value: float) -> float:
        """TBW.

        :return:
        """
        sorted_list = sorted(
            self.data_library[column].unique()
        )  # type: t.Sequence[float]
        index = bisect(sorted_list, value) - 1
        if index < 0:
            index = 0
        return sorted_list[index]

    def find_larger_neighbor(self, column: str, value: float) -> float:
        """TBW.

        :return:
        """
        sorted_list = sorted(
            self.data_library[column].unique()
        )  # type: t.Sequence[float]
        index = bisect(sorted_list, value)
        if index > len(sorted_list) - 1:
            index = len(sorted_list) - 1
        return sorted_list[index]

    def find_closest_neighbor(self, column: str, value: float) -> float:
        """TBW.

        :return:
        """
        sorted_list = sorted(
            self.data_library[column].unique()
        )  # type: t.Sequence[float]
        index_smaller = bisect(sorted_list, value) - 1
        index_larger = bisect(sorted_list, value)

        if index_larger >= len(sorted_list):
            return sorted_list[-1]
        elif (sorted_list[index_larger] - value) < (value - sorted_list[index_smaller]):
            return sorted_list[index_larger]
        else:
            return sorted_list[index_smaller]

    def select_stepsize_data(
        self, p_type: str, p_energy: float, p_track_length: float
    ) -> Path:
        """TBW.

        :param p_type: str
        :param p_energy: float (MeV)
        :param p_track_length: float (um)
        :return:
        """
        df = self.data_library

        distance = self.find_larger_neighbor(column="thickness", value=p_track_length)
        energy = self.find_closest_neighbor(column="energy", value=p_energy)

        df_filtered = df[
            (df.type == p_type) & (df.energy == energy) & (df.thickness == distance)
        ]  # type: pd.DataFrame

        serie = df_filtered["path"]  # type: pd.Series
        filename = serie.values[0]  # type: Path

        return filename

    def set_stepsize_distribution(self, step_size_file: Path) -> None:
        """TBW.

        :param step_size_file:
        :return:
        .. warning:: EXPERIMENTAL - NOT FINSHED YET
        """
        # # step size distribution in um
        self.step_size_dist = load_histogram_data(
            step_size_file, hist_type="step_size", skip_rows=4, read_rows=10000
        )

        cum_sum = np.cumsum(self.step_size_dist["counts"])
        cum_sum /= np.max(cum_sum)
        self.step_cdf = np.stack((self.step_size_dist["step_size"], cum_sum), axis=1)

        # # tertiary electron numbers created by secondary electrons
        self.elec_number_dist = load_histogram_data(
            step_size_file, hist_type="electron", skip_rows=10008, read_rows=10000
        )

        cum_sum_2 = np.cumsum(self.elec_number_dist["counts"])
        cum_sum_2 /= np.max(cum_sum_2)
        self.elec_number_cdf = np.stack(
            (self.elec_number_dist["electron"] - 0.5, cum_sum_2), axis=1
        )

        # # secondary electron spectrum in keV
        # self.kin_energy_dist = load_histogram_data(step_size_file, hist_type='energy', skip_rows=10008, read_rows=200)
        #
        # cum_sum = np.cumsum(self.kin_energy_dist['counts'])
        # cum_sum /= np.max(cum_sum)
        # self.kin_energy_cdf = np.stack((self.kin_energy_dist['energy'], cum_sum), axis=1)

    def event_generation(self) -> bool:
        """Generate an event.

        :return:
        """
        track_left = False
        electron_number_per_event = 0
        secondary_per_event = 0
        tertiary_per_event = 0
        geo = self.detector.geometry
        ioniz_energy = self.ionization_energy  # eV

        assert self.simulation_mode is not None
        assert self.particle_type is not None
        assert self.initial_energy is not None
        assert self.spectrum_cdf is not None
        assert self.position_ver is not None
        assert self.position_hor is not None
        assert self.position_z is not None

        self.particle = Particle(
            detector=self.detector,
            simulation_mode=self.simulation_mode,
            particle_type=self.particle_type,
            input_energy=self.initial_energy,
            spectrum_cdf=self.spectrum_cdf,
            starting_pos_ver=self.position_ver,
            starting_pos_hor=self.position_hor,
            starting_pos_z=self.position_z
            # self.angle_alpha, self.angle_beta)
        )

        particle = self.particle
        assert particle.track_length is not None

        self.track_length_lst_per_event += [particle.track_length]

        if self.energy_loss_data == "stepsize":
            # data_filename = self.select_stepsize_data(particle.type, particle.energy, particle.track_length)
            data_filename = self.select_stepsize_data(particle.type, 1000.0, 40.0)
            self.set_stepsize_distribution(data_filename)
            # TODO make a stack of stepsize cdfs and do not load them more than once!!!
        # elif self.energy_loss_data == 'geant4':
        #     pass
        elif self.energy_loss_data == "stopping":
            raise NotImplementedError  # TODO: implement this

        while True:
            if particle.energy <= self.energy_cut:
                break

            # particle.energy is in MeV !
            # particle.deposited_energy is in keV !

            if self.energy_loss_data == "stepsize":
                current_step_size = sampling_distribution(self.step_cdf)  # um
                # e_kin_energy = sampling_distribution(self.kin_energy_cdf)     # keV   TODO
            # elif self.energy_loss_data == 'geant4':
            #     pass
            elif self.energy_loss_data == "stopping":
                raise NotImplementedError  # TODO: implement this

            e_kin_energy = 1.0  # TODO
            particle.deposited_energy = e_kin_energy + ioniz_energy * 1e-3  # keV

            # UPDATE POSITION OF IONIZING PARTICLES
            particle.position[0] += particle.dir_ver * current_step_size  # um
            particle.position[1] += particle.dir_hor * current_step_size  # um
            particle.position[2] += particle.dir_z * current_step_size  # um

            # check if p is still inside detector and have enough energy:
            if (
                particle.position[0] <= 0.0
                or particle.position[0] >= geo.vert_dimension
            ):
                break
            if (
                particle.position[1] <= 0.0
                or particle.position[1] >= geo.horz_dimension
            ):
                break
            if (
                particle.position[2] <= -1 * geo.total_thickness
                or particle.position[2] >= 0.0
            ):
                break
            if particle.deposited_energy >= particle.energy * 1e3:
                break

            track_left = True

            particle.energy -= particle.deposited_energy * 1e-3  # MeV

            if self.energy_loss_data == "stepsize":
                # the +1 is the original secondary electron
                electron_number = int(sampling_distribution(self.elec_number_cdf)) + 1
                # electron_number = int(e_kin_energy * 1e3 / ioniz_energy) + 1
            # elif self.energy_loss_data == 'geant4':
            #     electron_number = electron_number_vector[g4_j]
            #     g4_j += 1
            elif self.energy_loss_data == "stopping":
                raise NotImplementedError

            secondary_per_event += 1
            tertiary_per_event += electron_number - 1
            electron_number_per_event += electron_number
            self.e_num_lst_per_step.append(electron_number)

            self.e_energy_lst.append(e_kin_energy * 1e3)  # eV
            self.e_pos0_lst.append(particle.position[0])  # um
            self.e_pos1_lst.append(particle.position[1])  # um
            self.e_pos2_lst.append(particle.position[2])  # um

            self.edep_per_step.append(particle.deposited_energy)  # keV
            particle.total_edep += particle.deposited_energy  # keV

            # save particle trajectory
            particle.trajectory = np.vstack((particle.trajectory, particle.position))
        # END of loop

        if track_left:
            self.total_edep_per_particle.append(particle.total_edep)  # keV
            self.e_num_lst_per_event.append(electron_number_per_event)
            self.sec_lst_per_event.append(secondary_per_event)
            self.ter_lst_per_event.append(tertiary_per_event)

        return False

    def event_generation_geant4(self) -> bool:
        """Generate an event running a geant4 app directly.

        :return:
        """
        # error = None
        electron_number_per_event = 0
        secondary_per_event = 0
        tertiary_per_event = 0

        secondaries = 0
        tertiaries = 0

        assert self.simulation_mode is not None
        assert self.particle_type is not None
        assert self.initial_energy is not None
        assert self.spectrum_cdf is not None
        assert self.position_ver is not None
        assert self.position_hor is not None
        assert self.position_z is not None

        self.particle = Particle(
            detector=self.detector,
            simulation_mode=self.simulation_mode,
            particle_type=self.particle_type,
            input_energy=self.initial_energy,
            spectrum_cdf=self.spectrum_cdf,
            starting_pos_ver=self.position_ver,
            starting_pos_hor=self.position_hor,
            starting_pos_z=self.position_z
            # self.angle_alpha, self.angle_beta
        )
        particle = self.particle

        assert particle.track_length is not None
        if particle.track_length < 1.0:
            return True

        self.track_length_lst_per_event.append(particle.track_length)
        self.p_energy_lst_per_event.append(particle.energy)
        self.alpha_lst_per_event.append(particle.alpha)
        self.beta_lst_per_event.append(particle.beta)

        error = subprocess.call(
            [
                "./pyxel/models/charge_generation/tars/data/geant4/TestEm18",
                "Silicon",
                particle.type,
                str(particle.energy),
                str(particle.track_length),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if error != 0:
            return True

        # mat = self.detector.material
        # subprocess.call(['./TestEm18', mat.xxx, particle.type,
        # str(particle.energy), str(particle.track_length)'])

        g4_data_energy_path = Path(__file__).parent.joinpath(
            "data", "geant4", "tars_geant4_energy.data"
        )
        g4energydata = read_data(g4_data_energy_path)  # MeV

        # primary_e_balance = g4energydata[0] * 1.E6
        all_e_loss = g4energydata[1] * 1.0e6
        primary_e_loss = g4energydata[2] * 1.0e6
        secondary_e_loss = g4energydata[3] * 1.0e6
        if all_e_loss > 0.0:
            self.electron_number_from_eloss.append(
                np.floor(all_e_loss / 3.6).astype(int)
            )
            self.secondaries_from_eloss.append(
                np.floor(primary_e_loss / 3.6).astype(int)
            )
            self.tertiaries_from_eloss.append(
                np.floor(secondary_e_loss / 3.6).astype(int)
            )

        g4_data_path = Path(__file__).parent.joinpath(
            "data", "geant4", "tars_geant4.data"
        )
        g4data = read_data(g4_data_path)  # mm (!)

        if g4data.shape == (
            3,
        ):  # alternative running mode, only all electron number without proton step size data
            electron_number_vector = [g4data[0].astype(int)]
            secondaries = g4data[1].astype(int)
            tertiaries = g4data[2].astype(int)
            step_size_vector = [0]
        elif g4data.shape == (0,):
            step_size_vector = []  # um
            electron_number_vector = []
        elif g4data.shape == (2,):
            step_size_vector = [g4data[0] * 1e3]  # um
            electron_number_vector = [g4data[1].astype(int)]
        else:
            step_size_vector = g4data[:, 0] * 1e3  # um
            electron_number_vector = g4data[:, 1].astype(int)

        if np.any(electron_number_vector):
            # for j in range(len(step_size_vector)):
            for j in range(len(electron_number_vector)):

                # UPDATE POSITION OF IONIZING PARTICLES
                particle.position[0] += particle.dir_ver * step_size_vector[j]  # um
                particle.position[1] += particle.dir_hor * step_size_vector[j]  # um
                particle.position[2] += particle.dir_z * step_size_vector[j]  # um

                electron_number_per_event += electron_number_vector[j]
                secondary_per_event += secondaries
                tertiary_per_event += tertiaries

                self.e_num_lst_per_step.append(electron_number_vector[j])
                self.e_pos0_lst.append(particle.position[0])  # um
                self.e_pos1_lst.append(particle.position[1])  # um
                self.e_pos2_lst.append(particle.position[2])  # um

                e_kin_energy = 1.0
                self.e_energy_lst.append(e_kin_energy)  # eV

                # self.edep_per_step.append(particle.deposited_energy)    # keV
                # particle.total_edep += particle.deposited_energy        # keV

                # save particle trajectory
                particle.trajectory = np.vstack(
                    (particle.trajectory, particle.position)
                )

            # END of loop

            # self.total_edep_per_particle.append(particle.total_edep)  # keV
            self.e_num_lst_per_event.append(electron_number_per_event)
            self.sec_lst_per_event.append(secondary_per_event)
            self.ter_lst_per_event.append(tertiary_per_event)

        # print('p energy: ', particle.energy, '\ttrack length: ', particle.track_length,
        #       '\telectrons/event: ', electron_number_per_event,
        #       '\tsteps: ', len(step_size_vector), '\terror: ', error)

        return False

    # def _ionization_(self, particle):
    #     """TBW.
    #
    #     :param particle:
    #     :return:
    #     """
    #     geo = self.detector.geometry
    #     ioniz_energy = geo.ionization_energy
    #     let_value = None
    #
    #     # particle.energy is in MeV !
    #     # particle.deposited_energy is in keV !
    #     if self.energy_loss_data == 'let':
    #         let_value = sampling_distribution(self.let_cdf)  # keV/um
    #     elif self.energy_loss_data == 'stopping':
    #         stopping_power = get_yvalue_with_interpolation(self.stopping_power, particle.energy)  # MeV*cm2/g
    #         let_value = 0.1 * stopping_power * geo.material_density  # keV/um
    #
    #     particle.deposited_energy = let_value * self.step_length  # keV
    #
    #     if particle.deposited_energy >= particle.energy * 1e3:
    #         particle.deposited_energy = particle.energy * 1e3
    #
    #     e_kin_energy = 0.1  # eV
    #     electron_number = int(particle.deposited_energy * 1e3 / (ioniz_energy + e_kin_energy))  # eV/eV = 1
    #
    #     self.e_num_lst += [electron_number]
    #     self.e_energy_lst += [e_kin_energy]
    #     self.e_pos0_lst += [particle.position[0]]
    #     self.e_pos1_lst += [particle.position[1]]
    #     self.e_pos2_lst += [particle.position[2]]
    #
    #     # keV
    #     particle.deposited_energy = electron_number * (e_kin_energy + ioniz_energy) * 1e-3
    #     particle.energy -= particle.deposited_energy * 1e-3     # MeV
    #
    #     self.edep_per_step.append(particle.deposited_energy)    # keV
    #     particle.total_edep += particle.deposited_energy        # keV
