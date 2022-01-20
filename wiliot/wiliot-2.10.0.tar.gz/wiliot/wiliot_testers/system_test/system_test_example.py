"""
Here is a sample code for a system test.
The purpose of the test is to test the tag's transmission characteristics during different scenarios.
The script can be run from the command line or from a GUI (by running it on any Python platform).

The test parameters are stored in the 'system_test_menu_defaults_file.json' file.
 to run the script using command line:
        go to the script location and type: system_test_example.py -f <file_name>
 <file_name> is the test parameters file, e.g.: system_test_menu_defaults_file.json

Outputs from tests are stored under the outputs folder.
Each test is saved under a different folder with an increasing number.

Change the calibration parameters under get_setup_calibration_data according to your setup.

Review all '# TODO' in the script and change/edit/add according to instructions
"""
import json
import serial.tools.list_ports
import argparse
import os
import tkinter as tk
import tkinter.font as font
import tkinter.filedialog
import matplotlib.pyplot as plt
import time
import datetime
import numpy as np
import csv
from shutil import copyfile
from wiliot.gateway_api.gateway import *  # pip install pywiliot first

# Set Global Parameters:
plt.switch_backend('agg')  # clean and init plot
verbose_flag = False
menu_defaults_global = {'verbose_flag': 1, 'tag_distance': 2.5, 'positioner_enable': 0, 'tag_angle': 0,
                        'gw_att_type': 'None', 'user_gw_dca_raw': 0, 'test_time_sec': 20.0, 'pause_time_sec': 180.0,
                        'number_of_test_iterations': 3, 'GW_Baud': 921600,
                        'energizing_pattern_list': '20', 'gw_timing_list': '(5/15)', 'N_LTBP': 10,
                        'pos_type_var': 'None', 'gw_port': 'Other', 'gw_att_port_var': 'Other',
                        'gw_port_other': ' ', 'gw_att_port_entry': ' ', 'num_rx_packets_to_stop_test': 'NA'}


def save_to_csv(output_csv_file_name, output_csv_file_fields, out_rows):
    """
    save data to the specified csv file

    :type output_csv_file_name: str
    :param output_csv_file_name: the file name where the data is going to be stored
    :type output_csv_file_fields: list
    :param output_csv_file_fields: the headers of the data to be stored
    :type out_rows: np.array
    :param out_rows: the data to be stored

    :return
    """
    with open(output_csv_file_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(output_csv_file_fields)
        csv_writer.writerows(out_rows)


def extract_port_selection(port_var, port_entry):
    """
    extract serial port for connection

    :type port_var: str
    :param port_var: the port variable according to the drop-down menu (all available ports + 'Other' option)
    :type port_entry: str
    :param port_entry: the manually added port. relevant only when port_var is 'Other'

    :return the relevant port
    """
    if 'Other' in port_var:
        port = port_entry
        print('Manual serial port selection: "{}"'.format(port))
    else:
        port = port_var

    return port


def extract_value_from_user_entry(user_entry, is_range=True):
    """
    extract the test parameters from a string when a string can contain a range, e.g. 0:15:90
    or a list of option, e.g. 20,17,52

    :type user_entry: str
    :param user_entry: the user entry string
    :type is_range: bool
    :param is_range: True if user input is a range of number, False if it is a list of options

    :return a list of the extracted value
    """
    if ':' in user_entry:
        sep_str = ':'
    elif ',' in user_entry:
        sep_str = ','
    elif '/' in user_entry:
        sep_str = '/'
    else:
        try:
            if '.' in user_entry:
                value_out = [float(user_entry)]
            else:
                value_out = [int(user_entry)]
            return value_out
        except Exception as e:
            print('please enter range in the following format 0:1:10 or 0,1,10 or '
                  'list in the following format 20,17,52 or 5/15')
            raise SystemExit

    try:
        value_int = [int(n) for n in user_entry.split(sep_str)]
    except ValueError:
        try:
            value_int = [float(n) for n in user_entry.split(sep_str)]
        except Exception as e:
            print('!' * 10 + ' Error: Could Not Extract Range from ' + user_entry + '!' * 10)
            print(e)
            raise SystemExit
    if is_range:
        if len(value_int) != 3:
            print('please enter range in the following format 0:1:10 or 0,1,10 or '
                  'list in the following format 20,17,52 or 5/15')
            raise SystemExit
        value_out = np.arange(value_int[0], value_int[2] + value_int[1], value_int[1])
    else:
        value_out = value_int
    return value_out


def extract_dca_att_range(user_gw_dca_raw):
    """
    extract the DCA Attenuator parameters from a string when a string can contain a range, e.g. 0:0.25:2
    or a number, e.g. 0

    :type user_gw_dca_raw: str
    :param user_gw_dca_raw: the user entry attenuation string

    :return a list of the extracted attenuation
    """
    dca_att_range_raw = extract_value_from_user_entry(user_gw_dca_raw, is_range=True)
    dca_att_range = []
    for dca_val in dca_att_range_raw:
        # TODO add here validation test for your DCA Attenuator:
        fixed_dca = dca_val
        if system_test_hardware.dca_valid_range is not None:
            fixed_dca = max(min(dca_val, system_test_hardware.dca_valid_range[1]),
                            system_test_hardware.dca_valid_range[0])  # make sure the user value is in range
        if dca_val != fixed_dca:
            print('?' * 10 + ' User-Defined DCA Value (' + str(dca_val) + 'dB) changed to: ' + str(
                fixed_dca) + 'dB')

        dca_att_range.append(fixed_dca)

    dca_att_range = np.unique(dca_att_range)
    return dca_att_range


def extract_positioner_angle_range(tag_angle, positioner_enable):
    """
    extract the positioner parameters from a string when a string can contain the angle range (deg), e.g. 0:15:90
    or a number (deg), e.g. 0

    :type positioner_enable: bool
    :param positioner_enable: the user entry position (angles) string
    :type tag_angle: str
    :param tag_angle: the user entry attenuation string

    :return a list of the extracted angles
    """
    if positioner_enable == 0:
        positioner_angle_range = [0]
    else:
        positioner_angle_range = extract_value_from_user_entry(tag_angle, is_range=True)
    return positioner_angle_range


def extract_gw_timing_list(gw_timing_str):
    """
    extract the time profiles parameters from a string when a string can contain a list of profiles, e.g. (5/15),(0/8)
    or a single profile, e.g. (5/15)

    :type gw_timing_str: str
    :param gw_timing_str: the user entry time profile string

    :return a list of the extracted time profiles
    """
    try:
        start_i = [i for i, c in enumerate(gw_timing_str) if c == '(']
        stop_i = [i for i, c in enumerate(gw_timing_str) if c == ')']
        time_profile_str = [gw_timing_str[i + 1:j] for i, j in zip(start_i, stop_i)]
        time_profile_list = [extract_value_from_user_entry(tp, is_range=False) for tp in time_profile_str]

        return time_profile_list
    except Exception as e:
        print('Error: Could not Extract GW Timing List!!! please write in the following format:(x/x),(x/x)')
        raise SystemExit


def generate_high_level_box_plot(results_data_mat, meas_type, y_label, data_col, number_of_test_iterations):
    """
    plot a boxplot of a specific measurement (meas_type, data_col) over all iteration per each test parameter.
    Each scenario (a set of test parameters) is plotted in a different subplot and each tag has a different box.
    The statistics is more significant as the number of iteration increases.
    The graph is saved as a pdf file and stored under the test folder

    :type results_data_mat: np.matrix
    :param results_data_mat: the
    :type meas_type: str
    :param meas_type: the specific measurement name to display
    :type y_label: str
    :param y_label: the y label string
    :type data_col: int
    :param data_col: the column of the relevant data (the specific measurements) to display
    :type number_of_test_iterations: int
    :param number_of_test_iterations: the number of iterations for each test

    :return a list of the extracted time profiles
    """
    tag_id_vec = results_data_mat[:, 9]
    angles_vec = results_data_mat[:, 6].astype(float)
    atts_vec = results_data_mat[:, 16].astype(float)
    energizing_pattern_vec = results_data_mat[:, 11].astype(int)
    time_profile_vec = results_data_mat[:, 12].astype(str)

    # per each parameter (attenuation, angles, timing profiles and energizing patterns):
    energizing_pattern_uni = np.unique(np.array(energizing_pattern_vec).flatten())
    time_profile_uni = np.unique(np.array(time_profile_vec).flatten())
    tag_id_uni = np.unique(np.array(tag_id_vec).flatten())
    angles_uni = np.unique(np.array(angles_vec).flatten())
    atts_uni = np.unique(np.array(atts_vec).flatten())

    n_rows = int(np.ceil(np.sqrt(angles_uni.shape[0])))
    n_cols = int(np.ceil(np.sqrt(angles_uni.shape[0])))

    output_graph_file_name = ''

    if angles_uni.shape[0] <= 9:
        font_size = 14
    else:
        font_size = 10

    for att in atts_uni:
        try:
            att = int(att)
        except Exception as e:
            pass
        for energizing_pattern in energizing_pattern_uni:
            for time_profile in time_profile_uni:
                if np.argwhere(np.logical_and(energizing_pattern_vec == energizing_pattern,
                                              np.logical_and(time_profile_vec == time_profile,
                                                             atts_vec == att)))[:, 0].shape[0] == 0:
                    continue

                plt.figure(figsize=(36, 28), dpi=35)
                for ang_index, ang in enumerate(angles_uni):
                    try:
                        ang = int(ang)
                    except Exception as e:
                        pass
                    output_sub_case_folder, _ = \
                        system_test_log.set_output_folder_and_files(ang, att,
                                                                    extract_gw_timing_list('(' + time_profile.
                                                                                           replace('ms', '') + ')')[0],
                                                                    energizing_pattern)
                    output_graph_file_name = os.path.join(output_sub_case_folder,
                                                          '{} - all iterations.pdf'.format(meas_type))
                    values = []
                    tag_enumeration = ''
                    x_labels = []
                    for tag_index, tag_id in enumerate(tag_id_uni):
                        tag_enumeration = tag_enumeration + ' ' + str(tag_index + 1) + '=' + tag_id + '\n'
                        value_indices = np.argwhere(np.logical_and(
                            np.logical_and(energizing_pattern_vec == energizing_pattern,
                                           time_profile_vec == time_profile),
                            np.logical_and(angles_vec == ang, tag_id_vec == tag_id)))[:, 0]
                        responses_vec = results_data_mat[value_indices, 14].astype(int)
                        values.append(
                            np.array(results_data_mat[value_indices, data_col]).astype(float).flatten())
                        x_labels.append(str(tag_index + 1) + '\n' + str(np.sum(responses_vec)) + '/' + str(
                            number_of_test_iterations))

                    plt.subplot(n_rows, n_cols, ang_index + 1)

                    plt.boxplot(values, vert=True, patch_artist=True, labels=x_labels)
                    plt.rcParams.update({'font.size': font_size - 2})
                    plt.title('ATT=' + str(att) + 'dB, Angle=' + str(int(ang)) + '$^o$', fontsize=font_size)
                    plt.xlabel('Tag Index\\n/N', fontsize=font_size)
                    plt.ylabel(y_label, fontsize=font_size)
                    plt.grid()

                    if ang_index + 1 == angles_uni.shape[0]:
                        bottom_x, top_x = plt.xlim()
                        bottom_y, top_y = plt.ylim()
                        plt.text(top_x, bottom_y, tag_enumeration, fontsize=font_size - 2)

                plt.suptitle('Test #' + str(system_test_log.max_folder_number) + ': Energizing Pattern=' + str(
                    energizing_pattern) + ', Timing Profile=' + time_profile + ', ' + str(
                    tag_id_uni.shape[0]) + ' Tags', fontsize=24)

                plt.savefig(output_graph_file_name)
                plt.close('all')
                if verbose_flag:
                    print(output_graph_file_name)

        plt.close('all')


def init_test_parameters():
    """
    initialize the test parameters by constant values
    :return a dictionary of the test parameters
    """
    test_parameters = {}
    system_test_log.set_main_test_folder()
    test_parameters['max_folder_number'] = system_test_log.max_folder_number
    test_parameters['main_test_folder'] = system_test_log.main_test_folder
    # ignoring the long time of the first packet transmission:
    test_parameters['num_packets_for_max_time_between_packets'] = 1
    test_parameters['output_csv_file_fields'] = ['Time to First Packet [sec]', 'Number of Received Packets (GW)',
                                                 'RX Rate (GW) [Hz]', 'Normalized RX Rate (GW) [Hz]',
                                                 'Longest Time between Packets (GW) [sec] ',
                                                 'Longest Time between Packets after ' +
                                                 str(test_parameters['num_packets_for_max_time_between_packets']) +
                                                 ' Packets (GW) [sec]',
                                                 'Tag Angle [Deg]', 'Tag Distance [m]', 'Test Iteration', 'Tag ID',
                                                 'GW BLE Chip SW Version', 'Energizing Pattern', 'Timing Profile',
                                                 'Test Time [sec]', 'Response', 'ATT Type', 'ATT Setting [dB]',
                                                 'RSSI',
                                                 'Energizing Emulated Distance [m]',
                                                 'Beacons Emulated Distance [m]']
    test_parameters['test_time_sec'] = 0.0
    test_parameters['pause_time_sec'] = 0.0
    return test_parameters


def cli_config_to_test_param(config_data):
    """
    according to the configuration file content and to constant values,
    the function assigns the relevant values to the test parameters and return them

    :type config_data: dict
    :param config_data: the configuration data

    :return a dictionary of the test parameters
    """
    test_parameters = init_test_parameters()
    global verbose_flag
    verbose_flag = config_data['verbose_flag']
    for key, value in config_data.items():
        test_parameters[key] = value
    # arrange unique parameters:
    test_parameters['energizing_pattern_list'] = extract_value_from_user_entry(config_data['energizing_pattern_list'],
                                                                               is_range=False)
    test_parameters['gw_timing_list'] = extract_gw_timing_list(str(config_data['gw_timing_list']))
    test_parameters['test_time_sec'] = float(config_data['test_time_sec'])
    test_parameters['pause_time_sec'] = float(config_data['pause_time_sec'])
    num_rx_packets_to_stop_test = config_data['num_rx_packets_to_stop_test']
    try:
        test_parameters['num_rx_packets_to_stop_test'] = int(num_rx_packets_to_stop_test)
    except Exception as e:
        test_parameters['num_rx_packets_to_stop_test'] = 0

    return test_parameters


class Log(object):
    """
    This class is responsible for all the files and folders name
    """

    def __init__(self):

        self.outputs_folder = os.path.join(os.path.dirname(__file__), 'outputs')  # outputs folder name
        self.max_folder_number = 0
        self.main_test_folder = ''
        self.config_file_name = ''

    def set_main_test_folder(self):
        """
        set the main test folder name.
        For each test a new folder is generated anf its name is an increases number
        """
        if not os.path.exists(self.outputs_folder):
            os.makedirs(self.outputs_folder)
        else:
            last_test_run_folders = os.listdir(self.outputs_folder)
            last_test_run_num = []
            for folder_name in last_test_run_folders:
                try:
                    last_test_run_num.append(int(folder_name))
                except Exception as e:
                    pass
            if last_test_run_num:
                self.max_folder_number = max(last_test_run_num)

        self.max_folder_number = self.max_folder_number + 1

        self.main_test_folder = os.path.join(self.outputs_folder, str(self.max_folder_number))
        if not os.path.exists(self.main_test_folder):
            os.makedirs(self.main_test_folder)
            if verbose_flag:
                print('Created Main Output Folder: {}'.format(self.main_test_folder))
        else:
            print('!' * 10 + ' ' + self.main_test_folder + ' already exist' + '!' * 10)
            raise SystemExit

        return

    def set_output_folder_and_files(self, positioner_angle, actual_gw_dca_att, time_profile, energizing_pattern):
        """
        set the output folders for each scenario, i.e.e set of test parameters according to the function inputs
        :type positioner_angle: int or str
        :param positioner_angle: the current test positioner angle in deg
        :type actual_gw_dca_att: int or str
        :param actual_gw_dca_att: the current test attenuation in dB
        :type time_profile: list
        :param time_profile: the current test GW time profile [on-value, period] in ms
        :type energizing_pattern: int or str
        :param energizing_pattern: the current test GW energizing pattern
        """
        output_sub_case_folder = os.path.join(self.main_test_folder, 'Ang=' + str(positioner_angle) + ' Deg',
                                              'ATT=' + str(actual_gw_dca_att) + 'dB',
                                              'Timing=(' + str(time_profile[0]) + ',' + str(time_profile[1]) + ')',
                                              'Pattern=' + str(energizing_pattern))

        if not os.path.exists(output_sub_case_folder):
            os.makedirs(output_sub_case_folder)
            if verbose_flag:
                print('Created Output Folder: ' + output_sub_case_folder)

        results_output_csv_file_name = os.path.join(output_sub_case_folder,
                                                    str(self.max_folder_number) + '. MTRST - Results.csv')
        return output_sub_case_folder, results_output_csv_file_name

    def set_config_file_name(self, new_file_name):
        """
        set new name to the configuration file

        :type new_file_name str
        :param new_file_name the new config file name
        """
        self.config_file_name = new_file_name


class Config(object):
    """
    This class is responsible for all the configuration functions
    """
    def __init__(self):
        self.calibration_param = []

    def get_setup_calibration_data(self):
        """
        GW_Pout - GW power out (in dBm)
        Setup_Conducted_Insertion_Line - the signal loss due to cable and connectors
        Horn_Gain - the signal/loss gain due to the antenna used in the test
        f_transmit - the GW freq in GHz
        Ref_GW_EIRP - the reference GW Effective Radiated Power (the estimated GW power out with its antenna
        """
        # TODO Add here your setup calibration parameters
        # CAL_Params=[GW_Pout, Setup_Conducted_IL, Horn_Gain, f_transmit, Ref_GW_EIRP]
        self.calibration_param = [21.7, 3.4, 11.4, 2.48, 23]
        return self.calibration_param

    def calc_emulated_distance(self, gw_att, tag_distance):
        """
        This function calculates the estimated emulated distance
        or the actual distance between the GW and the tag in the open space

        According to Friis equation [in dB]:
        transmitter = GW
        receiver = tag

        according to the test setup: Pr = Pt + Gt + Gr + 20*log(lambda/(4*pi*d))
        Pt = gw_power_out - setup_conducted_insertion_line + horn_gain [dB]
        d = tag_distance
        Gt = 0 [dB], Gr = 0 [dB]

        estimating the real-life-application distance between gw and tag in open space:
        d_e = (10^-((Pr_e - Pt_e -Gt_e - Gr_e)/20)) * (lambda/(4*pi))
        Pr_e = Pr [dB]
        Pt_e = reference_gw_EIRP [dB]
        Gt_e, Gr_e = 0 [dB]

        lambda - wavelength = v/f, when v in free space 3*10^8 and f = f_transmit*10^9
        lambda = (3*10^8)/(f_transmit*10^9) = 0.3/f_transmit
        """
        gw_pout, setup_conducted_il, horn_gain, f_transmit, ref_gw_eirp = self.calibration_param
        dis_tag = float(tag_distance)
        beacons_backoff = 0  # gw config parameter for reducing the beacons power. default is 0

        estimated_distance = []
        calc_types = ['energizing', 'beacons']
        for dis_type in calc_types:
            lambda_wave = 0.3 / f_transmit  # wave length according to the gw frequency in GHz
            p_t_setup = 0  # init
            if dis_type == 'energizing':
                p_t_setup = gw_pout - setup_conducted_il + horn_gain - gw_att  # the setup gain and loss components
            elif dis_type == 'beacons':
                p_t_setup = gw_pout - setup_conducted_il + horn_gain - gw_att - beacons_backoff

            p_r = p_t_setup + 20 * np.log10(lambda_wave/(4*np.pi*dis_tag))  # the power available at the receiver
            # calculate the estimated distance between the gw's antenna and tag's antenna without the setup's components
            d_e = round((10 ** (-((p_r - ref_gw_eirp)/20))) * (lambda_wave / (4 * np.pi)), 2)
            estimated_distance.append(d_e)

        return estimated_distance[0], estimated_distance[1]


class GUI(object):
    """
    This class is responsible for all the GUI functions
    """
    def __init__(self):
        """
        initialize all parameters and GUI screen
        """
        # init default values:
        self.stop_all = False
        self.system_test_menu_defaults_file_name = os.path.join(os.path.dirname(__file__),
                                                                'system_test_menu_defaults_file.json')
        if not os.path.isfile(self.system_test_menu_defaults_file_name) or \
                os.stat(self.system_test_menu_defaults_file_name).st_size == 0:
            # save the default values to json
            with open(self.system_test_menu_defaults_file_name, "w") as f:
                json.dump(menu_defaults_global, f)

        # start the GUI application
        master = tk.Tk()
        master.geometry("600x800+0+0")
        master.title("Multi-Tag System Test")
        font.nametofont('TkDefaultFont').configure(size=12)

        self.pad_x_0 = 10
        self.pad_x_1 = 350

        self.verbose_enable_checkbutton_status = tk.IntVar()
        tk.Checkbutton(master, text="Verbose Mode", variable=self.verbose_enable_checkbutton_status). \
            grid(row=0, padx=self.pad_x_0, sticky=tk.W)

        tk.Label(master, text="Distance [m]", fg='black').grid(row=1, column=0, sticky=tk.W, padx=self.pad_x_1 * .73)

        positioner_enable_checkbutton_status = tk.IntVar()
        tk.Checkbutton(master, text="Enable Positioner", variable=positioner_enable_checkbutton_status, fg='red'). \
            grid(row=2, padx=self.pad_x_0, sticky=tk.W)
        tk.Label(master, text="Positioner Type", fg='red').grid(row=2, column=0, sticky=tk.W, padx=self.pad_x_1 * .65)

        pos_type_list = ['Positioner1', 'Positioner2', 'Positioner3']
        pos_type_var = tk.StringVar()
        tk.OptionMenu(master, pos_type_var, *pos_type_list).grid(row=2, padx=self.pad_x_1, sticky=tk.W)

        tk.Label(master, text="Tag Angle [Degrees]", fg='red').grid(row=3, column=0, sticky=tk.W, padx=self.pad_x_0)
        tk.Label(master, text="GW ATT Type", fg='magenta').grid(row=4, padx=self.pad_x_0, sticky=tk.W)

        dca_type_list = ['DCA1', 'DCA2', 'None']
        self.gw_dca_type_var = tk.StringVar()
        tk.OptionMenu(master, self.gw_dca_type_var, *dca_type_list).grid(row=4, padx=self.pad_x_1, sticky=tk.W)

        tk.Label(master, text="GW ATT Value [dB]", fg='magenta').grid(row=5, padx=self.pad_x_0, sticky=tk.W)
        tk.Label(master, text="Test Time [sec]", fg='red').grid(row=9, column=0, sticky=tk.W, padx=self.pad_x_0)
        tk.Label(master, text="Pause Time [sec]", fg='red').grid(row=10, column=0, sticky=tk.W, padx=self.pad_x_0)
        tk.Label(master, text="Number of Iterations", fg='red').grid(row=11, column=0, sticky=tk.W, padx=self.pad_x_0)
        tk.Label(master, text="GW Energizing Pattern", fg='magenta').grid(row=14, column=0, sticky=tk.W,
                                                                          padx=self.pad_x_0)
        tk.Label(master, text="GW Timing Profile (ON-Time/Period) [ms]", fg='magenta').grid(row=15, column=0,
                                                                                            sticky=tk.W,
                                                                                            padx=self.pad_x_0)
        tk.Label(master, text="Required Number of RX Packets to Stop Test", fg='black').grid(row=19, column=0,
                                                                                             sticky=tk.W,
                                                                                             padx=self.pad_x_0)

        distance_entry = tk.Entry(master, fg='black', font="Calibri 12")
        tag_angle_entry = tk.Entry(master, fg='red', font="Calibri 12")
        gw_att_entry = tk.Entry(master, fg='magenta', font="Calibri 12")
        test_time_entry = tk.Entry(master, fg='red', font="Calibri 12")
        pause_time_entry = tk.Entry(master, fg='red', font="Calibri 12")
        num_iterations_entry = tk.Entry(master, fg='red', font="Calibri 12")
        energizing_pattern_entry = tk.Entry(master, fg='magenta', font="Calibri 12")
        timing_profile_entry = tk.Entry(master, fg='magenta', font="Calibri 12")
        num_packet_to_stop_single_tag_test_entry = tk.Entry(master, fg='black', font="Calibri 12")

        distance_entry.grid(row=1, column=0, sticky=tk.W, padx=self.pad_x_1)
        tag_angle_entry.grid(row=3, column=0, sticky=tk.W, padx=self.pad_x_1)
        gw_att_entry.grid(row=5, padx=self.pad_x_1, sticky=tk.W)
        test_time_entry.grid(row=9, column=0, sticky=tk.W, padx=self.pad_x_1)
        pause_time_entry.grid(row=10, column=0, sticky=tk.W, padx=self.pad_x_1)
        num_iterations_entry.grid(row=11, column=0, sticky=tk.W, padx=self.pad_x_1)
        energizing_pattern_entry.grid(row=14, column=0, sticky=tk.W, padx=self.pad_x_1)
        timing_profile_entry.grid(row=15, column=0, sticky=tk.W, padx=self.pad_x_1)
        num_packet_to_stop_single_tag_test_entry.grid(row=19, column=0, sticky=tk.W, padx=self.pad_x_1)

        tk.Button(master, text='Set Defaults', command=self.set_defaults, bg='blue', fg='yellow'). \
            grid(row=20, column=0, sticky=tk.W, padx=self.pad_x_1, pady=5)

        self.runtime_label = tk.Label(master, text='', fg='black')
        self.runtime_label.grid(row=21, column=0, sticky=tk.W, padx=180, pady=5)
        tk.Button(master, text='Calculate Runtime', command=self.calculate_runtime, bg='white', fg='green'). \
            grid(row=21, column=0, sticky=tk.W, padx=10, pady=5)

        self.config_file_name_label = tk.Label(master, text='', fg='black')
        self.config_file_name_label.grid(row=23, column=0, sticky=tk.W, padx=210)
        tk.Button(master, text='Set Config File Name', command=self.gui_set_config_file_name, bg='blue', fg='white'). \
            grid(row=23, column=0, sticky=tk.W, padx=10)
        tk.Button(master, text='Generate Config File', command=self.gui_generate_config_file,
                  bg='yellow', fg='black').grid(row=24, column=0, sticky=tk.W, pady=5, padx=10)

        available_ports = [s.device for s in serial.tools.list_ports.comports()]
        if len(available_ports) == 0:
            available_ports = [s.name for s in serial.tools.list_ports.comports()]
        available_ports.append('Other')
        # assign to gui variables
        si_labs_ports = available_ports
        non_si_labs_port = available_ports

        gw_port_var = tk.StringVar()
        tk.Label(master, text="GW Port", fg='black').grid(row=25, padx=self.pad_x_0, sticky=tk.W)
        tk.OptionMenu(master, gw_port_var, *si_labs_ports).grid(row=25, padx=self.pad_x_0 + 150, sticky=tk.W)

        gw_port_entry = tk.Entry(master, fg='black', font="Calibri 12")
        gw_port_entry.grid(row=25, column=0, sticky=tk.W, padx=self.pad_x_0 + 250)

        tk.Label(master, text="GW ATT Port", fg='black').grid(row=27, padx=self.pad_x_0, sticky=tk.W)
        gw_att_port_var = tk.StringVar()
        tk.OptionMenu(master, gw_att_port_var, *non_si_labs_port).grid(row=27, padx=self.pad_x_0 + 150, sticky=tk.W)

        gw_att_port_entry = tk.Entry(master, fg='black', font="Calibri 12")
        gw_att_port_entry.grid(row=27, column=0, sticky=tk.W, padx=self.pad_x_0 + 250)

        tk.Button(master, text='Run Test', command=lambda: run_main(gui_obj=self), bg='green', fg='white', width=20,
                  height=1,
                  font="Calibri 16").grid(row=29, column=0, sticky=tk.W, padx=10, pady=5)
        tk.Button(master, text='Quit', command=self.quit_gui, bg='red', fg='white', width=20, height=1,
                  font="Calibri 16").grid(row=29, column=0, sticky=tk.W, padx=250, pady=5)

        master.protocol("WM_DELETE_WINDOW", self.quit_gui)
        # saved variables:
        self.master = master
        self.gw_port_var = gw_port_var
        self.gw_port_entry = gw_port_entry
        self.gw_att_port_var = gw_att_port_var
        self.gw_att_port_entry = gw_att_port_entry
        self.pos_type_var = pos_type_var
        self.gw_att_entry = gw_att_entry
        self.tag_angle_entry = tag_angle_entry
        self.positioner_enable_checkbutton_status = positioner_enable_checkbutton_status
        self.distance_entry = distance_entry
        self.test_time_entry = test_time_entry
        self.pause_time_entry = pause_time_entry
        self.num_iterations_entry = num_iterations_entry
        self.energizing_pattern_entry = energizing_pattern_entry
        self.timing_profile_entry = timing_profile_entry
        self.num_packet_to_stop_single_tag_test_entry = num_packet_to_stop_single_tag_test_entry
        # set gui fields:
        try:
            self.revert_selections()
        except Exception as e:
            self.set_defaults()
        # start
        self.master.mainloop()

    def gui_extract_test_parameters(self, file_name_to_save=None):
        """
        according to the GUI user entry content and to constant values,
        the function assigns the relevant values to the test parameters and return them

        :type file_name_to_save: str
        :param file_name_to_save: the file name which the test parameters will be stored.
                                  if None the test parameters are stored at the default file (see Log() class)

        :return a dictionary of the test parameters
        """
        test_parameters = init_test_parameters()
        global verbose_flag
        verbose_flag = self.verbose_enable_checkbutton_status.get()
        test_parameters['verbose_flag'] = verbose_flag
        test_parameters['gw_att_type'] = self.gw_dca_type_var.get()
        test_parameters['gw_att_port_var'] = self.gw_att_port_var.get()
        test_parameters['gw_att_port_entry'] = self.gw_att_port_entry.get()
        test_parameters['user_gw_dca_raw'] = str(self.gw_att_entry.get())
        test_parameters['tag_angle'] = str(self.tag_angle_entry.get())
        test_parameters['positioner_enable'] = self.positioner_enable_checkbutton_status.get()
        test_parameters['pos_type_var'] = self.pos_type_var.get()
        test_parameters['tag_distance'] = str(self.distance_entry.get())
        test_parameters['test_time_sec'] = float(self.test_time_entry.get())
        test_parameters['pause_time_sec'] = float(self.pause_time_entry.get())
        test_parameters['number_of_test_iterations'] = int(self.num_iterations_entry.get())
        test_parameters['energizing_pattern_list'] = \
            extract_value_from_user_entry(self.energizing_pattern_entry.get(), is_range=False)
        test_parameters['gw_timing_list'] = extract_gw_timing_list(str(self.timing_profile_entry.get()))

        num_rx_packets_to_stop_test = self.num_packet_to_stop_single_tag_test_entry.get()
        if num_rx_packets_to_stop_test.isnumeric():
            test_parameters['num_rx_packets_to_stop_test'] = int(num_rx_packets_to_stop_test)
        else:
            test_parameters['num_rx_packets_to_stop_test'] = 0

        test_parameters['gw_port'] = extract_port_selection(self.gw_port_var.get(), self.gw_port_entry.get())

        menu_defaults = {'verbose_flag': self.verbose_enable_checkbutton_status.get(),
                         'tag_distance': self.distance_entry.get(),
                         'positioner_enable': self.positioner_enable_checkbutton_status.get(),
                         'tag_angle': self.tag_angle_entry.get(),
                         'gw_att_type': self.gw_dca_type_var.get(),
                         'user_gw_dca_raw': self.gw_att_entry.get(),
                         'test_time_sec': self.test_time_entry.get(),
                         'pause_time_sec': test_parameters['pause_time_sec'],
                         'number_of_test_iterations': test_parameters['number_of_test_iterations'],
                         'energizing_pattern_list': self.energizing_pattern_entry.get(),
                         'gw_timing_list': self.timing_profile_entry.get(),
                         'pos_type_var': self.pos_type_var.get(),
                         'gw_port': self.gw_port_var.get(),
                         'gw_att_port_var': self.gw_att_port_var.get(),
                         'gw_port_other': self.gw_port_entry.get(),
                         'gw_att_port_entry': self.gw_att_port_entry.get(),
                         'num_rx_packets_to_stop_test': test_parameters['num_rx_packets_to_stop_test']}
        if file_name_to_save is None:
            file_name_to_save = self.system_test_menu_defaults_file_name
        json.dump(menu_defaults, open(file_name_to_save, "w"))

        return test_parameters

    def gui_set_config_file_name(self):
        """
        starts to run if 'set config file' button is pressed.
        If a name was not selected after he dialog pop-up a default name to the config file is generated
        """
        # open a dialog
        user_selection = tk.filedialog.asksaveasfile(initialdir=os.path.dirname(__file__),
                                                     filetypes=[('json files', '*.json')],
                                                     defaultextension='.json')

        if user_selection is not None:
            system_test_log.set_config_file_name(user_selection.name)
        else:  # if the user did not select a name, a default name is created
            now = datetime.datetime.now()
            timestamp = datetime.datetime.timestamp(now)
            timestamp_str = str(timestamp).replace('.', '_')
            system_test_log.set_config_file_name(os.path.dirname(__file__) + '/config_' + timestamp_str + '.json')

        self.config_file_name_label.destroy()
        self.config_file_name_label = tk.Label(self.master, text=system_test_log.config_file_name,
                                               fg='black', wraplength=350, justify='left', font="Calibri 8")
        self.config_file_name_label.grid(row=23, column=0, sticky=tk.W, padx=210)

    def gui_generate_config_file(self):
        """
        starts to run if 'generate config file' button is pressed.
        this function saves all test parameters to the configuration file
        """
        if is_gui:  # this function runs only when gui is enabled
            now = datetime.datetime.now()
            timestamp = datetime.datetime.timestamp(now)
            timestamp_str = str(timestamp).replace('.', '_')
            if not system_test_log.config_file_name:
                system_test_log.set_config_file_name(
                    os.path.join(os.path.dirname(__file__), 'config_{}.json'.format(timestamp_str)))
            try:
                self.gui_extract_test_parameters(file_name_to_save=system_test_log.config_file_name)
                print('Configuration saved to file: ' + system_test_log.config_file_name)
            except Exception as e:
                print('an error occurred during saving new configuration:\n{}'.format(e))
        else:
            print("gui_generate_config_file is running although Command Line run method was applied")
            return

        tk.Label(self.master, text=system_test_log.config_file_name + ' saved' + ' ' * 1000, fg='black', wraplength=350,
                 justify='left', font="Calibri 8").grid(row=24, column=0, sticky=tk.W, padx=200)

    def calculate_runtime(self):
        """
        starts to run if 'calculate run time' button is pressed.
        this function calculate the whole test run time according to all user entry parameters including
        parameters range and pauses between tests iterations/cycles
        """
        tag_angle = str(self.tag_angle_entry.get())
        positioner_enable = self.positioner_enable_checkbutton_status.get()
        positioner_angle_range = extract_positioner_angle_range(tag_angle, positioner_enable)
        gw_att_type = self.gw_dca_type_var.get()
        user_gw_dca_raw = str(self.gw_att_entry.get())
        if gw_att_type == 'None':
            print('DCA Attenuator type was not define, hence no attenuation range is set')
            num_atts = 1
        else:
            dca_att_range = extract_dca_att_range(user_gw_dca_raw)
            num_atts = len(dca_att_range)

        if positioner_enable == 0:
            num_angles = 1
        else:
            num_angles = len(positioner_angle_range)

        test_time_sec = float(self.test_time_entry.get())
        pause_time_sec = float(self.pause_time_entry.get())
        number_of_test_iterations = int(self.num_iterations_entry.get())
        energizing_pattern_list = list(int(x) for x in self.energizing_pattern_entry.get().split(','))
        gw_timing_str = str(self.timing_profile_entry.get())
        gw_timing_list = extract_gw_timing_list(gw_timing_str)

        length_gw_timing_list = np.shape(gw_timing_list)[0]
        # calculate the number of iterations
        overall_number_of_iterations = num_atts * num_angles * number_of_test_iterations * len(
            energizing_pattern_list) * length_gw_timing_list
        # calculate the test tine in seconds:
        estimated_runtime_sec = overall_number_of_iterations * (test_time_sec + pause_time_sec + 5)

        if estimated_runtime_sec > 60:
            estimated_runtime_string = str(round(estimated_runtime_sec / 60, 2)) + ' Minutes'
        else:
            estimated_runtime_string = str(round(estimated_runtime_sec, 2)) + ' Seconds'
        if estimated_runtime_sec > 3600:
            estimated_runtime_string = str(round(estimated_runtime_sec / 3600, 2)) + ' Hours'
        if estimated_runtime_sec > 86400:
            estimated_runtime_string = str(round(estimated_runtime_sec / 86400, 2)) + ' Days'

        self.runtime_label.destroy()
        self.runtime_label = tk.Label(self.master, text=estimated_runtime_string, fg='black')
        self.runtime_label.grid(row=21, column=0, sticky=tk.W, padx=180, pady=5)

    def quit_gui(self):
        """
        starts to run if 'quit' button is pressed.
        This function can be used to stop all processes in a safe way
        """
        print('Operation terminated by user.')
        self.stop_all = True  # a flag that terminates a test even if not all iterations are completed

        raise SystemExit

    def set_gui_fields(self, menu_defaults):
        """
        This function sets all GUI fields and assign a default values

        :type menu_defaults: dict
        :param menu_defaults: the GUI fields default values
        """
        self.distance_entry.delete(0, 'end')
        self.tag_angle_entry.delete(0, 'end')
        self.test_time_entry.delete(0, 'end')
        self.pause_time_entry.delete(0, 'end')
        self.num_iterations_entry.delete(0, 'end')
        self.energizing_pattern_entry.delete(0, 'end')
        self.timing_profile_entry.delete(0, 'end')
        self.num_packet_to_stop_single_tag_test_entry.delete(0, 'end')
        self.gw_att_entry.delete(0, 'end')
        self.gw_port_entry.delete(0, 'end')
        self.gw_att_port_entry.delete(0, 'end')
        self.distance_entry.insert(10, menu_defaults['tag_distance'])
        self.tag_angle_entry.insert(10, menu_defaults['tag_angle'])
        self.test_time_entry.insert(10, menu_defaults['test_time_sec'])
        self.pause_time_entry.insert(10, menu_defaults['pause_time_sec'])
        self.num_iterations_entry.insert(10, menu_defaults['number_of_test_iterations'])
        self.energizing_pattern_entry.insert(10, menu_defaults['energizing_pattern_list'])
        self.timing_profile_entry.insert(10, menu_defaults['gw_timing_list'])
        self.num_packet_to_stop_single_tag_test_entry.insert(10, menu_defaults['num_rx_packets_to_stop_test'])
        self.gw_att_entry.insert(10, menu_defaults['user_gw_dca_raw'])

        self.positioner_enable_checkbutton_status.set(int(menu_defaults['positioner_enable']))
        self.pos_type_var.set(str(menu_defaults['pos_type_var']))
        self.verbose_enable_checkbutton_status.set(int(menu_defaults['verbose_flag']))
        self.gw_dca_type_var.set(str(menu_defaults['gw_att_type']))
        self.gw_port_var.set(menu_defaults['gw_port'])
        self.gw_att_port_var.set(menu_defaults['gw_att_port_var'])
        self.gw_att_port_entry.insert(10, menu_defaults['gw_att_port_entry'])

        self.calculate_runtime()

    def set_defaults(self):
        """
        Sets the default values for all GUI fields
        """
        menu_defaults = menu_defaults_global
        self.set_gui_fields(menu_defaults)

    def revert_selections(self):
        """
        starts to run if 'reset to default' button is pressed.
        This function overwrite users changes in the GUI and set the default values instead
        """
        try:
            menu_defaults = json.load(open(self.system_test_menu_defaults_file_name, "rb"))
        except Exception as e:
            menu_defaults = menu_defaults_global
            print('?' * 10 + ' Incompatible History File - Using Defaults Instead.')

        self.set_gui_fields(menu_defaults)


class TestEquipment(object):
    """
    This class is responsible for all scripts related to the test equipments including external position
    and DCA attenuator, that can be implemented during the system test.
    This class is only an example since for each setup a different functions and interfaces should be implemented
    """
    def __init__(self):
        """
        initialize equipment
        """
        # TODO add here specific range or conditions for each DCA type, e.g. valid range:
        self.dca_valid_range = [0, 20]
        # TODO add here specific range or conditions for the positioner, e.g. valid range:

    def test_equipment_connect_to_positioner(self, positioner_enable, pos_type_var, tag_angle):
        """
        This function connects to the positioner and return the positioner class and connections status

        :type positioner_enable bool
        :param positioner_enable: specified if the positioner is enable in the test setup
        :type pos_type_var str
        :param pos_type_var: the positioner name/type
        :type tag_angle str
        :param tag_angle: the desired angles for the positioner during the test

        :return the connection status (bool), the positioner object, the angles range (list of angles in deg)
        """
        if positioner_enable == 1:
            print("Connect to positioner: {}".format(pos_type_var))
            # TODO add here a connection to your positioner
            connect_pos_flag = True  # if connection was establish, connect_pos_flag is True
            my_pos = []  # your positioner class for further actions
            pos_range = extract_positioner_angle_range(tag_angle,
                                                       positioner_enable)  # the test range for the positioner
        else:
            connect_pos_flag = False
            my_pos = None
            pos_range = None
        return connect_pos_flag, my_pos, pos_range

    def test_equipment_connect_to_dca(self, att_type, port_var, port_entry, user_dca_raw):
        """
        This function connects to the DCA attenuator and return the attenuator class and connections status

        :type att_type str
        :param att_type: the attenuator name/type
        :type port_var str
        :param port_var: the attenuator serial port
        :type port_entry str
        :param port_entry: the attenuator manually serial port (relevant only if port_var is 'Other'
        :type user_dca_raw str
        :param user_dca_raw: the desired attenuation range for the positioner during the test

        :return the connection status (bool), the positioner object, the angles range (list of angles in deg)
        """
        dca_port = extract_port_selection(port_var, port_entry)
        print("Connect to DCA: type {}, port:".format(att_type, dca_port))
        # TODO add here a connection to your DCA logic
        connect_dca_flag = True  # if connection was establish, connect_dac_flag is True
        my_att = []  # your attenuator class for further actions
        dca_att_range = extract_dca_att_range(user_dca_raw)  # the test range for the attenuator

        return connect_dca_flag, my_att, dca_att_range

    def exit(self):
        """
        This function exit and close all processes related to the test equipment
        """
        # TODO close all connections and exit
        pass


# ======================Main Code Starts===============================================


def run_test(gui_obj, output_sub_case_folder, gw_obj, test_time_sec, test_iteration, energizing_pattern,
             num_packets_for_max_time_between_packets,
             tag_angle_str, tag_distance, time_profile, gw_att_type, actual_gw_dca_att,
             gw_ver, num_rx_packets_to_stop_test, t_start):
    """
    This function runs the core test
    First parameters and GW are initiated
    Then a while loop runs until timeout or after N received packets if num_rx_packets_to_stop_test is specified
    During the while loop the tags' packets are stored and checked for validity and for new tags
    At the end of the loop the GW is configured to stop transmitting energy to the tags.
    After each iteration and csv with all packets data is saved together with two graphs (as pdf files) containing the
    boxplot (distribution) of the time between packets and a temporal graph of the number of packets per tag vs. time

    :type gui_obj: GUI class
    :param gui_obj: the object of the GUI class
    :type output_sub_case_folder: str
    :param output_sub_case_folder: the folder path of the current test results
    :type gw_obj: WiliotGateway
    :param gw_obj: the object of the WiliotGateway class
    :type test_time_sec: int
    :param test_time_sec: the test timeout in seconds
    :type test_iteration: int
    :param test_iteration: the current test iteration
    :type energizing_pattern: int
    :param energizing_pattern: the current test energizing pattern for the GW
    :type num_packets_for_max_time_between_packets: int
    :param num_packets_for_max_time_between_packets: the number of packet from which the longest time after N packets
                                                    is measured
    :type tag_angle_str: str
    :param tag_angle_str: the tag angle in deg
    :type tag_distance: int or float
    :param tag_distance: the tag distance in the test setup
    :type time_profile: list
    :param time_profile: the current test time profile for the GW
    :type gw_att_type: str
    :param gw_att_type: the attenuator type for logging
    :type actual_gw_dca_att: int or float
    :param actual_gw_dca_att: the current test attentuation
    :type gw_ver: str
    :param gw_ver: the GW version for logging
    :type num_rx_packets_to_stop_test: int
    :param num_rx_packets_to_stop_test: if specified (larger than 0) the current test continued until
                                        the received packets have reached this number or if timeout occurred
    :type t_start: int
    :param t_start: the start time of the test in seconds

    :return the data output (2D list), the test completion time in sec
    """
    dis_energizing, dis_beacons = system_test_config.calc_emulated_distance(actual_gw_dca_att, tag_distance)
    test_time_sec_local = test_time_sec

    packet_data = []
    t_vec = []
    tag_id_vec = []
    rssi_vec = []
    tag_id_list = []

    time_profile_str = str(time_profile[0]) + 'ms/' + str(time_profile[1]) + 'ms'
    # GW:
    if gw_obj is None:
        gw_obj = WiliotGateway(baud=921600, auto_connect=True, verbose=False)
    # config
    gw_obj.config_gw(energy_pattern_val=energizing_pattern, time_profile_val=time_profile)
    gw_obj.check_current_config()
    gw_obj.reset_buffer()

    t0 = time.time()
    timeout = t0 + test_time_sec_local

    print('Starting Multi-Tag System Test (Duration=' + str(test_time_sec_local) + ' Seconds)...')
    time_remaining_prev = test_time_sec_local
    gw_obj.run_packets_listener(do_process=True)

    while time.time() < timeout:
        time.sleep(0.0)  # help the cpu to recover between loops
        if gui_obj is not None:
            gui_obj.master.update()
            if gui_obj.stop_all:
                break
        if not gw_obj.is_data_available():
            continue
        # data is available - let's get data:
        # data_in = gw_obj.get_data(action_type=ActionType.FIRST_SAMPLES, num_of_packets=1, data_type=DataType.RAW)
        data_in = gw_obj.get_data(action_type=ActionType.FIRST_SAMPLES, num_of_packets=1, data_type=DataType.PROCESSED)
        if not data_in:
            continue
        # new packet has arrived:
        packet_data.append(data_in['packet'])
        t_vec.append(data_in['time_from_start'])
        # check the advertising address:
        # processes_packet = gw_obj.run_process_packet(raw_data=[data_in])
        tag_id_vec.append(data_in['adv_address'])
        rssi_vec.append(data_in['rssi'])
        if not data_in['adv_address'] in tag_id_list:
            print('********** New Tag Detected: ' + data_in['adv_address'] + ' **********')
            tag_id_list.append(data_in['adv_address'])

        # check if need to print:
        time_remaining = timeout - time.time()
        if time_remaining_prev - time_remaining >= 1:
            print(tag_angle_str + u'\N{DEGREE SIGN}, GW ATT [dB] ' + str(actual_gw_dca_att) + ' (' + str(
                dis_energizing) + ' m), ' + time_profile_str +
                  ', Pattern ' + str(energizing_pattern) + ', Iteration ' + str(test_iteration) +
                  ', Time Remaining [sec]: ' + str(round(time_remaining)) + ', Tag Count: ' + str(len(tag_id_list)) +
                  ', Overall Packet Count: ' + str(len(packet_data)))

            time_remaining_prev = time_remaining

        # check if we received enough packets:
        if num_rx_packets_to_stop_test > 0:
            if len(packet_data) >= num_rx_packets_to_stop_test:
                print('*' * 10 + ' ' + str(
                    num_rx_packets_to_stop_test) + ' Packets Received - Stopping Iteration. ' + '*' * 10)
                test_time_sec_local = t_vec[-1]
                break

    gw_obj.stop_processes()
    gw_obj.config_gw(time_profile_val=[0, 15])  # stop transmitting
    gw_obj.check_current_config()

    # check if there are more packets in the GW API buffer that have received before the end of the test:
    while True:
        data_in = gw_obj.get_data(action_type=ActionType.FIRST_SAMPLES, num_of_packets=1, data_type=DataType.PROCESSED)
        if not data_in or data_in['time_from_start'] > test_time_sec_local:
            break
        else:
            packet_data.append(data_in['packet'])
            t_vec.append(data_in['time_from_start'])
            tag_id_vec.append(data_in['adv_address'])
            if not (data_in['adv_address'] in tag_id_list):
                print('********** New Tag Detected: ' + data_in['adv_address'] + ' **********')
                tag_id_list.append(data_in['adv_address'])

    # write data to csv:
    if len(packet_data) > 0:
        packets_output_csv_file_name = output_sub_case_folder + '/' + str(test_iteration) + '. MTRST - Packets Data.csv'
        output_csv_file_fields = ['Time [sec]', 'Tag ID', 'Packets Data']
        save_to_csv(packets_output_csv_file_name, output_csv_file_fields,
                    np.transpose([t_vec, tag_id_vec, packet_data]))

    # check duplication
    packet_data_wo_rssi = []
    for full_packet in packet_data:
        packet_data_wo_rssi.append(full_packet[:74])

    _, unique_packet_data_indices = np.unique(packet_data_wo_rssi,
                                              return_index=True)
    unique_packet_data_indices = np.sort(unique_packet_data_indices)
    unique_packet_data = np.array(packet_data)[unique_packet_data_indices.astype(int)]
    t_vec_without_duplicated_packets = np.array(t_vec)[unique_packet_data_indices.astype(int)]
    tag_id_vec_without_duplicated_packets = np.array(tag_id_vec)[unique_packet_data_indices.astype(int)]
    tag_id_list = np.unique(tag_id_vec_without_duplicated_packets)

    # arrange data to save csv and graphs (as pdf)
    output_wo_dup = []

    for packet_index in range(len(unique_packet_data)):
        pixie_analyzer_out_row = [t_start + t_vec[packet_index], tag_angle_str, tag_distance, test_iteration, gw_ver,
                                  energizing_pattern, time_profile_str, test_time_sec_local, gw_att_type,
                                  actual_gw_dca_att, dis_energizing, dis_beacons]

        output_wo_dup.append(pixie_analyzer_out_row)

    plt.figure(figsize=(16, 12), dpi=100)
    temporal_graph_file_name = output_sub_case_folder + '/' + str(
        test_iteration) + '. MTRST - Temporal Graph.pdf'
    box_plot_tbp_file_name = output_sub_case_folder + '/' + str(test_iteration) + '. MTRST - TBP BP.pdf'

    out_rows = []
    rates_rx_tx = []
    ttfp_vec = []
    tbp = []

    for tag_id, rssi in zip(tag_id_list, rssi_vec):
        # find the indices of each tag (w/o duplications)
        indices_wo_dup = np.argwhere(np.array(tag_id_vec_without_duplicated_packets).flatten() == tag_id)
        t_wo_dup = np.array(t_vec_without_duplicated_packets[indices_wo_dup]).flatten()
        # calculate the time between packets
        tbp.append(list(np.diff(t_wo_dup)))
        # find the indices of each tag (including duplications)
        indices_with_dup = np.argwhere(np.array(tag_id_vec).flatten() == tag_id)
        t_with_dup = np.array(np.array(t_vec)[indices_with_dup]).flatten()
        # find the time to first packet of each tag
        ttfp = t_wo_dup[0]
        ttfp_vec.append(ttfp)
        num_rx_packets = len(indices_wo_dup)  # number of packets per tag
        # calculate the receiving rate: #of packets divided by th time
        rx_rate = num_rx_packets / test_time_sec_local
        # calculate the longest time between packets
        if num_rx_packets == 1:
            ltbp = test_time_sec_local - t_wo_dup[-1]
            norm_rx_rate = 1 / test_time_sec_local
            ltbp_after_n_packets = 0
        else:
            ltbp = np.max([np.max(np.diff(t_wo_dup)), test_time_sec_local - t_wo_dup[
                -1]])
            if test_time_sec_local - ttfp == 0:  # not supposed to happen
                norm_rx_rate = num_rx_packets / test_time_sec_local
            else:
                norm_rx_rate = num_rx_packets / (test_time_sec_local - ttfp)
            if num_rx_packets > num_packets_for_max_time_between_packets + 1:
                # longest time between packets after n Packets
                ltbp_after_n_packets = np.max(
                    [np.max(np.diff(t_wo_dup[num_packets_for_max_time_between_packets - 1:-1])),
                     test_time_sec_local - t_wo_dup[-1]])
            else:
                ltbp_after_n_packets = 0

        # plotting the received packets vs. time
        p = plt.step(t_with_dup, range(1, len(t_with_dup) + 1), '--', where='pre', label=None)
        plt.step(t_wo_dup, range(1, len(t_wo_dup) + 1), ':', color=p[-1].get_color(), label=tag_id + ', RX')

        out_row = [np.transpose(np.array(
            [ttfp, num_rx_packets, rx_rate, norm_rx_rate, ltbp, ltbp_after_n_packets, tag_angle_str, tag_distance,
             test_iteration, tag_id, gw_ver, energizing_pattern, time_profile_str, test_time_sec_local, '1',
             gw_att_type, actual_gw_dca_att, rssi, dis_energizing, dis_beacons]))]
        # concatenate data:
        if len(out_rows) == 0:
            out_rows = out_row
        else:
            if len(out_row) > 0:
                out_rows = np.vstack([out_rows, out_row])

        rates_rx_tx.append(norm_rx_rate)

    if len(tag_id_list) > 0:
        plt.legend()
        plt.title('Tag Count: ' + str(len(tag_id_list)))
        plt.xlabel('Time [sec]')
        plt.ylabel('Packet Count')
        plt.grid(axis='both')
        plt.savefig(temporal_graph_file_name)
        plt.close('all')

        plt.figure(figsize=(16, 12), dpi=100)
        plt.boxplot(tbp, vert=True, patch_artist=True, labels=tag_id_list)
        plt.title('Tag Count: ' + str(len(tag_id_list)))
        plt.ylabel('Time between Packets [sec]')
        plt.grid()
        plt.savefig(box_plot_tbp_file_name)
        plt.close('all')

    plt.close('all')

    return out_rows, test_time_sec_local


def run_main(with_gui=True, gui_obj=None):
    """
    This function run the whole test with all its iterations
    At first, the function initializes all parameters, establishes connection with the GW and all other test equipment,
    and sets all test folder names.
    Then it runs over several loops, a loop per each user-specified parameter.
    for each scenario, i.e. a different set of test parameter, the function calls the run_test to preform the test.
    At the end of each iteration a combined file containing all iteration results is saved and stored under the
    test folder. At the end of all iterations the function exits from all functions, GW and test equipment processes
    """
    system_test_config.get_setup_calibration_data()
    generate_high_level_box_plot_flag = False
    if with_gui:
        test_parameters = gui_obj.gui_extract_test_parameters()  # Not CLI
    else:
        if not cli_configuration:
            print("please add test parameters to '{}'".format(system_test_log.config_file_name))
            raise SystemExit
        else:
            test_parameters = cli_config_to_test_param(cli_configuration)

    number_of_test_iterations = test_parameters['number_of_test_iterations']

    # Gateway:
    gw_obj = WiliotGateway(baud=921600, port=test_parameters['gw_port'], verbose=False)
    gw_obj.reset_gw()
    # config to main param without transmitting (time profile - ON value is 0)
    gw_obj.config_gw(filter_val=False, pacer_val=False, time_profile_val=[0, 15], beacons_backoff_val=0,
                     received_channel=37, modulation_val=True)
    gw_sw_ver, gw_hw_ver = gw_obj.get_gw_version()
    gw_ver = gw_hw_ver + '=' + gw_sw_ver
    # DCA Attenuator:
    connect_gw_dca_flag, my_gw_att, gw_dca_att_range = \
        system_test_hardware.test_equipment_connect_to_dca(test_parameters['gw_att_type'],
                                                           test_parameters['gw_att_port_var'],
                                                           test_parameters['gw_att_port_entry'],
                                                           test_parameters['user_gw_dca_raw'])
    # Positioner
    connect_pos_flag, my_pos, positioner_angle_range = \
        system_test_hardware.test_equipment_connect_to_positioner(bool(test_parameters['positioner_enable']),
                                                                  test_parameters['pos_type_var'],
                                                                  test_parameters['tag_angle'])

    output_sub_case_folder_list = []
    out_rows_all_test_cases = []

    t_start = 0

    for positioner_angle in positioner_angle_range:  # positioner loop
        if test_parameters['positioner_enable'] == 1:
            print('Moving Positioner by ' + str(positioner_angle) + ' Degrees.')
            # TODO implement positioner movement:
            # my_pos.move_to_pos_deg(positioner_angle)
            tag_angle_str = str(positioner_angle)
        else:
            tag_angle_str = test_parameters['tag_angle']

        for gw_dca_att in gw_dca_att_range:  # attenuation loop
            if connect_gw_dca_flag:
                print('DCA set to ' + str(gw_dca_att) + 'dB')
                # TODO implement attenuation setup for your DCA:
                # my_gw_att.set_attn(gw_dca_att)
                actual_gw_dca_att = gw_dca_att
            else:
                actual_gw_dca_att = 0

            for time_profile in test_parameters['gw_timing_list']:  # time profile loop
                for energizing_pattern in test_parameters['energizing_pattern_list']:  # energizing pattern loop
                    test_iteration = 0
                    out_rows_all = []

                    while test_iteration < number_of_test_iterations:  # iterations loop
                        test_iteration = test_iteration + 1
                        if gui_obj is not None:
                            if gui_obj.stop_all:
                                break
                        output_sub_case_folder, results_output_csv_file_name = \
                            system_test_log.set_output_folder_and_files(positioner_angle, actual_gw_dca_att,
                                                                        time_profile, energizing_pattern)
                        output_sub_case_folder_list.append(output_sub_case_folder)
                        print('Iteration Number ' + str(test_iteration) + ', Pausing for ' + str(
                            test_parameters['pause_time_sec']) + ' Seconds...')
                        time.sleep(test_parameters['pause_time_sec'])

                        t_start = t_start + test_parameters['pause_time_sec']

                        out_rows, test_time_sec_local = \
                            run_test(gui_obj, output_sub_case_folder, gw_obj,
                                     test_parameters['test_time_sec'], test_iteration,
                                     energizing_pattern, test_parameters['num_packets_for_max_time_between_packets'],
                                     tag_angle_str, test_parameters['tag_distance'],
                                     time_profile, test_parameters['gw_att_type'], actual_gw_dca_att,
                                     gw_ver, test_parameters['num_rx_packets_to_stop_test'], t_start)

                        t_start = t_start + test_time_sec_local
                        # concatenate results:
                        if len(out_rows) > 0:
                            if len(out_rows_all) == 0:
                                out_rows_all = out_rows
                            else:
                                if len(out_rows) > 0:
                                    out_rows_all = np.vstack([out_rows_all, out_rows])

                            if verbose_flag:
                                # print(out_rows_all)
                                print(results_output_csv_file_name)

                            save_to_csv(results_output_csv_file_name, test_parameters['output_csv_file_fields'],
                                        out_rows_all)

                    if len(out_rows_all_test_cases) == 0:
                        out_rows_all_test_cases = out_rows_all
                    else:
                        if len(out_rows_all) > 0:
                            out_rows_all_test_cases = np.vstack((out_rows_all_test_cases, out_rows_all))

                    if len(out_rows_all_test_cases) > 0:
                        combined_output_csv_file_name = os.path.join(system_test_log.main_test_folder,
                                                                     '{}. MTRST - All Results.csv'.
                                                                     format(system_test_log.max_folder_number))
                        save_to_csv(combined_output_csv_file_name, test_parameters['output_csv_file_fields'],
                                    out_rows_all_test_cases)

                        # TODO change this flag to true if you want to generate box plot including
                        #  all iterations of a specific test parameters
                        if generate_high_level_box_plot_flag:
                            generate_high_level_box_plot(np.matrix(out_rows_all_test_cases), meas_type='TTFP',
                                                         y_label='TTFP [sec]', data_col=0,
                                                         number_of_test_iterations=number_of_test_iterations)
                            generate_high_level_box_plot(np.matrix(out_rows_all_test_cases), meas_type='RX-Rate',
                                                         y_label='Normalized RX Rate w/o Dup. [Hz]', data_col=2,
                                                         number_of_test_iterations=number_of_test_iterations)
                            generate_high_level_box_plot(np.matrix(out_rows_all_test_cases), meas_type='LTBP',
                                                         y_label='LTBP [sec]', data_col=4,
                                                         number_of_test_iterations=number_of_test_iterations)
                    if gui_obj is not None:
                        if gui_obj.stop_all:
                            gw_obj.exit_gw_api()
                            system_test_hardware.exit()
                            print('Done.')
                            return

    # close all connection
    gw_obj.exit_gw_api()
    system_test_hardware.exit()
    print('Done.')

    raise SystemExit


# ======================Main Code Ends===============================================
if __name__ == '__main__':
    # init Log and Config
    is_gui = False
    system_test_log = Log()
    system_test_config = Config()
    system_test_hardware = TestEquipment()
    # read from command line if applicable:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='File_Name',
                        help='File_Name - Configuration File Name (Json Format, *.json)')
    args = vars(parser.parse_args())
    system_test_log.config_file_name = args['File_Name']
    cli_configuration = {}

    if system_test_log.config_file_name is None:
        # run using GUI
        is_gui = True
        system_test_gui = GUI()

    else:
        # run using Command line
        is_gui = False
        cli_configuration = json.load(open(system_test_log.config_file_name, "rb"))
        verbose_flag = cli_configuration['verbose_flag']
        run_main(with_gui=False)
