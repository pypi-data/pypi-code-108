# -*- coding: utf-8 -*-
r"""
Pyvista implementation for visualizing energy surface on 2d configuration spaces.
"""
import numpy as np
import pyvista as pv
from pathlib import Path
from spinterface.visualizations.energylandscapes.ivisualizer import IVisualizer
from spinterface.visualizations.energylandscapes.i2dfunction import I2DFunction
from typing import Union, List, Tuple


class CVisualPyVista(IVisualizer):
    r"""
    Pyvista implementation for visualizing function on 2d space
    """

    def __init__(self, x: np.ndarray, y: np.ndarray, function: I2DFunction,
                 cam: Union[List[Tuple[float, float, float]], None] = None) -> None:
        r"""
        Initializes the visualization

        Args:
            x(np.array): x array - can be created with linspace (together with y a meshgrid will be created.
            y(np.array): y array - can be created with linspace (together with x a meshgrid will be created.
            function (I2DFunction): function which meets the requirements for this visualization technique
            camera: camera position, default None
        """
        super().__init__(x=x, y=y, function=function)
        self.cam = cam
        self.meshes_options, self.meshes = [], []
        self._make_plotter()

    def add_mesh(self, mesh, **kwargs):
        self.plotter.add_mesh(mesh, **kwargs)
        self.meshes_options.append(dict(**kwargs))
        self.meshes.append(mesh)

    def _make_plotter(self, offscreen: bool = False):
        r"""
        Creates the plotter. The plotter will be recreated when saving the image
        """
        self._configureplotter(offscreen)
        self.plotter.camera_position = self.cam
        self._cloud = self._make_pointcloud()
        # delaunay_
        self._surf = self._triangulation()
        # use height information for cmap and contour plots
        self._surf.point_arrays['scalars'] = self._surf.points[:, 2]
        self._cont = self._surf.contour()
        self.plotter.add_mesh(self._surf, scalars='scalars', show_scalar_bar=False)
        self.plotter.add_mesh(self._cont, color='white', show_scalar_bar=False, line_width=3.5)
        for (idx, mesh) in enumerate(self.meshes):
            self.plotter.add_mesh(mesh, **self.meshes_options[idx])

    def _triangulation(self, technique: str = 'delaunay_2d') -> pv.PolyData:
        r"""
        Creates pyvista surface from point cloud

        Args:
            technique(str): technique which is used for triangulation

        Returns:
            the triangulated surface in pyvista fashion
        """
        if technique == 'delaunay_2d':
            return self._cloud.delaunay_2d()
        else:
            raise NotImplementedError('Triangulation technique not implemented yet.')

    def _make_pointcloud(self) -> pv.PolyData:
        r"""
        Takes the points from the grid defined on the 2d conf. space together with the function values and creates
        a 3D point cloud with the requirements of pyvista.

        Returns:
            pyvista polydata object for further use
        """
        self.r = np.dstack([self.xgrid, self.ygrid, self.zgrid])
        self.rr = np.reshape(self.r, (self.r.shape[0] * self.r.shape[1], self.r.shape[2]))
        return pv.PolyData(self.rr)

    def _configureplotter(self, offscreen: bool) -> None:
        r"""
        Configures the plotter object
        """
        theme = pv.themes.ParaViewTheme()
        theme.transparent_background = True
        self.plotter = pv.Plotter(off_screen=offscreen, lighting='three lights', theme=theme)

        def cam() -> None:
            print('Camera postion: ', self.plotter.camera_position)

        self.plotter.add_key_event('c', cam)

    def __call__(self, outpath: Path = Path.cwd() / 'landscape.png'):
        r"""
        Saves the image to a file

        Args:
            outpath(Path): output path for the png image created.
        """
        self._make_plotter(offscreen=True)
        self.plotter.window_size = [4000, 4000]
        self.plotter.screenshot(str(outpath.stem))

    def show(self) -> None:
        r"""
        Shows the plotter
        """
        print('Look what you have done.......')
        print('to get current cam-position press key c')
        self.plotter.show()

    def show_grid_topview(self) -> None:
        r"""
        Shows the topview with grid to get an idea concerning the position of points
        """
        self.plotter.show_grid(color='k')
        self.plotter.view_xy()
        self.plotter.show()

    def placepointonsurface(self, xypoint: np.ndarray, color: str = 'k', point_size: float = 20) -> np.ndarray:
        r"""
        Projects a 2d point on the energy surface and add the mesh to the plotter

        Args:
            xypoint: 2d numpy array which will be projected

        Returns:
            xyz coordinates of point
        """
        if len(xypoint) != 2:
            raise ValueError("xypoint has to have length 2 (xy-coords.)")
        l_point = self.projectosurface(xypoint=xypoint)
        l_pointpolydata = pv.PolyData(l_point)
        self.add_mesh(l_pointpolydata, color=color, point_size=point_size, render_points_as_spheres=True)
        return l_point

    def projectosurface(self, xypoint: np.ndarray) -> np.ndarray:
        r"""
        Takes a 2D point, projects it on the surface (f(x,y)) and returns a 3d point
        Args:
            xypoint: array

        Returns:
            [x,y,f(x,y)]
        """
        z = self.func(x=xypoint[0], y=xypoint[1])
        return np.array([xypoint[0], xypoint[1], z])

    def placepointsequenceonsurface(self, seq_xypoint: np.ndarray, color_points: str = 'k', color_line: str = 'gray',
                                    point_size: float = 20, tuberadius: float = 0.025) -> np.ndarray:
        r"""
        Places a sequence of points on the 2d surface and connect them with a tube.

        Args:
            seq_xypoint: a sequence of 2d points: [[x1,y1],[x2,y2],...]
            color_points: the color of the points
            color_line: the color of the connecting tube
            point_size: the size of the points

        Returns:
            the sequence of points in 3D [[x1,y1,f(x1,y1)],...]
        """

        def build_path_section(start: np.ndarray, end: np.ndarray, num: int = 10) -> List[np.ndarray]:
            r"""
            gets the xy position of a start and endpoint and distributes num equally space points between them.

            Args:
                start: 3d point
                end: 3d point
                num: number of intermediate points

            Returns:
                all points
            """
            vec = end - start
            l = np.linalg.norm(vec) / float(num)
            points = []
            for i in range(num + 1):
                p2d = start.copy() + l * i * (vec / np.linalg.norm(vec))
                points.append(p2d)
            return points

        if np.shape(seq_xypoint)[1] != 2:
            raise ValueError("sequence has to have xypoints with length 2 (xy-coords.)")
        z = self.func(x=seq_xypoint[:, 0], y=seq_xypoint[:, 1])
        l_points = np.column_stack((seq_xypoint[:, 0], seq_xypoint[:, 1], z))
        l_pointpolydata = pv.PolyData(l_points)
        path = []
        for (idx, point) in enumerate(l_points[:-1]):
            path.extend(build_path_section(start=point, end=l_points[idx + 1]))
        spline = pv.Spline(path, 1000)
        spline["scalars"] = np.arange(spline.n_points)
        self.add_mesh(spline.tube(radius=tuberadius), smooth_shading=True, color=color_line)
        self.add_mesh(l_pointpolydata, color=color_points, point_size=point_size, render_points_as_spheres=True)
        return l_points

    @staticmethod
    def paraboloid(x: np.ndarray, y: np.ndarray, x0: float, y0: float, eps_x: float, eps_y: float,
                   yoffset: float) -> np.ndarray:
        r"""

        Args:
            x: x array for the 2d points
            y: y array for the 2d points
            x0,y0: zero point
            eps_x, eps_y: prefactor for the paraboloid directions x and y, if one of the eps-values is negative the
            result is a hyperbolic paraboloid.

        Returns:
            f(x) = eps_x * x^2 + eps_y * y^2
        """
        # the following does not work!
        # angle between first eigenvector and the x axis
        # phi = np.arccos(evec[0]/np.linalg.norm(evec))
        # return eps_x * (np.cos(phi) *(x-x0)-np.sin(phi * (y-y0))) ** 2 + eps_y * (np.sin(phi) * (x-x0) + np.cos(phi) * (y-y0)) ** 2 + yoffset
        return eps_x * (x - x0) ** 2 + eps_y * (y - y0) ** 2 + yoffset

    def create_eigenvalue_parabola(self, point: np.ndarray, evals: np.ndarray, evecs: np.ndarray, nr_points: int = 10,
                                   point_distance_xy: float = 1.0, color_points: str = 'k', color_line: str = 'gray',
                                   point_size: float = 20, tuberadius: float = 0.025, show_surface: bool = True,
                                   x_width: float = 2,
                                   y_width: float = 2, y_offset: float = 0.0) -> None:
        r"""
        Creates the two parabolas representing the diagonalization of the hessian for a given state. This means
        visualizing a parabola (with curvature of the eigenvalue eps) in the direction of each eigenvector
        f(p) = eps * dp + p0

        with dp = |p-p0| and p0 the initial point

        Args:
            show_surface: boolean whether the paraboloic surface will be visualized as a surface
            color_line: color of the line parabola along the certain eigenvector
            color_points: color of the points along the certain eigenmode
            tuberadius: radius of the line
            point_size: size of the points
            nr_points: number of points for which the parabola is evaluated
            point_distance_xy: the xy-distance between the points
            evecs: the eigenvectors of the "point"-state
            point: the points which eigenvectors will be visualized
            evals: the eigenvalues of the "point"-state
        """
        # create points
        for (idx, evec) in enumerate(evecs):
            eval = evals[idx]
            evec = evec / np.linalg.norm(evec)
            points_positive, energy_positive = [], []
            for n in range(nr_points):
                points_positive.append(point + point_distance_xy * n * evec)
                # calc energy value (leaving the energy surface)
                energy_positive.append(
                    self.func(x=point[0], y=point[1]) + eval * (point_distance_xy * n) ** 2 + y_offset)
            points_positive.reverse()
            energy_positive.reverse()
            # mirror the parabola
            points_negative, energy_negative = [], []
            for n in range(nr_points):
                points_negative.append(point - point_distance_xy * n * evec)
                # calc energy value (leaving the energy surface)
                energy_negative.append(
                    self.func(x=point[0], y=point[1]) + eval * (point_distance_xy * n) ** 2 + y_offset)
            points = np.asarray(points_positive + points_negative)
            energy = np.asarray(energy_positive + energy_negative)
            l_points = np.column_stack((points[:, 0], points[:, 1], energy))
            l_pointpolydata = pv.PolyData(l_points)
            spline = pv.Spline(l_points, 1000)
            spline["scalars"] = np.arange(spline.n_points)
            self.add_mesh(spline.tube(radius=tuberadius), smooth_shading=True, color=color_line)
            self.add_mesh(l_pointpolydata, color=color_points, point_size=point_size, render_points_as_spheres=True)
            if show_surface:
                xx = np.linspace(point[0] - x_width / 2, point[0] + x_width / 2, 20)
                yy = np.linspace(point[1] - y_width / 2, point[1] + y_width / 2, 20)
                xgrid, ygrid = np.meshgrid(xx, yy)
                # evaluate the
                zgrid = self.paraboloid(xgrid, ygrid, x0=point[0], y0=point[1], eps_x=evals[0], eps_y=evals[1],
                                        yoffset=float(self.func(point[0], point[1])) + y_offset)
                points = np.dstack([xgrid, ygrid, zgrid])
                print(points)
                r_points = pv.PolyData(np.reshape(points, (points.shape[0] * points.shape[1], points.shape[2])))
                surf = r_points.delaunay_2d().triangulate()
                self.add_mesh(surf, color=color_line, show_scalar_bar=False)

    @staticmethod
    def create_sequence_between_points(initial: np.ndarray, final: np.ndarray, nr: int) -> np.ndarray:
        r"""
        Creates a sequence of (nr) points on a direct 2d connection between the initial and final point.

        Args:
            initial: start point (2D)
            final: final point
            nr: number of points

        Returns:
            the creates sequence
        """
        r = (final - initial) / nr
        seq = []
        for n in range(nr + 1):
            seq.append(initial + n * r)
        return np.asarray(seq)
