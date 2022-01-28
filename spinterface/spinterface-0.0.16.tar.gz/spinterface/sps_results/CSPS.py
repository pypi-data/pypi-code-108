r"""
Main class for defining a result-visualization for a saddle point search implementation
"""
from pathlib import Path
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
from typing import Union, Dict, List, Tuple, Any
from spinterface.sps_results.inputreader.CInputReader import CInputReader
import spinterface.sps_results.constants_CSPS as const
from spinterface.sps_results.stage_visualizer.cvisdisp import CVisDisp
from spinterface.sps_results.stage_visualizer.cvisesc import CVisEsc
from spinterface.sps_results.stage_visualizer.cvisconv import CVisConv
from spinterface.sps_results.stage_visualizer.cvistree import CVisTree
from spinterface.sps_results.stage_visualizer.ivisstage import IVisStage


class CSPS:
    r"""

    """

    def __init__(self, inputfile: Union[Path, str] = Path.cwd() / 'sps.in', stage: str = 'DISP',
                 info_disp: Union[Path, str] = Path.cwd() / 'info_sps_disp.dat',
                 info_esc: Union[Path, str] = Path.cwd() / 'info_sps_esc.dat',
                 info_conv: Union[Path, str] = Path.cwd() / 'info_sps_conv.dat',
                 cameras_spin_files: Union[List[Tuple[float, float, float]], None] = None) -> None:
        r"""
        Initializes SPS-Visualization
        """
        self.inputfile = inputfile
        self.info_disp = info_disp
        self.info_esc = info_esc
        self.info_conv = info_conv
        l_inp_reader = CInputReader(fpath=inputfile)
        self._cameras_spin_files = cameras_spin_files
        self.sps_settings = self._check_settings(l_inp_reader.content)
        self._idisp, self._iesc, self._iconv, self._iesca, self._itree = self._parse_stage(stage)
        self.stages = self._create_visualizer()

    def __call__(self) -> None:
        r"""
        Executes the visualizations
        """
        for (stagename, stage) in self.stages.items():
            print(f'Visualizing stage: {stagename}')
            stage()

    def stage_visualizer(self, name: str) -> IVisStage:
        r"""
        Gets the stage visualizer to access the methods of these classes directly
        """
        try:
            stage = self.stages[name]
        except KeyError:
            raise ValueError(f'Stage {name} not initialized. Current stages available are: {self.stages.keys()}.')
        return stage

    def show_initial_structure(self, topview: bool = False):
        r"""
        shows initial structure
        """
        # Visualize the initial configuration
        l_latt = CLattice(source='STM', path=self.info_disp.parent / 'SpinSTMi.dat')
        l_visu = CVisualPyVista(lattice=l_latt, cam=self._cameras_spin_files)
        pngfile = self.info_disp.parent / 'SpinSTMi.png'
        if topview:
            l_visu.plotter.view_xy()
        l_visu.show()
        l_visu(outpath=pngfile)
        l_visu.plotter.close()

    def _create_visualizer(self) -> Dict[str, IVisStage]:
        r"""
        Initializes the visualizers for the tasks
        """
        l_stages = {}
        if self._idisp:
            l_stages['DISP'] = CVisDisp(strategy=self.sps_settings['algo_displace'], info_file=self.info_disp,
                                        camera_spin_files=self._cameras_spin_files)
        if self._iesc:
            l_stages['ESC'] = CVisEsc(strategy=self.sps_settings['algo_escape'], info_file=self.info_esc,
                                      camera_spin_files=self._cameras_spin_files)
        if self._iconv:
            l_stages['CONV'] = CVisConv(strategy=self.sps_settings['algo_escape'], info_file=self.info_conv,
                                       camera_spin_files=self._cameras_spin_files)
        if self._itree:
            l_stages['TREE'] = CVisTree(strategy=2, info_file_disp=self.info_disp, info_file_esc=self.info_esc,
                                        info_file_conv=self.info_conv)
        return l_stages

    @staticmethod
    def _parse_stage(stage: str) -> Tuple[bool, bool, bool, bool, bool]:
        r"""
        Parses the parse information decider string.
        """
        if stage not in ['ALL', 'DISP', 'ESC', 'CONV', 'ESCA', 'TREE']:
            raise ValueError(f'Stage: {stage} not in allowed options (ALL, DISP, ESC, CONV, ESCA, TREE).')
        if stage == 'ALL':
            return True, True, True, True, True
        else:
            return stage == 'DISP', stage == 'ESC', stage == 'CONV', stage == 'ESCA', stage == 'TREE'

    @staticmethod
    def _check_settings(settings: Dict[str, List]) -> Dict[str, Any]:
        r"""
        Checks if all the necessary settings are available and convert the data types.
        """
        checked_settings = {}
        for (key, valuetype) in const.KEYS.items():
            try:
                l_value = settings[key][0]
            except KeyError:
                raise ValueError(f"The following necessary key is not provided in input file: {key}.")

            if valuetype == float:
                l_value = l_value.replace('d', 'e')
            if valuetype == bool:
                if l_value in ['.T.', '.True.']:
                    checked_settings[key] = True
                    continue
                if l_value in ['.F.', '.False.']:
                    checked_settings[key] = False
                    continue
            checked_settings[key] = valuetype(l_value)
        return checked_settings
