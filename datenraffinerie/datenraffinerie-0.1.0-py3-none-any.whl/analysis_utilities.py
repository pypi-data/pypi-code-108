"""
Utilities for the use with the handling of the gathered data 
in the datenraffinerie.
"""
import pandas as pd
import numpy as np
import pytest
import uproot
import os
import yaml
from pathlib import Path
import subprocess


class AnalysisError(Exception):
    def __init__(self, message):
        self.message = message


def create_measurement_dataframe(data_directory: str,
                                 channels_of_interest: list):
    """
    get the data from the *.root and the metadata from the *.yaml
    files and merge them together into a dataframe.

    This function parses and combines all the data from the root and
    yaml files into a single pandas dataframe. While performing the
    merging, only the channels selected in the *.yaml['chip_params']
    dictionary entry are selected to be merged together. All other
    channels are ignored. The selection of channels happens for each run
    so the channels of different runs may be different. All files are
    merged into a single pandas dataframe.
    """
    runs = []
    data_directory = Path(data_directory)
    rootfiles = [rf for rf in data_directory.iterdir()
            if os.path.splitext(rf)[1] == '.root']
    for rootfile in rootfiles:
        run_config_file = Path(os.path.splitext(rootfile)[0]+'.yaml')
        if run_config_file.is_file():
            run_config = extract_metadata(run_config_file)
            if run_config['keepRawData'] == 1:
                raise NotImplementedError("raw data mode not implemented")
            else:
                run_data = extract_data(rootfile)
            runs.append((run_data, run_config))
        else:
            raise AnalysisError(
                f"There was no {run_config_file} for {rootfile}")
    for i, run in enumerate(runs):
        runs[i] = merge_in_config_params(run[0], run[1])
    for i, run in enumerate(runs):
        runs[i] = split_channels(run, channels_of_interest)

    return (pd.concat([r[0] for r in runs], axis=0),  # the channels
            pd.concat([r[1] for r in runs], axis=0),  # the calib channels
            pd.concat([r[2] for r in runs], axis=0))  # the common mode chans

def split_channels(run_data, plot_channels):
    """
    split the dataset into three different sets, one for the
    normal channels, one for the calibration channels and one for the
    common mode channels.
    Also create the chip-'half' identifier in the data

    From the channels filter out the channels of interest
    """
    channel_data = pd.concat([run_data[run_data['channel'] == chan]
                             for chan in plot_channels])
    channel_data = channel_data[channel_data['channeltype'] == 0]
    channel_data.assign(half=(channel_data.channel//36)+1)
    calibration_channel_data = run_data[run_data['channeltype'] == 100]
    common_mode_data = run_data[run_data['channeltype'] == 1]
    return (channel_data, calibration_channel_data, common_mode_data)


def extract_metadata(run_config_file):
    """
    Interpret the metadata from the yaml file
    """
    with open(run_config_file, 'r') as file:
        meta_Data = yaml.safe_load(file.read())
        return meta_Data['run_params']


def extract_data(rootfile, raw_data=False):
    """
    Extract the Data from the rootfile and put it
    into a Pandas dataframe
    """
    with uproot.open(rootfile) as rfile:
        if raw_data is False:
            run_data = {}
            ttree = rfile['runsummary/summary;1']
            for cname in ttree.keys():
                run_data[cname] = pd.Series(
                    np.array(ttree[cname].array()),
                    list(range(len(ttree[cname].array()))))
            return pd.DataFrame(run_data)
        else:
            raise NotImplementedError(
                "The extraction of individual events"
                " has not been implemented")


def add_channel_wise_data(measurement_data: pd.DataFrame, complete_config: dict) -> pd.DataFrame:
    """Add channel wise data adds the data from the configuration
    to every channel that is specific to that channel

    :measurement_data: data that was gathered from the chip
    :complete_config: the complete configuration (so the default config with the
                      patch appled that is the measurement configuration
    :returns: a pandas dataframe where a column has been added for each configuration
              parameter that is channel specific the channels are determined by the
              names and types present in the measurement data.
    """
    channel_keys = roc_channel_to_dict(0, 0, 0, complete_config)
    for key in channel_keys:
        measurement_data[key] = measurement_data.apply(
                lambda x: roc_channel_to_dict(
                    x['chip'],
                    x['channel'],
                    x['channeltype'],
                    complete_config)[key], axis=1)
    return measurement_data


def add_half_wise_data(measurement_data: pd.DataFrame, complete_config: dict) -> pd.DataFrame:
    """add the config information of the chip half that corresponds to the particular
    channel

    :measurement_data: data measured from the rocs
    :complete_config: configuration of the rocs at the time of measurement.
        the half wise parameters of the rocs from this config will be added to every
        channel of the corresponding half in the `measurement_data`
    :returns: the dataframe measurement_data with added columns for the half wise
              parameters

    """
    channel_keys = roc_channel_to_globals(0, 0, 1, complete_config)
    for key in channel_keys:
        measurement_data[key] = measurement_data.apply(
                lambda x: roc_channel_to_globals(
                    x['chip'],
                    x['channel'],
                    x['channeltype'],
                    complete_config)[key], axis=1)
    return measurement_data


def add_global_data(measurement_data: pd.DataFrame, global_config: dict) -> pd.DataFrame:
    """add global Data to the dataframe. Currently there is no global data
    so there is nothing to add

    :measurement_data: the dataframe that the global parameters should be added to
    :global_config: the configuration containing the global parameter that should
        be added to the measurement dataframe (it will be added to every channel of every
        chip)
    :returns: Data with the the global parameters added to every channel currently nothing
        is done

    """
    return measurement_data

def roc_channel_to_dict(chip_id, channel_id, channel_type, complete_config):
    """Map a channel identifier to the correct part of the config

    :chip_id: chip_id from the measurement in range 0,1,2 for LD hexaboard
    :channel_id: the channel number of the channel
    :channel_type: the channel type from the measurement
    :complete_config: the complete config of the chip
    :returns: TODO

    """
    id_map = {0: 'roc_s0', 1: 'roc_s1', 2: 'roc_s2'}
    channel_type_map = {0: 'ch', 1: 'calib', 100: 'cm'}
    return complete_config[id_map[int(chip_id)]]\
        [channel_type_map[int(channel_type)]][int(channel_id)]


def roc_channel_to_globals(chip_id, channel_id, channel_type, complete_config):
    """get the chip-half wise configuration from the 

    :chip_id: TODO
    :channel_id: TODO
    :channel_type: the channel type either a normal channel.
                   calibration channel or common mode channel
    :complete_config: The complete configuration of the chip at time of measurement
    :returns: a dictionary of all global setting for the given channel

    """
    id_map = {0: 'roc_s0', 1: 'roc_s1', 2: 'roc_s2'}
    channel_type_map = {0: 'ch', 1: 'calib', 100: 'cm'}
    roc_global_keys = ['DigitalHalf', 'GlobalAnalog', 'MasterTdc', 'ReferenceVoltage']
    channel_type = channel_type_map[channel_type]
    if channel_type == 'ch':
        chip_half = 0 if channel_id < 36 else 1
    if channel_type == 'cm':
        chip_half = 0 if channel_id < 2 else 1
    if channel_type == 'calib':
        chip_half = channel_id
    roc_config = complete_config[id_map[chip_id]]
    result = {}
    for gl_key in roc_global_keys:
        for key, val in roc_config[gl_key][chip_half].items():
            result[key] = val
    return result


def merge_in_config_params(run_data: pd.DataFrame, run_config: dict):
    """
    merge the run_data with the chip parameters for that run

    Note: for the injected_channels chip parameter a column is added
          that is true when the channel was injected into and false
          otherwise.
    """
    run_params = run_config
    for param in run_params.keys():
        if param == 'injection_channels':
            injected_channels = run_params['injection_channels']
            run_data['injected'] = [y in injected_channels
                                    for y in run_data['channel']]
        elif param not in run_data.columns:
            run_param = pd.Series(run_params[param],
                                  index=run_data.index,
                                  name=param)
            run_data = pd.concat([run_data, run_param], axis=1)
    return run_data


def test_extract_data():
    test_root_path = Path('./tests/data/run.root')
    frame = extract_data(test_root_path.resolve())
    expected_columns = ['chip', 'channel', 'channeltype',
                        'adc_median', 'adc_iqr', 'tot_median',
                        'tot_iqr', 'toa_median', 'toa_iqr', 'adc_mean',
                        'adc_stdd', 'tot_mean',
                        'tot_stdd', 'toa_mean', 'toa_stdd', 'tot_efficiency',
                        'tot_efficiency_error', 'toa_efficiency',
                        'toa_efficiency_error']
    for col in expected_columns:
        _ = frame[col]


def test_add_channel_wise_data():
    """ test that all the channel wise parameters appear as a
    column in the dataframe
    """
    import config_utilities as cfu
    test_data_path = Path('./tests/data/run.root')
    frame = extract_data(test_data_path.resolve())
    configuration = cfu.load_configuration('tests/data/default.yaml')
    overlay = cfu.load_configuration('tests/data/run.yaml')
    configuration = cfu.update_dict(configuration, overlay)
    frame = add_channel_wise_data(frame, configuration)
    expected_columns = ['Adc_pedestal',
                        'Channel_off',
                        'DAC_CAL_CTDC_TOA',
                        'DAC_CAL_CTDC_TOT',
                        'DAC_CAL_FTDC_TOA',
                        'DAC_CAL_FTDC_TOT',
                        'DIS_TDC',
                        'ExtData',
                        'HZ_inv',
                        'HZ_noinv',
                        'HighRange',
                        'IN_FTDC_ENCODER_TOA',
                        'IN_FTDC_ENCODER_TOT',
                        'Inputdac',
                        'LowRange',
                        'mask_AlignBuffer',
                        'mask_adc',
                        'mask_toa',
                        'mask_tot',
                        'probe_inv',
                        'probe_noinv',
                        'probe_pa',
                        'probe_toa',
                        'probe_tot',
                        'sel_trig_toa',
                        'sel_trig_tot',
                        'trim_inv',
                        'trim_toa',
                        'trim_tot'
                       ]
    for col in expected_columns:
        print(col, frame[col])


def test_add_half_wise_data():
    """test that all the half_wise parameters are added to the dataframe
    :returns: Nothing

    """
    import config_utilities as cfu
    test_data_path = Path('./tests/data/run.root')
    frame = extract_data(test_data_path.resolve())
    default = cfu.load_configuration('tests/data/default.yaml')
    overlay = cfu.load_configuration('tests/data/run.yaml')
    config = cfu.update_dict(default, overlay)
    frame = add_half_wise_data(frame, config)
    expected_columns = [
            'Adc_TH',
            'Bx_offset',
            'CalibrationSC',
            'ClrAdcTot_trig',
            'IdleFrame',
            'L1Offset',
            'MultFactor',
            'SC_testRAM',
            'SelTC4',
            'Tot_P0',
            'Tot_P1',
            'Tot_P2',
            'Tot_P3',
            'Tot_P_Add',
            'Tot_TH0',
            'Tot_TH1',
            'Tot_TH2',
            'Tot_TH3',
            'sc_testRAM',
            'Cf',
            'Cf_comp',
            'Clr_ADC',
            'Clr_ShaperTail',
            'Delay40',
            'Delay65',
            'Delay87',
            'Delay9',
            'En_hyst_tot',
            'Ibi_inv',
            'Ibi_inv_buf',
            'Ibi_noinv',
            'Ibi_noinv_buf',
            'Ibi_sk',
            'Ibo_inv',
            'Ibo_inv_buf',
            'Ibo_noinv',
            'Ibo_noinv_buf',
            'Ibo_sk',
            'ON_pa',
            'ON_ref_adc',
            'ON_rtr',
            'ON_toa',
            'ON_tot',
            'Rc',
            'Rf',
            'S_inv',
            'S_inv_buf',
            'S_noinv',
            'S_noinv_buf',
            'S_sk',
            'SelExtADC',
            'SelRisingEdge',
            'dac_pol',
            'gain_tot',
            'neg',
            'pol_trig_toa',
            'range_indac',
            'range_inv',
            'range_tot',
            'ref_adc',
            'trim_vbi_pa',
            'trim_vbo_pa',
            'BIAS_CAL_DAC_CTDC_P_D',
            'BIAS_CAL_DAC_CTDC_P_EN',
            'BIAS_FOLLOWER_CAL_P_CTDC_EN',
            'BIAS_FOLLOWER_CAL_P_D',
            'BIAS_FOLLOWER_CAL_P_FTDC_D',
            'BIAS_FOLLOWER_CAL_P_FTDC_EN',
            'BIAS_I_CTDC_D',
            'BIAS_I_FTDC_D',
            'CALIB_CHANNEL_DLL',
            'CTDC_CALIB_FREQUENCY',
            'CTRL_IN_REF_CTDC_P_D',
            'CTRL_IN_REF_CTDC_P_EN',
            'CTRL_IN_REF_FTDC_P_D',
            'CTRL_IN_REF_FTDC_P_EN',
            'CTRL_IN_SIG_CTDC_P_D',
            'CTRL_IN_SIG_CTDC_P_EN',
            'CTRL_IN_SIG_FTDC_P_D',
            'CTRL_IN_SIG_FTDC_P_EN',
            'EN_MASTER_CTDC_DLL',
            'EN_MASTER_CTDC_VOUT_INIT',
            'EN_MASTER_FTDC_DLL',
            'EN_MASTER_FTDC_VOUT_INIT',
            'EN_REF_BG',
            'FOLLOWER_CTDC_EN',
            'FOLLOWER_FTDC_EN',
            'FTDC_CALIB_FREQUENCY',
            'GLOBAL_DISABLE_TOT_LIMIT',
            'GLOBAL_EN_BUFFER_CTDC',
            'GLOBAL_EN_BUFFER_FTDC',
            'GLOBAL_EN_TOT_PRIORITY',
            'GLOBAL_EN_TUNE_GAIN_DAC',
            'GLOBAL_FORCE_EN_CLK',
            'GLOBAL_FORCE_EN_OUTPUT_DATA',
            'GLOBAL_FORCE_EN_TOT',
            'GLOBAL_INIT_DAC_B_CTDC',
            'GLOBAL_LATENCY_TIME',
            'GLOBAL_MODE_FTDC_TOA',
            'GLOBAL_MODE_NO_TOT_SUB',
            'GLOBAL_MODE_TOA_DIRECT_OUTPUT',
            'GLOBAL_SEU_TIME_OUT',
            'GLOBAL_TA_SELECT_GAIN_TOA',
            'GLOBAL_TA_SELECT_GAIN_TOT',
            'INV_FRONT_40MHZ',
            'START_COUNTER',
            'VD_CTDC_N_D',
            'VD_CTDC_N_DAC_EN',
            'VD_CTDC_N_FORCE_MAX',
            'VD_CTDC_P_D',
            'VD_CTDC_P_DAC_EN',
            'VD_FTDC_N_D',
            'VD_FTDC_N_DAC_EN',
            'VD_FTDC_N_FORCE_MAX',
            'VD_FTDC_P_D',
            'VD_FTDC_P_DAC_EN',
            'sel_clk_rcg',
            'Calib',
            'ExtCtest',
            'IntCtest',
            'Inv_vref',
            'Noinv_vref',
            'ON_dac',
            'Refi',
            'Toa_vref',
            'Tot_vref',
            'Vbg_1v',
            'probe_dc',
            'probe_dc1',
            'probe_dc2',
           ]
    for col in expected_columns:
        print(frame[col])
