"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import threading
import serial
import datetime
import os
import time
import serial.tools.list_ports
from enum import Enum
from collections import deque
import logging

# parameters:
packet_length = 78


class ConfigParam:
    def __init__(self):
        self.energy_pattern = None
        self.received_channel = None
        self.time_profile_on = None
        self.time_profile_period = None
        self.beacons_backoff = None
        self.pacer_val = None
        self.filter = None
        self.modulation = None


def init_raw_data():
    out = {'raw': '',
           'time': 0.0}
    return out


def init_processed_data():
    out = {'packet': None,
           'is_valid_tag_packet': False,
           'adv_address': None,
           'group_id': None,
           'rssi': None,
           'stat_param': None,
           'time_from_start': None,
           'counter_tag': 0
           }
    return out


class PacketStruct:
    def __init__(self, packet):
        self.packet = packet
        self.adv_address = ''
        self.group_id = ''
        self.rssi = None
        self.stat_param = None

    def fill_packet(self, packet_content):
        self.packet = packet_content
        self.adv_address = packet_content[:12]
        self.group_id = packet_content[20:26]
        self.rssi = packet_content[74:76]
        self.stat_param = packet_content[76:80]

    def tag_packet_content(self, packet):
        if packet.startswith("process_packet"):
            return packet.split('"')[1]
        else:
            return ''

    def is_short_packet(self, packet_content):
        return len(packet_content) < packet_length


class ActionType(Enum):
    ALL_SAMPLE = 'all_samples'
    FIRST_SAMPLES = 'first_samples'
    CURRENT_SAMPLES = 'current_samples'


class DataType(Enum):
    RAW = 'raw'
    PROCESSED = 'processed'


class WiliotGateway(object):
    """
    Wiliot Gateway (GW) API

    * the baud rate is defined to baud value and saved
    * If the port is defined (no None) than automatically try to connect to GW according to the port and baud.
    * If not, Run function FindCOMPorts to find all available ports and saves them
    * If the auto_connect is TRUE, then the function Open is running on each port until a connection is established.

    :type baud: int
    :param baud: the GW baud rate
    :type port: str
    :param port: The GW port if it is already know.
    :type auto_connect: bool
    :param auto_connect: If TRUE, connect automatically to the GW.

    :exception during open serial port process
    """

    def __init__(self, baud=921600, port=None, auto_connect=False, lock_print=None, logger_name=None, verbose=True):
        """
        :type baud: int
        :param baud: the GW baud rate
        :type port: str
        :param port: The GW port if it is already know.
        :type auto_connect: bool
        :param auto_connect: If TRUE, connect automatically to the GW.
        :type lock_print: threading.Lock()
        :param lock_print: used for async printing
        :type logger_name: str
        :param logger_name: the logger name using 'logging' python package add printing information to the log.
                            (the default logger name when using 'logging' is 'root')

        :exception:
        * could not open port 'COMX'... - make sure the baud rate is correct. if port specified, check if correct
        """

        # initialization attributes:
        # -------------------------- #
        # locking variables:
        self._lock_read_serial = threading.Lock()
        if lock_print is None:
            self._lock_print = threading.Lock()
        else:
            self._lock_print = lock_print

        # flag variable:
        self._stop_all = [True, True]
        self._is_running_analysis = False
        self.available_data = False
        self.connected = False
        self.verbose = verbose

        # serial port variables:
        self._comPortObj = None
        self.port = ''
        self.baud = baud

        # GW variables:
        self.config_param = ConfigParam()
        self.sw_version = ''
        self.hw_version = ''

        # data variables:
        self.exceptions_threads = ['', '']
        self._recv_data = deque()
        self._analysis_recv = deque()
        self._processed = deque()
        self._port_listener_thread = None
        self._packet_analyzer_thread = None

        # logging:
        if logger_name is None:
            self._do_log = False
        else:
            self._do_log = True
            self.logger = logging.getLogger(logger_name)

        # connection:
        # -------------- #
        # connect automatically if port is specified
        if port is not None:
            if self.open_port(port, self.baud):
                self._printing_func("connection was established: {}={}".format(self.hw_version, self.sw_version),
                                    'init')
                self.connected = True
                return

        # if port is None - let's search for all available ports
        self.available_ports = [s.device for s in serial.tools.list_ports.comports()]
        if len(self.available_ports) == 0:
            self.available_ports = [s.name for s in serial.tools.list_ports.comports()]
            if len(self.available_ports) == 0:
                self._printing_func("no serial ports were found. please check your connections", "init", True)
                return

        # if user want to connect automatically - connecting to the first available COM with valid gw version
        if auto_connect:
            for p in self.available_ports:
                try:
                    if self.open_port(p, self.baud):
                        self._printing_func("connection was established: {}={}".
                                            format(self.hw_version, self.sw_version), 'init')
                        self.connected = True
                        break
                except Exception as e:
                    self._printing_func("tried to connect {} but failed, moving to the next port".format(p), 'init')

    def open_port(self, port, baud):
        """
        Open a serial connection according to the port and baud
        If the port is open, The GW version is read (All last messages are read since some messages can contains the tag
        packets)
        If the version name is valid (contains 'SW_VER') the GW type (BLE/WIFI/LTI) is saved together with the software
        version. If the version name is invalid, closing the serial port.

        :type  port: str
        :param port: The GW port - mandatory
        :type  baud: int
        :param baud: the GW baud rate - mandatory

        :return: TRUE if GW is connection and FALSE otherwise

        :exception:
        * could not open port 'COMX'... - make sure the baud rate and port are correct
        """
        if self.connected:
            self._printing_func("GW is already connected", 'open_port')
            return self.connected
        # open UART connection
        try:
            self._comPortObj = serial.Serial(port, baud, timeout=0.1)
            time.sleep(0.5)
            if self._comPortObj.isOpen():
                self.connected = True
                self.write("!version")
                time.sleep(0.1)
                # read GW version:
                version_msg = self.read_specific_message(msg='SW_VER', read_timeout=3)
                if version_msg != '':
                    self.sw_version = version_msg.split('=', 1)[1].split(' ', 1)[0]
                    self.hw_version = version_msg.split('=', 1)[0]
                    self.port = port
                    self.connected = True
                    self.update_version(check_only=True)
                    return self.connected
                else:
                    # we read all the last lines and cannot find a valid version name
                    self._printing_func('serial connection was established but gw version could not be read.\n'
                                        'Check your baud rate and port.\nDisconnecting and closing port', 'open_port')
                    self.close_port(True)
                    return self.connected
            else:
                self.connected = False
                return self.connected

        except Exception as e:
            self._printing_func('connection failed', 'open_port')
            raise e

    def write(self, cmd):
        """
        Check if the cmd is not empty, if not the function adds new lines characters ("\r\n")
        Then try to write the command to the  GW serial port

        :type cmd: str or bytes
        :param cmd: the command for the gw, not including "\r\n" - mandatory
        :return:
        """
        # write a single command - basic command
        if self.connected:
            if isinstance(cmd, str):
                cmd = cmd.encode()
            if cmd != b'':
                if len(cmd) >= 2:             # check last characters
                    if cmd[-2:] != b'\r\n':
                        cmd += b'\r\n'
                else:
                    cmd += b'\r\n'
                if cmd[0:1] != b'!':           # check first character
                    cmd = b'!' + cmd

                try:
                    self._comPortObj.write(cmd)
                except Exception as e:
                    self._printing_func("failed to send the command to GW (check your physical connection:\n{}"
                                        .format(e), 'write')
                    raise e
        else:
            self._printing_func("gateway is not connected. please initiate connection and then send a command", 'write')

    def read_specific_message(self, msg, read_timeout=1):
        """
        search for specific message in the input buffer
        :type msg: str
        :param msg: the message or part of the message that needed to be read
        :type read_timeout: int
        :param read_timeout: if until read_timeout in seconds the message was not found exit the function
        :return: if specific message has found, return it. if not return an empty string
        """
        with self._lock_read_serial:
            time_start_msg = datetime.datetime.now()
            dt_check_version = datetime.datetime.now() - time_start_msg
            while dt_check_version.total_seconds() < read_timeout:
                try:
                    data_in = self._comPortObj.readline()
                    if msg in data_in.decode():
                        return data_in.decode()
                except Exception as e:
                    pass
                dt_check_version = datetime.datetime.now() - time_start_msg

            # we read all the last lines and cannot find the specific message till read timeout
            return ''

    def close_port(self, is_reset=False):
        """
        If is_reset is TRUE, running the Reset function.
        Closing GW serial port

        :type is_reset: bool
        :param is_reset: if TRUE, running the Reset function before closing the port
        :return:
        """
        # close UART connection
        if self.connected:
            if is_reset:
                # reset for stop receiving messages from tag.
                try:
                    self.reset_gw()
                except Exception as e:
                    raise e
            try:
                self._comPortObj.close()
                self.connected = self._comPortObj.isOpen()
            except Exception as e:
                self._printing_func('Exception during close_port:{}'.format(e), 'close_port')
        else:
            self._printing_func('The gateway is already disconnected', 'close_port')

    def reset_gw(self, reset_gw=True, reset_port=True):
        """
        Reset the GW serial port
        Flush and reset input buffer

        :type reset_gw: bool
        :param reset_gw: if True sends a reset command
        :type reset_port: bool
        :param reset_port: if True reset the serial port
        :return:
        """
        if self.connected:
            if reset_port:
                try:
                    self._comPortObj.flush()
                    self.reset_buffer()
                except Exception as e:
                    self._printing_func("Exception during reset port: {}\ncheck the gw physical connection to pc"
                                        .format(e), 'reset_gw')
                    raise e
            if reset_gw:
                try:
                    self.write(b'!reset\r\n')
                except Exception as e:
                    raise e
                time.sleep(.1)
        else:
            self._printing_func("gateway is not connected please initiate connection and then try to reset", 'reset_gw')

    def reset_buffer(self):
        """
        Reset input buffer of the GW serial COM and reset software queue (raw data and processed data)
        :return:
        """
        # reset software buffers:
        self._recv_data.clear()
        self._analysis_recv.clear()
        self.available_data = False
        # reset serial input buffer:
        if self.connected:
            # reset input buffer
            try:
                self._comPortObj.reset_input_buffer()
            except Exception as e:
                self._printing_func("Exception during reset_buffer:\n{}".format(e), 'reset_buffer')
                raise

    def stop_processes(self, packet_listener_process=True, packet_analysis_process=True):
        """
        stops all threads - data acquisition and analysis
        :type packet_listener_process: bool
        :param packet_listener_process: stop the data acquisition thread (com_port_listener)
        :type packet_analysis_process: bool
        :param packet_analysis_process: stop the analysis thread (process_packet)
        :return:
        """
        if packet_listener_process:
            self._stop_all[0] = True
        if packet_analysis_process:
            self._stop_all[1] = True

    def config_gw(self, filter_val=None, pacer_val=None, energy_pattern_val=None, time_profile_val=None,
                  beacons_backoff_val=None, received_channel=None, modulation_val=None, max_wait=1,
                  check_validity=False, check_current_config_only=False, start_gw_app=True):
        """
        set all the input configuration

        :type filter_val: bool
        :param filter_val: set packet filter.
        :type pacer_val: int
        :param pacer_val: Set pacer interval
        :type energy_pattern_val: int
        :param energy_pattern_val: set Energizing Pattern
        :type time_profile_val: list
        :param time_profile_val: set Timing Profile where the first element is the ON value and the
                                 2nd element is the period value.
        :type beacons_backoff_val: int
        :param beacons_backoff_val: Set beacons backoff.
        :type received_channel: int
        :param received_channel: the rx channel.
        :type modulation_val: bool
        :param modulation_val: set modulation (on/off)
        :type max_wait: int
        :param max_wait: the time in milliseconds to wait for gw acknowledgement after sending the config command.
        :type check_validity: bool
        :param check_validity: if True, a validity check is done on the configuration parameters
        :type check_current_config_only: bool
        :param check_current_config_only: if True only print the current GW configuration without changing it
        :return: ConfigParam class with all the configuration parameters that were set
        :rtype: ConfigParam
        """

        def check_config_gw_validity():
            """
            Check all input configuration parameters and change them if are not valid.
            :return: T/F if the all config parameters are valid or not
            """

            is_config_valid = True
            # packet filter:
            # no validity tests

            # pacer interval:
            if pacer_val is not None:
                if pacer_val < 0 or pacer_val > 65535:  # max value is 2^16 (2 bytes)
                    self._printing_func("invalid pacer interval. please select a valid value: 0-65535",
                                        'config_gw')
                    is_config_valid = False

            # Energizing Pattern:
            energy_pattern_valid = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                                    24, 25, 26, 27, 28, 50, 51, 52)
            if energy_pattern_val is not None:
                if energy_pattern_val not in energy_pattern_valid:
                    self._printing_func("invalid energizing pattern. please select a valid value: "
                                        "[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,27,28,50,51,52]",
                                        'config_gw')
                    is_config_valid = False

            # Time Profile:
            if time_profile_val is not None:
                if time_profile_val[1] < 6 or time_profile_val[1] > 50:
                    self._printing_func("invalid period time (rx+tx time). please select a valid value: 6-50",
                                        'config_gw')
                    is_config_valid = False
                else:
                    if time_profile_val[0] < 0 or time_profile_val[0] > time_profile_val[1] - 3:
                        self._printing_func("invalid ON time (tx time). please select a valid value: 0 to 3 ms "
                                            "less than period time", 'config_gw')
                        is_config_valid = False

            # beacon backoff:
            valid_bb = (0, 2, 7, 12, 19, 20, 21, 22, 23, 24, 25, 27, 29, 30, 33, 36, 40)
            if beacons_backoff_val is not None:
                if beacons_backoff_val not in valid_bb:
                    self._printing_func("invalid beacons backoff. "
                                        "please select a valid value: "
                                        "[0,2,7,12,19,20,21,22,23,24,25,27,29,30,33,36,40]",
                                        'config_gw')
                    is_config_valid = False

            # Modulation:
            if modulation_val is not None:
                if not modulation_val:
                    self._printing_func("according to bluetooth regulation modulation should be ON. "
                                        "However setting modulation to off is currently valid", 'config_gw')

            # Received Channel:
            valid_received_channel = (37, 38, 39)
            if received_channel is not None:
                if received_channel not in valid_received_channel:
                    self._printing_func("invalid received channel. please select a valid value: [37,38,39]",
                                        'config_gw')
                    is_config_valid = False

            # update parameters
            return is_config_valid

        def quick_wait(wait_time):
            """
            this function replaces the time.sleep(max_wait*0.001) for more accurate wait time
            :type wait_time: float
            :param wait_time: wait time in seconds
            """
            t_i = datetime.datetime.now()
            dt = datetime.datetime.now() - t_i
            while dt.total_seconds() < wait_time:
                dt = datetime.datetime.now() - t_i
            return

        # check current configuration:
        if check_current_config_only:
            self.check_current_config()
            return {}
        # start configuration:

        # check the validity of the config parameters:
        if check_validity:
            if not check_config_gw_validity():
                self._printing_func("configuration failed", 'config_gw')
                return

        # set filter
        if filter_val is not None:
            if filter_val:
                str_f = 'on'
            else:
                str_f = 'off'
            self.write('!set_packet_filter_' + str_f)
            self.config_param.filter = filter_val
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        # set pacer interval
        if pacer_val is not None:
            self.write('!set_pacer_interval {}'.format(pacer_val))
            self.config_param.pacer_val = pacer_val
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        # set Received Channel
        if received_channel is not None:
            self.write('!scan_ch {}'.format(received_channel))
            self.config_param.received_channel = received_channel
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        # set Time Profile
        if time_profile_val is not None:
            self.write('!time_profile {} {}'.format(time_profile_val[1], time_profile_val[0]))
            self.config_param.time_profile_on = time_profile_val[0]
            self.config_param.time_profile_period = time_profile_val[1]
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        # set Beacons Backoff:
        if beacons_backoff_val is not None:
            self.write(bytes('!beacons_backoff {}\r\n'.format(beacons_backoff_val), encoding='utf-8'))
            self.config_param.beacons_backoff = beacons_backoff_val
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        # set modulation
        if modulation_val is not None:
            if modulation_val:
                str_m = 'on'
            else:
                str_m = 'off'
            self.write('!set_modulation_' + str_m)
            self.config_param.modulation = modulation_val
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        # set Energizing Pattern:
        if energy_pattern_val is not None:
            self.write(bytes('!set_energizing_pattern {}\r\n'.format(energy_pattern_val), encoding='utf-8'))
            self.config_param.energy_pattern = energy_pattern_val
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        # starting transmitting + listening:
        if start_gw_app:
            self.write('!gateway_app')
            # wait to prevent buffer overflow:
            quick_wait(max_wait * 0.001)

        self._printing_func("configuration is set", 'config_gw')
        return self.config_param  # return the config parameters

    def check_current_config(self):
        """
        print the current gw configuration
        :return:
        """
        self.write("!print_config")
        # read current configuration:
        data_in = self.read_specific_message(msg='Energizing Pattern', read_timeout=3)
        if data_in != '':
            self._printing_func("current gateway configuration:\n{}".format(data_in), 'config_gw')
            return
        else:
            # we read all the last lines and cannot find a valid message
            self._printing_func("cannot read gateway configuration", 'config_gw')
            return

    def run_packets_listener(self, max_packets=None, max_time=None, tag_packets_only=True, do_process=False):
        """
        Run the com_port_listener function
        If both max_packets and max_time are None, then a non-blocking method is applied by defining a thread.
        *Notice*: if non-blocking method is applied, there might be a delay in receiving packets
                 (the serial buffer might accumulate more elements )
        If max_packets and/or max_time are defined, then a blocking method is applied to run com_port_listener function

        :type max_packets: int
        :param max_packets: The maximum packets to read. If None, read infinite number of packets
        :type max_time: int
        :param max_time: The maximum time to read in seconds. If None, read for infinite time
        :type tag_packets_only: bool
        :param tag_packets_only: If True, save only the tag packets without the GW responses
        :type do_process: bool
        :param do_process: relevant only for the non-blocking method where both max_packets and max_time are None.
                           if True, the process function is automatic initiate
        :return:

        :exception:
        'NoneType' object has no attribute 'hEvent' - check gw connection
        """
        # init:
        new_data = init_raw_data()
        self._recv_data.clear()
        self._analysis_recv.clear()
        self.available_data = False

        def com_port_listener():
            """
            Intended to be initiated by run_packets_listener
            An infinite loop with the following stop-conditions:
            * If the running time of the function has reached the max_time
            * If the number of received packets has reached the max_packets
            If a valid message is available, the message is appended to the inner parameter recv_data_queue depends on
            the tag_packets_only flag. If a valid message has not yet been received for more than 5 seconds the
            input buffer is reset
            """

            def is_stop_conditions():
                if self._stop_all[0]:
                    self._printing_func("Stop comPortListener Thread by the User", 'run_packet_listener', True)
                    self.exceptions_threads[0] = ''
                    return True
                elapsed_time_packet = datetime.datetime.now() - start_time
                if max_time is not None:
                    if elapsed_time_packet.total_seconds() > max_time:
                        self._printing_func("the maximal time has elapsed", 'run_packet_listener')
                        self.exceptions_threads[0] = ''
                        return True
                if max_packets is not None:
                    if n_packets >= max_packets:
                        self._printing_func("{} packets have arrived".format(n_packets), 'run_packet_listener')
                        self.exceptions_threads[0] = ''
                        return True
                # no stop condition was found:
                return False

            def new_packet_received():
                time_from_start = datetime.datetime.now() - start_time
                time_msg = time_from_start.total_seconds()
                # fill raw data list
                new_data['raw'] = msg
                new_data['time'] = time_msg
                self._recv_data.append(new_data.copy())
                # fill analysis list:
                if self._is_running_analysis:
                    self._analysis_recv.append([msg, time_msg])

            # intend to be use as a thread/process (non-blocking) or as a blocking process
            buf = b''
            n_packets = 0
            consecutive_exception_counter = 0
            self._printing_func("comPortListener Start", 'run_packet_listener', True)
            # reset buffer if only tag packets are relevant:
            
            if tag_packets_only:
                self.reset_buffer()
            # init time:
            start_time = datetime.datetime.now()

            while True:
                try:
                    # stop conditions:
                    if is_stop_conditions():
                        return

                    # reading the incoming data:
                    with self._lock_read_serial:
                        data = self._comPortObj.readline()

                    # data handler:
                    if b'\n' in data:
                        # check if buffer is full:
                        if self._comPortObj.in_waiting // packet_length > 10:
                            self._printing_func("more than 10 packets are waiting in the serial port buffer",
                                                'run_packet_listener')
                        # get data and check it:
                        buf += data
                        if isinstance(buf, bytes):
                            msg = buf.decode().strip(' \t\n\r')
                            if (tag_packets_only and msg.startswith("process_packet")) or not tag_packets_only:
                                # a valid packet:
                                new_packet_received()
                                n_packets += 1
                                self.available_data = True
                        buf = b''
                    else:  # if timeout occurs during packet receiving, concatenate the message until '\n'
                        buf += data

                    # complete the loop with no exceptions
                    consecutive_exception_counter = 0

                except Exception as e:
                    # saving the first exception
                    
                    if consecutive_exception_counter == 0:
                        self.exceptions_threads[0] = str(e)
                    self._printing_func("received: {}\ncomPortListener Exception({}/10):\n{}".
                                        format(data, consecutive_exception_counter, e), 'run_packet_listener')
                    consecutive_exception_counter = consecutive_exception_counter + 1
                    buf = b''
                    if consecutive_exception_counter > 10:
                        self._printing_func("more than 10 Exceptions, stop comPortListener thread",
                                            'run_packet_listener')
                        if self._comPortObj.isOpen():
                            self._comPortObj.close()
                        else:
                            self._printing_func("gateway is not connected. please initiate connection and try to "
                                                "read data again", 'run_packet_listener')
                        return
                    else:  # less than 10 successive exceptions
                        if self._comPortObj.isOpen():
                            pass
                        else:
                            self._printing_func("gateway is not connected. please initiate connection and try to "
                                                "read data again", 'run_packet_listener')
                            return

        # start listening:
        self._stop_all[0] = False

        if max_packets is None and max_time is None:
            # non-blocking
            if self._port_listener_thread is not None:
                if self._port_listener_thread.is_alive():
                    self.stop_processes(packet_listener_process=True, packet_analysis_process=False)
                    self._port_listener_thread.join()
                    self._stop_all[0] = False

            self._port_listener_thread = threading.Thread(target=com_port_listener, args=())
            self._port_listener_thread.start()
            if do_process:  # check if the process function should run as well:
                self.run_process_packet()
            return

        else:
            # blocking
            com_port_listener()
            self._stop_all[0] = True  # stop listening
            data_out = self.get_data(action_type=ActionType.ALL_SAMPLE, data_type=DataType.RAW)
            # check if the process function should run as well:
            if do_process:
                data_out = self.run_process_packet(raw_data=data_out)
            return data_out

    def run_process_packet(self, raw_data=None, process_only_current=False):
        """
        Run the process_packet function
        If both raw_data is None, then a non-blocking method is applied by defining a thread.
        *Notice*: if non-blocking method is applied, there might be a delay in receiving packets
                 (the serial buffer might accumulate more elements ) and hence processing them
        If packets and/or max_time are defined, then a blocking method is applied to run process_packet function

        :type raw_data: list or dict
        :param raw_data: a list of dictionary with two keys: raw packets that needs to be processed and
                                                             packets timestamps that are needed for the packets process
        :type process_only_current: bool
        :param process_only_current: if True, only the last element in the raw packets list is analyzed.
               relevant for live processing (non-blocking method)
        :return:
        """
        # init output:
        new_proc = init_processed_data()
        self._processed.clear()

        def process_packet():
            """
            Intended to be initiated by run_process_packet
            An infinite loop with the following stop-conditions: if stop_all flag is True
            If a packet is available in the analysis queue (list), the following outputs are processed:
                * packet: [str]the packet content without the additional strings
                * is_valid_tag_packet: [bool] if current packet is a tag's packet
                * adv_address: [str]the advertising address (unique number of each tag, before brown out)
                * group_id: [str] the group id of each tag. relevant for the decryption key
                * rssi: [int] Received signal strength indication - the lower the number the stronger the signal
                * stat_param: [int] number of filtered packets or packet time according to gw clock [ms]
                              if gw is in tester mode.
                * time_from_start: [float] the elapsed time (seconds) from the start running time until packet arrived
                * counter_tag: [int] the number of occurrences of the same advertising address

            """

            def is_stop_conditions():
                if self._stop_all[1]:
                    self._printing_func("Stop ProcessPacket Thread by the User", 'run_process_packet', True)
                    self.exceptions_threads[1] = ''
                    return True
                if raw_data is not None:
                    if ind_pro >= len(raw_data):
                        self._printing_func("complete packet analysis", 'run_process_packet', True)
                        self.exceptions_threads[1] = ''
                        return True
                return False

            consecutive_exception_counter = 0
            ind_pro = 0
            tag_list = {"adv_address": [], "counter_tag": []}
            self._printing_func("ProcessPacket Start", 'run_process_packet', True)

            while True:
                try:
                    # stop conditions:
                    if is_stop_conditions():
                        return

                    # reading data:
                    packet = []
                    packet_time = []

                    if self._is_running_analysis:  # online analysis
                        time.sleep(0)  # important for the processor performance when a thread
                        if self._analysis_recv:
                            if process_only_current:
                                tmp = self._analysis_recv.pop()
                            else:
                                tmp = self._analysis_recv.popleft()
                            packet = tmp[0]
                            packet_time = tmp[1]
                        else:
                            # need to wait for a new data
                            pass
                    else:
                        # analysis offline
                        packet = raw_data[ind_pro]['raw']
                        packet_time = raw_data[ind_pro]['time']
                        ind_pro += 1

                    # start processing:
                    if packet and packet_time:
                        # arrange the received packet:
                        new_packet = PacketStruct(packet)
                        packet_content = new_packet.tag_packet_content(packet)
                        if packet_content and not new_packet.is_short_packet(packet_content):
                            new_packet.fill_packet(packet_content)
                            new_proc['is_valid_tag_packet'] = True
                        else:
                            # invalid tag packet (short) or not a tag packet:
                            new_proc['is_valid_tag_packet'] = False

                        # process:
                        # check if the tag has already sent a packet:
                        if not new_packet.adv_address:
                            new_proc['counter_tag'] = None
                            new_proc['time_from_start'] = None
                        else:  # a valid tag packet:
                            tag_index_list = None
                            if new_packet.adv_address in tag_list["adv_address"]:
                                tag_list["adv_address"].reverse()  # find the last index
                                tag_index_list = tag_list["adv_address"].index(new_packet.adv_address)
                                tag_list["adv_address"].reverse()  # reverse back

                            # counter per tag:
                            if tag_index_list is None:
                                # a new tag is detected
                                new_proc['counter_tag'] = 1
                                tag_list["counter_tag"].append(1)
                            else:
                                # an additional appearance of the tag
                                tag_index_list = len(tag_list["adv_address"]) - 1 - tag_index_list  # reverse tag index
                                new_proc['counter_tag'] = tag_list["counter_tag"][tag_index_list] + 1
                                tag_list["counter_tag"].append(tag_list["counter_tag"][tag_index_list] + 1)
                            # update tag_list advertising address:
                            tag_list["adv_address"].append(new_packet.adv_address)

                            # update time:
                            new_proc['time_from_start'] = packet_time

                        # append data:
                        for key, value in new_packet.__dict__.items():
                            if key == 'rssi' or key == 'stat_param':
                                if value is None:
                                    new_proc[key] = value
                                else:
                                    new_proc[key] = int(value, base=16)
                            else:
                                new_proc[key] = value

                        self._processed.append(new_proc.copy())

                        consecutive_exception_counter = 0

                except Exception as e:
                    if consecutive_exception_counter == 0:
                        self.exceptions_threads[1] = str(e)
                    self._printing_func("ProcessPacket Exception({}/10):\n{}".
                                        format(consecutive_exception_counter, e), 'run_process_packet')
                    consecutive_exception_counter = consecutive_exception_counter + 1
                    if consecutive_exception_counter > 10:
                        self._printing_func("more than 10 exceptions, Stop ProcessPacket thread", 'run_process_packet')
                        return

        # start processing:
        self._stop_all[1] = False

        if raw_data is None:
            # non-blocking
            if self._packet_analyzer_thread is not None:
                if self._packet_analyzer_thread.is_alive():
                    self.stop_processes(packet_listener_process=False, packet_analysis_process=True)
                    self._packet_analyzer_thread.join()
                    self._stop_all[1] = False

            self._is_running_analysis = True
            self._packet_analyzer_thread = threading.Thread(target=process_packet, args=())
            self._packet_analyzer_thread.start()
            return
        else:
            # blocking
            process_packet()
            self._stop_all[1] = True  # stop processing
            data_out = self.get_data(action_type=ActionType.ALL_SAMPLE, data_type=DataType.PROCESSED)
            return data_out

    def get_data(self, action_type=ActionType.FIRST_SAMPLES, num_of_packets=1, data_type=DataType.RAW):
        """
        Extract packets from the received packets in recv_data or from the processed packets in processed (based on
        data_type) according to the following methods:
                all_samples: return all available packets.
                first_samples: return all the X first packets (the oldest packets ) according to num_of_packages
                current_samples: return all the X last packets (the newest packets ) according to num_of_packages
        If num_of_packets is larger than the available packets, an error is printed and an empty list is returned

        :type action_type: ActionType
        :param action_type: {'all_samples','first_samples','current_samples'}.
                            the method of data extraction (see description).
        :type num_of_packets: int
        :param num_of_packets: number of packets to extract
        :type data_type: DataType
        :param data_type: {'raw','processed'}.
                          the data type to extract (see description)
        :return: a list of dictionaries or on only dictionary (if only one packet has had received)
                 with all the extracted raw or processed data.
                 Dictionary keys of RAW: 'raw','time'
                 Dictionary keys of PROCESSED: 'packet','is_valid_tag_packet','adv_address','group_id','rssi',
                                               'stat_param','time_from_start','counter_tag'


        """
        # check if threads 'raised' exceptions:
        if self._port_listener_thread is not None:
            if not self._port_listener_thread.is_alive() and self.exceptions_threads[0] != '':
                raise Exception("packet listener thread stopped due to the following exception:\n{}"
                                .format(self.exceptions_threads[0]))
        if self._packet_analyzer_thread is not None:
            if not self._packet_analyzer_thread.is_alive() and self.exceptions_threads[1] != '':
                raise Exception("packet analyzer thread stopped due to the following exception:\n{}"
                                .format(self.exceptions_threads[1]))
        if data_type.value == 'raw':
            data_in = self._recv_data
        elif data_type.value == 'processed':
            data_in = self._processed
        else:
            self._printing_func("data_type can be only one of the following strings: 'raw', 'processed'", 'get_data')
            return {}

        data_out = []
        # check if the received packets list is empty:
        if not len(data_in):
            self._printing_func("there are no new packets to read", 'get_data', True)
            self.available_data = False
            return data_out
        # check if the user asked for more elements than what there is:
        if num_of_packets > len(data_in):
            self._printing_func("there are not enough packets to extract", 'get_data')
            return data_out

        # extract messages:
        if action_type.value == 'all_samples':
            n_output_packets = len(data_in)
            is_left_dir = True
        elif action_type.value == 'first_samples':
            n_output_packets = num_of_packets
            is_left_dir = True
        elif action_type.value == 'current_samples':
            n_output_packets = num_of_packets
            is_left_dir = False
        else:
            self._printing_func("action_type can be only one of the following strings: "
                                "'all_samples', 'first_samples', 'current_samples'", 'get_data')
            return

        for n in range(n_output_packets):
            if is_left_dir:
                data_out.append(data_in.popleft())
            else:
                data_out.append(data_in.pop())

        # if len(data_out) == 1:
        #     data_out = data_out[0]

        if not len(data_in):
            self.available_data = False

        return data_out

    def update_version(self, version="Latest", versions_path="", check_only=False):
        """
        first check if the required version has a matched zip file under the gw versions folder.
        Then, compare the gw version with the required version. if the versions are different,
        then it checks if the required version has a matched zip file under the gw versions folder.
        if the file exists, a version update is done by send the gw to bootloader mode and burn the version u
        sing nRF utils

        :type versions_path: str
        :param versions_path: the path of the gateway version zip file. If defined, the update is run regardless to the
                              current gw version
        :type version: str
        :param version: the version string in the following format 'x.x.x'.
                        if version is 'Latest' than the latest version is selected
        :type check_only: bool
        :param check_only: if True the function only checks the version but does not update it
        :return: True if GW version is up to date, False if GW version is old and None if a problem occur
        """
        required_version = ''
        if versions_path == "":
            # check available versions:
            try:
                required_version, new_version_path = self.get_latest_version_number(version=version,
                                                                                    versions_path=versions_path)
            except Exception as e:
                raise e
            if not required_version:
                return

            # check if the GW is already with the right version:
            if self.sw_version == required_version:
                self._printing_func("Your Gateway is already updated", 'update_version')
                return True
        else:
            new_version_path = '"{}"'.format(versions_path)  # to avoid failure when path contains spaces

        # The GW need to be updated
        if check_only:
            self._printing_func("Your Gateway needs to be updated", 'update_version')
            return False
        # a version need to be updated:

        # change the GW to bootloader state
        if self.connected:
            self.write('!move_to_bootloader')
            time.sleep(0.1)
            self.close_port()

            # run the nRF Util to burn the version:
            time.sleep(.1)
            p = os.popen(
                'nrfutil dfu serial  --package {} -p {} -fc 0 -b 115200 -t 10'.format(new_version_path, self.port))
            # wait until burn was completed
            self._printing_func("please wait for approx. 30 seconds...", 'update_version')
            self._printing_func(p.read(), 'update_version')

            self._printing_func("Rebooting and opening serial port again...", 'update_version')
            time.sleep(5)
            # open GW again
            self.open_port(self.port, baud=self.baud)
            if versions_path == "":
                if self.sw_version == required_version:
                    self._printing_func("Your Gateway is updated", 'update_version')
                    return True
                else:
                    self._printing_func("update failed. please try again", 'update_version')
                    return False
        else:
            self._printing_func("Gateway is not connected. please initiate connection before update versions",
                                'update_version')
            return False

    def exit_gw_api(self):
        """
        check that all threads are terminated and serial com is closed
        :return:
        """
        if self._port_listener_thread is not None:
            if self._port_listener_thread.is_alive():
                self.stop_processes()
                time.sleep(0.2)
                if self._port_listener_thread.is_alive():
                    self._printing_func("run_packets_listener thread is still running", 'exit_gw_api')

        if self._packet_analyzer_thread is not None:
            if self._packet_analyzer_thread:
                self.stop_processes()
                time.sleep(0.2)
                if self._packet_analyzer_thread.is_alive():
                    self._printing_func("run_process_packet thread is still running", 'exit_gw_api')

        if self._comPortObj is not None:
            if self._comPortObj.isOpen():
                self.close_port()
                if self._comPortObj.isOpen():
                    self._printing_func("encounter a problem to close serial port", 'exit_gw_api')

    def _printing_func(self, str_to_print, func_name, is_info=False):
        if self.verbose or not is_info:
            with self._lock_print:
                print(str_to_print)
                if self._do_log:
                    if self.logger.handlers:
                        self.logger.handlers.pop()
                    self.logger.info('GW API: {}: {}'.format(func_name, str_to_print))

    def get_connection_status(self):
        """
        :return: if gateway is connected, return True, the serial port and baud rate used for the connection.
                 if not, return False, and None for port and baud
        """
        if self.connected:
            return self.connected, self.port, self.baud
        else:
            return self.connected, None, None

    def get_gw_version(self):
        """
        :return: the gateway software version, the gw hardware type
        """
        return self.sw_version, self.hw_version

    def get_latest_version_number(self, version="Latest", versions_path=""):
        """
        return the latest version in the gw_version folder or in versions_path if specified

        :type version: str
        :param version: the version string in the following format 'x.x.x'.
                        if version is 'Latest' than the latest version is selected
        :type versions_path: str
        :param versions_path: the folder path of the gateway versions zip files
        :return: the latest available version number to be installed and its path
        """
        # check available versions:
        if versions_path == "":
            versions_path = os.path.join(os.path.dirname(__file__), 'gateway_versions')

        try:
            versions_files = [f for f in os.listdir(versions_path) if f.endswith(".zip")]
        except Exception as e:
            self._printing_func("while running update_version function:\n{}\n"
                                "check if the version_path is correct".format(e), 'update_version')
            raise e

        versions_num = []
        first_exception = None
        for version_file in versions_files:
            try:
                version_num = version_file.split('.')[0:3]
                if not version_num[-1].isnumeric():
                    version_num[-1] = version_num[-1][0:-1]  # assuming it's a patch version 1.2.3a
                versions_num.append(int(''.join(version_num)))
            except Exception as e:

                self._printing_func("version zip file name should be as follow 'x.x.x'. Hence {} is not considered "
                                    "as a valid version file".format(version_file), 'update_version')
                first_exception = e
        if not versions_num:
            if first_exception:
                # no valid versions files
                self._printing_func("no valid version files have found - version update failed", 'update_version')
                raise first_exception
            else:
                # empty folder:
                self._printing_func("versions folder is empty - version update failed", 'update_version')
                return None, None

        # select the relevant version to load
        if version == "Latest":
            version_ind = versions_num.index(max(versions_num))
        else:
            if version + ".zip" in versions_files:
                version_ind = versions_files.index(version + ".zip")
            else:
                self._printing_func("no version file matches {} version".format(version), 'update_version')
                return None, None

        # check if the GW is already with the right version:
        required_version = versions_files[version_ind].split(".zip")[0]
        new_version_path = file_name = os.path.join(versions_path, versions_files[version_ind])
        return required_version, new_version_path

    def is_data_available(self):
        """
        :return: True if data is available tp get, False otherwise
        """
        return self.available_data
    # def register_gw(self):
    #     pass
    #
    # def decrypt_packet(self):
    #     pass
    #
    # def get_key_by_group_id(self):
    #     pass
