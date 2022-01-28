r"""
Visualizer for the disp-stage of the sps algorithm
"""
from spinterface.sps_results.stage_visualizer.ivisstage import IVisStage
from pathlib import Path
from typing import Union, Tuple, List
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
import pandas as pd


class CVisDisp(IVisStage):
    r"""

    """

    def __call__(self) -> None:
        r"""
        Excecutes the visualization for the displace stage
        """
        if self.strategy in [2]:
            self._visualize_displaced_configuration()
            self._visualize_superposition_eigenvector()

    def __init__(self, strategy: int, info_file: Union[Path, str],
                 camera_spin_files: Union[List[Tuple[float, float, float]], None] = None):
        r"""
        Initializes the visualizer for the displace-stage of SPS
        Args:
            strategy(int): displace strategy
            info_file(Path,str): the file which holds information about the locations
            of the corresponding files. It is always in the same directory as the sps.in therefore all paths in the info
            file are relative to this.
        """
        super().__init__(strategy, camera_spin_files)
        self.parent_directory = Path(info_file).parent
        self.keys, self.folders, self.spinfiles = self._read_info_file(info_file=info_file)

    @staticmethod
    def _read_info_file(info_file: Union[Path, str]) -> Tuple[pd.Series, pd.Series, pd.Series]:
        r"""
        Reads the columns of the displace-info file.
        """
        df = pd.read_csv(info_file, sep=r'\s+')
        return df['DISPKEY'], df['folder'], df['spin_file']

    @property
    def stage(self) -> str:
        r"""
        Returns:
            the stage
        """
        return 'Displace'

    def _stagestrategytext(self) -> str:
        r"""
        Returns:
            the displace strategy in words
        """
        if self.strategy == 1:
            return 'Not displacing at all.'
        elif self.strategy == 2:
            return 'Creating a random superposition of eigenvectors of initial state and rotate conf. along this ' \
                   'superpos. '
        else:
            return 'Describing text for this strategy not yet coded.'

    def _visualize_displaced_configuration(self):
        r"""
        Visualizes the spin configurations for all displaced configurations
        """
        for spinfile in self.spinfiles:
            l_latt = CLattice(source='STM', path=self.parent_directory / spinfile)
            l_visu = CVisualPyVista(lattice=l_latt, cam=self.spincam)
            pngfile = spinfile.replace('.dat', '.png')
            pngfile_splitted = pngfile.split('/')
            pngpath = self.parent_directory
            for pathpart in pngfile_splitted:
                pngpath = pngpath / pathpart
            l_visu(outpath=pngpath)
            l_visu.plotter.close()

    def _visualize_superposition_eigenvector(self):
        r"""
        Visualizes the spin configurations for all displaced configurations
        """
        for spinfile in self.spinfiles:
            evecfile = spinfile.replace('spin', 'evec')
            l_latt = CLattice(source='evec', path=self.parent_directory / evecfile)
            l_visu = CVisualPyVista(lattice=l_latt, cam=self.spincam)
            pngfile = evecfile.replace('.dat', '.png')
            pngfile_splitted = pngfile.split('/')
            pngpath = self.parent_directory
            for pathpart in pngfile_splitted:
                pngpath = pngpath / pathpart
            l_visu(outpath=pngpath)
            l_visu.plotter.close()
