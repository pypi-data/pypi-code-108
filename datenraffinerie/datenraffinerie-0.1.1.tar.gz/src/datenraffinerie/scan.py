"""
Module containing the classes that together constitute a measurement
and encapsulate the different steps needed to take a measurement using the
hexaboard
"""
from pathlib import Path
from functools import reduce
import os
import operator
import pandas as pd
import luigi
import yaml
import zmq
from . import config_utilities as cfu
from . import analysis_utilities as anu


class ScanConfiguration(luigi.Task):
    """ builds the configuration for a single measurement from the
    default power on config of the target and the scan config of the
    measurement
    """
    output_path = luigi.Parameter(significant=True)
    calibration = luigi.Parameter(significant=True)
    target_power_on_config = luigi.DictParameter(significant=True)
    root_config_path = luigi.Parameter(significant=True)
    output_dir = luigi.Parameter(significant=True)
    analysis_module_path = luigi.Parameter(significant=True)

    def requires(self):
        from .valve_yard import ValveYard
        # if a calibration is needed then the delegate finding
        # the calibration and adding the subsequent tasks to the
        # to the ValveYard
        if self.calibration is not None:
            return ValveYard(self.root_config_path,
                             self.calibration,
                             str(Path(self.output_dir).resolve()),
                             str(Path(self.analysis_module_path).resolve()))

    def output(self):
        output_config_path = Path(self.output_path).resolve()
        output_config_path = output_config_path /\
            'target_config_with_calibration.yaml'
        return luigi.LocalTarget(output_config_path)

    def run(self):
        calibration_overlay = None
        if self.calibration is not None:
            with self.input()['calibration'].open('r') as calibration_file:
                calibration_overlay = yaml.safe_load(calibration_file.read())
        run_config = cfu.unfreeze(self.target_power_on_config)
        if calibration_overlay is not None:
            run_config = cfu.update_dict(run_config, calibration_overlay)
        with self.output().open('w') as target_pwr_on_config_file:
            yaml.safe_dump(run_config, target_pwr_on_config_file)


class Measurement(luigi.Task):
    """
    Task that unpacks the raw data into the desired data format
    also merges the yaml chip configuration with the reformatted
    data.
    """
    # configuration and connection to the target
    # (aka hexaboard/SingleROC tester)
    target_config = luigi.DictParameter(significant=False)
    target_default_config = luigi.DictParameter(significant=False)

    # configuration of the (daq) system
    daq_system_config = luigi.DictParameter(significant=False)

    # Directory that the data should be stored in
    output_dir = luigi.Parameter(significant=True)
    output_format = luigi.Parameter(significant=False)
    label = luigi.Parameter(significant=True)
    identifier = luigi.IntParameter(significant=True)

    # the path to the root config file so that the Configuration
    # task can call the valveyard if a calibration is required
    root_config_path = luigi.Parameter(True)
    # calibration if one is required
    calibration = luigi.OptionalParameter(significant=False)
    analysis_module_path = luigi.OptionalParameter(significant=False)
    network_config = luigi.DictParameter(significant=True)

    def requires(self):
        return ScanConfiguration(self.output_dir,
                                 self.calibration,
                                 self.target_default_config,
                                 self.root_config_path,
                                 self.output_dir)

    def output(self):
        """
        define the file that is to be produced by the unpacking step
        the identifier is used to make the file unique from the other
        unpacking steps
        """
        formatted_data_path = Path(self.output_dir) / \
            (self.label + str(self.identifier) + '-data.' + self.output_format)
        return luigi.LocalTarget(formatted_data_path.resolve())

    def run(self):
        # load the configurations
        target_config = cfu.unfreeze(self.target_config)
        daq_system_config = cfu.unfreeze(self.daq_system_config)
        power_on_default = cfu.unfreeze(self.target_default_config)
        with self.input().open('r') as calibrated_default_config_file:
            calibrated_default_config = cfu.unfreeze(yaml.safe_load(
                calibrated_default_config_file.read()))

        # calculate the configuration to send to the backend
        full_target_config = cfu.update_dict(calibrated_default_config,
                                             target_config)
        target_config = cfu.diff_dict(power_on_default, full_target_config)
        complete_config = {'daq': daq_system_config,
                           'target': target_config}

        # send config to the backend and wait for the response
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(
                f"tcp://{self.network_config['daq_coordinator']['hostname']}:" +
                f"{self.network_config['daq_coordinator']['port']}")
        socket.send_string('measure;'+yaml.safe_dump(complete_config))
        data = socket.recv()
        socket.close()
        context.term()
        raw_data_file_path = self.output().path + '.raw'

        # save the data in a file so that the unpacker can work with it
        with open(raw_data_file_path, 'wb') as raw_data_file:
            raw_data_file.write(data)

        # 'unpack' the data from the raw data gathered into a root file that
        # can then be merged with the configuration into a large table
        unpack_command = 'unpack'
        input_file = ' -i ' + str(raw_data_file_path)
        data_file_path = self.output().path + '.root'
        output_command = ' -o ' + data_file_path
        output_type = ' -t unpacked'
        full_unpack_command = unpack_command + input_file + output_command\
            + output_type
        os.system(full_unpack_command)

        # load the data from the unpacked root file and merge in the
        # data from the configuration for that run with the data
        measurement_data = anu.extract_data(data_file_path)
        os.remove(data_file_path)
        os.remove(raw_data_file_path)
        measurement_data = anu.add_channel_wise_data(measurement_data,
                                                     full_target_config)
        measurement_data = anu.add_half_wise_data(measurement_data,
                                                  full_target_config)
        with self.output().temporary_path() as tmp_out_path:
            measurement_data.to_hdf(tmp_out_path, 'data')


class Scan(luigi.Task):
    """
    A Scan over one parameter or over other scans

    The scan uses the base configuration as the state of the system
    and then modifies it by applying patches constructed from
    parameter/value pairs passed to the scan and then calling either
    the measurement task or a sub-scan with the patched configurations
    as their respective base configurations
    """
    # parameters describing the position of the parameters in the task
    # tree
    identifier = luigi.IntParameter(significant=True)

    # parameters describing to the type of measurement being taken
    # and the relevant information for the measurement/scan
    label = luigi.Parameter(significant=False)
    output_dir = luigi.Parameter(significant=False)
    output_format = luigi.Parameter(significant=False)
    scan_parameters = luigi.ListParameter(significant=True)

    # configuration of the target and daq system that is used to
    # perform the scan (This may be extended with an 'environment')
    target_config = luigi.DictParameter(significant=False)
    target_default_config = luigi.DictParameter(significant=False)
    daq_system_config = luigi.DictParameter(significant=False)

    root_config_path = luigi.Parameter(significant=True)
    # calibration if one is required
    calibration = luigi.OptionalParameter(significant=False,
                                          default=None)
    analysis_module_path = luigi.OptionalParameter(significant=False,
                                                   default=None)
    network_config = luigi.DictParameter(significant=False)
    defaults_configured = luigi.BoolParameter(significant=True)
    supported_formats = ['hdf5']

    def requires(self):
        """
        Determine the measurements that are required for this scan to proceed.

        The Scan class is a recursive task. For every parameter(dimension) that
        is specified by the parameters argument, the scan task requires a
        set of further scans, one per value of the values entry associated with
        the parameter that the current scan is to scan over, essentially
        creating the Cartesian product of all parameters specified.
        """
        required_tasks = []
        values = self.scan_parameters[0][1]
        parameter = list(self.scan_parameters[0][0])
        target_config = cfu.unfreeze(self.target_config)
        # if there are more than one entry in the parameter list the scan still
        # has more than one dimension. So spawn more scan tasks for the lower
        # dimension
        if len(self.scan_parameters) > 1:
            # calculate the id of the task by multiplication of the length of
            # the dimensions still in the list
            task_id_offset = reduce(operator.mul,
                                    [len(param[1]) for param in
                                     self.scan_parameters[1:]])
            for i, value in enumerate(values):
                patch = cfu.generate_patch(
                            parameter, value)
                subscan_target_config = cfu.update_dict(
                        target_config,
                        patch)
                required_tasks.append(Scan(self.identifier + 1 + task_id_offset
                                           * i,
                                           self.label,
                                           self.output_dir,
                                           self.output_format,
                                           self.scan_parameters[1:],
                                           subscan_target_config,
                                           self.target_default_config,
                                           self.daq_system_config,
                                           self.root_config_path,
                                           self.calibration,
                                           self.analysis_module_path,
                                           self.network_config))
        # The scan has reached the one dimensional case. Spawn a measurement
        # for every value that takes part in the scan
        else:
            for i, value in enumerate(values):
                patch = cfu.generate_patch(parameter, value)
                measurement_config = cfu.patch_configuration(
                        target_config,
                        patch)
                required_tasks.append(Measurement(measurement_config,
                                                  self.target_default_config,
                                                  self.daq_system_config,
                                                  self.output_dir,
                                                  self.output_format,
                                                  self.label,
                                                  self.identifier + i,
                                                  self.root_config_path,
                                                  self.calibration,
                                                  self.analysis_module_path,
                                                  self.network_config))
        return required_tasks

    def run(self):
        """
        concatenate the files of a measurement together into a single file
        and write the merged data
        """
        data_seg = []
        for data_file in self.input():
            print(data_file.path)
            data_seg.append(pd.read_hdf(data_file.path))
        merged_data = pd.concat(data_seg, ignore_index=True, axis=0)
        with self.output().temporary_path() as outfile:
            merged_data.to_hdf(outfile, 'data')

    def output(self):
        """
        generate the output file for the scan task
        """
        if self.output_format in self.supported_formats:
            out_file = str(self.identifier) + 'merged.' + self.output_format
            output_path = Path(self.output_dir) / out_file
            return luigi.LocalTarget(output_path)
        raise KeyError("The output format for the scans needs to"
                       " one of the following:\n"
                       f"{self.supported_formats}")
