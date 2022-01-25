import luigi
import importlib
import os
import sys
from pathlib import Path
import pandas as pd
from .config_utilities import unfreeze
from .errors import OutputError

class Distillery(luigi.Task):
    """ Task that encapsulates analysis tasks and makes them executable
    inside the Datenraffinerie
    """
    name = luigi.Parameter(significant=True)
    python_module = luigi.Parameter(significant=True)
    daq = luigi.Parameter(significant=True)
    output_dir = luigi.Parameter(significant=True)
    parameters = luigi.DictParameter(significant=True)
    root_config_path = luigi.Parameter(significant=True)
    analysis_module_path = luigi.OptionalParameter(significant=True,
                                                   default=None)
    network_config = luigi.DictParameter(significant=False)

    def requires(self):
        from .valve_yard import ValveYard
        """ Determin which analysis needs to be run to produce
        the data for the analysis
        :returns: The acquisition procedure needed to produce the data
        """
        return ValveYard(self.root_config_path, self.daq, self.output_dir,
                         self.analysis_module_path, self.network_config)

    def output(self):
        """ Define the files that are produced by the analysis
        :returns: dictionary with the keys 'summary', 'calibration'
            and 'plots', where 'summary's value is a string for a
            relative path to the summary, same as calibration is a
            relative path to the calibration yaml file
            and the value associated to 'plots' is a list of relative
            paths. All paths should be strings.
        """
        analysis = self.import_analysis(self.analysis_module_path,
                                        self.python_module)
        analysis_parameters = unfreeze(self.parameters)
        analysis = analysis(analysis_parameters)
        output = {}
        for key, paths in analysis.output().items():
            if key == 'plots':
                try:
                    if len(paths) == 0:
                        continue
                    output[key] = [luigi.LocalTarget(
                        (Path(self.output_dir) / path).resolve())
                        for path in paths]
                except TypeError as err:
                    raise OutputError('The plots output must be a list ' +
                                      'of paths. Use an empty list if ' +
                                      'no plots are generated') from err
            else:
                if paths is None:
                    continue
                output[key] = (Path(self.output_dir) / paths).resolve()
        return output

    def run(self):
        """ perform the analysis using the imported distillery
        :returns: TODO

        """
        # import the class definition
        analysis = self.import_analysis(self.analysis_module_path,
                                            self.python_module)
        # instantiate an analysis object from the imported analysis class
        analysis = analysis(unfreeze(self.parameters))

        # open and read the data
        data = pd.read_hdf(self.input().path)
        analysis.run(data, self.output_dir)

    @staticmethod
    def import_analysis(distillery_path: str, name: str):
        """ Import the distillery for the analysis.

        :distillery_path: The path in which to find the distilleries
            module
        :name: The name of the distillery to load
        :returns: the distillery loaded into the local namespace
        """
        if distillery_path is not None:
            pathstr = str(Path(distillery_path).resolve())
            pythonpath_entry = os.path.split(pathstr)[0]
            module_name = os.path.split(pathstr)[1]
            sys.path.append(pythonpath_entry)
            i = importlib.import_module(module_name)
            distillery = getattr(i, name)
        else:
            import datenraffinerie_distilleries as distilleries
            distillery = getattr(distilleries, name)
        return distillery
