#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel TARS model to generate charge by ionization."""

import typing as t

import numpy as np
from typing_extensions import Literal

from pyxel.detectors import Detector
from pyxel.models.charge_generation.cosmix.util import sampling_distribution


class Particle:
    """Particle class define a particle together with its characteristics."""

    def __init__(
        self,
        detector: Detector,
        simulation_mode: Literal[
            "cosmic_ray", "cosmics", "radioactive_decay", "snowflakes"
        ],
        particle_type: Literal[
            "proton", "ion", "alpha", "beta", "electron", "gamma", "x-ray"
        ],
        input_energy: t.Union[int, float, Literal["random"]],
        spectrum_cdf: np.ndarray,
        starting_pos_ver: t.Union[str, np.ndarray],
        starting_pos_hor: t.Union[str, np.ndarray],
        starting_pos_z: t.Union[str, np.ndarray],
        # input_alpha='random', input_beta='random'
    ):
        """Creation of a particle according to some parameters.

        :param detector:
        :param simulation_mode:
        :param particle_type:
        :param input_energy:
        :param spectrum_cdf:
        :param starting_pos_ver:
        :param starting_pos_hor:
        :param starting_pos_z:
        """
        self.detector = detector
        geo = self.detector.geometry

        # starting_position_vertical = None
        # starting_position_horizontal = None
        # starting_position_z = None

        # if starting_pos_ver == 'random':
        #     starting_position_vertical = geo.vert_dimension * np.random.random()
        # elif isinstance(starting_pos_ver, int) or isinstance(starting_pos_ver, float):
        #     starting_position_vertical = starting_pos_ver
        # if starting_pos_hor == 'random':
        #     starting_position_horizontal = geo.horz_dimension * np.random.random()
        # elif isinstance(starting_pos_hor, int) or isinstance(starting_pos_hor, float):
        #     starting_position_horizontal = starting_pos_hor
        #
        # if starting_pos_z == 'random':
        #     starting_position_z = geo.total_thickness * np.random.random()
        # elif isinstance(starting_pos_z, int) or isinstance(starting_pos_z, float):
        #     starting_position_z = starting_pos_z
        #
        # self.starting_position = np.array([starting_position_vertical,
        #                                    starting_position_horizontal,
        #                                    starting_position_z])
        # self.position = np.copy(self.starting_position)
        # self.trajectory = np.copy(self.starting_position)

        # if input_alpha == 'random' and starting_pos_z == 0.:
        #     alpha = 2 * math.pi * np.random.random()
        # elif input_alpha == 'random' and starting_pos_z != 0.:
        #     alpha = 2 * math.pi * np.random.random()
        # else:
        #     alpha = input_alpha  # between 0 and 2*pi
        #
        # if input_beta == 'random':
        #     beta = 2. * math.pi * np.random.random()
        # else:
        #     beta = input_beta
        # self.angle = np.array([alpha, beta])
        #
        # self.dir_z = -1 * math.sin(alpha)
        # self.dir_ver = math.cos(alpha) * math.cos(beta)
        # self.dir_hor = math.cos(alpha) * math.sin(beta)

        # if input_alpha != 'random':
        #     self.alpha = input_alpha
        # if input_beta != 'random':
        #     self.beta = input_beta
        # # update direction:
        # self.dir_ver, self.dir_hor, self.dir_z = get_direction_from_angles()

        self.track_length = None  # type: t.Optional[float]

        self.dir_ver, self.dir_hor, self.dir_z = isotropic_direction()

        self.random_det_pt_vert = geo.vert_dimension * np.random.random()
        self.random_det_pt_horz = geo.horz_dimension * np.random.random()
        self.random_det_pt_z = -1 * geo.total_thickness * np.random.random()

        self.alpha, self.beta = self.get_angles()  # rad

        mode_1 = ["cosmic_ray", "cosmics"]
        mode_2 = ["radioactive_decay", "snowflakes"]
        if (
            simulation_mode in mode_1
        ):  # cosmic rays coming from OUTSIDE the detector volume
            self.starting_position = self.get_surface_point()
        elif simulation_mode in mode_2:  # radioactive decay INSIDE the detector volume
            self.starting_position = np.array(
                [self.random_det_pt_vert, self.random_det_pt_horz, self.random_det_pt_z]
            )

        if starting_pos_ver != "random":
            self.starting_position[0] = starting_pos_ver
        if starting_pos_hor != "random":
            self.starting_position[1] = starting_pos_hor
        if starting_pos_z != "random":
            self.starting_position[2] = starting_pos_z

        self.position = np.copy(self.starting_position)
        self.trajectory = np.copy(self.starting_position)

        if input_energy == "random":
            self.energy = sampling_distribution(spectrum_cdf)  # type: float
        elif isinstance(input_energy, int) or isinstance(input_energy, float):
            self.energy = input_energy
        else:
            raise ValueError("Given particle energy could not be read")

        self.deposited_energy = 0.0  # type: float
        self.total_edep = 0.0  # type: float

        self.type = particle_type
        ionizing_particles = ("proton", "ion", "alpha", "beta", "electron")
        non_ionizing_particles = ("gamma", "x-ray")  # 'photon'

        if self.type in ionizing_particles:
            # call direct ionization func when needed - already implemented in simulation
            pass

        elif self.type in non_ionizing_particles:
            # call NON-direct ionization func when needed - need to be implemented
            raise NotImplementedError(
                "Given particle type simulation is not yet implemented"
            )

        else:
            raise ValueError("Given particle type can not be simulated")

    def get_surface_point(self) -> np.ndarray:
        """TBW.

        :return:
        """
        geo = self.detector.geometry

        norm_vectors = [
            np.array(
                [0.0, 0.0, -1.0]
            ),  # top plane (usually particle enters vol. via this)
            np.array(
                [0.0, 0.0, 1.0]
            ),  # bottom plane (usually particle leaves vol. via this)
            np.array([0.0, 1.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
            np.array([0.0, -1.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
        ]  # type: t.List[np.ndarray]

        points = [
            np.array(
                [0.0, 0.0, 0.0]
            ),  # top plane (usually particle enters vol. via this)
            np.array(
                [0.0, 0.0, -1 * geo.total_thickness]
            ),  # bottom plane (usually particle leaves vol. via this)
            np.array([0.0, 0.0, 0.0]),
            np.array([geo.vert_dimension, 0.0, 0.0]),
            np.array([geo.vert_dimension, geo.horz_dimension, 0.0]),
            np.array([0.0, geo.horz_dimension, 0.0]),
        ]  # type: t.List[np.ndarray]

        intersect_points = np.zeros((6, 3))
        track_direction = np.array([self.dir_ver, self.dir_hor, self.dir_z])
        random_det_point = np.array(
            [self.random_det_pt_vert, self.random_det_pt_horz, self.random_det_pt_z]
        )

        surface_start_point = None  # type: t.Optional[np.ndarray]
        surface_end_point = None  # type: t.Optional[np.ndarray]
        for i in range(6):
            intersect_points[i, :] = find_intersection(
                n=norm_vectors[i], p0=points[i], ls=random_det_point, lv=track_direction
            )

            eps = 1e-8
            if 0.0 - eps <= intersect_points[i, 0] <= geo.vert_dimension + eps:
                if 0.0 - eps <= intersect_points[i, 1] <= geo.horz_dimension + eps:
                    if (
                        -1 * geo.total_thickness - eps
                        <= intersect_points[i, 2]
                        <= 0.0 + eps
                    ):
                        if (
                            np.dot(
                                track_direction,
                                intersect_points[i, :] - random_det_point,
                            )
                            < 0
                        ):
                            surface_start_point = self.intersection_correction(
                                intersect_points[i, :]
                            )
                        else:
                            surface_end_point = self.intersection_correction(
                                intersect_points[i, :]
                            )

        assert surface_start_point is not None
        assert surface_end_point is not None

        self.track_length = np.linalg.norm(surface_end_point - surface_start_point)

        if np.all(surface_start_point == surface_end_point):
            raise ValueError("This should not happen")
        if surface_start_point is None:
            raise ValueError("This should not happen")
        if surface_end_point is None:
            raise ValueError("This should not happen")

        return surface_start_point

    def get_angles(self) -> t.Tuple[float, float]:
        """TBW.

        :return:
        """
        beta = np.arccos(
            np.dot(np.array([1.0, 0.0]), np.array([self.dir_ver, self.dir_hor]))
        )

        alpha = np.arccos(
            np.dot(
                np.array([0.0, 0.0, 1.0]),
                np.array([self.dir_ver, self.dir_hor, self.dir_z]),
            )
        )

        if self.dir_hor < 0.0:
            beta += np.pi
            alpha += np.pi

        return alpha, beta

    # def track_length(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     geo = self.detector.geometry
    #
    #     norm_vectors = [np.array([0., 0., -1.]),    # top plane (usually particle enters vol. via this)
    #                     np.array([0., 0., 1.]),     # bottom plane (usually particle leaves vol. via this)
    #                     np.array([0., 1., 0.]),
    #                     np.array([-1., 0., 0.]),
    #                     np.array([0., -1., 0.]),
    #                     np.array([1., 0., 0.])]
    #
    #     points = [np.array([0., 0., 0.]),                       # top plane (usually particle enters vol. via this)
    #               np.array([0., 0., -1 * geo.total_thickness]), # bottom plane (usually particle leaves vol. via this)
    #               np.array([0., 0., 0.]),
    #               np.array([geo.vert_dimension, 0., 0.]),
    #               np.array([geo.vert_dimension, geo.horz_dimension, 0.]),
    #               np.array([0., geo.horz_dimension, 0.])]
    #
    #     track_length = np.inf
    #     intersect_points = np.zeros((6, 3))
    #     dir_array = np.array([self.dir_ver,
    #                           self.dir_hor,
    #                           self.dir_z])
    #     for i in range(6):
    #         intersect_points[i, :] = find_intersection(n=norm_vectors[i], p0=points[i],
    #                                                    ls=self.starting_position, lv=dir_array)
    #         track_length_new = np.linalg.norm(intersect_points[i, :] - self.starting_position)
    #         if track_length_new < track_length and track_length_new != 0.:
    #             track_length = track_length_new
    #
    #     return track_length

    # TODO: warning this method modify input parameter 'array' !!!
    def intersection_correction(self, array: np.ndarray) -> np.ndarray:
        """TBW.

        :param array:
        :return:
        """
        eps = 1e-8
        geo = self.detector.geometry
        if abs(array[0] - geo.vert_dimension) < eps:
            array[0] = geo.vert_dimension
        if abs(array[0]) < eps:
            array[0] = 0.0
        if abs(array[1] - geo.horz_dimension) < eps:
            array[1] = geo.horz_dimension
        if abs(array[1]) < eps:
            array[1] = 0.0
        if abs(array[2] + geo.total_thickness) < eps:
            array[2] = -1 * geo.total_thickness
        if abs(array[2]) < eps:
            array[2] = 0.0

        return array


def find_intersection(
    n: np.ndarray, p0: np.ndarray, ls: np.ndarray, lv: np.ndarray
) -> t.Optional[np.ndarray]:
    """TBW.

    https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
    :param n: normal vector of the plane
    :param p0: point of the plane
    :param ls: starting point of particle track
    :param lv: direction of particle track
    :return:
    """
    if np.dot(lv, n) == 0:  # No intersection of track and detector plane
        return None
    else:
        d = np.dot((p0 - ls), n) / np.dot(lv, n)
        p = d * lv + ls  # type: np.ndarray
        return p


def isotropic_direction() -> t.Tuple[float, float, float]:
    """TBW.

    :param n:
    :return:
    """
    u = 2 * np.random.random() - 1
    r = np.sqrt(1 - u ** 2)
    kszi = np.random.random()
    v = r * np.cos(2 * np.pi * kszi)
    w = r * np.sin(2 * np.pi * kszi)
    return u, v, w


def non_isotropic_direction(n: int) -> t.Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """TBW.

    :param n:
    :return:
    """
    alpha = 2 * np.pi * np.random.random(n)
    beta = 2 * np.pi * np.random.random(n)
    x = np.cos(alpha) * np.sin(beta)
    y = np.cos(alpha) * np.cos(beta)
    z = np.sin(alpha)
    return x, y, z
