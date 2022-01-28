r"""
Visualizer for the esc-stage of the sps algorithm
"""
from spinterface.sps_results.stage_visualizer.ivisstage import IVisStage
from pathlib import Path
from typing import Union, Tuple, List
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
import pandas as pd


class CVisConv(IVisStage):
    r"""

    """

    def __call__(self) -> None:
        r"""
        Excecutes the visualization for the converge stage
        """
        if self.strategy in [1]:
            self._visualize_converged_configuration()
            self._visualize_eigenvector_start_end()

    def __init__(self, strategy: int, info_file: Union[Path, str],
                 camera_spin_files: Union[List[Tuple[float, float, float]], None] = None):
        r"""
        Initializes the visualizer for the converge-stage of SPS
        Args:
            strategy(int): converge strategy
            info_file(Path,str): the file which holds information about the locations
            of the corresponding files. It is always in the same directory as the sps.in therefore all paths in the info
            file are relative to this.
        """
        super().__init__(strategy, camera_spin_files)
        self.parent_directory = Path(info_file).parent
        self.keys, self.esckeys, self.sp_or_convex, self.folders, self.spinfiles = self._read_info_file(
            info_file=info_file)

    @staticmethod
    def _read_info_file(info_file: Union[Path, str]) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
        r"""
        Reads the columns of the converge-info file.
        """
        df = pd.read_csv(info_file, sep=r'\s+')
        return df['DISPKEY'], df['ESCKEY'], df['sp_or_convex'], df['folder'], df['spin_file']

    @property
    def stage(self) -> str:
        r"""
        Returns:
            the stage
        """
        return 'Converge'

    def _stagestrategytext(self) -> str:
        r"""
        Returns:
            the converge strategy in words
        """
        if self.strategy == 1:
            return 'Use minimummodefollowing to converge on saddlepoint.'
        else:
            return 'Describing text for this strategy not yet coded.'

    def _visualize_converged_configuration(self):
        r"""
        Visualizes the spin configurations for all converged or re-entered configurations
        """
        for spinfile in self.spinfiles:
            print(f'Visualizig: {spinfile}...')
            l_latt = CLattice(source='STM', path=self.parent_directory / spinfile)
            l_visu = CVisualPyVista(lattice=l_latt, cam=self.spincam)
            pngfile = spinfile.replace('.dat', '.png')
            pngfile_splitted = pngfile.split('/')
            pngpath = self.parent_directory
            for pathpart in pngfile_splitted:
                pngpath = pngpath / pathpart
            l_visu(outpath=pngpath)
            l_visu.plotter.close()
            print('...done')

    def _visualize_eigenvector_start_end(self):
        r"""
        Visualizes the spin configurations for all converged configurations
        """
        for spinfile in self.spinfiles:
            evecfile_end = spinfile.replace('spin', 'evec')
            print(f'Visualizig: {evecfile_end}...')
            l_latt_end = CLattice(source='evec', path=self.parent_directory / evecfile_end)
            l_visu_end = CVisualPyVista(lattice=l_latt_end, cam=self.spincam)
            pngfile_end = evecfile_end.replace('.dat', '.png')
            pngfile_splitted_end = pngfile_end.split('/')
            pngpath_end = self.parent_directory
            for pathpart in pngfile_splitted_end:
                pngpath_end = pngpath_end / pathpart
            l_visu_end(outpath=pngpath_end)
            l_visu_end.plotter.close()
            print('...done')
            evecfile_start = evecfile_end.replace('end', '0')
            print(f'Visualizig: {evecfile_start}...')
            l_latt_start = CLattice(source='evec', path=self.parent_directory / evecfile_start)
            l_visu_start = CVisualPyVista(lattice=l_latt_start, cam=self.spincam)
            pngfile_start = evecfile_start.replace('.dat', '.png')
            pngfile_splitted_start = pngfile_start.split('/')
            pngpath_start = self.parent_directory
            for pathpart in pngfile_splitted_start:
                pngpath_start = pngpath_start / pathpart
            l_visu_start(outpath=pngpath_start)
            l_visu_start.plotter.close()
            print('...done')
