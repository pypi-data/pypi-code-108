"""
The ValveYard is a class in the datenraffinerie that is responsible
for parsing the user configuration and requiring the right scan or
analysis task and passing it all necessary values from their proper
functioning

Author: Alexander Becker (a.becker@cern.ch)
Date: 2021-12-16
"""
import os
from pathlib import Path
import luigi
import zmq
import yaml
from .scan import Scan
from .distillery import DistilleryAdapter
from . import config_utilities as cfu
from . import control_adapter as ctrl


class ValveYard(luigi.WrapperTask):
    root_config_file = luigi.Parameter(significant=True)
    procedure_label = luigi.Parameter(significant=True)
    output_dir = luigi.Parameter(significant=True)
    analysis_module_path = luigi.Parameter(significant=True)
    network_config = luigi.DictParameter(significant=True)

    def output(self):
        return self.input()

    def requires(self):
        """ A wrapper that parses the configuration and starts the procedure
        with the corresponding procedure label

        :raises: ConfigFormatError if either the type of the configuration entry
            does not match the allowed ones or if the YAML is malformed
        :raises: DAQConfigError if the DAQ configuration is malformed
        """
        data_dir = Path(self.output_dir)
        if not data_dir.exists():
            os.makedirs(data_dir)
        output_dir = data_dir
        procedures, workflows = cfu.parse_config_file(self.root_config_file)
        procedure_names = list(map(lambda p: p['name'], procedures))
        if self.procedure_label in procedure_names:
            procedure_index = procedure_names.index(self.procedure_label)
        else:
            raise ctrl.DAQConfigError(f"No '{self.procedure_label}' found in"
                                      " the config files")
        procedure = procedures[procedure_index]
        if procedure['type'] == 'analysis':
            return DistilleryAdapter(name=self.procedure_label,
                              daq=procedure['daq'],
                              output_dir=str(
                                  (output_dir/self.procedure_label).resolve()),
                              parameters=procedure['parameters'],
                              root_config_path=str(
                                  Path(self.root_config_file).resolve()),
                              analysis_module_path=self.analysis_module_path,
                              network_config=self.network_config)
        if procedure['type'] == 'daq':
            # the default values for the DAQ system and the target need to
            # be loaded on to the backend
            print('creating socket')
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            print('connecting')
            socket.connect(
                    f"tcp://{self.network_config['daq_coordinator']['hostname']}:"
                    f"{self.network_config['daq_coordinator']['port']}")
            print('connected')
            complete_default_config = {
                    'daq': procedure['daq_system_default_config'],
                    'target': procedure['target_power_on_default_config']}
            print('sending message')
            socket.send_string('load defaults;' +
                               yaml.safe_dump(complete_default_config))
            print('waiting for response')
            resp = socket.recv()
            if resp != b'defaults loaded':
                raise ctrl.DAQConfigError('Default config could not be loaded into the backend')
            print(f'response received: {resp}')
            return Scan(identifier=0,
                        label=self.procedure_label,
                        output_dir=str(output_dir.resolve()),
                        output_format='hdf5',
                        scan_parameters=procedure['parameters'],
                        target_config=procedure['target_init_config'],
                        target_default_config=procedure['target_power_on_default_config'],
                        daq_system_config=procedure['daq_system_config'],
                        root_config_path=str(
                            Path(self.root_config_file).resolve()),
                        calibration=procedure['calibration'],
                        analysis_module_path=self.analysis_module_path,
                        network_config=self.network_config,
                        defaults_configured=False)
        raise cfu.ConfigFormatError("The type of an entry must be either "
                                    "'daq' or 'analysis'")
