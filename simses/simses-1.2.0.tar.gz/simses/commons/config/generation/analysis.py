from simses.commons.config.analysis.analysis_config import AnalysisConfig
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.config.generation.generator import ConfigGenerator


class AnalysisConfigGenerator(ConfigGenerator):

    """
    The AnalysisConfigGenerator is a convenience class for generating a config for SimSES analysis. Several options
    can be activated or deactivated.
    """

    def __init__(self):
        super(AnalysisConfigGenerator, self).__init__()

    def load_default_config(self) -> None:
        """
        Loads defaults config

        Returns
        -------

        """
        path: str = AnalysisConfig.CONFIG_PATH
        path += AnalysisConfig.CONFIG_NAME
        path += AnalysisConfig.DEFAULTS
        self.load_config_from(path)

    def load_local_config(self) -> None:
        """
        Loads local config

        Returns
        -------

        """
        path: str = AnalysisConfig.CONFIG_PATH
        path += AnalysisConfig.CONFIG_NAME
        path += AnalysisConfig.LOCAL
        self.load_config_from(path)

    def do_data_export(self, export: bool = True) -> None:
        """
        Analysis results will be written to files

        Parameters
        ----------
        export :
            True: data is exported, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.EXPORT_ANALYSIS_TO_CSV, export)

    def print_results(self, printing: bool = False) -> None:
        """
        Analysis results will be printed to console

        Parameters
        ----------
        printing :
            True: results are printed, default: False

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.PRINT_RESULTS_TO_CONSOLE, printing)

    def do_batch_analysis(self, batch: bool = False) -> None:
        """
        Multiple simulation results can be merge for comparison of results

        Parameters
        ----------
        batch :
            True: comparison data is written, default: False

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.EXPORT_ANALYSIS_TO_BATCH, batch)

    def merge_analysis(self, merge: bool = True) -> None:
        """
        Analysis results are combined to an HTML file showing results and plots

        Parameters
        ----------
        merge :
            True: HTML file is written, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.MERGE_ANALYSIS, merge)

    def do_technical_analysis(self, analyze: bool = True) -> None:
        """
        Provide a technical analysis of the simulation results, e.g., efficiency and aging

        Parameters
        ----------
        analyze :
            True: Technical analysis is conducted, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.TECHNICAL_ANALYSIS, analyze)

    def do_economical_analysis(self, analyze: bool = True) -> None:
        """
        Provide an economical analysis of the simulation results, e.g., NPV and IRR (only top level system is considered)

        Parameters
        ----------
        analyze :
            True: Economical analysis is conducted, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.ECONOMICAL_ANALYSIS, analyze)

    def do_plotting(self, plot: bool = True) -> None:
        """
        Figures are created and shown in merged HTML file

        Parameters
        ----------
        plot :
            True: Figures are plotted, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.PLOTTING, plot)

    def do_system_analysis(self, analyze: bool = True) -> None:
        """
        Provide a technical analysis on system level

        Parameters
        ----------
        analyze :
            True: Results are analyzed, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.SYSTEM_ANALYSIS, analyze)

    def do_lithium_ion_analysis(self, analyze: bool = True) -> None:
        """
        Provide a technical analysis for lithium-ion batteries

        Parameters
        ----------
        analyze :
            True: Results are analyzed, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.LITHIUM_ION_ANALYSIS, analyze)

    def do_redox_flow_analysis(self, analyze: bool = True) -> None:
        """
        Provide a technical analysis for redox flow batteries

        Parameters
        ----------
        analyze :
            True: Results are analyzed, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.REDOX_FLOW_ANALYSIS, analyze)

    def do_hydrogen_analysis(self, analyze: bool = True) -> None:
        """
        Provide a technical analysis for hydrogen systems

        Parameters
        ----------
        analyze :
            True: Results are analyzed, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.HYDROGEN_ANALYSIS, analyze)

    def do_site_level_analysis(self, analyze: bool = True) -> None:
        """
        Provide a technical analysis on site level, e.g., comparison of site load

        Parameters
        ----------
        analyze :
            True: Results are analyzed, default: True

        Returns
        -------

        """
        self._set_bool(GeneralAnalysisConfig.SECTION, GeneralAnalysisConfig.SITE_LEVEL_ANALYSIS, analyze)
