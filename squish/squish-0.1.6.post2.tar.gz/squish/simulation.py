from __future__ import annotations
from typing import Optional

import pickle, numpy as np
from math import log10, sqrt
from scipy.linalg import null_space
from timeit import default_timer as timer
from pathlib import Path

from .common import DomainParams, Energy, generate_filepath, OUTPUT_DIR


class Simulation:
    """Generic container for simulations.

    Attributes:
        domain (DomainParams): Domain Parameters for this simulation.
        energy (Energy): energy being used for caluclations.
        path (Path): Path to location of where to store simulation files.
        frames (List[VoronoiContainer]): Stores frames of the simulation.

    """

    __slots__ = ["domain", "energy", "path", "frames"]

    def __init__(
        self, domain: DomainParams, energy: Energy, name: Optional[str, int] = None
    ) -> None:
        self.domain, self.energy = domain, energy
        self.frames = []

        if name is None:
            self.path = generate_filepath(self, OUTPUT_DIR)
        elif isinstance(name, int):
            self.path = generate_filepath(self, OUTPUT_DIR, name)
        else:
            self.path = OUTPUT_DIR / name

    def __iter__(self) -> Iterator:
        return iter(self.frames)

    def __getitem__(self, key: int) -> Energy:
        return self.frames[key]

    def __len__(self) -> int:
        return len(self.frames)

    def add_frame(self, points: Optional[numpy.ndarray] = None) -> None:
        if points is None:
            points = np.random.random_sample((self.domain.n, 2)) * self.domain.dim
        else:
            if points.shape[1] != 2 or len(points.shape) > 2:
                raise ValueError("Sites should be 2 dimensional!")

            if points.shape[0] != self.domain.n:
                raise ValueError("Number of sites provided do not match the array!")

        self.frames.append(self.energy.mode(*self.domain, points % self.domain.dim))

    def normalize(self) -> None:
        new_frames = []
        for frame in self.frames:
            aspect = frame.w / frame.h
            new_domain = DomainParams(
                frame.n, sqrt(frame.n * aspect), sqrt(frame.n / aspect), frame.r
            )

            new_points = frame.site_arr * np.array(
                [new_domain.w / frame.w, new_domain.h / frame.h]
            )

            new_frames.append(self.energy.mode(*new_domain, new_points))

        self.frames = new_frames

    def get_distinct(self) -> List[int]:
        """Gets the distinct configurations based on the average radii of the sites.
        and returns the number of configurations for each distinct configuration.
        """

        distinct_avg_radii, distinct_count, new_frames = [], [], []

        for frame in self.frames:
            try:
                stats = frame.stats
            except AttributeError:
                stats = frame["stats"]  # When we have a loaded simulations.

            avg_radii = np.sort(stats["avg_radius"])
            is_in = False
            for i, dist_radii in enumerate(distinct_avg_radii):
                if np.allclose(avg_radii, dist_radii, atol=1e-5):
                    is_in = True
                    distinct_count[i] += 1
                    break

            if not is_in:
                distinct_avg_radii.append(avg_radii)
                distinct_count.append(1)
                new_frames.append(frame)

        self.frames = new_frames
        return distinct_count

    def save(self, info: Dict, overwrite: bool = False) -> None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        self.path.mkdir(exist_ok=True)
        path = self.path / "data.squish"

        with open(path, "wb" if overwrite else "ab") as out:
            pickle.dump(info, out, pickle.HIGHEST_PROTOCOL)

    def save_all(self) -> None:
        self.save(self.initial_data, True)
        for i in range(len(self.frames)):
            self.save(self.frame_data(i))

    def frame_data(self, index: int) -> None:
        f = self[index]
        info = {
            "arr": f.site_arr,
            "domain": (f.n, f.w, f.h, f.r),
            "energy": f.energy,
            "stats": f.stats,
        }
        return info

    @staticmethod
    def load(path: str) -> Tuple[Simulation, Generator]:
        path = Path(path)

        def frames() -> Dict:
            with open(path / "data.squish", "rb") as infile:
                first = True
                while True:
                    try:
                        if first:
                            pickle.load(infile)
                            first = False
                            continue
                        yield pickle.load(infile)
                    except EOFError:
                        break

        with open(path / "data.squish", "rb") as infile:
            sim_info = pickle.load(infile)

            domain = DomainParams(*sim_info["domain"])
            energy = Energy(sim_info["energy"])
            sim = STR_TO_SIM[sim_info["mode"]](
                domain, energy, *list(sim_info.values())[3:]
            )
            sim.path = path

            return sim, frames()

    @staticmethod
    def from_file(path: str) -> Simulation:
        sim, frames = Simulation.load(path)
        for frame in frames:
            sim.frames.append(sim.energy.mode(*frame["domain"], frame["arr"]))
            sim.frames[-1].stats = frame["stats"]

        return sim


class Flow(Simulation):
    """Finds an equilibrium from initial sites.

    Attributes:
        domain (DomainParams): domain parameters for this simulation.
        energy (Energy): energy being used for caluclations.
        path (Path): path to the location of where to store simulation files.
        frames (List[VoronoiContainer]): stores frames of the simulation.
        step_size (float): size fo step by for each iteration.
        thres (float): threshold for the stopping condition.
        adaptive (bool): set to True if adaptive stepping is desired.

    """

    __slots__ = ["step_size", "thres", "adaptive"]
    attr_str = "flow"
    title_str = "Flow"

    def __init__(
        self,
        domain: DomainParams,
        energy: Energy,
        step_size: float,
        thres: float,
        adaptive: bool,
        name: Optional[str] = None,
    ) -> None:
        super().__init__(domain, energy, name=name)
        self.step_size, self.thres, self.adaptive = step_size, thres, adaptive

    @property
    def initial_data(self) -> Dict:
        info = {
            "mode": self.attr_str,
            "domain": (self.domain.n, self.domain.w, self.domain.h, self.domain.r),
            "energy": self.energy.attr_str,
            "step_size": self.step_size,
            "thres": self.thres,
            "adaptive": self.adaptive,
        }
        return info

    def run(
        self,
        save: bool,
        log: bool,
        log_steps: int,
        new_sites: Optional[numpy.ndarray] = None,
    ) -> None:
        if log:
            print(f"Find - {self.domain}", flush=True)
        if save and len(self) == 0:
            self.save(self.initial_data, True)
        if len(self) == 0:
            self.add_frame(new_sites)

        i, stop = len(self) - 1, False

        while not stop:  # Get to threshold.
            if save:
                self.save(self.frame_data(i))
                frame = self[i]
            else:
                frame = self[0]

            # Iterate and generate next frame using RK-2
            start = timer()
            change, grad = frame.iterate(self.step_size)

            new_frame = self.energy.mode(*self.domain, frame.add_sites(change))
            grad_norm = np.linalg.norm(grad)
            end = timer()

            if self.adaptive:
                error = change - grad * self.step_size
                tol = 10 ** min(-4, -3 + log10(grad_norm))
                # tol = 10 ** -7
                self.step_size *= (tol / np.linalg.norm(error)) ** 0.5

            if not save:
                del self.frames[0]

            self.frames.append(new_frame)
            stop = grad_norm < self.thres

            i += 1
            if (log and i % log_steps == 0) or stop:
                print(
                    f"Iteration: {i:05} | Energy: {frame.energy: .5f}"
                    + f" | Gradient: {grad_norm:.8f} | Step: {self.step_size: .5f} | "
                    + f"Time: {end-start: .3f} |",
                    flush=True,
                )


class Search(Simulation):
    """Searches for a given number of equilibria.

    Attributes:
        domain (DomainParams): domain parameters for this simulation.
        energy (Energy): energy being used for caluclations.
        path (Path): path to the location of where to store simulation files.
        frames (List[VoronoiContainer]): stores frames of the simulation.
        step_size (float): size fo step by for each iteration.
        thres (float): threshold for the stopping condition.
        adaptive (bool): set to True if adaptive stepping is desired.
        kernel_step (float): size to step on manifold if nullity of hessian > 2.
        count (int): number of equilibria to find.

    """

    __slots__ = ["step_size", "thres", "adaptive", "kernel_step", "count"]
    attr_str = "search"
    title_str = "Search"

    def __init__(
        self,
        domain: DomainParams,
        energy: Energy,
        step_size: float,
        thres: float,
        adaptive: bool,
        kernel_step: float,
        count: int,
        name: Optional[str] = None,
    ) -> None:
        super().__init__(domain, energy, name=name)
        self.step_size, self.thres, self.adaptive = step_size, thres, adaptive
        self.kernel_step, self.count = kernel_step, count

    @property
    def initial_data(self) -> Dict:
        info = {
            "mode": self.attr_str,
            "domain": (self.domain.n, self.domain.w, self.domain.h, self.domain.r),
            "energy": self.energy.attr_str,
            "step_size": self.step_size,
            "thres": self.thres,
            "adaptive": self.adaptive,
            "kernel_step": self.kernel_step,
            "count": self.count,
        }
        return info

    def run(
        self,
        save: bool,
        log: bool,
        log_steps: int,
        new_sites: Optional[numpy.ndarray] = None,
    ) -> None:
        if log:
            print(f"Search - {self.domain} - {len(self)}", flush=True)
        if save and len(self) == 0:
            self.save(self.initial_data, True)

        for i in range(len(self), self.count):
            # Get to equilibrium.
            sim = Flow(
                self.domain, self.energy, self.step_size, self.thres, self.adaptive
            )
            sim.add_frame(new_sites)
            sim.run(False, log, log_steps)

            self.frames.append(sim[-1])
            # Get Hessian,and check nullity. If > 2, perturb.
            hess = self.frames[i].hessian
            eigs = np.sort(np.linalg.eig(hess)[0])
            self.frames[i].stats["eigs"] = eigs

            if save:
                self.save(self.frame_data(i))
            if log:
                print(f"Equilibrium: {i:04}\n", flush=True)
            zero_eigs = np.count_nonzero(
                np.isclose(eigs, np.zeros((len(eigs),)), atol=1e-4)
            )

            if zero_eigs == 2:
                new_sites = None
            else:
                print("Warning: Nullity > 2. Expected if AreaEnergy.", flush=True)
                ns = null_space(hess, 10e-4).T
                vec = ns[random.randint(0, len(ns) - 1)].reshape(
                    (self.domain.n, 2)
                )  # Random vector.
                new_sites = self.frames[i].add_sites(self.kernel_step * vec)


class Shrink(Simulation):
    """Shrinks width and finds nearest equilibrium.

    Attributes:
        domain (DomainParams): domain parameters for this simulation.
        energy (Energy): energy being used for calcu1lations.
        path (Path): path to the location of where to store simulation files.
        frames (List[VoronoiContainer]): stores frames of the simulation.
        step_size (float): size fo step by for each iteration.
        thres (float): threshold for the stopping condition.
        adaptive (bool): set to True if adaptive stepping is desired.
        delta (float): percent to change w each iteration.
        stop_width (float): percent at which to stop iterating.

    """

    __slots__ = ["step_size", "thres", "adaptive", "delta", "stop_width"]
    attr_str = "shrink"
    title_str = "Shrink"

    def __init__(
        self,
        domain: DomainParams,
        energy: Energy,
        step_size: float,
        thres: float,
        adaptive: bool,
        delta: float,
        stop_width: float,
        name: Optional[str] = None,
    ) -> None:
        super().__init__(domain, energy, name=name)
        self.step_size, self.thres, self.adaptive = step_size, thres, adaptive
        self.delta, self.stop_width = (
            self.domain.w * delta / 100,
            self.domain.w * stop_width,
        )

    @property
    def initial_data(self) -> Dict:
        info = {
            "mode": self.attr_str,
            "domain": (self.domain.n, self.domain.w, self.domain.h, self.domain.r),
            "energy": self.energy.attr_str,
            "step_size": self.step_size,
            "thres": self.thres,
            "adaptive": self.adaptive,
            "delta": self.delta,
            "stop_width": self.stop_width,
        }
        return info

    def run(
        self,
        save: bool,
        log: bool,
        log_steps: int,
        new_sites: Optional[numpy.ndarray] = None,
    ) -> None:
        if log:
            print(f"Shrink - {self.domain}", flush=True)
        if save and len(self) == 0:
            self.save(self.initial_data, True)

        width = self.domain.w if len(self.frames) == 0 else self.frames[-1].w
        i = 0
        while width >= self.stop_width:
            # Get to equilibrium.
            new_domain = DomainParams(
                self.domain.n, width, self.domain.h, self.domain.r
            )
            sim = Flow(
                new_domain, self.energy, self.step_size, self.thres, self.adaptive
            )
            sim.add_frame(new_sites)
            sim.run(False, log, log_steps)
            new_sites = sim[-1].site_arr

            self.frames.append(sim[-1])
            if save:
                self.save(self.frame_data(i))

            if log:
                print(f"Width: {width:.4f}\n")

            width -= self.delta
            i += 1


STR_TO_SIM = {"flow": Flow, "search": Search, "shrink": Shrink}
