from pathlib import Path
from spinterface.inputs.lattice.ILattice import ILattice
from spinterface.visualizations.lattices.ivisualizer import IVisualizer
from spinterface.visualizations.lattices.utilities import get_colormap
from typing import List, Union, Tuple
import pyvista as pv
import numpy as np


class CVisualPyvistaBilayer(IVisualizer):
    r"""
        It visualizes a bilayer spin lattice with three different perspectives. A
        view of the top layer, of the bot layer and a view perspective from the middle
    """

    def __init__(self, lattice: ILattice, tiplength: float = 1.0, tipradius: float = 0.35,
                 arrowscale: float = 0.7, cam_mid: Union[List[Tuple[float, float, float]], None] = None,
                 cmap: str = 'hsv_spind', dist_top: float = 10, dist_bot: float = 10,
                 filter_around_layercenter: Union[None, float] = None,
                 dist_betweenlayers: float = 3, filter_half: bool = False) -> None:
        r"""
        Initializes the visualization of a bilayer spin lattice.

        Args:
            tiplength(float): geometry of arrow: tiplength
            tipradius(float): geometry of arrow: tipradius
            arrowscale(float): geometry of arrow: arrowscale
            cam_mid: camera position for the middle layer
            dist_bot (float): distance of the camera (in z direction) from the bottom layer
            dist_top (float): distance of the camera (in z direction) from the top layer
            cmap: string for the choice of the colormap. Defined in utilities module
            filter_around_layercenter(float, None): if not none each layer is filtered according to a circle around
            its layer midpoint
            dist_betweenlayers(float): The distance between the two layers in the middle picture
            filter_half(bool): if the half of the cylinder should be displayer
        """
        if lattice.nlayer != 2:
            raise ValueError('This visualization class is only valid for bilayer systems.')
        super().__init__(lattice)
        self._geom = pv.Arrow(start=np.array([-arrowscale / 2.0, 0, 0]), tip_length=tiplength,
                              tip_radius=tipradius, scale=arrowscale)
        self.cmap = get_colormap(cmap)
        self.cam_mid = cam_mid
        self.dist_top = dist_top
        self.dist_bot = dist_bot
        self.dist_betweenlay = dist_betweenlayers
        self.filter_around_layercenter = filter_around_layercenter
        self.filter_half = filter_half
        self._make_plotter()
        if self.filter_around_layercenter is not None:
            self._make_cylinder()

    def _make_cylinder(self):
        r"""
        Adds a grey cylinder to the central image view from the side
        """
        l_cyl = pv.Cylinder(center=self.lattice.midpoint + np.array([0, 0, self.dist_betweenlay / 2]) - np.array(
            [0, 0, self.lattice.midpoint[2]]), direction=np.array([0, 0, 1]), radius=self.filter_around_layercenter,
                            height=self.dist_betweenlay + 2 * self.lattice.midpoint[2])
        l_cyl = l_cyl.clip(normal='y')
        self.plotter.subplot(0)
        self.plotter.add_mesh(l_cyl, opacity=1, color='gray')

    def _make_plotter(self, offscreen: bool = False):
        r"""
        Creates the plotter. The plotter will be recreated when saving the image
        """
        self.plotter = pv.Plotter(shape=('1|2'), off_screen=offscreen, lighting='three lights')
        self._configureplotter()
        plotpoints1, plotspins1, plotsz1 = self._make_plot_points(layer=0)
        plotpoints2, plotspins2, plotsz2 = self._make_plot_points(layer=1)
        # shift the upper layer
        plotpoints1_mid, plotspins1_mid, plotsz1_mid = self._make_plot_points(layer=0, filter_half=self.filter_half)
        plotpoints2_mid, plotspins2_mid, plotsz2_mid = self._make_plot_points(layer=1, filter_half=self.filter_half)
        plotpoints2_mid = plotpoints2_mid + np.array([0.0, 0.0, self.dist_betweenlay])

        self.PolyData1 = pv.PolyData(plotpoints1)
        self.PolyData1.vectors = plotspins1
        self.PolyData1['oop'] = plotsz1
        self.Glyphs1 = self.PolyData1.glyph(orient=True, scale=True, geom=self._geom)
        self.PolyData2 = pv.PolyData(plotpoints2)
        self.PolyData2.vectors = plotspins2
        self.PolyData2['oop'] = plotsz2
        self.Glyphs2 = self.PolyData2.glyph(orient=True, scale=True, geom=self._geom)

        self.PolyData2_mid = pv.PolyData(plotpoints2_mid)
        self.PolyData2_mid.vectors = plotspins2_mid
        self.PolyData2_mid['oop'] = plotsz2_mid
        self.Glyphs2_mid = self.PolyData2_mid.glyph(orient=True, scale=True, geom=self._geom)
        self.PolyData1_mid = pv.PolyData(plotpoints1_mid)
        self.PolyData1_mid.vectors = plotspins1_mid
        self.PolyData1_mid['oop'] = plotsz1_mid
        self.Glyphs1_mid = self.PolyData1_mid.glyph(orient=True, scale=True, geom=self._geom)

        self.plotter.subplot(1)
        self.plotter.add_mesh(self.Glyphs2, show_scalar_bar=False, cmap=self.cmap)
        self.plotter.subplot(0)
        self.plotter.add_mesh(self.Glyphs1_mid, show_scalar_bar=False, cmap=self.cmap)
        self.plotter.add_mesh(self.Glyphs2_mid, show_scalar_bar=False, cmap=self.cmap)
        self.plotter.subplot(2)
        self.plotter.add_mesh(self.Glyphs1, show_scalar_bar=False, cmap=self.cmap)

    def _make_plot_points(self, layer: int = 1, filter_half: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        r"""
        We always want to norm the colormap in the interval -1, 1 even we have a lattice which spins have only SZ comp.
        in the interval e.g. (1,0.5). There is now easy way to do this with pyvista since there is no interface for nor-
        malizing. Therefore, we add an invisible point in the center of the lattice here.

        Returns:
            the points, the spins and the sz components
        """
        if self.filter_around_layercenter is not None:
            mag_structure_layer = self._filter_layercenter(magstructure=self.lattice.getlayer_by_idx(layer),
                                                           layer=layer)
        else:
            mag_structure_layer = self.lattice.getlayer_by_idx(layer)
        if filter_half:
            mag_structure_layer = mag_structure_layer[mag_structure_layer[:, 1] <= 0]
        points = mag_structure_layer[:, :3]
        spins = mag_structure_layer[:, 3:6]
        SZ = mag_structure_layer[:, 5]
        midpoint = self.lattice.layermidpoints[layer]
        plotpoints = np.append(points, np.array([midpoint, midpoint]), axis=0)
        plotspins = np.append(spins, np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]), axis=0)
        plotsz = np.append(SZ, np.array([1.0, -1.0]))
        return plotpoints, plotspins, plotsz

    def _filter_layercenter(self, magstructure: np.ndarray, layer: int = 0) -> np.ndarray:
        r"""
        Applies a circular filter to a layer.

        Args:
            layer(int): adress of the layer
            magstructure(np.ndarray): struct. to filter
        Returns:
            updated magstructure
        """
        magstructure_layer = self.lattice.getlayer_by_idx(layer)
        mp = self.lattice.layermidpoints[layer]
        new_structure_layer = magstructure_layer[
            np.linalg.norm(magstructure_layer[:, :3] - mp, axis=1) <= self.filter_around_layercenter]
        return new_structure_layer

    def _configureplotter(self) -> None:
        r"""
        Configures the plotter object
        """
        pv.set_plot_theme("ParaView")
        pv.rcParams['transparent_background'] = True
        self.plotter.subplot(1)
        self.plotter.set_background('white')
        mp = self.lattice.layermidpoints[1]
        self.plotter.camera_position = [(mp[0], mp[1], mp[2] + self.dist_top), (mp[0], mp[1], mp[2]), (0, 1, 0)]
        self.plotter.subplot(0)
        self.plotter.set_background('white')
        self.plotter.camera_position = self.cam_mid
        self.plotter.subplot(2)
        mp = self.lattice.layermidpoints[0]
        self.plotter.camera_position = [(mp[0], mp[1], mp[2] + self.dist_bot), (mp[0], mp[1], mp[2]), (0, 1, 0)]
        self.plotter.set_background('white')

        def camtop() -> None:
            self.plotter.subplot(1)
            print('Camera postion: ', self.plotter.camera_position)

        def cambot() -> None:
            self.plotter.subplot(2)
            print('Camera postion: ', self.plotter.camera_position)

        def cammid() -> None:
            self.plotter.subplot(0)
            print('Camera postion: ', self.plotter.camera_position)

        def help() -> None:
            print('the commands and keys are: camtop: t, cambot: b, cammid: c')

        self.plotter.add_key_event('h', help)
        self.plotter.add_key_event('c', cammid)
        self.plotter.add_key_event('t', camtop)
        self.plotter.add_key_event('b', cambot)

    def __call__(self, outpath: Path = Path.cwd() / 'bilayerspin.png') -> None:
        r"""
        Saves the image to a file

        Args:
            outpath(Path): output path for the png image created.
        """
        self._make_plotter(offscreen=True)
        if self.filter_around_layercenter:
            self._make_cylinder()
        self.plotter.window_size = [3000, 2000]
        self.plotter.screenshot(str(outpath.stem))

    def show(self) -> None:
        r"""
        Shows the plotter
        """
        print('Look what you have done.......')
        print('to get current cam-position press key c')
        self.plotter.show()
