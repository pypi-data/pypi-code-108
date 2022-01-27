import os
import pathlib
from configparser import ConfigParser
from simses.commons.config.analysis.analysis_config import AnalysisConfig
from simses.commons.utils.utilities import convert_path_codec


class GeneralAnalysisConfig(AnalysisConfig):

    """
    General analysis configs
    """
    SECTION: str = 'GENERAL'
    SIMULATION: str = 'SIMULATION'
    SYSTEM_ANALYSIS: str = 'SYSTEM_ANALYSIS'
    LITHIUM_ION_ANALYSIS: str = 'LITHIUM_ION_ANALYSIS'
    REDOX_FLOW_ANALYSIS: str = 'REDOX_FLOW_ANALYSIS'
    HYDROGEN_ANALYSIS: str = 'HYDROGEN_ANALYSIS'
    SITE_LEVEL_ANALYSIS: str = 'SITE_LEVEL_ANALYSIS'
    PLOTTING: str = 'PLOTTING'
    TECHNICAL_ANALYSIS: str = 'TECHNICAL_ANALYSIS'
    ECONOMICAL_ANALYSIS: str = 'ECONOMICAL_ANALYSIS'
    EXPORT_ANALYSIS_TO_CSV: str = 'EXPORT_ANALYSIS_TO_CSV'
    PRINT_RESULTS_TO_CONSOLE: str = 'PRINT_RESULTS_TO_CONSOLE'
    EXPORT_ANALYSIS_TO_BATCH: str = 'EXPORT_ANALYSIS_TO_BATCH'
    MERGE_ANALYSIS: str = 'MERGE_ANALYSIS'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    def get_result_for(self, path: str) -> str:
        """Returns name of the simulation to analyse."""
        simulation = convert_path_codec(self.get_property(self.SECTION, self.SIMULATION))
        if simulation == 'LATEST':
            result_dirs = list()
            tmp_dirs = os.listdir(path)
            # res = filter(os.path.isdir, tmp_dirs)
            for dir in tmp_dirs:
                if os.path.isdir(path + dir):
                    result_dirs.append(path + dir + '/')
            return max(result_dirs, key=os.path.getmtime)
        elif os.path.isabs(simulation):
            return pathlib.Path(simulation).as_posix() + '/'
        else:
            return path + simulation + '/'

    @property
    def system_analysis(self) -> bool:
        """Returns boolean value for system_analysis after the simulation"""
        return self.get_property(self.SECTION, self.SYSTEM_ANALYSIS) in ['True']

    @property
    def lithium_ion_analysis(self) -> bool:
        """Returns boolean value for lithium_ion_analysis after the simulation"""
        return self.get_property(self.SECTION, self.LITHIUM_ION_ANALYSIS) in ['True']

    @property
    def redox_flow_analysis(self) -> bool:
        """Returns boolean value for redox_flow_analysis after the simulation"""
        return self.get_property(self.SECTION, self.REDOX_FLOW_ANALYSIS) in ['True']

    @property
    def hydrogen_analysis(self) -> bool:
        """Returns boolean value for redox_flow_analysis after the simulation"""
        return self.get_property(self.SECTION, self.HYDROGEN_ANALYSIS) in ['True']

    @property
    def site_level_analysis(self) -> bool:
        """Returns boolean value for redox_flow_analysis after the simulation"""
        return self.get_property(self.SECTION, self.SITE_LEVEL_ANALYSIS) in ['True']

    @property
    def plotting(self) -> bool:
        """Returns boolean value for matplot_plotting after the simulation"""
        return self.get_property(self.SECTION, self.PLOTTING) in ['True']

    @property
    def technical_analysis(self) -> bool:
        """Returns boolean value for technical analysis directly after the simulation"""
        return self.get_property(self.SECTION, self.TECHNICAL_ANALYSIS) in ['True']

    @property
    def economical_analysis(self) -> bool:
        """Returns boolean value for economical analysis directly after the simulation"""
        return self.get_property(self.SECTION, self.ECONOMICAL_ANALYSIS) in ['True']

    @property
    def export_analysis_to_csv(self) -> bool:
        """Defines if analysis results are to be exported to csv files"""
        return self.get_property(self.SECTION, self.EXPORT_ANALYSIS_TO_CSV) in ['True']

    @property
    def print_result_to_console(self) -> bool:
        """Defines if analysis results are to be printed to console"""
        return self.get_property(self.SECTION, self.PRINT_RESULTS_TO_CONSOLE) in ['True']

    @property
    def export_analysis_to_batch(self) -> bool:
        """Defines if analysis results are written to batch files"""
        return self.get_property(self.SECTION, self.EXPORT_ANALYSIS_TO_BATCH) in ['True']

    @property
    def merge_analysis(self) -> bool:
        """Defines if analysis results are merged"""
        return self.get_property(self.SECTION, self.MERGE_ANALYSIS) in ['True']

    @property
    def logo_file(self) -> str:
        return self.get_data_path(self.get_property(self.SECTION, 'LOGO_FILE'))
