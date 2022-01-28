from __future__ import annotations
from typing import Tuple, List, Optional

import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

import numpy as np, os, math
from matplotlib.ticker import MaxNLocator, FormatStrFormatter
from scipy.spatial import Voronoi, voronoi_plot_2d
from multiprocessing import Pool, cpu_count

from .common import DomainParams, OUTPUT_DIR

SYMM = np.array(
    [[0, 0], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
)


class SimData:
    """Stores diagram information for a simulation.

    Attributes:
        path (Path): path to output directory.
        domains (List[DomainParams]): domain parameters from simulation frames,
        energies (List[float]): energy from simulation frames.
        voronois (List[Voronoi]): voronoi information from scipy from simulation frames.
        stats (List[numpy.ndarray]): statistics from simulation frames.

    """

    __slots__ = ["path", "domains", "energies", "voronois", "stats"]

    def __init__(self, sim: Simulation) -> None:
        if sim is not None:
            self.path = sim.path
            self.domains = list([DomainParams(s.n, s.w, s.h, s.r) for s in sim])
            self.energies = list([s.energy for s in sim])
            self.voronois = list([s.vor_data for s in sim])
            self.stats = list([s.stats for s in sim])

    def __len__(self) -> int:
        return len(self.domains)

    def slice(self, indices: List[int]) -> SimData:
        new_data = SimData(None)
        new_data.path = self.path

        new_data.domains = list([self.domains[i] for i in indices])
        new_data.energies = list([self.energies[i] for i in indices])
        new_data.voronois = list([self.voronois[i] for i in indices])
        new_data.stats = list([self.stats[i] for i in indices])

        return new_data

    def hist(
        self,
        stat: str,
        i: int,
        bins: int = 10,
        bounds: Optional[Tuple[float, float]] = None,
        cumul: bool = False,
        avg: bool = False,
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """Generates a histogram from the selected data.

        Arguments:
            stat (str): name of data to obtain
            i (int): which frame to select from
            bins (int): number of bins for the histogram.
            bounds (Optional[Tuple[float, float]]): upper and lower bounds of the
                histogram. This will automatically take the minimum and maximum value
                if not set.
            cumul (bool): aggregates all data up to frame i if True.
            avg (bool): will average the data based on number of frames if True.

        Returns:
            Tuple[numpy.ndarray, numpy.ndarray]: the histogram and its bins.

        """

        if cumul:
            values = np.concatenate([f[stat] for f in self.stats[: (i + 1)]])
        else:
            values = self.stats[i][stat]

        if np.var(values) <= 1e-8:
            hist = np.zeros((bins,))
            val = np.average(values)
            hist[(bins + 1) // 2 - 1] = len(values)
            bin_list = np.linspace(0, val, bins // 2 + 1, endpoint=True)
            bin_list = np.concatenate((bin_list, (bin_list + val)[1:]))
            return hist, bin_list[not (bins % 2) :]

        hist, bin_edges = np.histogram(values, bins=bins, range=bounds)
        bin_list = np.array(
            [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)]
        )

        if avg and cumul:
            return hist / (i + 1), bin_list

        return hist, bin_list


class Diagram:
    """Class for generating diagrams.

    Attributes:
        sim (SimData): the simulation data that contains all the frames and information.
        diagrams (numpy.ndarray): array that selects which diagrams to show.
        cumulative (bool): selects whether or not graph statistics are cumulative.

    """

    __slots__ = ["sim", "diagrams", "cumulative"]

    def __init__(
        self, sim: Simulation, diagrams: np.ndarray, cumulative: bool = False
    ) -> None:
        self.sim = SimData(sim)
        self.diagrams = np.atleast_2d(diagrams)
        self.cumulative = cumulative

    def generate_frame(self, frame: int, mode: str, fol: str, name: str = None) -> None:
        if mode not in ["save", "open"]:
            raise ValueError("Not a valid mode for diagrams!")

        shape = self.diagrams.shape

        plt.rcParams.update(
            {
                "axes.titlesize": 45,
                "axes.labelsize": 45,
                "xtick.labelsize": 40,
                "ytick.labelsize": 40,
                "xtick.major.width": 2,
                "ytick.major.width": 2,
                "xtick.major.size": 5,
                "ytick.major.size": 5,
                "xtick.minor.width": 1,
                "ytick.minor.width": 1,
                "xtick.minor.size": 3,
                "ytick.minor.size": 3,
                "legend.fontsize": 40,
                "lines.linewidth": 3,
                "font.family": "cm",
                "font.size": 40,
                "text.usetex": True,
                "text.latex.preamble": r"\usepackage{amsmath}",
                "figure.constrained_layout.use": True,
            }
        )

        fig = plt.figure(figsize=(shape[1] * 15, shape[0] * 15))
        gs = fig.add_gridspec(shape[0], shape[1])
        # fig, axes = plt.subplots(*shape, figsize=(shape[1] * 15, shape[0] * 15))

        if self.diagrams.shape == (1, 1):
            ax = fig.add_subplot(gs[0])
            getattr(self, str(self.diagrams[0][0]) + "_plot")(frame, ax)
        else:
            # axes = np.atleast_2d(axes)
            it = np.nditer(self.diagrams, flags=["multi_index"])
            for diagram in it:
                if diagram == "":
                    continue

                ax = fig.add_subplot(gs[it.multi_index])
                getattr(self, str(diagram) + "_plot")(frame, ax)

        # plt.tight_layout()
        if name is None:
            name = f"img{frame:05}.png"

        if mode == "save":
            plt.savefig(self.sim.path / fol / name)
            plt.close(fig)
        elif mode == "show":
            plt.show()

    def voronoi_plot(self, i: int, ax: AxesSubplot) -> None:
        domain = self.sim.domains[i]
        n, w, h = domain.n, domain.w, domain.h
        scale = 1.5
        area = n <= 50

        offset = (
            2
            - 2 * domain.r * (6 * 3 ** (-0.25) * math.sqrt(2) * math.atanh(0.5))
            + 2 * math.pi * domain.r ** 2
        )

        # Make color map axis.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        voronoi_plot_2d(
            self.sim.voronois[i], ax, show_vertices=False, show_points=False
        )

        # Mark location axis with 3 ticks.
        ax.set_xticks([0, w / 2, w])
        ax.set_yticks([0, h / 2, h])

        # Obtain site energies, and make color map.
        energies = self.sim.stats[i]["site_energies"][:n]
        norm = mpl.colors.Normalize(vmin=-2, vmax=2, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cm.magma)
        cbar = plt.colorbar(mapper, cax=cax, ticks=np.linspace(-2, 2, 5))

        # Fill polygons with energy colormap.
        for j, p in enumerate(self.sim.voronois[i].point_region):
            region = self.sim.voronois[i].regions[p]
            if not -1 in region:
                polygon = [self.sim.voronois[i].vertices[k] for k in region]
                ax.fill(
                    *zip(*polygon),
                    color=mapper.to_rgba(energies[j % n] - offset),
                    zorder=0,
                )

        line_color, point_color = "white", "lightseagreen"

        # Periodic border
        ax.plot([-w, 2 * w], [0, 0], line_color, linewidth="4")
        ax.plot([-w, 2 * w], [h, h], line_color, linewidth="4")
        ax.plot([0, 0], [-h, 2 * h], line_color, linewidth="4")
        ax.plot([w, w], [-h, 2 * h], line_color, linewidth="4")
        ax.axis("equal")
        ax.set_xlim([(1 - 0.85 * scale) * w / 2, (1 + 0.85 * scale) * w / 2])
        ax.set_ylim([(1 - scale) * h / 2, (1 + scale) * h / 2])
        ax.set_title("Voronoi Tessellation")

        # Marking sites and defects.
        defects = {5: {"x": [], "y": []}, 7: {"x": [], "y": []}}
        for j in range(n):
            for s in SYMM:
                vec = self.sim.voronois[i].points[j] + s * self.sim.domains[i].dim
                if area:
                    txt = ax.text(
                        *vec, str(round(self.sim.stats[i]["site_areas"][j], 3))
                    )
                    txt.set_clip_on(True)

                if self.sim.stats[i]["site_edge_count"][j] == 5:
                    defects[5]["x"].append(vec[0])
                    defects[5]["y"].append(vec[1])
                elif self.sim.stats[i]["site_edge_count"][j] == 7:
                    defects[7]["x"].append(vec[0])
                    defects[7]["y"].append(vec[1])
                else:
                    ax.scatter(
                        vec[0], vec[1], s=(40 - n / 100), color=point_color, zorder=1
                    )

        ax.scatter(
            defects[5]["x"],
            defects[5]["y"],
            marker="p",
            s=(200 - n / 100),
            color=point_color,
            zorder=1,
        )
        ax.scatter(
            defects[7]["x"],
            defects[7]["y"],
            marker="*",
            s=(200 - n / 100),
            color=point_color,
            zorder=1,
        )

        # Make VEE text in top left.
        props = dict(boxstyle="round", facecolor="white", alpha=0.8, zorder=20)
        ax.text(
            0.065,
            0.935,
            f"VEE: {round(sum(energies)/n - offset, 8)}",
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props,
        )

    def energy_plot(self, i: int, ax: AxesSubplot) -> None:
        ax.set_xlim([0, len(self.sim)])

        energies = self.sim.energies[: (i + 1)]
        ax.plot(list(range(i + 1)), energies)
        ax.title.set_text("Energy vs. Time")
        # max_value = round(self.sim[0].energy)
        # min_value = round(self.sim[-1].energy)
        # diff = max_value-min_value
        # ax.set_yticks(np.arange(int(min_value-diff/5), int(max_value+diff/5), diff/25))
        ax.set_xlabel("Iterations")
        ax.set_ylabel("Energy")
        ax.grid()

    def site_areas_plot(self, i: int, ax: AxesSubplot) -> None:
        y, x = self.sim.hist("site_areas", i, cumul=self.cumulative, avg=True)

        ax.bar(x, y, width=0.8 * (x[1] - x[0]))
        ax.title.set_text("Site Areas")
        ax.set_xlabel("Area")
        ax.set_ylabel("Average Occurances")
        ax.set_xticks(x)
        ax.ticklabel_format(useOffset=False)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        # for xtick, color in zip(ax.get_xticklabels(), areas_bar[2]):
        #     if color != 'C0':
        #         xtick.set_color(color)

    def site_edge_count_plot(self, i: int, ax: AxesSubplot) -> None:
        y, x = self.sim.hist(
            "site_edge_count", i, bounds=(1, 11), cumul=self.cumulative, avg=True
        )

        ax.bar(x, y, width=0.8 * (x[1] - x[0]))
        ax.title.set_text("Edges per Site")
        ax.set_xlabel("Number of Edges")
        ax.set_ylabel("Average Occurances")
        ax.set_xticks(x)
        ax.set_xticklabels([int(z) for z in x])
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    def site_isos_plot(self, i: int, ax: AxesSubplot) -> None:
        y, x = self.sim.hist(
            "site_isos", i, bounds=(0, 1), cumul=self.cumulative, avg=True
        )

        ax.bar(x, y, width=0.8 * (x[1] - x[0]))
        ax.title.set_text("Isoparametric Values")
        ax.set_xlabel("Isoparametric Value")
        ax.set_ylabel("Average Occurances")
        ax.set_xticks(x)
        ax.ticklabel_format(useOffset=False)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        # for xtick, color in zip(ax.get_xticklabels(), isoparam_bar[2]):
        #     if color != 'C0':
        #         xtick.set_color(color)

    def site_energies_plot(self, i: int, ax: AxesSubplot) -> None:
        y, x = self.sim.hist("site_energies", i, cumul=self.cumulative, avg=True)

        ax.bar(x, y, width=0.8 * (x[1] - x[0]))
        ax.title.set_text("Site Energies")
        ax.set_xlabel("Energy")
        ax.set_ylabel("Average Occurances")
        ax.set_xticks(x)
        ax.ticklabel_format(useOffset=False)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    def avg_radius_plot(self, i: int, ax: AxesSubplot) -> None:
        y, x = self.sim.hist("avg_radius", i, cumul=self.cumulative, avg=True)

        ax.bar(x, y, width=0.8 * (x[1] - x[0]))
        ax.title.set_text("Site Average Radii")
        ax.set_xlabel("Average Radius")
        ax.set_ylabel("Average Occurances")
        ax.set_xticks(x)
        ax.ticklabel_format(useOffset=False)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    def isoparam_avg_plot(self, i: int, ax: AxesSubplot) -> None:
        y, x = self.sim.hist("isoparam_avg", i, cumul=self.cumulative, avg=True)

        ax.bar(x, y, width=0.8 * (x[1] - x[0]))
        ax.title.set_text("Site Isoperimetric Averages")
        ax.set_xlabel("Isoperimetric Average")
        ax.set_ylabel("Average Occurances")
        ax.set_xticks(x)
        ax.ticklabel_format(useOffset=False)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    def edge_lengths_plot(self, i: int, ax: AxesSubplot) -> None:
        y, x = self.sim.hist("edge_lengths", i, 30, cumul=self.cumulative, avg=True)

        ax.bar(x, y, width=0.8 * (x[1] - x[0]))
        ax.title.set_text("Edge Lengths")
        ax.set_xlabel("Length")
        ax.set_ylabel("Average Occurances")
        ax.set_xticks(x)
        ax.set_xticklabels(ax.get_xticks(), rotation=90)
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
        # ax.ticklabel_format(useOffset=False)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        # for xtick, color in zip(ax.get_xticklabels(), lengths_bar[2]):
        #     if color != 'C0':
        #         xtick.set_color(color)

    def eigs_plot(self, i: int, ax: AxesSubplot) -> None:
        try:
            eigs = self.sim.stats[i]["eigs"]
            for i, eig in enumerate(eigs):
                if eig > 1e-4:
                    ax.annotate(
                        f"Coercivity: {eig:.5f}",
                        xy=(i, eig),
                        xytext=(50, -50),
                        textcoords="offset points",
                        arrowprops={"arrowstyle": "->", "color": "black"},
                    )
                    break

            ax.plot(
                list(range(40)),
                eigs[:40],
                marker="o",
                linestyle="dashed",
                color="C0",
                markersize=8,
            )

            ax.plot([0, 40], [0, 0], color="red")
        except KeyError:
            ax.text(0.5, 0.5, "Not Computed")

        ax.grid()
        ax.set_title("Sorted Hessian Eigenvalues")
        ax.set_xlabel("")
        ax.set_ylabel("Value")

    def render_frames(self, frames: List[int], fol: str = "frames") -> None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        self.sim.path.mkdir(exist_ok=True)
        (self.sim.path / fol).mkdir(exist_ok=True)
        combo_list = []
        for i in range(cpu_count()):
            start, end = (
                int(i * len(frames) / cpu_count()),
                int((i + 1) * len(frames) / cpu_count()),
            )
            new_dia = Diagram(None, self.diagrams, self.cumulative)
            new_dia.sim = self.sim.slice(frames[start:end])
            combo_list.append(
                (new_dia, fol, start, len(frames[start:end]), len(frames))
            )

        # Free up memory, since it's already duplicated to other cores.
        self.sim = self.sim.slice([])
        with Pool(cpu_count()) as pool:
            for _ in pool.imap_unordered(render_frame_range, combo_list):
                pass

        print(flush=True)
        print(f'Wrote to "{self.sim.path / fol}".', flush=True)

    def render_video(self, time: int, mode: str) -> None:
        if mode not in ["use_all", "sample"]:
            raise ValueError("Not a valid mode for videos!")

        if mode == "use_all":
            frames = list(range(len(self.sim)))
        elif mode == "sample":
            fps = 30
            if len(self.sim) < fps * time:
                frames = list(range(len(self.sim)))
                fps = len(self.sim) / time
            else:
                frames = list(
                    np.round(np.linspace(0, len(self.sim) - 1, fps * time)).astype(int)
                )

        self.render_frames(frames, "temp")
        path = self.sim.path / "simulation.mp4"

        print("Assembling MP4...", flush=True)
        os.system(
            f"ffmpeg -hide_banner -loglevel error -r {fps} -i"
            + f' "{self.sim.path}/temp/img%05d.png"'
            + f" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -vf"
            + f' "scale=trunc(iw/2)*2:trunc(ih/2)*2" -f mp4 "{path}"'
        )

        # Remove files.
        for i in range(len(frames)):
            os.remove(self.sim.path / f"temp/img{i:05}.png")

        os.rmdir(self.sim.path / "temp")
        print(f'Wrote to "{path}".', flush=True)


def render_frame_range(combo: Tuple[Diagram, str, int, int, int]) -> None:
    self, fol, offset, length, num_frames = combo
    for i in range(length):
        self.generate_frame(i, "save", fol, f"img{i+offset:05}.png")
        i = len(list((self.sim.path / fol).iterdir()))
        hashes = int(21 * i / num_frames)
        print(
            f'Generating frames... |{"#"*hashes}{" "*(20-hashes)}|'
            + f" {i}/{num_frames} frames rendered.",
            flush=True,
            end="\r",
        )
