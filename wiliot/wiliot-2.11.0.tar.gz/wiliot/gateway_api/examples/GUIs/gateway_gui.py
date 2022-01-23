from os.path import isfile
from tkinter import Tk, INSERT, END
import serial.tools.list_ports
import pygubu
import json
import multiprocessing
from wiliot.gateway_api.gateway import *
from wiliot.packet_data_tools.process_encrypted_packets import *
import csv

# default config values:
EP_DEFAULT = 20  # Energizing pattern
EPs_DEFAULT = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
               50, 51, 52)  # All Energizing pattern
TP_O_DEFAULT = 5  # timing profile on
TP_P_DEFAULT = 15  # timing profile period
PI_DEFAULT = 0  # pace interval
RC_DEFAULT = 37
RCs_DEFAULT = (37, 38, 39)
VIEW_TYPES = ('current samples', 'first samples')
DATA_TYPES = ('raw', 'processed')
CONFIG_SUM = "EP:{EP}\nTP_ON:{TP_ON}\nTP_P:{TP_P}\nRC:{RC}\nPI:{PI}\nF:{F}"
baud_rates = ["921600"]


class GatewayUI(object):
    gwCommandsPath = '.gwCommands.json'
    gwUserCommandsPath = '.gwUserCommands.json'
    gwAllCommands = []
    gwCommands = []
    gwUserCommands = []
    filter_state = False
    show_both_screens = False
    portActive = False
    log_state = False
    autoscroll_state = True
    csv_from_cur_log_state = True
    log_path = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + 'gw_log.log'
    logger = logging.getLogger('root')
    stat_type = StatType.N_FILTERED_PACKETS

    def __init__(self, main_app_folder='', array_out=None, tk_frame=None):
        print('GW UI mode is activated')
        self.busy_processing = False
        self.close_requested = False
        # 1: Create a builder
        self.builder = builder = pygubu.Builder()

        # 2: Load an ui file
        uifile = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__))), 'utils', 'gw_debugger_v2.ui')
        builder.add_from_file(uifile)

        if tk_frame:
            self.ttk = tk_frame  # tkinter.Frame , pack(fill="both", expand=True)
        else:
            self.ttk = Tk()
        self.ttk.title("Wiliot Gateway Test Application")

        # 3: Create the widget using a self.ttk as parent
        self.mainwindow = builder.get_object('mainwindow', self.ttk)

        self.ttk = self.ttk

        # set the scroll bar of the main textbox
        textbox = self.builder.get_object('recv_box')
        scrollbar = self.builder.get_object('scrollbar')
        textbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=textbox.yview)
        self.builder.get_object('scrollbar').set(self.builder.get_object('recv_box').index(INSERT),
                                                 self.builder.get_object('recv_box').index(END))
        self.builder.get_object('recv_box').grid()

        self.builder.connect_callbacks(self)

        # upload pre-defined commands
        self.gwCommandsPath = os.path.join(main_app_folder, self.gwCommandsPath)
        if isfile(self.gwCommandsPath):
            with open(self.gwCommandsPath, 'r') as f:
                self.gwCommands = json.load(f)

        self.gwUserCommandsPath = os.path.join(main_app_folder, self.gwUserCommandsPath)
        if isfile(self.gwUserCommandsPath):
            with open(self.gwUserCommandsPath, 'r') as f:
                self.gwUserCommands = json.load(f)

        self.gwAllCommands = self.gwCommands + self.gwUserCommands

        # define array to export data for other applications
        if array_out is None:
            self.data_out = multiprocessing.Queue()
        else:
            self.data_out = array_out

        self.ttk.lift()
        self.ttk.attributes("-topmost", True)
        self.ttk.attributes("-topmost", False)

        self.ObjGW = WiliotGateway(logger_name='root')
        self.config_param = {}

        # update ui
        self.ui_update('init')
        self.ui_update('available_ports')

        self.ttk.protocol("WM_DELETE_WINDOW", self.close_window)

        self.ttk.after_idle(self.periodic_call)
        self.ttk.mainloop()

    def close_window(self):
        self.close_requested = True
        print("User requested close at:", time.time(), "Was busy processing:", self.busy_processing)

    def periodic_call(self):
        if not self.close_requested:
            self.busy_processing = True
            self.busy_processing = False
            self.ttk.after(500, self.periodic_call)

        else:
            print("Destroying GUI at:", time.time())
            try:
                self.ObjGW.exit_gw_api()
                if self.log_state:
                    logging.FileHandler(self.log_path).close()
                self.ttk.destroy()
            except Exception as e:
                print(e)
                exit(1)

    def on_connect(self):
        if not self.portActive:
            try:
                port = self.builder.get_object('port_box').get().rsplit(' ', 1)[0]
                baud = self.builder.get_object('baud_rate_box').get().rsplit(' ', 1)[0]
                if port == '' or baud == '':
                    return

                if self.ObjGW.open_port(port, baud):  # open and check if succeed
                    self.print_function(str_in="> Port successfully opened")
                    self.portActive = True
                    self.builder.get_object('connect_button').configure(text='Disconnect')
                    # print version:
                    self.print_function(str_in=self.ObjGW.hw_version + '=' + self.ObjGW.sw_version)
                    self.builder.get_object('recv_box').see(END)
                    # config gw to receive packets (and not only manage bridges):
                    self.ObjGW.write('!enable_brg_mgmt 0')
                    # update UI:
                    self.ui_update('connect')
                    # start listening:
                    self.ObjGW.run_packets_listener(do_process=True, tag_packets_only=False)
                    data_handler_listener = threading.Thread(target=self.recv_data_handler, args=())
                    data_handler_listener.start()

                else:
                    self.print_function(str_in="> Can't open Port - check connection parameters and try again")
                    self.portActive = False
            except Exception as e:
                self.print_function(str_in="> Encounter a problem during connection")
                print(e)

        else:  # Port is open, close it...
            try:
                self.print_function(str_in="> Disconnecting from Port")
                self.ObjGW.exit_gw_api()
                self.builder.get_object('connect_button').configure(text="Connect")
                self.portActive = False
                self.ui_update('connect')
            except Exception as e:
                print(e)

    def on_search_ports(self):
        self.ObjGW.available_ports = [s.device for s in serial.tools.list_ports.comports()]
        if len(self.ObjGW.available_ports) == 0:
            self.ObjGW.available_ports = [s.name for s in serial.tools.list_ports.comports()]
        # update ui:
        self.ui_update('available_ports')

    def on_both_screens(self):
        self.show_both_screens = self.builder.get_variable('autoscroll_state').get()
        if self.show_both_screens:
            self.print_function(str_in="> Show data on both screens")
        else:
            self.print_function(str_in="> Show data only here")

    def recv_data_handler(self):
        print("DataHandlerProcess Start")
        consecutive_exception_counter = 0
        while True:
            time.sleep(0)
            try:
                if self.close_requested or not self.portActive:
                    print("DataHandlerProcess Stop")
                    return

                # check if there is data to read
                if self.ObjGW.is_data_available():
                    # check which data type to read:
                    action_type = ''
                    if self.builder.get_object('view_type').get() == 'current samples':
                        action_type = ActionType.CURRENT_SAMPLES
                    elif self.builder.get_object('view_type').get() == 'first samples':
                        action_type = ActionType.FIRST_SAMPLES
                    # get data
                    data_type = DataType.RAW
                    if self.builder.get_object('data_type').get() == 'raw':
                        data_type = DataType.RAW
                    elif self.builder.get_object('data_type').get() == 'processed':
                        data_type = DataType.PROCESSED

                    data_in = self.ObjGW.get_data(action_type=action_type, num_of_packets=1, data_type=data_type)
                    if not data_in:
                        continue
                    if isinstance(data_in, list):
                        print("we extracted more than one element at a time.\nonly the first packet is printed")
                        data_in = data_in[0]
                    # print
                    data_str = []
                    for key, value in data_in.items():
                        data_str.append("{} : {}".format(key, value))
                    all_data_str = ', '.join(data_str)
                    self.print_function(str_in=all_data_str)
                    # add it to the JTAG GUI if needed:
                    if self.show_both_screens:
                        self.data_out.put(data_in)
                    consecutive_exception_counter = 0
            except Exception as e:
                print(e)
                print("DataHandlerProcess Exception")
                consecutive_exception_counter = consecutive_exception_counter + 1
                if consecutive_exception_counter > 10:
                    print("Abort DataHandlerProcess")
                    return

    def on_update_gw_version(self):
        self.print_function(str_in="> Updating GW version, please wait...")
        version_path_entry = self.builder.get_object('version_path').get()
        if version_path_entry:
            version_path_entry = version_path_entry.strip("\u202a")  # strip left-to-right unicode if exists
            if not os.path.isfile(version_path_entry):
                self.print_function(str_in="> cannot find the entered gw version file:")
                return

        success_update = self.ObjGW.update_version(versions_path=version_path_entry)
        # listen again:
        self.ObjGW.run_packets_listener(do_process=True, tag_packets_only=False)
        if success_update:
            self.print_function(str_in="> Update GW version was completed ")
        else:
            self.print_function(str_in="> Update GW version was failed ")

    def on_reset(self):
        self.ObjGW.reset_gw()

    def on_write(self):
        cmd_value = self.builder.get_object('write_box').get()
        self.ObjGW.write(cmd_value)

        if cmd_value.strip() not in list(self.builder.get_object('write_box')['values']):
            temp = list(self.builder.get_object('write_box')['values'])

            # keep only latest instances
            if temp.__len__() == 20:
                temp.pop(0)
            if len(self.gwUserCommands) >= 20:
                self.gwUserCommands.pop(0)
            self.gwUserCommands.append(cmd_value)
            temp.append(cmd_value)
            self.builder.get_object('write_box')['values'] = tuple(temp)
            with open(self.gwUserCommandsPath, 'w+') as f:
                json.dump(self.gwUserCommands, f)

        if 'set_tester_mode 1' in cmd_value:
            self.stat_type = StatType.GW_PACKET_TIME
        elif 'set_tester_mode 0' in cmd_value:
            self.stat_type = StatType.N_FILTERED_PACKETS

        self.ui_update(state='config')

    def on_config(self):
        filter_val = self.filter_state
        pacer_val = int(self.builder.get_object('pace_inter').get())
        energ_ptrn_val = int(self.builder.get_object('energizing_pattern').get())
        time_profile_val = [int(self.builder.get_object('timing_profile_on').get()),
                            int(self.builder.get_object('timing_profile_period').get())]
        received_channel_val = int(self.builder.get_object('received_channel').get())
        self.print_function(str_in="> Setting GW configuration...")

        config_param_set = self.ObjGW.config_gw(filter_val=filter_val, pacer_val=pacer_val,
                                                energy_pattern_val=energ_ptrn_val, time_profile_val=time_profile_val,
                                                received_channel=received_channel_val,
                                                modulation_val=True)
        # update config parameters:
        for key, value in config_param_set.__dict__.items():
            if key == 'filter' or key == 'modulation':
                self.config_param[key] = str(value)[0]
            else:
                self.config_param[key] = str(value)

        self.ui_update(state='config')
        self.print_function(str_in="> Configuration is set")

    def on_set_filter(self):
        self.filter_state = self.builder.get_variable('filter_state').get()
        self.print_function(str_in='> Setting filter...')
        config_param_set = self.ObjGW.config_gw(filter_val=self.filter_state)
        self.config_param["filter"] = str(config_param_set.filter)[0]

        self.ui_update(state='config')

    def on_clear(self):
        self.builder.get_object('recv_box').delete('1.0', END)
        self.builder.get_object('recv_box').see(END)

    def on_log(self):
        self.log_state = not self.log_state
        if self.log_state:
            self.log_path = self.builder.get_object('log_path').get()
            if self.log_path:
                self.log_path = self.log_path.strip("\u202a")  # strip left-to-right unicode if exists
            else:
                self.log_state = False
                self.print_function(str_in='> Log path is invalid')
                self.builder.get_object('log_button')['text'] = 'Start Log'
                return
            try:
                logging.basicConfig(filename=self.log_path, filemode='a',
                                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                    datefmt='%H:%M:%S', level=logging.DEBUG)
                self.logger.addHandler(logging.FileHandler(self.log_path))
                self.print_function(str_in='> Start Logging')
                self.builder.get_object('log_button')['text'] = 'Stop Log'
                return
            except Exception as e:
                print(e)
                self.print_function(str_in='> Log path is invalid')
                self.log_state = False
                self.builder.get_object('log_button')['text'] = 'Start Log'
                return
        else:
            self.builder.get_object('log_button')['text'] = 'Start Log'
            self.print_function(str_in='> Stop Logging')
            logging.FileHandler(self.log_path).close()

    def on_autoscroll(self):
        self.autoscroll_state = self.builder.get_variable('autoscroll_state').get()

    def on_csv_cur(self):
        self.csv_from_cur_log_state = self.builder.get_variable('csv_cur_state').get()
        if self.csv_from_cur_log_state:
            if self.builder.get_object('csv_path').get():
                self.builder.get_object('csv_path').delete('0', END)
            self.builder.get_object('csv_path').insert(END, self.log_path)
            self.builder.get_object('csv_path')['state'] = 'disabled'
        else:
            self.builder.get_object('csv_path')['state'] = 'enabled'

    def on_export_csv(self):
        if self.csv_from_cur_log_state:
            csv_path = self.log_path
        else:
            csv_path = self.builder.get_object('csv_path').get()
        self.create_csv(log_path=csv_path)
        # check if csv file was created
        if isfile(csv_path.replace('.log', '_data.csv')):
            self.print_function('csv data file was created: {}'.format(csv_path.replace('.log', '_data.csv')))
        else:
            self.print_function('csv data file was not created')
        if isfile(csv_path.replace('.log', '_config.csv')):
            self.print_function('csv config file was created: {}'.format(csv_path.replace('.log', '_config.csv')))
        else:
            self.print_function('csv config file was not created')

    def extract_packets_from_log(self, log_path=None):
        if log_path is None:
            self.print_function(str_in='no log path was found. Export csv failed')
            return
        try:
            packets = []
            packets_time = []
            if isfile(log_path):
                f = open(log_path, 'r')
                lines = f.readlines()

                for line in lines:
                    if 'raw : process_packet("' in line or 'is_valid_tag_packet : True' in line:
                        # a data line
                        if 'raw : process_packet("' in line:
                            packet_raw = str(line.split('raw : ')[-1].split(',')[0])
                        else:
                            packet_raw = str('process_packet("{}")'.format(line.split('packet : ')[1].split(',')[0]))
                        if 'time_from_start : ' in line:
                            packet_time = float(line.split(', time_from_start : ')[-1].split(',')[0])
                        else:
                            packet_time = float(line.split(', time : ')[-1])

                        packets.append(packet_raw)
                        packets_time.append(packet_time)
                f.close()
            return packets, packets_time
        except Exception as e:
            print(e)
            self.print_function(str_in='export packets from log was failed')
            return None, None

    def create_csv(self, log_path=None):

        def create_config_csv(data_in):
            # create config type:
            comments = self.builder.get_object('csv_comment').get()
            if comments == 'add comments':
                comments = '-'
            config_data = {'commonRunName': [common_run_name],
                             'comments': [comments]}
            # generate the csv file:
            with open(log_path.replace('.log', '_config.csv'), 'w', newline='') as f_config:
                writer_cld = csv.writer(f_config)
                writer_cld.writerow(list(config_data.keys()))
                writer_cld.writerows(list(map(list, zip(*[val for val in config_data.values()]))))
                f_config.close()

        if log_path is None:
            self.print_function(str_in='no log path was found. Export csv failed')
            return

        common_run_name = 'gw_gui_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            if isfile(log_path):
                packets, packets_time = self.extract_packets_from_log(log_path=log_path)
                if packets is None or packets_time is None:
                    self.print_function(str_in='export csv was failed')
                    return

                data_to_csv = {'commonRunName': [common_run_name] * len(packets),
                               'encryptedPacket': packets, 'time': packets_time}

                # generate the csv file:
                with open(log_path.replace('.log', '_data.csv'), 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(list(data_to_csv.keys()))
                    writer.writerows(list(map(list, zip(*[val for val in data_to_csv.values()]))))
                    f.close()
                # generate config file according to cloud convention:
                create_config_csv(data_to_csv)
            else:
                self.print_function(str_in='invalid log path: {}\nexport csv was failed'.format(log_path))
        except Exception as e:
            print(e)
            self.print_function(str_in='export csv was failed')

    def on_processed_data(self):
        if self.csv_from_cur_log_state:
            log_path = self.log_path
        else:
            log_path = self.builder.get_object('csv_path').get()
        packets, packets_time = self.extract_packets_from_log(log_path=log_path)
        processed_data = process_encrypted_packet(packets=packets, packets_time=packets_time, stat_type=self.stat_type)
        # generate the csv file:
        try:
            with open(log_path.replace('.log', '_encrypted_process.csv'), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(list(processed_data.keys()))
                writer.writerows(list(map(list, zip(*[val for val in processed_data.values()]))))
                f.close()
        except Exception as e:
            self.print_function('processed csv file was failed due to: {}'.format(e))
            return

        # check if csv file was created
        if isfile(log_path.replace('.log', '_encrypted_process.csv')):
            self.print_function('csv file was created: {}'.format(log_path.replace('.log', '_encrypted_process.csv')))
        else:
            self.print_function('csv file was not created')

    def ui_update(self, state):
        # updating UI according to the new state
        if state == 'init':
            self.builder.get_object('write_box')['values'] = tuple(self.gwAllCommands)
            # default config values:
            self.builder.get_object('energizing_pattern')['values'] = tuple(EPs_DEFAULT)
            self.builder.get_object('energizing_pattern').set(EP_DEFAULT)
            self.builder.get_object('timing_profile_on').set(TP_O_DEFAULT)
            self.builder.get_object('timing_profile_period').set(TP_P_DEFAULT)
            self.builder.get_object('pace_inter').set(PI_DEFAULT)
            self.builder.get_object('received_channel')['values'] = tuple(RCs_DEFAULT)
            self.builder.get_object('received_channel').set(RC_DEFAULT)

            self.config_param = {"energy_pattern": str(EP_DEFAULT),
                                 "received_channel": str(RC_DEFAULT),
                                 "time_profile_on": str(TP_O_DEFAULT),
                                 "time_profile_period": str(TP_P_DEFAULT),
                                 "pacer_val": str(PI_DEFAULT),
                                 "filter": "N"}

            self.builder.get_object('config_sum').insert(END, CONFIG_SUM.format(
                RC="", EP="", TP_ON="", TP_P="", PI="", F=""))
            self.builder.get_object('config_sum').see(END)

            self.builder.get_object('view_type')['values'] = tuple(VIEW_TYPES)
            self.builder.get_object('view_type').set('first samples')
            self.builder.get_object('data_type')['values'] = tuple(DATA_TYPES)
            self.builder.get_object('data_type').set('raw')

            self.builder.get_object('log_button')['text'] = 'Start Log'
            self.builder.get_object('log_path').insert(END, self.log_path)

            self.builder.get_variable('autoscroll_state').set(self.autoscroll_state)
            self.builder.get_variable('both_screens_state').set(self.show_both_screens)
            self.builder.get_variable('csv_cur_state').set(self.csv_from_cur_log_state)
            if self.csv_from_cur_log_state:
                self.builder.get_object('csv_path').insert(END, self.log_path)
                self.builder.get_object('csv_path')['state'] = 'disabled'

            ver_num, _ = self.ObjGW.get_latest_version_number()
            if ver_num is not None:
                self.builder.get_object('version_num').insert(END, 'new:' + ver_num)
            self.builder.get_object('version_num_cur').insert(END, 'current:')

        elif state == 'available_ports':
            if self.ObjGW.available_ports:
                self.print_function(str_in=f'> Finished searching for ports, available ports: '
                                           f'{", ".join(self.ObjGW.available_ports)}')
                self.builder.get_object('port_box')['values'] = tuple(self.ObjGW.available_ports)
            else:
                self.print_function(str_in="no serial ports were found. please check your connections and refresh")
            self.builder.get_object('baud_rate_box')['values'] = tuple(baud_rates)
            self.builder.get_object('port_box')['state'] = 'enabled'
            self.builder.get_object('baud_rate_box')['state'] = 'enabled'
            self.builder.get_object('baud_rate_box').set(baud_rates[0])

        elif state == 'connect':
            if self.portActive:
                # connected
                enable_disable_str = 'enabled'
                enable_disable_con_str = 'disabled'
                self.builder.get_object('version_num_cur').delete('1.0', END)
                self.builder.get_object('version_num_cur').insert(END, 'current:' + self.ObjGW.sw_version)
            else:
                # disconnected
                enable_disable_str = 'disabled'
                enable_disable_con_str = 'enabled'
                self.builder.get_object('version_num_cur').delete('1.0', END)
                self.builder.get_object('version_num_cur').insert(END, 'current:')

            self.builder.get_object('config_button')['state'] = enable_disable_str
            self.builder.get_object('energizing_pattern')['state'] = enable_disable_str
            self.builder.get_object('timing_profile_on')['state'] = enable_disable_str
            self.builder.get_object('timing_profile_period')['state'] = enable_disable_str
            self.builder.get_object('pace_inter')['state'] = enable_disable_str
            self.builder.get_object('set_filter')['state'] = enable_disable_str
            self.builder.get_object('write_button')['state'] = enable_disable_str
            self.builder.get_object('write_box')['state'] = enable_disable_str
            self.builder.get_object('reset_button')['state'] = enable_disable_str
            self.builder.get_object('view_type')['state'] = enable_disable_str
            self.builder.get_object('show_both_screen')['state'] = enable_disable_str
            self.builder.get_object('received_channel')['state'] = enable_disable_str
            self.builder.get_object('data_type')['state'] = enable_disable_str
            self.builder.get_object('update_button')['state'] = enable_disable_str
            self.builder.get_object('version_path')['state'] = enable_disable_str

            self.builder.get_object('port_box')['state'] = enable_disable_con_str
            self.builder.get_object('baud_rate_box')['state'] = enable_disable_con_str

        elif state == 'config':
            self.builder.get_object('config_sum').delete(1.0, END)
            self.builder.get_object('config_sum').insert(END,
                                                         CONFIG_SUM.format(RC=self.config_param["received_channel"],
                                                                           EP=self.config_param["energy_pattern"],
                                                                           TP_ON=self.config_param["time_profile_on"],
                                                                           TP_P=self.config_param[
                                                                               "time_profile_period"],
                                                                           PI=self.config_param["pacer_val"],
                                                                           F=self.config_param["filter"]))
            self.builder.get_object('config_sum').see(END)

    def print_function(self, str_in):
        self.builder.get_object('recv_box').insert(END, str_in + '\n')
        if self.autoscroll_state:
            self.builder.get_object('recv_box').see(END)
        if self.log_state:
            if self.logger.handlers:
                self.logger.handlers.pop()
            self.logger.info(str_in)


if __name__ == '__main__':
    # Run the UI
    app_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    GWApp = GatewayUI(main_app_folder=app_folder)
