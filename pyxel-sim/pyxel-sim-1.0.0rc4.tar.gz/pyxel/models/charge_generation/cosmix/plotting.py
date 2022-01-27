#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel CosmiX model to generate charge by ionization."""

import typing as t
from pathlib import Path

import numpy as np
import pandas as pd

if t.TYPE_CHECKING:
    from pyxel.models.charge_generation.cosmix.cosmix import Cosmix

try:
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
except ImportError:
    # raise Warning('Matplotlib cannot be imported')
    pass


class PlottingCosmix:
    """Plotting class for CosmiX."""

    def __init__(
        self,
        cosmix: "Cosmix",
        draw_plots: bool = False,
        save_plots: bool = False,
        file_format: str = "png",
    ) -> None:
        self.cosmix = cosmix

        self.draw_plots = draw_plots
        self.save_plots = save_plots
        self.file_format = file_format

    def save_and_draw(self, fig_name: str) -> None:
        """TBW.

        :param fig_name:
        """
        file_name = fig_name + "." + self.file_format
        if self.save_plots:
            plt.savefig(file_name)
        if self.draw_plots:
            plt.draw()

    def show(self) -> None:
        """TBW."""
        plt.show()

    def save_edep(self) -> None:
        """TBW."""
        np.save("orig2_edep_per_step_10k", self.cosmix.sim_obj.edep_per_step)
        np.save(
            "orig2_edep_per_particle_10k", self.cosmix.sim_obj.total_edep_per_particle
        )

    def plot_edep_per_step(self) -> tuple:
        """TBW."""
        plt.figure()
        n, bins, patches = plt.hist(
            self.cosmix.sim_obj.edep_per_step, 300, facecolor="b"
        )
        plt.xlabel("E_dep (keV)")
        plt.ylabel("Counts")
        plt.title("Histogram of E deposited per step")
        # plt.axis([0, 0.003, 0, 1.05*max(n)])
        plt.grid(True)
        self.save_and_draw("edep_per_step")
        return n, bins, patches

    def plot_edep_per_particle(self) -> tuple:
        """TBW."""
        plt.figure()
        n, bins, patches = plt.hist(
            self.cosmix.sim_obj.total_edep_per_particle, 200, facecolor="g"
        )
        plt.xlabel("E_dep (keV)")
        plt.ylabel("Counts")
        plt.title("Histogram of total E deposited per particle")
        # plt.axis([0, 0.4, 0, 1.05*max(n)])
        plt.grid(True)
        self.save_and_draw("edep_per_particle")
        return n, bins, patches

    def plot_spectrum_cdf(self) -> None:
        """TBW."""
        sim_obj = self.cosmix.sim_obj
        assert sim_obj.spectrum_cdf is not None
        assert sim_obj.flux_dist is not None

        lin_energy_range = sim_obj.spectrum_cdf[:, 0]
        cum_sum = sim_obj.spectrum_cdf[:, 1]
        plt.figure()
        plt.title("Spectrum CDF")
        plt.xlabel("Energy (MeV)")
        plt.ylabel("Probability")
        plt.semilogx(lin_energy_range, cum_sum)
        self.save_and_draw("spectrum_cdf")

    def plot_flux_spectrum(self) -> None:
        """TBW."""
        sim_obj = self.cosmix.sim_obj
        assert sim_obj.spectrum_cdf is not None
        assert sim_obj.flux_dist is not None

        lin_energy_range = sim_obj.spectrum_cdf[:, 0]
        flux_dist = sim_obj.flux_dist
        plt.figure()
        plt.title("Proton flux spectrum (CREME data)")
        plt.xlabel("Energy (MeV)")
        plt.ylabel("Flux (1/(s*MeV))")
        plt.loglog(lin_energy_range, flux_dist)
        self.save_and_draw("flux_spectrum")

    def plot_spectrum_hist(self, data: t.Optional[str] = None) -> None:
        """TBW."""
        plt.figure()
        plt.title("Proton flux spectrum sampled by CosmiX")
        plt.xlabel("Energy (MeV)")
        plt.ylabel("Counts")
        # plt.ylabel('Flux (1/(s*MeV))')
        # plt.loglog(lin_energy_range, flux_dist)

        if isinstance(data, str):
            if data.endswith(".npy"):
                data = np.load(data)

        hist_bins = 250
        # hist_range = (1e-1, 1e5)
        # col = (0, 1, 1, 1)
        plt.hist(data, bins=np.logspace(np.log10(0.1), np.log10(1e5), hist_bins))
        plt.gca().set_xscale("log")
        # plt.legend(loc='upper right')
        self.save_and_draw("tars_spectrum")

    def plot_charges_3d(self) -> None:
        """TBW."""
        geo = self.cosmix.sim_obj.detector.geometry

        # set up a figure twice as wide as it is tall
        fig = plt.figure(figsize=plt.figaspect(0.5))
        # fig = plt.figure()

        e_num_lst_per_event = self.cosmix.sim_obj.e_num_lst_per_event
        size = [x / 10.0 for x in e_num_lst_per_event]
        # ax = fig.add_subplot(1, 2, 1, projection='3d')
        ax = fig.add_subplot(1, 2, 1, projection="3d")
        ax.scatter(
            self.cosmix.sim_obj.e_pos0_lst,
            self.cosmix.sim_obj.e_pos1_lst,
            self.cosmix.sim_obj.e_pos2_lst,
            c="b",
            marker=".",
            s=size,
        )
        # ax.plot(self.cosmix.sim_obj.particle.trajectory[:, 0],
        #         self.cosmix.sim_obj.particle.trajectory[:, 1],
        #         self.cosmix.sim_obj.particle.trajectory[:, 2], 'c-')

        # ax2 = fig.add_subplot(1, 2, 2, projection='3d')
        # ax2.scatter(self.cosmix.sim_obj.e_pos0_lst, self.cosmix.sim_obj.e_pos1_lst, 0,
        #             c='r', marker='.', s=size)

        # ax.hold(True)
        point1 = np.array([0, 0, 0])
        point2 = np.array([0, 0, -1 * geo.total_thickness])
        # point3 = np.array([1, 2, 3])
        normal = np.array([0, 0, 1])
        # norma2 = np.array([0, 1, 0])
        # norma3 = np.array([1, 0, 0])

        # point2 = np.array([10, 50, 50])

        # a plane is a*x+b*y+c*z+d=0
        # [a,b,c] is the normal. Thus, we have to calculate
        # d and we're set
        d1 = -point1.dot(normal)
        d2 = -point2.dot(normal)
        # d3 = -point3.dot(norma3)

        # create x,y
        xx, yy = np.meshgrid(
            range(int(geo.vert_dimension)), range(int(geo.horz_dimension))
        )

        # calculate corresponding z
        z1 = (-normal[0] * xx - normal[1] * yy - d1) * 1.0 / normal[2]
        z2 = (-normal[0] * xx - normal[1] * yy - d2) * 1.0 / normal[2]
        # z3 = (-norma3[0] * xx - norma3[1] * yy - d3) * 1. / norma3[2]

        ax.plot_surface(xx, yy, z1, alpha=0.2, color=(0, 0, 1))
        ax.plot_surface(xx, yy, z2, alpha=0.2, color=(0, 0, 1))
        # ax.plot_surface(xx, yy, z3, alpha=0.2)

        ax.set_xlim(0, geo.vert_dimension)
        ax.set_ylim(0, geo.horz_dimension)
        ax.set_zlim(-1 * geo.total_thickness, 0)
        ax.set_xlabel(r"vertical ($\mu$m)")
        ax.set_ylabel(r"horizontal ($\mu$m)")
        ax.set_zlabel(r"z ($\mu$m)")

        # ax2.set_xlim(0, geo.vert_dimension)
        # ax2.set_ylim(0, geo.horz_dimension)
        # ax2.set_zlim(-1 * geo.total_thickness, 0)
        # ax2.set_xlabel(r'vertical ($\mu$m)')
        # ax2.set_ylabel(r'horizontal ($\mu$m)')
        # ax2.set_zlabel(r'z ($\mu$m)')

    # def plot_let_cdf(self) -> None:
    #     """TBW."""
    #     plt.figure()
    #     plt.title('LET CDF')
    #     plt.plot(self.cosmix.sim_obj.let_cdf[:, 0], self.cosmix.sim_obj.let_cdf[:, 1], '.')
    #     self.save_and_draw('let_cdf')

    def plot_step_cdf(self) -> None:
        """TBW."""
        plt.figure()
        plt.title("Step size CDF")
        plt.plot(
            self.cosmix.sim_obj.step_cdf[:, 0], self.cosmix.sim_obj.step_cdf[:, 1], "."
        )
        self.save_and_draw("step_cdf")

    def plot_step_dist(self) -> None:
        """TBW."""
        plt.figure()
        plt.title("Step size distribution")
        plt.xlabel("step size (um)")
        plt.ylabel("counts")
        plt.plot(
            self.cosmix.sim_obj.step_size_dist["step_size"],
            self.cosmix.sim_obj.step_size_dist["counts"],
            ".",
        )
        self.save_and_draw("step_dist")

    def plot_tertiary_number_cdf(self) -> None:
        """TBW."""
        plt.figure()
        plt.title("Tertiary electron number CDF")
        plt.plot(
            self.cosmix.sim_obj.elec_number_cdf[:, 0],
            self.cosmix.sim_obj.elec_number_cdf[:, 1],
            ".",
        )
        self.save_and_draw("elec_number_cdf")

    def plot_tertiary_number_dist(self) -> None:
        """TBW."""
        plt.figure()
        plt.title("Tertiary electron number distribution")
        plt.plot(
            self.cosmix.sim_obj.elec_number_dist["electron"],
            self.cosmix.sim_obj.elec_number_dist["counts"],
            ".",
        )
        self.save_and_draw("elec_number_dist")

    # def plot_let_dist(self) -> None:
    #     """TBW."""
    #     plt.figure()
    #     plt.title('LET dist')
    #     plt.plot(self.cosmix.sim_obj.let_dist[:, 1], self.cosmix.sim_obj.let_dist[:, 2], '.')
    #     self.save_and_draw('let_dist')

    def plot_trajectory_xy(self) -> None:
        """TBW."""
        plt.figure()
        geo = self.cosmix.sim_obj.detector.geometry

        particle = self.cosmix.sim_obj.particle
        assert particle is not None

        # self.trajectory[:, 0] - VERTICAL COORDINATE
        # self.trajectory[:, 1] - HORIZONTAL COORDINATE
        plt.plot(particle.trajectory[:, 1], particle.trajectory[:, 0], ".")
        plt.xlabel(r"horizontal ($\mu$m)")
        plt.ylabel(r"vertical ($\mu$m)")
        plt.title("p trajectory in CCD")
        plt.axis([0, geo.horz_dimension, 0, geo.vert_dimension])
        plt.grid(True)
        self.save_and_draw("trajectory_xy")

    def plot_trajectory_xz(self) -> None:
        """TBW."""
        plt.figure()
        geo = self.cosmix.sim_obj.detector.geometry
        particle = self.cosmix.sim_obj.particle
        assert particle is not None

        # self.trajectory[:, 2] - Z COORDINATE
        # self.trajectory[:, 1] - HORIZONTAL COORDINATE
        plt.plot(particle.trajectory[:, 1], particle.trajectory[:, 2], ".")
        plt.xlabel(r"horizontal ($\mu$m)")
        plt.ylabel(r"z ($\mu$m)")
        plt.title("p trajectory in CCD")
        plt.axis([0, geo.horz_dimension, -1 * geo.total_thickness, 0])
        plt.grid(True)
        self.save_and_draw("trajectory_xz")

    def plot_track_histogram(
        self, histogram_data: t.Union[str, np.ndarray], normalize: bool = False
    ) -> None:
        """TBW."""
        hist_bins = 1000
        hist_range = (0, 1000)

        plt.figure()
        plt.title("Proton track length distribution")

        if isinstance(histogram_data, str):
            if histogram_data.endswith(".npy"):
                data = np.load(histogram_data)  # type: np.ndarray
            else:
                raise NotImplementedError
        else:
            data = histogram_data

        col = (1, 0, 1, 1)

        if normalize:
            plt.hist(data, bins=hist_bins, range=hist_range, fc=col, density=True)
        else:
            plt.hist(data, bins=hist_bins, range=hist_range, fc=col)

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel("Track length")
        plt.ylabel("Counts")
        plt.legend(loc="upper right")
        self.save_and_draw("track_length")

    def plot_step_size_histograms(self, normalize: bool = False) -> None:
        """TBW."""
        energies = ["100MeV"]
        thicknesses = ["40um", "50um", "60um", "70um", "100um"]
        p_types = ["proton"]

        path = Path(__file__).parent.joinpath("data", "inputs")

        # step_rows = 10000

        plt.figure()
        plt.title("Step size")
        for p_type in p_types:
            for energy in energies:
                for thickness in thicknesses:
                    filename = (
                        "stepsize_"
                        + p_type
                        + "_"
                        + energy
                        + "_"
                        + thickness
                        + "_Si_10k.ascii"
                    )
                    step_size = pd.read_csv(
                        str(Path(path, filename)),
                        delimiter="\t",
                        names=["step_size", "counts"],
                        usecols=[1, 2],
                        skiprows=4,
                        nrows=10000,
                    )

                    if normalize:
                        plotted_counts = step_size["counts"] / sum(step_size["counts"])
                    else:
                        plotted_counts = step_size["counts"]

                    plt.plot(
                        step_size["step_size"],
                        plotted_counts,
                        ".-",
                        label=p_type + ", " + energy + ", " + thickness,
                    )

        plt.axis([0, 20, 0, 0.010])
        plt.xlabel("Step size (um)")
        plt.ylabel("Counts")
        plt.legend(loc="upper right")
        self.save_and_draw("step_size_histograms")

    #
    # def plot_secondary_spectra(self, normalize: bool=None):
    #     """TBW."""
    #     energies = ['100MeV', '1GeV']
    #     thicknesses = ['10um', '50um', '100um', '200um']
    #     p_types = ['proton']
    #
    #     path = Path(__file__).parent.joinpath('data', 'inputs')
    #
    #     # step_rows = 10000
    #
    #     plt.figure()
    #     plt.title('Electron spectrum')
    #     for p_type in p_types:
    #         for energy in energies:
    #             for thickness in thicknesses:
    #                 filename = 'stepsize_' + p_type + '_' + energy + '_' + thickness + '_1M.ascii'
    #                 spectrum = pd.read_csv(str(Path(path, filename)),
    #                                        delimiter="\t", names=["energy", "counts"], usecols=[1, 2],
    #                                        skiprows=10008, nrows=200)
    #
    #                 if normalize:
    #                     plotted_counts = spectrum['counts'] / sum(spectrum['counts'])
    #                 else:
    #                     plotted_counts = spectrum['counts']
    #
    #                 plt.plot(spectrum['energy'], plotted_counts, '.-',
    #                          label=p_type + ', ' + energy + ', ' + thickness)
    #
    #     # plt.axis([0, 6.0, 0, 0.12])
    #     plt.xlabel('Energy')
    #     plt.ylabel('Counts')
    #     plt.legend(loc='upper right')
    #     self.save_and_draw('secondary_spectra')

    def plot_gaia_vs_gras_hist(self, normalize: bool = False) -> None:
        """TBW."""
        # GRAS simulation results (by Marco) + GAIA BAM data - Perfect overlap in case of normalization!
        path = Path(__file__).parent.joinpath(
            "data",
            "validation",
            "Gaia_CCD_study-20180404T115340Z-001",
            "Gaia_CCD_study",
            "Data",
        )
        hist_names = [
            "CRs_from_BAM_Gaia_CCDs.npy",  # GAIA BAM data
            "complete_G4_H_He_GCR_sim_deposition.npy",  # G4, contains a lot of events with ZERO number of e-!
            r"C:\dev\work\pyxel\pyxel\models\charge_generation"
            + r"\cosmix\data\validation\G4_app_results_20180425\cosmix-e_num_lst_per_event.npy",
        ]
        labels = ["Gaia BAM CCD data", "GRAS simulation", "CosmiX (Pyxel) simulation"]
        i = 0

        hist_bins = 250
        hist_range = (1, 15e3)

        plt.figure()
        ax = plt.axes()

        plt.title("Charges deposited per single event")
        for filename in hist_names:

            histogram = np.load(str(Path(path, filename)))

            if i == 0:
                col = (0, 0, 1, 0.7)  # blue
            if i == 1:
                col = (0, 1, 0, 0.7)  # green
            if i == 2:
                col = (1, 0, 0, 0.7)  # red
            # cyan      (0, 1, 1, 0.5)
            # magenta   (1, 0, 1, 0.5)

            if normalize:
                plt.hist(
                    histogram,
                    bins=hist_bins,
                    range=hist_range,
                    histtype="step",
                    label=labels[i],
                    color=col,
                    density=True,
                )
            else:
                plt.hist(
                    histogram,
                    bins=hist_bins,
                    range=hist_range,
                    histtype="step",
                    label=labels[i],
                    color=col,
                )

            i += 1

        plt.axis([0, 15e3, 0, 3.0e-4])

        plt.xlabel("Number of electrons")
        plt.ylabel("Counts (normalized)")

        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        plt.legend(loc="upper right")
        self.save_and_draw("gaia_vs_gras_electron_hist")

    def plot_old_tars_hist(self, normalize: bool = False) -> None:
        """TBW."""
        # earlier TARS results of Lionel
        folder_path = Path(__file__).parent.joinpath(
            "data", "validation", "Results-20180404T121902Z-001", "Results"
        )
        hist_names = [
            # '10000 events from random protons CREME96 (16um - SM)(22-08-2016_16h36)',  # 16 um SM
            "10000 events from random protons CREME96 (16um - SM)(22-08-2016_16h41)",  # 16 um SM
            "10000 events from random protons CREME96 (step=0.5)(16-08-2016_15h56)",  # 40 um BAM
        ]
        labels = ["TARS data (Lionel), SM (16um)", "TARS data (Lionel), BAM (40um)"]
        i = 0

        hist_bins = 500
        hist_range = (1, 15e3)

        plt.figure()
        plt.title("Number of electrons per event")
        for filename in hist_names:

            histogram = np.load(
                str(
                    Path(
                        folder_path.joinpath(filename),
                        "Raw data/Electrons_generated.npy",
                    )
                )
            )

            if i == 0:
                col = (1, 0, 0, 0.5)
            if i == 1:
                col = (0, 1, 0, 0.5)

            if normalize:
                plt.hist(
                    histogram,
                    bins=hist_bins,
                    range=hist_range,
                    label=labels[i],
                    fc=col,
                    density=True,
                )
            else:
                plt.hist(
                    histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col
                )

            i += 1

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel("")
        plt.ylabel("Counts")
        plt.legend(loc="upper right")
        self.save_and_draw("old_tars_electron_hist")

    def plot_gaia_bam_vs_sm_electron_hist(self, normalize: bool = False) -> None:
        """TBW."""
        path = Path(__file__).parent.joinpath("data", "validation")
        hist_names = [
            # 'Gaia_bam_ccd_events(13259).npy', NEM JOOOOO
            "Gaia_CCD_study-20180404T115340Z-001/Gaia_CCD_study/Data/CRs_from_SM_Gaia_CCDs.npy",
            "Gaia_CCD_study-20180404T115340Z-001/Gaia_CCD_study/Data/CRs_from_BAM_Gaia_CCDs.npy",
        ]
        labels = ["GAIA SM (16um) data", "GAIA BAM (40um) data"]
        i = 0

        hist_bins = 500
        hist_range = (1, 15e3)

        plt.figure()
        plt.title("Number of electrons per event")
        for filename in hist_names:

            histogram = np.load(str(Path(path, filename)))

            if i == 0:
                col = (1, 0, 0, 0.5)
            if i == 1:
                col = (0, 0, 1, 0.5)

            if normalize:
                plt.hist(
                    histogram,
                    bins=hist_bins,
                    range=hist_range,
                    label=labels[i],
                    fc=col,
                    density=True,
                )
            else:
                plt.hist(
                    histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col
                )

            i += 1

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel("")
        plt.ylabel("Counts")
        plt.legend(loc="upper right")
        self.save_and_draw("gaia_BAM_vs_SM_electron_hist")

    def plot_electron_hist(
        self,
        data1: t.Union[str, np.ndarray],
        data2: t.Optional[np.ndarray] = None,
        data3: t.Optional[np.ndarray] = None,
        title: str = "",
        hist_bins: int = 500,
        hist_range: t.Tuple[int, int] = (0, 15000),
        normalize: bool = False,
    ) -> None:
        """TBW."""
        labels = [
            "TARS (David), 40um"
            # 'secondary e-',
            # 'tertiary e-'
        ]
        i = 0

        # hist_bins = 5000
        # hist_range = (0, 15000)

        # hist_bins = 500
        # hist_range = (10, 2E4)

        plt.figure()
        plt.title(title)

        if isinstance(data1, str):
            if data1.endswith(".npy"):
                data1 = np.load(data1)

        # data1 = data1[data1 > ]
        # data1 = data1[data1 < 15000]

        if normalize:
            plt.hist(
                data1,
                bins=hist_bins,
                range=hist_range,
                label=labels[i],
                fc=(1, 0, 0, 0.5),
                density=True,
            )
            if data2:
                i += 1
                plt.hist(
                    data2,
                    bins=hist_bins,
                    range=hist_range,
                    label=labels[i],
                    fc=(1, 1, 0, 0.5),
                    density=True,
                )
                if data3:
                    i += 1
                    plt.hist(
                        data3,
                        bins=hist_bins,
                        range=hist_range,
                        label=labels[i],
                        fc=(0, 1, 1, 0.5),
                        density=True,
                    )

        else:
            plt.hist(
                data1,
                bins=hist_bins,
                range=hist_range,
                label=labels[i],
                fc=(1, 0, 0, 0.5),
            )
            if data2:
                i += 1
                plt.hist(
                    data2,
                    bins=hist_bins,
                    range=hist_range,
                    label=labels[i],
                    fc=(1, 1, 0, 0.5),
                )
                if data3:
                    i += 1
                    plt.hist(
                        data3,
                        bins=hist_bins,
                        range=hist_range,
                        label=labels[i],
                        fc=(0, 1, 1, 0.5),
                    )

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel("")
        plt.ylabel("Counts")
        plt.legend(loc="upper right")
        self.save_and_draw("electron_hist")

    def polar_angle_dist(self, theta: t.Union[str, np.ndarray]) -> None:
        """TBW."""
        if isinstance(theta, str):
            if theta.endswith(".npy"):
                theta_data = np.load(theta)  # type: np.ndarray
            else:
                raise NotImplementedError
        else:
            theta_data = theta

        fig = plt.figure()
        fig.add_subplot(111, polar=True)
        # theta = 2 * np.pi * np.random.rand(10000)
        plt.hist(theta_data, bins=360, histtype="step")
        # plt.polar(theta)
        plt.xlabel("")
        plt.ylabel("")
        plt.title("Incident angle distribution")
        self.save_and_draw("polar_angle")
