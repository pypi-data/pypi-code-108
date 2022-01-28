# -*- coding: utf-8 -*-
r"""
Python implementation of the NEB-method for a two dimensional configuration space. Greatly inspired by the
implementation of Stephan von Malottki. This can be used to create visualization of the paths and energy landscapes for
low dimensional systems. Useful for shematic explanations of the GNEB method in presentations or texts.
"""
import numpy as np
from typing import Callable, Union, Tuple
from pathlib import Path
import pandas as pd


class CNEB2D:
    r"""
    NEB-method for 2D configuration space
    """

    def __init__(self, f: Callable, initial: np.ndarray, final: np.ndarray, nim: int, ds: float = 0.00005,
                 kappa: float = 0.5, converge: float = 0.05, read_path_from_file: Union[Path, None] = None) -> None:
        r"""
        Initializer for the NEB-method

        Args:
            f(Callable): z = f(x,y)

            initial(np.ndarray): initial point for the path

            final(np.ndarray): final point for the path

            nim(int): number of images

            ds(float):

            kappa(float):

            converge(float):

            read_path_from_file: Read path from file. Default is None. In that case an initial path is created as the
            shortest distance between initial and final (line).

        """
        # physical inputs
        self._f = self._function_wrapper(f)
        if (len(initial) != 2) or (len(final) != 2):
            raise ValueError('Initial and final states have to be 2D points on the XY-plane.')
        self._initial = initial
        self._final = final
        self._nim = nim
        # simulation parameters:
        self._ds = ds
        self._kappa = kappa
        self._converge = converge
        self._displacement = converge * 5
        self._displacement_old = converge * 15.0
        # outputs:
        if read_path_from_file is None:
            self._path = self._create_initial_path()
        else:
            self._path = self.read_convergedpath_fromfile(file=read_path_from_file)

    def _function_wrapper(self, f: Callable) -> Callable:
        r"""
        This wrapper changes the input structure of the callable to be in line with the visualization interface. The
        visualization interface uses a function which takes f(x,y) while the methods in this class need a callable with
        the parameter f(r(x,y)). This wrapper provides this functionality.
        Args:
            f: takes a callable with the functionality f(x,y)

        Returns: a function with f(r).
        """

        def wrapper(r: np.ndarray) -> np.ndarray:
            if len(np.shape(r)) == 1:
                x = r[0]
                y = r[1]
            else:
                x = r[:, 0]
                y = r[:, 1]
            return f(x, y)

        return wrapper

    def _create_initial_path(self) -> np.ndarray:
        r"""
        Creates an initial path as the linear connection between the initial and final state.

        Returns:
            the initial path: [[x_ini,y_ini],[x1,y1],[x2,y2],...,[x_fin,y_fin]]
        """
        dx = (self._final[0] - self._initial[0]) / (self._nim - 1)
        dy = (self._final[1] - self._initial[1]) / (self._nim - 1)
        return np.array([[self._initial[0] + dx * i, self._initial[1] + dy * i] for i in range(self._nim)])

    def __call__(self, i_write_out: bool = False, gralog: int = 1000,
                 write_out: Path = Path.cwd() / 'NEB.dat') -> np.ndarray:
        r"""
        Calls the NEB algorithm!

        Args:
            gralog(int): frequency for writing the output
            write_out(True): in the frequency of gralog write the actual path to a file.

        Returns:
            the converged path
        """
        i = 1
        if i_write_out:
            write_dict = {'iteration': [0], 'force': [self._displacement], 'path': [self._path]}

        while self._displacement > self._converge:
            if np.mod(i, gralog) == 0:
                print(f"iteration GNEB: {i}, {self._displacement}")
                # Here we can produce the outputs!
                if i_write_out:
                    write_dict['iteration'].append(i)
                    write_dict['force'].append(self._displacement)
                    write_dict['path'].append(self._path)
                    df = pd.DataFrame(write_dict)
                    df.to_json(write_out)
            # updates self._path and self._displacement!
            self._relax_path_NEB()
            i += 1

        # final
        if i_write_out:
            write_dict['iteration'].append(i)
            write_dict['force'].append(self._displacement)
            write_dict['path'].append(self._path)
            df = pd.DataFrame(write_dict)
            df.to_json(write_out)
        return self._path

    def _relax_path_NEB(self):
        r"""
        Does one relaxations step with the forces of NEB algorithm
        """
        path_new = self._path.copy()
        l_dist, l_sd_r, l_sd_l = self._springs()
        force = 0.0

        for idx in range(1, len(self._path) - 1):
            dp = 0.01
            p = self._path[idx]
            dfdx, dfdy = self._calc_derivative(p, dp)
            dEr = self._f(self._path[idx + 1]) - self._f(p)
            dEl = self._f(p) - self._f(self._path[idx - 1])
            dE_max = max(np.abs(dEr), np.abs(dEl))
            dE_min = min(np.abs(dEr), np.abs(dEl))
            sd = l_sd_r[idx]

            if self._f(self._path[idx + 1]) > self._f(p) > self._f(self._path[idx - 1]):
                sd = l_sd_r[idx]
            elif self._f(self._path[idx + 1]) < self._f(p) < self._f(self._path[idx - 1]):
                sd = l_sd_l[idx]
            elif self._f(self._path[idx + 1]) > self._f(self._path[idx - 1]):
                sd[0] = l_sd_r[idx][0] * dE_max + l_sd_l[idx][0] * dE_min
                sd[1] = l_sd_r[idx][1] * dE_max + l_sd_l[idx][1] * dE_min
            else:
                sd[0] = l_sd_r[idx][0] * dE_min + l_sd_l[idx][0] * dE_max
                sd[1] = l_sd_r[idx][1] * dE_min + l_sd_l[idx][1] * dE_max
            # normalize direction
            sd = sd / np.linalg.norm(sd)
            dfdx_new = dfdx - np.dot([dfdx, dfdy], sd) * sd[0]
            dfdy_new = dfdy - np.dot([dfdx, dfdy], sd) * sd[1]
            dfdx = dfdx_new
            dfdy = dfdy_new
            force = max(force, np.sqrt(
                (-dfdx + sd[0] * l_dist[idx] * self._kappa) ** 2 + (-dfdy + sd[1] * l_dist[idx] * self._kappa) ** 2))

        for i in range(1, len(self._path) - 1):
            dp = 0.01
            case = 0
            p = self._path[i]
            dfdx, dfdy = self._calc_derivative(p, dp)
            dEr = self._f(self._path[i + 1]) - self._f(self._path[i])
            dEl = self._f(self._path[i]) - self._f(self._path[i - 1])
            dE_max = max(np.abs(dEr), np.abs(dEl))
            dE_min = min(np.abs(dEr), np.abs(dEl))
            sd = l_sd_r[i]
            if self._f(self._path[i + 1]) > self._f(self._path[i]) > self._f(self._path[i - 1]):
                sd = l_sd_r[i]
                case = 1
            elif self._f(self._path[i + 1]) < self._f(self._path[i]) < self._f(self._path[i - 1]):
                sd = l_sd_l[i]
                case = 2
            elif self._f(self._path[i + 1]) > self._f(self._path[i - 1]):
                sd[0] = l_sd_r[i][0] * dE_max + l_sd_l[i][0] * dE_min
                sd[1] = l_sd_r[i][1] * dE_max + l_sd_l[i][1] * dE_min
                case = 3
            else:
                sd[0] = l_sd_r[i][0] * dE_min + l_sd_l[i][0] * dE_max
                sd[1] = l_sd_r[i][1] * dE_min + l_sd_l[i][1] * dE_max
                case = 4
            sd = sd / np.linalg.norm(sd)
            dfdx_new = dfdx - np.dot([dfdx, dfdy], sd) * sd[0]
            dfdy_new = dfdy - np.dot([dfdx, dfdy], sd) * sd[1]
            dfdx = dfdx_new
            dfdy = dfdy_new
            image_new_x = self._path[i][0] + (-dfdx + sd[0] * l_dist[i] * self._kappa) * self._ds / force
            image_new_y = self._path[i][1] + (-dfdy + sd[1] * l_dist[i] * self._kappa) * self._ds / force
            path_new[i][0] = image_new_x
            path_new[i][1] = image_new_y
        self._displacement = force
        self._path = path_new

    def _springs_previous(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        r"""

        """
        sd_r = np.zeros(shape=(len(self._path) - 1, 2))
        sd_l = np.zeros(shape=(len(self._path) - 1, 2))
        sd_r[1:] = np.diff(self._path[:-1], axis=0)
        sd_l[1:] = np.diff(self._path[1:], axis=0)
        distance = np.linalg.norm(sd_r, axis=1) - np.linalg.norm(sd_l, axis=1)
        return distance, sd_r, sd_l

    def _springs(self):
        distance = [0]
        sd_r = [[0, 0]]
        sd_l = [[0, 0]]
        for i in range(1, len(self._path) - 1):
            dx_l = self._path[i][0] - self._path[i - 1][0]
            dx_r = self._path[i + 1][0] - self._path[i][0]
            dy_l = self._path[i][1] - self._path[i - 1][1]
            dy_r = self._path[i + 1][1] - self._path[i][1]
            dr_l = np.sqrt(dx_l ** 2 + dy_l ** 2)
            dr_r = np.sqrt(dx_r ** 2 + dy_r ** 2)
            ddr = dr_r - dr_l
            distance.append(ddr)
            #      spring_directions.append([(dx_r/norm_r+dx_l/norm_l)/2.0,(dy_r/norm_r+dy_l/norm_l)/2.0])
            #      norm_sd=np.sqrt((dx_r+dx_l)**2+(dy_r+dy_l)**2)
            #      sd_x=(dx_r+dx_l)/norm_sd
            #      sd_y=(dy_r+dy_l)/norm_sd
            sd_r.append([dx_r, dy_r])
            sd_l.append([dx_l, dy_l])
        return distance, sd_r, sd_l

    def _calc_derivative(self, p: np.ndarray, dp: float) -> Tuple[float, float]:
        r"""
        Calculates the finite element derivative of the function f for the image p

        Args:
            p(np.ndarray): current image
            dp(float): step width

        Returns:
            dfdx: derivative in x direction, dfdy: derivative in y direction
        """
        dfdx = (self._f([p[0] + dp, p[1]]) - self._f([p[0] - dp, p[1]])) / (2.0 * dp)
        dfdy = (self._f([p[0], p[1] + dp]) - self._f([p[0], p[1] - dp])) / (2.0 * dp)
        return dfdx, dfdy

    @staticmethod
    def read_convergedpath_fromfile(file: Path) -> np.ndarray:
        r"""
        The path is sometimes written to files to avoid re-computing the path again and again

        Args:
            file: path saved in file

        Returns:
            the last path (mostly the converged one) (sequence of points)
        """
        df = pd.read_json(file)
        max_iter = np.max(df['iteration'].to_numpy())
        path = df['path'][df['iteration'] == max_iter].to_list()
        pl = []
        for p in path[0]:
            pl.append(np.array(p))
        return np.vstack(tuple(pl))


class CciNEB2d:
    r"""
    The climbing image implementation of the two dimensional NEB. Inheriting from the NEB method.
    """

    def __init__(self, function: Callable, file: Path, ds: float = 0.00005, kappa: float = 0.5,
                 converge: float = 0.05) -> None:
        r"""
        Initializes the ci GNEB method

        Args:
            path: file of a converged GNEB calculation. The climbing image method needs some kind of start path
        """
        self._path = self.read_convergedpath_fromfile(file)
        self._f = self._function_wrapper(function)
        self._kappa = kappa
        self._converge = converge
        self._ds = ds
        self._displacement = converge * 5
        self._ci = self.find_ci()

    def find_ci(self) -> int:
        r"""
        Returns:
            the index of the current climbing image (image with the highest energy
        """
        ci = 0
        z_max = self._f(self._path[0])
        for (i, image) in enumerate(self._path):
            if self._f(image) > z_max:
                z_max = self._f(image)
                ci = i
        return ci

    def _function_wrapper(self, f: Callable) -> Callable:
        r"""
        This wrapper changes the input structure of the callable to be in line with the visualization interface. The
        visualization interface uses a function which takes f(x,y) while the methods in this class need a callable with
        the parameter f(r(x,y)). This wrapper provides this functionality.
        Args:
            f: takes a callable with the functionality f(x,y)

        Returns: a function with f(r).
        """

        def wrapper(r: np.ndarray) -> np.ndarray:
            if len(np.shape(r)) == 1:
                x = r[0]
                y = r[1]
            else:
                x = r[:, 0]
                y = r[:, 1]
            return f(x, y)

        return wrapper

    def __call__(self, i_write_out: bool = False, gralog: int = 1000,
                 write_out: Path = Path.cwd() / 'ciNEB.dat') -> Tuple[np.ndarray, int]:
        r"""
        Calls the ciNEB algorithm!

        Args:
            gralog(int): frequency for writing the output
            write_out(True): in the frequency of gralog write the actual path to a file.

        Returns:
            the converged path, and the saddlepoint
        """
        i = 1
        if i_write_out:
            write_dict = {'iteration': [0], 'force': [self._displacement], 'path': [self._path]}

        while self._displacement > self._converge:
            if np.mod(i, gralog) == 0:
                print(f"iteration ciNEB: {i}, {self._displacement}")
                # Here we can produce the outputs!
                if i_write_out:
                    write_dict['iteration'].append(i)
                    write_dict['force'].append(self._displacement)
                    write_dict['path'].append(self._path)
                    df = pd.DataFrame(write_dict)
                    df.to_json(write_out)
            # updates self._path and self._displacement!
            self._ci = self.find_ci()
            l_displacement_old = self._displacement
            self._relax_path_ciNEB()
            if abs(l_displacement_old-self._displacement) <= 0.0000001:
                break
            i += 1

        # final
        if i_write_out:
            write_dict['iteration'].append(i)
            write_dict['force'].append(self._displacement)
            write_dict['path'].append(self._path)
            df = pd.DataFrame(write_dict)
            df.to_json(write_out)
        return self._path, self._ci

    def _relax_path_ciNEB(self):
        r"""
        Does one relaxations step with the forces of ciNEB algorithm
        """
        path_new = self._path.copy()
        l_dist, l_sd_r, l_sd_l = self._springs()
        force = 0.0

        for idx in range(1, len(self._path) - 1):
            dp = 0.01
            p = self._path[idx]
            dfdx, dfdy = self._calc_derivative(p, dp)
            dEr = self._f(self._path[idx + 1]) - self._f(p)
            dEl = self._f(p) - self._f(self._path[idx - 1])
            dE_max = max(np.abs(dEr), np.abs(dEl))
            dE_min = min(np.abs(dEr), np.abs(dEl))
            sd = l_sd_r[idx]

            if self._f(self._path[idx + 1]) > self._f(p) > self._f(self._path[idx - 1]):
                sd = l_sd_r[idx]
            elif self._f(self._path[idx + 1]) < self._f(p) < self._f(self._path[idx - 1]):
                sd = l_sd_l[idx]
            elif self._f(self._path[idx + 1]) > self._f(self._path[idx - 1]):
                sd[0] = l_sd_r[idx][0] * dE_max + l_sd_l[idx][0] * dE_min
                sd[1] = l_sd_r[idx][1] * dE_max + l_sd_l[idx][1] * dE_min
            else:
                sd[0] = l_sd_r[idx][0] * dE_min + l_sd_l[idx][0] * dE_max
                sd[1] = l_sd_r[idx][1] * dE_min + l_sd_l[idx][1] * dE_max
            # normalize direction
            sd = sd / np.linalg.norm(sd)
            if idx == self._ci:
                dfdx_new = dfdx - 2.0 * np.dot([dfdx, dfdy], sd) * sd[0]
                dfdy_new = dfdy - 2.0 * np.dot([dfdx, dfdy], sd) * sd[1]
                dfdx = dfdx_new
                dfdy = dfdy_new
            else:
                dfdx_new = dfdx - np.dot([dfdx, dfdy], sd) * sd[0]
                dfdy_new = dfdy - np.dot([dfdx, dfdy], sd) * sd[1]
                dfdx = dfdx_new
                dfdy = dfdy_new
            force = max(force, np.sqrt(
                (-dfdx + sd[0] * l_dist[idx] * self._kappa) ** 2 + (-dfdy + sd[1] * l_dist[idx] * self._kappa) ** 2))

        for i in range(1, len(self._path) - 1):
            dp = 0.01
            case = 0
            p = self._path[i]
            dfdx, dfdy = self._calc_derivative(p, dp)
            dEr = self._f(self._path[i + 1]) - self._f(self._path[i])
            dEl = self._f(self._path[i]) - self._f(self._path[i - 1])
            dE_max = max(np.abs(dEr), np.abs(dEl))
            dE_min = min(np.abs(dEr), np.abs(dEl))
            sd = l_sd_r[i]
            if self._f(self._path[i + 1]) > self._f(self._path[i]) > self._f(self._path[i - 1]):
                sd = l_sd_r[i]
                case = 1
            elif self._f(self._path[i + 1]) < self._f(self._path[i]) < self._f(self._path[i - 1]):
                sd = l_sd_l[i]
                case = 2
            elif self._f(self._path[i + 1]) > self._f(self._path[i - 1]):
                sd[0] = l_sd_r[i][0] * dE_max + l_sd_l[i][0] * dE_min
                sd[1] = l_sd_r[i][1] * dE_max + l_sd_l[i][1] * dE_min
                case = 3
            else:
                sd[0] = l_sd_r[i][0] * dE_min + l_sd_l[i][0] * dE_max
                sd[1] = l_sd_r[i][1] * dE_min + l_sd_l[i][1] * dE_max
                case = 4
            sd = sd / np.linalg.norm(sd)
            if idx == self._ci:
                dfdx_new = dfdx - 2.0 * np.dot([dfdx, dfdy], sd) * sd[0]
                dfdy_new = dfdy - 2.0 * np.dot([dfdx, dfdy], sd) * sd[1]
                dfdx = dfdx_new
                dfdy = dfdy_new
            else:
                dfdx_new = dfdx - np.dot([dfdx, dfdy], sd) * sd[0]
                dfdy_new = dfdy - np.dot([dfdx, dfdy], sd) * sd[1]
                dfdx = dfdx_new
                dfdy = dfdy_new
            if idx == self._ci:
                image_new_x = self._path[i][0] + (-dfdx) * self._ds / force
                image_new_y = self._path[i][1] + (-dfdy) * self._ds / force
            else:
                image_new_x = self._path[i][0] + (-dfdx + sd[0] * l_dist[i] * self._kappa) * self._ds / force
                image_new_y = self._path[i][1] + (-dfdy + sd[1] * l_dist[i] * self._kappa) * self._ds / force
            path_new[i][0] = image_new_x
            path_new[i][1] = image_new_y
        self._displacement = force
        self._path = path_new

    @staticmethod
    def read_convergedpath_fromfile(file: Path) -> np.ndarray:
        r"""
        The path is sometimes written to files to avoid re-computing the path again and again

        Args:
            file: path saved in file

        Returns:
            the last path (mostly the converged one) (sequence of points)
        """
        df = pd.read_json(file)
        max_iter = np.max(df['iteration'].to_numpy())
        path = df['path'][df['iteration'] == max_iter].to_list()
        pl = []
        for p in path[0]:
            pl.append(np.array(p))
        return np.vstack(tuple(pl))

    def _springs(self):
        distance = [0]
        sd_r = [[0, 0]]
        sd_l = [[0, 0]]
        for i in range(1, len(self._path) - 1):
            dx_l = self._path[i][0] - self._path[i - 1][0]
            dx_r = self._path[i + 1][0] - self._path[i][0]
            dy_l = self._path[i][1] - self._path[i - 1][1]
            dy_r = self._path[i + 1][1] - self._path[i][1]
            dr_l = np.sqrt(dx_l ** 2 + dy_l ** 2)
            dr_r = np.sqrt(dx_r ** 2 + dy_r ** 2)
            ddr = dr_r - dr_l
            distance.append(ddr)
            #      spring_directions.append([(dx_r/norm_r+dx_l/norm_l)/2.0,(dy_r/norm_r+dy_l/norm_l)/2.0])
            #      norm_sd=np.sqrt((dx_r+dx_l)**2+(dy_r+dy_l)**2)
            #      sd_x=(dx_r+dx_l)/norm_sd
            #      sd_y=(dy_r+dy_l)/norm_sd
            sd_r.append([dx_r, dy_r])
            sd_l.append([dx_l, dy_l])
        return distance, sd_r, sd_l

    def _calc_derivative(self, p: np.ndarray, dp: float) -> Tuple[float, float]:
        r"""
        Calculates the finite element derivative of the function f for the image p

        Args:
            p(np.ndarray): current image
            dp(float): step width

        Returns:
            dfdx: derivative in x direction, dfdy: derivative in y direction
        """
        dfdx = (self._f([p[0] + dp, p[1]]) - self._f([p[0] - dp, p[1]])) / (2.0 * dp)
        dfdy = (self._f([p[0], p[1] + dp]) - self._f([p[0], p[1] - dp])) / (2.0 * dp)
        return dfdx, dfdy
