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
import copy
from enum import Enum

from yoctopuce.yocto_temperature import *
import http.client
import mimetypes
from codecs import encode
import threading
import logging
import traceback
import json
import serial.tools.list_ports
import time
import pandas as pd
import os
from csv import writer, DictWriter
import ast
from threading import Event
import numpy as np
import statistics
from queue import Queue
from os.path import dirname
import sys
from os.path import exists, isfile, abspath, dirname, join
from wiliot.packet_data_tools.process_encrypted_packets import *
import PySimpleGUI as SimGUI
import socket

###########################################
#            Tester Management            #
###########################################


class TesterName(Enum):
    """
    determines tester type (affects output file format set in class CsvLog)
    """
    OFFLINE = 'offline'
    TAL15K = 'tal15k'
    CONVERSION = 'conversion'
    SAMPLE = 'sample'
    NONE = ''


class HeaderType(Enum):
    """
    determines which output file is generated in class CsvLog (run data or tags data)
    """
    TAG = 'tag'
    RUN = 'run'
    PACKETS = 'packets'
    NONE = ''


def get_ports(device_name):
    """
    search the com ports for the desired device (arduino/ gw)
    :type device_name: string
    :param device_name: arduino or gw (gateway)
    :return: ports list of the desired devices
    """
    if device_name == 'gw' or device_name == 'gateway':
        str_device = 'Wiliot GW'
        baud = 921600
    elif device_name == 'arduino':
        str_device = 'Wiliot Tester GPIO unit'
        baud = 1000000
    else:
        print("please selecet a valid device names: {'gw','arduino'}")
        return []
    ports = list(serial.tools.list_ports.comports())
    device_ports = []
    for p in ports:
        try:
            s = serial.Serial(port=p.device, baudrate=baud, timeout=1)
            if s.isOpen():
                s.write(b'*IDN?')
                current_device = s.readline()
                if str_device in current_device.decode():
                    device_ports.append(p.device)
                    print(current_device.decode())
                s.close()
        except (OSError, serial.SerialException):
            pass
        except Exception as e:
            raise(e)
    return device_ports


def set_temperature():
    """
    initialize yocto temperature sensor
    :return: current temperature
    """
    # object tenp sens
    errmsg = YRefParam()
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        sys.exit("init error :" + errmsg.value)
    cur_temp = YTemperature.FirstTemperature()
    print("Temp :  " + "%2.3f" % cur_temp.get_currentValue() + "°C (Ctrl-C to stop)")
    return cur_temp


def print_exception(exception_details, printing_lock=None):
    """
    prints an exception to screen and to log
    :type exception_details: type(sys.exc_info())
    :param exception_details: desired printed exception
    :type printing_lock: threading.Lock()
    :param printing_lock: lock for printing
    """
    # print except - print_lock if None nothing else with
    exc_type, exc_obj, exc_trace = exception_details
    # deal with the exception
    if printing_lock is not None:
        with printing_lock:
            print('Exception details: ')
            print(exc_type)
            print(exc_obj)
            traceback.print_tb(exc_trace, limit=None, file=None)
    else:
        print('Exception details: ')
        print(exc_type)
        print(exc_obj)
        traceback.print_tb(exc_trace, limit=None, file=None)
    try:
        logging.warning('Exception details: exc_type = {}, exc_obj = {}'.format(exc_type, exc_obj))
    except Exception:
        pass


def config_gw(gw_obj, rssi_threshold=None, energizing_pattern=None, tx_power=None, time_profile=None, pl_delay=None,
              filter_val=None, pacer_val=None, received_channel=None, modulation_val=None,
              set_interrupt=None):
    """
    :type gw_obj: WiliotGateway
    :type rssi_threshold: int or str
    :type energizing_pattern: int or str
    :type tx_power:  int or str
    :type time_profile:  list or str
    :type pl_delay: int or str
    :type set_interrupt: bool

    :param gw_obj:
    :param rssi_threshold:
    :param energizing_pattern:
    :param tx_power:
    :param time_profile:
    :param pl_delay:
    :param set_interrupt:
    :return:
    """
    # print version
    # print('{}={}'.format(gw_obj.hw_version, gw_obj.sw_version))
    # config:
    if energizing_pattern is not None:
        int_energizing_pattern = int(energizing_pattern)
    else:
        int_energizing_pattern = None
    if time_profile is not None:
        if isinstance(time_profile, str):
            time_profile = [int(time_profile.split(',')[0]), int(time_profile.split(',')[1])]
        else:
            print("time_profile can be a string 'x,x' or list of int [5,15]")
    gw_obj.config_gw(filter_val=filter_val, pacer_val=pacer_val, energy_pattern_val=int_energizing_pattern,
                     time_profile_val=time_profile, received_channel=received_channel, modulation_val=modulation_val)
    if set_interrupt is not None:
        gw_obj.write('!pl_gw_config {}'.format(int(set_interrupt)))
        time.sleep(0.002)
    if rssi_threshold is not None:
        gw_obj.write('!set_rssi_th {}'.format(hex(int(rssi_threshold))))
        time.sleep(0.002)
        gw_obj.write('!send_rssi_config 1')
        time.sleep(0.002)
    if tx_power is not None:
        gw_obj.write('!output_power pos{}dBm'.format(tx_power))
        time.sleep(0.002)
    if pl_delay is not None:
        gw_obj.write('!set_pl_delay {}'.format(pl_delay))


def encrypted_packet_decoder(processed_data):
    """
    extracts only the data relevant to the tester
    :type processed_data: dictionary (output of WiliotGateway.get_data())
    :return dictionary of relevant fields
    """
    packet_dict = {'advAddress': processed_data['adv_address'],
                   'packet_time': processed_data['time_from_start'],
                   'raw_data': processed_data['packet'],
                   'rssi': processed_data['rssi']}

    return packet_dict


def open_json(folder_path, file_path, default_values=None):
    """
    opens config json
    :type folder_path: string
    :param folder_path: the folder path which contains the desired file
    :type file_path: string
    :param file_path: the file path which contains the json
            (including the folder [file_path = folder_path+"json_file.json"])
    :type default_values: dictionary
    :param default_values: default values for the case of empty json
    :return: the desired json object
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_exists = os.path.isfile(file_path)
    if not file_exists or os.stat(file_path).st_size == 0:
        # save the default values to json
        with open(file_path, "w") as out_file:
            json.dump(default_values, out_file)

        return json.load(open(file_path, "rb"))
    else:
        with open(file_path) as f:
            json_content = f.read()
        if len(json_content) == 0:
            with open(file_path, "w") as out_file:
                json.dump(default_values, out_file)
            json_content = json.load(open(file_path, "rb"))
        else:
            json_content = json.loads(json_content)
        return json_content


def printing_func(str_to_print, logging_entity, lock_print=None, do_log=True, logger_type='info'):
    """
    print and log
    :type str_to_print: string
    :param str_to_print: string to print
    :type logging_entity: string
    :param logging_entity: what thread is asking to log
    :type lock_print: threading.Lock
    :param lock_print: lock to prevent cutting printing in the middle
    :type do_log: bool
    :param do_log: if True log the data, do not log otherwise
    :type logger_type: string (info, debug, warning)
    :param logger_type: how to log the str_to_print
    """

    msg = str(logging_entity) + ':\t' + str(str_to_print)
    if lock_print is not None:
        with lock_print:
            print(msg)
    else:
        print(msg)
    if do_log:
        if logger_type == 'info':
            logging.info(msg)
        elif logger_type == 'debug':
            logging.debug(msg)
        elif logger_type == 'warning':
            logging.warning(msg)

###########################################
#              Tester Classes             #
###########################################


class CounterThread(threading.Thread):
    """
    a class that manages and interacts with arduino_counter code

    Parameters:
        @type stop: Event
        @param stop: when set, close the port and exit
        @type printing_lock: threading.Lock
        @param printing_lock: a lock to access screen printing
        @type arduino_ports: list
        @param arduino_ports: list of arduino ports connected to PC

        global param tested: will use a global variable called tested

    Exceptions: None

    Events:
        listen/ waits on:
            stop => when set, close the port and exit

    Logging:
        debug: 'Warning: Could not decode counter data'
    """

    def __init__(self, stop: Event, printing_lock, arduino_ports):
        super(CounterThread, self).__init__()
        self.stop = stop
        self.printing_lock = printing_lock
        self.port = arduino_ports
        if len(self.port) > 1:
            print("too many USB Serial Device connected, can't figure out which is the counter")
        elif len(self.port) < 1:
            print("No USB Serial Device connected, please connect the counter")
        else:  # there is only one port of usb that is not GW
            self.port = self.port[0]
        self.baud = '9600'
        self.comPortObj = serial.Serial(self.port, self.baud, timeout=0.1)

    def run(self):
        global tested
        while not self.stop.isSet():
            data = self.comPortObj.readline()
            buf = b''
            if data.__len__() > 0:
                buf += data
                if b'\n' in buf:
                    try:
                        tmp = buf.decode().strip(' \t\n\r')
                        if "pulses detected" in tmp:
                            tested += 1

                    except Exception:
                        with self.printing_lock:
                            print('Warning: Could not decode counter data')
                        logging.debug('Warning: Could not decode counter data')
                        continue

        self.comPortObj.close()


class TagsHandling:
    """
    controls the tags adv_address seen in the run, filtering bad packets, duplications etc.
    """

    def __init__(self, tags_list_len, lock_print=None, rssi_threshold=None, logging_thread=None,
                 only_add_tags_after_location_ends=False, add_to_black_list_after_locations=2):
        """
        :type tags_list_len: int
        :param tags_list_len: how long back to look for duplications
        :type lock_print: threading.lock
        :param lock_print: printing lock
        :type rssi_threshold: int
        :param rssi_threshold: max rssi value allowed for a packet
        :type logging_thread: string
        :param logging_thread: name of thread that will log the data
        :type only_add_tags_after_location_ends: bool
        :param only_add_tags_after_location_ends: if True will add the adv_addresses to
                                                  self.adv_addresses_in_current_location when calling to
                                                  self.set_new_location()
        :type add_to_black_list_after_locations: int (minimum is 2)
        :param add_to_black_list_after_locations: amount of locations a tag should appear in until
                                                  it will be added to black list
        """
        self.lock_print = lock_print
        self.rssi_threshold = int(rssi_threshold)
        self.only_add_tags_after_location_ends = only_add_tags_after_location_ends
        self.tags_list = []
        self.tags_list_len = tags_list_len
        self.cur_tag_adv_addr = None
        self.cur_tag_location = -1  # to make the first location be 0 (when calling set_new_location())
        self.cur_tag_min_rssi = np.inf  # big value, any real value will be much smaller
        self.group_id_hist = {}  # histogram of the group_id in this run
        self.black_list = []  # tags to ignore during the run
        self.black_list_candidates_hist = {}  # holds tags that will be added to black list if will reach to threshold
        self.add_to_black_list_after_locations = add_to_black_list_after_locations
        self.packets_in_current_location = []  # list of dictionaries (raw_data) of packets in this location
        self.adv_addresses_in_current_location = []  # list of adv_address from this location
        self.logging_thread = logging_thread
        self.problem_in_locations_hist = {'tag from black list': 0, 'bad group id': 0, 'above rssi threshold': 0,
                                          'packet from bridge': 0, 'duplication': 0, 'no singularization': 0}
        self.prev_location_problem_in_locations_hist = copy.copy(self.problem_in_locations_hist)

    def encrypted_packet_filter(self, raw_data):
        """
        checks if the packet is good in terms of RSSI, tag UID
        :type raw_data: dictionary (return value from gw_api.packet_listener (PROCESSED))
        :param raw_data: raw data of the tags
        :return: is_good_packet - is the packet relevant for this run,
                 need_to_check_TBP - you should open wide window for catching more packets (using get_rates())
                                     due to Duplication/ non singularity issue (TBP =  time between packets)
                 reason_to_fail - string with reason for failing the packet (for logging in debug mode)
        """
        try:
            time.sleep(0)
            # check if the tag is in the black list
            if raw_data['adv_address'] in self.black_list:
                msg = str(raw_data['packet']) + " - tag that is in the black list (will be ignored)"
                printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                reason_to_fail = 'blackList'
                self.add_hist_val('tag from black list')
                return False, False, reason_to_fail

            else:
                self.packets_in_current_location.append(raw_data)

                # check if it is a bridge packet
                if self.is_packet_from_bridge(raw_data):
                    self.add_tag_to_black_list(raw_data['adv_address'])
                    msg = str(raw_data['packet']) + " - packet generated by Wiliot bridge found, " \
                                                    "will add it to the black list"
                    printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                    reason_to_fail = 'bridge'
                    self.add_hist_val('packet from bridge')
                    return False, False, reason_to_fail

                # check if the tag group_id is the same as the rest of the tags
                bad_group_id = False
                if raw_data['group_id'] is not None:
                    if raw_data['group_id'] not in self.group_id_hist.keys():
                        if len(self.group_id_hist) > 0:
                            max_group_id = max(self.group_id_hist.values())
                            for i, (group, group_val) in enumerate(self.group_id_hist.items()):
                                if group_val == max_group_id and not raw_data['group_id'] == group:
                                    bad_group_id = True
                        self.group_id_hist[raw_data['group_id']] = 1
                    else:
                        if len(self.group_id_hist) > 0:
                            max_group_id = max(self.group_id_hist.values())
                            for i, (group, group_val) in enumerate(self.group_id_hist.items()):
                                if group_val == max_group_id and not raw_data['group_id'] == group:
                                    bad_group_id = True
                        self.group_id_hist[raw_data['group_id']] += 1
                    if bad_group_id:
                        msg = str(raw_data['packet']) + " - packet with wrong group_id found (group_id = " + \
                              str(raw_data['group_id']) + ', group_id seen so far (from all packets) = ' + \
                              str(self.group_id_hist) + ')'
                        printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                        reason_to_fail = 'group_id'
                        self.add_hist_val('bad group id')
                        return False, False, reason_to_fail

                # check if the RSSI is good
                if self.rssi_threshold is not None:
                    if int(raw_data['rssi']) > self.rssi_threshold:
                        msg = str(raw_data['packet']) + " - Packet rssi is too high"
                        printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                        reason_to_fail = 'rssi'
                        self.add_hist_val('above rssi threshold')
                        return False, False, reason_to_fail

                is_new_tag = self.add_new_tag_to_tags_list(raw_data)

                # check if the tag was already caught in the GW
                if not is_new_tag:
                    msg = str(raw_data['packet']) + " - Duplication from a tag we have seen before (advAddress = " \
                          + raw_data['adv_address'] + ")"
                    printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                    reason_to_fail = 'duplication'
                    self.add_hist_val('duplication')
                    return True, True, reason_to_fail

                # check if this packet is from new tag
                if is_new_tag and self.cur_tag_adv_addr != raw_data['adv_address'] and \
                        self.cur_tag_adv_addr is not None:
                    msg = str(raw_data['packet']) + " - no singularity issue (did not see this tag before), " \
                          "new tag advAddress = " + str(raw_data['adv_address']) \
                          + ", new tag rssi = " + str(raw_data['rssi']) \
                          + ', current tag rssi = ' + str(self.cur_tag_min_rssi)
                    printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                    reason_to_fail = 'no singularity'
                    self.add_hist_val('no singularization')
                    return True, True, reason_to_fail

                self.cur_tag_adv_addr = raw_data['adv_address']
                if self.cur_tag_min_rssi > int(raw_data['rssi']):
                    self.cur_tag_min_rssi = int(raw_data['rssi'])

                reason_to_fail = 'good'
                return True, False, reason_to_fail

        except Exception as e:
            printing_func('Exception during encrypted_packet_filter: ' + str(e), self.logging_thread,
                          self.lock_print, logger_type='debug')
            return False, False, 'exception'

    def is_packet_from_bridge(self, raw_data):
        """
        check if the packet generated by Wiliot bridge
        :type raw_data: dictionary (return value from gw_api.packet_listener)
        :param raw_data: raw data of the tags
        :return: True if the tag is bridge packet, False otherwise
        """
        chars_starts_with10_bits = ['8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        if str(raw_data['packet'])[0].upper() in chars_starts_with10_bits and 'AFFD' in str(raw_data['packet']):
            return True

    def add_new_tag_to_tags_list(self, raw_data):
        """
        adds a new tag's adv_address to the list of the tags we have seen before
        :type raw_data: dictionary (return value from gw_api.packet_listener)
        :param raw_data: raw data of the tags
        :return: True if the tag is a new tag, False otherwise
        """
        if self.only_add_tags_after_location_ends:
            if raw_data['adv_address'] not in self.adv_addresses_in_current_location:
                self.adv_addresses_in_current_location.append(raw_data['adv_address'])
            if raw_data['adv_address'] not in self.tags_list:
                return True
            else:
                return False

        elif raw_data['adv_address'] not in self.tags_list:
            if len(self.tags_list) <= self.tags_list_len:
                self.tags_list.append(str(raw_data['adv_address']))
            else:
                del self.tags_list[0]
                self.tags_list.append(str(raw_data['adv_address']))
            return True
        else:
            return False

    def add_tag_to_black_list(self, adv_address):
        """
        adds a tag's adv_address to the black list (tags to ignore during the run)
        :type adv_address: string
        :param adv_address: adv_address of the tag to add to black list
        :return: True if the tag is a new tag, False otherwise
        """
        if adv_address not in self.black_list:
            self.black_list.append(adv_address)
            return True
        else:
            return False

    def add_hist_val(self, key):
        """
        :type key: string
        :param key: one of the keys in self.problem_in_locations_hist
        """
        if key not in self.prev_location_problem_in_locations_hist.keys() or \
                key not in self.problem_in_locations_hist.keys():
            return

        if self.prev_location_problem_in_locations_hist[key] == self.problem_in_locations_hist[key]:
            self.problem_in_locations_hist[key] += 1

    def set_new_location(self):
        """
        reset all packet rates from previous tags, will start rates comparison with tags received from now
        until this function will be called again
        """
        for adv_address in self.adv_addresses_in_current_location:
            if adv_address not in self.tags_list:
                if self.only_add_tags_after_location_ends:
                    if len(self.tags_list) <= self.tags_list_len:
                        self.tags_list.append(str(adv_address))
                    else:
                        del self.tags_list[0]
                        self.tags_list.append(str(adv_address))
            else:
                if adv_address not in self.black_list_candidates_hist.keys():
                    self.black_list_candidates_hist[adv_address] = 2  # already appeared in previous location
                else:
                    self.black_list_candidates_hist[adv_address] += 1
                if self.black_list_candidates_hist[adv_address] >= self.add_to_black_list_after_locations:
                    self.add_tag_to_black_list(adv_address)

        self.adv_addresses_in_current_location = []
        self.packets_in_current_location = []
        self.cur_tag_location += 1
        self.cur_tag_adv_addr = None
        self.prev_location_problem_in_locations_hist = copy.copy(self.problem_in_locations_hist)

    def get_rates(self):
        """
        calculates the rate of packets from the same sprinkler
        :return: min_times_found - list of dictionaries ({'adv_address': XXXX,
                                                          'min_time_between_packet_in_sprinkler': YYYY,
                                                          'avg_rssi': ZZZZ})
                 of adv_address that was calculated for min time between packets from the same sprinkler,
                 packets_time_diff - dictionary of packets time differences
        """

        min_times_found = []
        duplicate_idx = []
        # to avoid rssi and timestamp fields
        tmp_packets_in_current_location = []
        for i in range(len(self.packets_in_current_location)):
            tmp_copy = self.packets_in_current_location[i].copy()
            tmp_packets_in_current_location.append(tmp_copy)
            tmp_packets_in_current_location[i]['packet'] = tmp_copy['packet'][0:74]

        packets_df = pd.DataFrame(tmp_packets_in_current_location)
        packets_time_diff = {}
        for adv_address in list(packets_df['adv_address'].unique()):
            if adv_address is not None:
                # take only the packets with the same adv_address field
                df_packet_data_by_id = packets_df[packets_df['adv_address'] == adv_address]
                # use only the packets for duplicated func
                packets = df_packet_data_by_id['packet']
                # keep only the packets that appears more than once
                df_packet_data_duplicates = packets[packets.duplicated(keep=False)]
                # order the packets and keep the index
                df_packet_data_duplicates_index_groups = df_packet_data_duplicates.groupby(
                    list(df_packet_data_duplicates)).apply(lambda x: tuple(x.index)).tolist()
                # keep only the packets that appeared more than 3 times
                df_packet_data_duplicates_highest = [t for t in df_packet_data_duplicates_index_groups if len(t) > 3]

                duplicate_idx = df_packet_data_duplicates_highest

            if len(duplicate_idx) == 0:
                avg_rssi_list = packets_df[packets_df['adv_address'] == adv_address]
                avg_rssi_list = avg_rssi_list['rssi']
                avg_rssi = sum(avg_rssi_list) / len(avg_rssi_list)
                min_times_found.append({'adv_address': adv_address,
                                        'min_time_between_packet_in_sprinkler': None,
                                        'avg_rssi': avg_rssi})
                continue
            # go over all groups of packets from the same sprinkler
            duplicates_delta_min = np.inf
            estimate_diff_time = np.inf
            df_duplicates_data = {}
            packets_df_2 = pd.DataFrame(self.packets_in_current_location)
            for i in range(len(duplicate_idx)):
                # take the time of the packets needed for the calculation
                dup_idx = np.array(duplicate_idx[i]) - 1
                df_duplicates_data = packets_df_2.iloc[list(dup_idx)]
                df_duplicates_times = df_duplicates_data['time_from_start']
                # compute the min time between packets
                duplicates_times_list = list(df_duplicates_times)
                df_duplicates_packets = df_duplicates_data['packet']
                # compute the min time between packets
                duplicates_packets_list = list(df_duplicates_packets)
                estimate_diff_time = estimate_diff_packet_time(packets=duplicates_packets_list,
                                                               packets_time=duplicates_times_list)
                del estimate_diff_time[0]  # the first value is always None
                if min(estimate_diff_time) < duplicates_delta_min:
                    duplicates_delta_min = min(estimate_diff_time)
                # save the time diff for this packet
                packets_time_diff[duplicates_packets_list[0][16:90]] = estimate_diff_time
                if len(df_duplicates_data) == 0:
                    continue
            avg_rssi_list = df_duplicates_data['rssi']
            avg_rssi = sum(avg_rssi_list) / len(avg_rssi_list)
            min_times_found.append({'adv_address': adv_address,
                                    'min_time_between_packet_in_sprinkler': duplicates_delta_min,
                                    'avg_rssi': avg_rssi})
        return min_times_found, packets_time_diff

    def get_estimated_tag_in_location(self):
        """
        decides what is the tag being tested in this location with the data gathered so far
        :return: adv_address (string) of the estimated tag or None if no packet found,
                 tag_appeared_before (bool) True if the tag has appeared in other location, False otherwise,
                 packets_time_diff  (dictionary) packets time differences
        """
        chosen_tag = None
        if len(self.packets_in_current_location) == 0:
            return chosen_tag, False, {}

        min_times_found, packets_time_diff = self.get_rates()
        min_time = np.inf
        min_rssi = np.inf

        # first check if the data received is enough to decide if the tag passed
        for i in range(len(min_times_found)):
            if min_times_found[i]['min_time_between_packet_in_sprinkler'] is not None:
                if min_times_found[i]['min_time_between_packet_in_sprinkler'] < min_time:
                    min_time = min_times_found[i]['min_time_between_packet_in_sprinkler']
                    chosen_tag = min_times_found[i]['adv_address']
        # decide by rssi
        if chosen_tag is None:
            for i in range(len(min_times_found)):
                if min_times_found[i]['avg_rssi'] < min_rssi:
                    min_rssi = min_times_found[i]['avg_rssi']
                    chosen_tag = min_times_found[i]['adv_address']

        tag_appeared_before = False
        if chosen_tag in self.tags_list:
            tag_appeared_before = True

        return chosen_tag, tag_appeared_before, packets_time_diff

    def get_black_list_size(self):
        return len(self.black_list)

###########################################
#              Tester GUI             #
###########################################


def credentials_gui():
    """
    open GUI for getting user_name, password and owner_id from user
    """
    layout = [
        [SimGUI.Text('Please insert FusionAuth Credentials for uploading and serialization this run data')],
        [SimGUI.Text('User name (email address):'),
         SimGUI.InputText('', key='user_name')],
        [SimGUI.Text('Password:'),
         SimGUI.InputText('', key='password')],
        [SimGUI.Text('Owner Id:'),
         SimGUI.InputText('wiliot-ops', key='owner_id')],
        [SimGUI.Submit()]]

    window = SimGUI.Window('User Credentials', layout)
    while True:
        event, values = window.read()
        if event == 'Submit':
            break
        elif event is None:
            print('User exited the program')
            window.close()
            exit()

    window.close()
    return values


def upload_conclusion(failed_tags=None, succeeded_csv_uploads=None):
    """
    :type failed_tags: list
    :param failed_tags: list of dictionaries ({'tag_id': XXX, 'status': YYY}) of tags that failed in serialization
    :type succeeded_csv_uploads: bool
    :param succeeded_csv_uploads: if True - upload of csv has succeeded
    """
    if failed_tags is None or len(failed_tags) == 0:
        serialization_line = [SimGUI.Text("Serialization succeeded", border_width=10, background_color='green')]
    else:
        serialization_line = [SimGUI.Text("Serialization failed, look in log file for more details\n"
                                          "please serialize manually", border_width=10,
                                          background_color='red')]

    if succeeded_csv_uploads is None or succeeded_csv_uploads:
        csv_uploads_line = [SimGUI.Text("Upload CSV's succeeded", border_width=10, background_color='green')]
    else:
        csv_uploads_line = [SimGUI.Text("Upload CSV's Failed, look in log file for more details\n"
                                        "please upload manually", border_width=10,
                                        background_color='red')]

    if failed_tags is None:
        layout = [csv_uploads_line, [SimGUI.Exit()]]
    else:
        layout = [serialization_line, csv_uploads_line, [SimGUI.Exit()]]

    window2 = SimGUI.Window('Conclusion', layout)
    event, values = window2.read()
    window2.close()

###########################################
#              Cloud Functions            #
###########################################


def check_user_config_is_ok(tester_type=TesterName.OFFLINE.value):
    """
    checks if the user_config.json is valid
    :type tester_type: string
    :param tester_type: indicates in which folder the config folder should be:
                        'offline', 'conversion', 'tal15k', 'yield'
    :return: file_path, user_name, password, owner_id, is_successful
    (True if configs/user_config.json has the parameters
    ("UserName", "Password", "OwnerId") False otherwise)
    """
    available_testers = [getattr(TesterName, test).value for test in TesterName.__members__ if
                         getattr(TesterName, test).value != '']
    if tester_type not in available_testers:
        raise Exception('unsupported tester_type inserted to check_user_config_is_ok()')

    folder_path = tester_type
    if tester_type == TesterName.OFFLINE.value:
        folder_path = os.path.join('..', tester_type)
    folder_path = os.path.join(folder_path, 'configs')
    cfg_file_name = 'user_configs.json'
    # if file or folder doesn't exist will create json file with Authorization = 'None' and raise exception
    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, cfg_file_name)
        if os.path.exists(file_path):
            cfg_data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, cfg_file_name))
            try:
                user_name = cfg_data['UserName']
                password = cfg_data['Password']
                owner_id = cfg_data['OwnerId']
                if user_name is None or password is None or owner_id is None:
                    raise Exception()
            except Exception:
                print("Config file missing some variables")
                values = credentials_gui()
                user_name = values['user_name']
                password = values['password']
                owner_id = values['owner_id']
                with open(file_path, 'w') as cfg:
                    json.dump({"Authorization": "None", "UserName": user_name, "Password": password,
                               "OwnerId": owner_id}, cfg)
        else:
            print("Config file doesn't exist\n")
            values = credentials_gui()
            user_name = values['user_name']
            password = values['password']
            owner_id = values['owner_id']
            with open(file_path, 'w') as cfg:
                json.dump({"Authorization": "None", "UserName": user_name, "Password": password,
                           "OwnerId": owner_id}, cfg)

    else:
        print("'wiliot_testers/' + tester_type + '/configs' directory doesn't exist\n"
              "Creating directory and user_config.json")
        os.mkdir(folder_path)
        file_path = os.path.join(folder_path, cfg_file_name)
        values = credentials_gui()
        user_name = values['user_name']
        password = values['password']
        owner_id = values['owner_id']
        with open(file_path, 'w') as cfg:
            json.dump({"Authorization": "None", "UserName": user_name, "Password": password,
                       "OwnerId": owner_id}, cfg)

    if user_name == '' or password == '':
        print('Unable to get token from cloud because the user_name or password were not documented\n'
              'to Upload files please insert your FusionAuth User name and Password in file:\n'
              'configs/user_configs.json\n')
        return file_path, user_name, password, owner_id, False

    return file_path, user_name, password, owner_id, True


def get_new_token_api(tester_type=TesterName.OFFLINE.value, rec_run_itter=0):
    """
    uses user name and password to get a token for uploading files
    saves the Bearer token to Json
    :type tester_type: string
    :param tester_type: indicates in which folder the config folder should be:
                        'offline', 'conversion', 'tal15k', 'yield'
    :type rec_run_itter: int
    :param rec_run_itter: if bigger than 1 will return without running will run otherwise
    return: True if got token and saved it successfully False otherwise
    """
    if rec_run_itter > 1:
        return False
    rec_run_itter += 1
    file_path, user_name, password, owner_id, is_successful = check_user_config_is_ok(tester_type)

    conn = http.client.HTTPSConnection("api.wiliot.com")
    payload = ''
    headers = {}
    url = "/v1/auth/token?username=" + user_name + '&password=' + password
    conn.request("POST", url, payload, headers)
    res = conn.getresponse()
    data = res.read()

    if str(res.status) == '500':
        print('There was a problem at the Server side (status 500), '
              'please try get_new_token_api() again or reach Wiliot')
        return False
    elif str(res.status) in ['401', '400']:
        folder_path = tester_type
        if tester_type == TesterName.OFFLINE.value:
            folder_path = os.path.join('..', tester_type)
        folder_path = os.path.join(folder_path, 'configs')
        cfg_file_name = 'user_configs.json'
        file_path = os.path.join(folder_path, cfg_file_name)
        if os.path.exists(file_path):
            values = credentials_gui()
            user_name = values['user_name']
            password = values['password']
            owner_id = values['owner_id']
            with open(file_path, 'w') as cfg:
                json.dump({"Authorization": "None", "UserName": user_name, "Password": password,
                           "OwnerId": owner_id}, cfg)
        print('There was a problem with the authorization,\n'
              'Please make sure your user name and password is correct or reach Wiliot')
        print('Status code is: ' + str(res.status))
        print('Please resubmit the credentials')
        get_new_token_api(tester_type=TesterName.OFFLINE.value, rec_run_itter=rec_run_itter)
        return False
    elif str(res.status)[0:2] == '40':
        print('There was a problem at the request side (status 40*), '
              'please try get_new_token_api() again or reach Wiliot')
        print('Status code is: ' + str(res.status))
        return False
    elif str(res.status) == '200':
        print('The token drawn successfully from Wiliot cloud')

    res_dict = ast.literal_eval(data.decode("utf-8"))
    if is_successful:
        with open(file_path, 'w') as cfg:
            try:
                json.dump({"Authorization": res_dict['access_token'], "UserName": user_name,
                           "Password": password, "OwnerId": owner_id}, cfg)
                return True
            except Exception:
                json.dump({"Authorization": 'None', "UserName": user_name,
                           "Password": password, "OwnerId": owner_id}, cfg)
                raise Exception('failed to get token from cloud')


def upload_to_cloud_api(batch_name, tester_type, run_data_csv_name=None, tags_data_csv_name=None, to_logging=False,
                        env='prod', is_batch_name_inside_logs_folder=True):
    """
    uploads a tester log to Wiliot cloud
    :type batch_name: string
    :param batch_name: folder name of the relevant log
    :type run_data_csv_name: string
    :param run_data_csv_name: name of desired run_data log to upload,
                              should contain 'run_data' and end with .csv
    :type tags_data_csv_name: string
    :param tags_data_csv_name: name of desired tags_data log to upload,
                               should contain 'tags_data' and end with .csv
    :type tester_type: string
    :param tester_type: name of the tester the run was made on (offline, tal15k, conversion, yield)
    :type to_logging: bool
    :param to_logging: if true, write to logging.debug the result of the upload
    :type env: string (prod, dev, test)
    :param env: to what cloud environment should we upload the files
    :type is_batch_name_inside_logs_folder: bool
    :param is_batch_name_inside_logs_folder: flag to indicate if the batch_name is the regular run folder (logs) or
                                             this function is being used in a way we will need the full path
    :return: True for successful upload, False otherwise
    """
    if tester_type not in ['offline', 'tal15k', 'conversion', 'yield']:
        print('Unsupported tester_type inserted to upload_to_cloud_api()\nPlease change it and retry')
        return
    if run_data_csv_name is not None and 'run_data' not in run_data_csv_name:
        print('Unsupported run_data_csv_name inserted to upload_to_cloud_api()\nPlease change it and retry')
        return
    if tags_data_csv_name is not None and 'tags_data' not in tags_data_csv_name:
        print('Unsupported tags_data_csv_name inserted to upload_to_cloud_api()\nPlease change it and retry')
        return

    folder_path = os.path.join('..', tester_type)
    folder_path = os.path.join(folder_path, 'configs')
    cfg_file_name = 'user_configs.json'
    # if file or folder doesn't exist will create json file with Authorization = 'None' and raise exception
    if not get_new_token_api():
        raise Exception('get_new_token_api() failed')

    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, cfg_file_name)
        if os.path.exists(file_path):
            cfg_data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, cfg_file_name))
            bearer_token = cfg_data['Authorization']
        else:
            print("Config file doesn't exist\n Creating user_config.json")
            with open(file_path, 'w') as cfg:
                json.dump({"Authorization": "None", "OwnerId": "None"}, cfg)
            raise Exception('user_config.json was created\n')
    else:
        print("'wiliot_testers/" + tester_type + "/configs' directory doesn't exist\n "
                                                 "Creating directory and user_config.json")
        os.mkdir(folder_path)
        file_path = os.path.join(folder_path, cfg_file_name)
        with open(file_path, 'w') as cfg:
            json.dump({"Authorization": "None", "OwnerId": "None"}, cfg)
        raise Exception('user_config.json was created to Upload files '
                        'please insert your OwnerId Bearer token in file:\n'
                        'wiliot_testers/' + tester_type + '/configs/user_configs.json under \n'
                        '"Authorization": "<enter your Bearer token here>"\n')
    print('Upload to cloud has began\nWaiting for the server response, please wait...')
    conn = http.client.HTTPSConnection("api.wiliot.com")
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    headers = {
        'Authorization': 'Bearer ' + bearer_token,
        'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
    }

    if env == 'prod':
        url = "/v1/manufacturing/upload/testerslogs/"
    elif env == 'test':
        url = "/test/v1/manufacturing/upload/testerslogs/"
    elif env == 'dev':
        url = "/dev/v1/manufacturing/upload/testerslogs/"
    else:
        print('unsupported env value was inserted (env = ' + str(env) + ')')
        return False

    url += tester_type

    if run_data_csv_name is not None:
        # run_url = url + '-tester-runs-indicators'
        run_url = url + '-tester/runs-indicators'
        print("Run data csv upload started")
        if to_logging:
            logging.debug("Run data csv upload started")
        data_list = []
        data_list.append(encode('--' + boundary))
        if is_batch_name_inside_logs_folder:
            run_data_path = 'logs/' + batch_name
        else:
            run_data_path = batch_name
        run_data_path = os.path.join(run_data_path, run_data_csv_name)

        if not os.path.exists(run_data_path):
            exception_string = str(run_data_path) + ' run_data_path could not be found \n' + \
                               'please find it and try to upload again'
            raise Exception(exception_string)

        data_list.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format(run_data_path)))
        file_type = mimetypes.guess_type(run_data_path)[0] or 'application/octet-stream'
        data_list.append(encode('Content-Type: {}'.format(file_type)))
        data_list.append(encode(''))
        with open(run_data_path, 'rb') as f:
            data_list.append(f.read())
        data_list.append(encode('--' + boundary + '--'))
        data_list.append(encode(''))
        body = b'\r\n'.join(data_list)
        payload = body

        conn.request("POST", run_url, payload, headers)
        run_data_res = conn.getresponse()
        run_data_data = run_data_res.read()
        print("answer from cloud is:")
        print(run_data_data.decode("utf-8"))
        if to_logging:
            logging.debug("answer from cloud is:")
            logging.debug(run_data_data.decode("utf-8"))
        if str(run_data_res.status) == '500':
            print('There was a problem at the Server side (status 500), please try to upload again or reach Wiliot')
            return False
        elif str(run_data_res.status) in ['401', '400']:
            get_new_token_api(tester_type=TesterName.OFFLINE.value, rec_run_itter=0)
            return False
        elif str(run_data_res.status)[0:2] == '40':
            print('There was a problem with the request (status 40*), please try to upload again or reach Wiliot')
            print('Status code is: ' + str(run_data_res.status))
            return False
        elif str(run_data_res.status) == '200':
            print('The file "' + run_data_csv_name + '" was uploaded successfully to Wiliot cloud')

    if tags_data_csv_name is not None:
        # tags_url = url + '-tester-tags-indicators'
        tags_url = url + '-tester/tags-indicators'
        print("Tags data csv upload started")
        if to_logging:
            logging.debug("Tags data csv upload started")
        data_list = []
        data_list.append(encode('--' + boundary))
        if is_batch_name_inside_logs_folder:
            tags_data_path = 'logs/' + batch_name
        else:
            tags_data_path = batch_name
        tags_data_path = os.path.join(tags_data_path, tags_data_csv_name)
        if not os.path.exists(tags_data_path):
            exception_string = str(tags_data_path) + ' tags_data_path could not be found \n' + \
                               'please find it and try to upload again'
            raise Exception(exception_string)
        data_list.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format(tags_data_path)))
        file_type = mimetypes.guess_type(tags_data_path)[0] or 'application/octet-stream'
        data_list.append(encode('Content-Type: {}'.format(file_type)))
        data_list.append(encode(''))
        with open(tags_data_path, 'rb') as f:
            data_list.append(f.read())
        data_list.append(encode('--' + boundary + '--'))
        data_list.append(encode(''))
        body = b'\r\n'.join(data_list)
        payload = body

        conn.request("POST", tags_url, payload, headers)
        tags_data_res = conn.getresponse()
        tags_data_data = tags_data_res.read()
        print("answer from cloud is:")
        print(tags_data_data.decode("utf-8"))
        if to_logging:
            logging.debug("answer from cloud is:")
            logging.debug(tags_data_data.decode("utf-8"))
        if str(tags_data_res.status) == '500':
            print('There was a problem at the Server side (status 500), please try to upload again or reach Wiliot')
            return False
        elif str(tags_data_res.status) in ['401', '400']:
            get_new_token_api(tester_type=TesterName.OFFLINE.value, rec_run_itter=0)
            return False
        elif str(tags_data_res.status)[0:2] == '40':
            print('There was a problem at the request side (status 40*), please try to upload again or reach Wiliot')
            print('Status code is: ' + str(tags_data_res.status))
            return False
        elif str(tags_data_res.status) == '200':
            print('The file "' + tags_data_csv_name + '" was uploaded successfully to Wiliot cloud')
    print('-----------------------------------------------------------------------\n'
          'upload to cloud is finished successfully, the program will end now\n'
          '-----------------------------------------------------------------------')
    return True


class SerializationAPI(threading.Thread):

    def __init__(self, batch_dictionary, to_logging=False, get_new_token=True, try_serialize_again=None,
                 printing_lock=None):
        """
        uploads 1 batch using serialization API and puts the result in batch_dictionary['response']
        :type batch_dictionary:
            {'response': string,
             'upload_data': [{"payload": packet (string, of full packets w/o 'post_process("' or '")' ),
                              "tagId": externalId (string)},....],
             'writing_lock': threading.Lock()}
        :param batch_dictionary: dictionary of a specific batch to upload
        :type to_logging: bool
        :param to_logging: if true, write to logging.debug the result of the upload
        :type try_serialize_again: threading.Event
        :param try_serialize_again: if set will make all threads that failed for the first time to try again
        :type printing_lock: threading.Lock
        :param printing_lock: printing lock
        """
        super(SerializationAPI, self).__init__()
        self.batch_dictionary = batch_dictionary
        self.kill_thread = threading.Event()  # will be set by the part that called this class
        self.try_serialize_again = try_serialize_again
        self.to_logging = to_logging
        self.get_new_token = get_new_token
        self.printing_lock = printing_lock
        self.exception_queue = Queue()
        self.is_done = False
        self.failed_tags = []
        with self.batch_dictionary['writing_lock']:
            self.batch_dictionary['response'] = 'waiting for cloud response'
            self.batch_dictionary['failed_already'] = False
        self.tags_in_batch = []
        for i in range(len(batch_dictionary['upload_data'])):
            self.tags_in_batch.append(batch_dictionary['upload_data'][i]['tagId'])

    def run(self):
        """
        will do the upload, will save the result to batch_dictionary['response'] when done
        """
        try:
            time.sleep(0)
            data, res = self.serialize()
            if res is not None:
                if str(res.status) == '504':
                    message = 'There was a problem at the Server side (status 504), ' \
                              'will try to upload again (only once)'
                    if self.printing_lock is not None:
                        printing_func(str_to_print=message, logging_entity="serializationThread",
                                      lock_print=self.printing_lock, do_log=self.to_logging)
                    else:
                        print(message)
                    if self.to_logging:
                        logging.debug('Serialization: ' + str(message))
                    # try again
                    data, res = self.serialize()

            self.check_cloud_return_values(data, res)
            if self.try_serialize_again is not None and self.batch_dictionary['failed_already']:
                self.try_serialize_again.wait()
                data, res = self.serialize()
                self.check_cloud_return_values(data, res)

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

        finally:
            self.kill_thread.wait()
            self.is_done = True

    def get_response(self):
        with self.batch_dictionary['writing_lock']:
            return self.batch_dictionary['response']

    def serialize(self):
        """
        serializing the tags
        :return: data (bytes) - data inside the message returned from cloud
        :return: res (http.client.HTTPSConnection.getResponse() return value) - return code
        """
        # take only the relevant part from the packets
        for i in range(len(self.batch_dictionary['upload_data'])):
            self.batch_dictionary['upload_data'][i]['payload'] = \
                self.batch_dictionary['upload_data'][i]['payload'][16:74]

        if self.to_logging:
            logging.debug('Serialization: sends the following upload_data: ' +
                          str(self.batch_dictionary['upload_data']))
        folder_path = os.path.join('..', 'offline')  # only offline tester should do serialization
        folder_path = os.path.join(folder_path, 'configs')
        cfg_file_name = 'user_configs.json'
        # if file or folder doesn't exist will create json file with Authorization = 'None' and raise exception
        if self.get_new_token:
            if not get_new_token_api():
                raise Exception('get_new_token_api() failed')

        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, cfg_file_name)
            if os.path.exists(file_path):
                cfg_data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, cfg_file_name))
                bearer_token = cfg_data['Authorization']
            else:
                message = "Config file doesn't exist\n Creating user_config.json"
                if self.printing_lock is not None:
                    printing_func(str_to_print=message, logging_entity="serializationThread",
                                  lock_print=self.printing_lock, do_log=self.to_logging)
                else:
                    print(message)
                with open(file_path, 'w') as cfg:
                    json.dump({"Authorization": "None"}, cfg)
                raise Exception('user_config.json was created\n')
        else:
            message = "'wiliot_testers/offline/configs' directory doesn't exist\n" \
                      " Creating directory and user_config.json"
            if self.printing_lock is not None:
                printing_func(str_to_print=message, logging_entity="serializationThread",
                              lock_print=self.printing_lock, do_log=self.to_logging)
            else:
                print(message)
            os.mkdir(folder_path)
            file_path = os.path.join(folder_path, cfg_file_name)
            with open(file_path, 'w') as cfg:
                json.dump({"Authorization": "None"}, cfg)
            raise Exception('user_config.json was created to Upload files please insert your'
                            ' Bearer token in file:\n'
                            'wiliot_testers/offline/configs/user_configs.json under \n'
                            '"Authorization": "<enter your Bearer token here>"\n')

        message = 'Serialization process has began (for tags ' + str(self.tags_in_batch) + \
                  ')\nWill update when a server response is received'
        if self.printing_lock is not None:
            printing_func(str_to_print=message, logging_entity="serializationThread",
                          lock_print=self.printing_lock, do_log=self.to_logging)
        else:
            print(message)

        conn = http.client.HTTPSConnection("api.wiliot.com")
        payload = json.dumps(self.batch_dictionary['upload_data'])
        headers = {
            'Authorization': 'Bearer ' + bearer_token,
            'Content-Type': 'application/json'
        }
        url = "/v1/owner/" + cfg_data["OwnerId"] + "/serialize"
        try:
            conn.request("POST", url, payload, headers)
            res = conn.getresponse()
            data = res.read()
        except Exception:
            exc_type, exc_obj, exc_trace = sys.exc_info()
            data, res = None, None

            if exc_type == socket.gaierror and str(exc_obj) == "[Errno 11002] getaddrinfo failed" or \
                    "Remote end closed connection without response" in str(exc_obj):
                conn = http.client.HTTPSConnection("api.wiliot.com")
                payload = json.dumps(self.batch_dictionary['upload_data'])
                headers = {
                    'Authorization': 'Bearer ' + bearer_token,
                    'Content-Type': 'application/json'
                }
                url = "/v1/owner/" + cfg_data["OwnerId"] + "/serialize"
                try:
                    conn.request("POST", url, payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                except Exception:
                    pass

        return data, res

    def check_cloud_return_values(self, data, res):
        """
        checks cloud return values are correct
        :type data: bytes
        :param data: data inside the message returned from cloud
        :type res: http.client.HTTPSConnection.getResponse() return value
        :param res: return code
        """
        tags_in_batch = []
        self.failed_tags = []
        for i in range(len(self.batch_dictionary['upload_data'])):
            tag_id = self.batch_dictionary['upload_data'][i]['tagId']
            tags_in_batch.append(tag_id)
            if res is not None:
                self.failed_tags.append({'tag_id': tag_id, 'status': str(res.status)})
            else:
                self.failed_tags.append({'tag_id': tag_id, 'status': 'unknown error'})
        message = ''
        if res is None:
            message = 'upload failed with unknown error code, please look inside log and reach wiliot'
        elif str(res.status) == '500':
            message = 'There was a problem at the Server side (status 500), ' \
                      'please try to upload again or reach Wiliot'

        elif str(res.status) == '401':
            message = 'There was a problem with the authorization (status 401),\n ' \
                      'Please make sure your user name and password in wiliot_testers/' \
                      'offline/configs/user_configs.json is correct or reach Wiliot'

        elif str(res.status)[0:2] == '40':
            message = 'There was a problem with the request (status 40*), ' \
                      'please try to upload again or reach Wiliot \n' \
                      'Status code is: ' + str(res.status)

        elif str(res.status) == '200':
            self.failed_tags = []
            message = 'uploaded Successfully'
        else:
            message = 'There was a problem, Status code is: ' + str(res.status)
        message = "Answer from cloud for uploading tags " + str(self.tags_in_batch) + ' is: ' + message + \
                  '\nmessage received = ' + str(data.decode("utf-8"))
        if self.printing_lock is not None:
            printing_func(str_to_print=message, logging_entity="serializationThread",
                          lock_print=self.printing_lock, do_log=self.to_logging)
        else:
            print(message)

        with self.batch_dictionary['writing_lock']:
            self.batch_dictionary['response'] = message
        if res is not None:
            if not str(res.status) == '200':
                all_tags_serialized_already = False
                have_to_end_this_run = False
                if str(res.status) == '207':  # serialization succeeded partially
                    self.failed_tags = []
                    all_tags_serialized_already = True
                    string_received = data.decode("utf-8")
                    parts = string_received.split('","message":"')
                    for msg in range(len(parts)):
                        if msg == 0:
                            continue
                        is_pass = False
                        if '"isSuccess":true' in parts[msg - 1]:
                            is_pass = True
                        tag_id = parts[msg - 1].split(',"tagId":"')[1].split('"}')[0]
                        # the same request was already executed
                        if "Tag ID was already assigned" not in parts[msg].split('"')[0]:
                            all_tags_serialized_already = False
                        if "Tag ID already exists. Cannot serialize tag, " in parts[msg].split('"')[0]:
                            message = "\nTag " + tag_id + \
                                      " was already assigned to a different tag, please remove this tag\n"
                            if self.printing_lock is not None:
                                printing_func(str_to_print=message, logging_entity="serializationThread",
                                              lock_print=self.printing_lock, do_log=self.to_logging)
                            else:
                                print(message)
                            have_to_end_this_run = True
                            self.failed_tags.append({'tag_id': tag_id, 'status': message.replace('\n', '')})

                        if "Tag already serialized in this request" in parts[msg].split('"')[0]:
                            message = "\nTag " + tag_id + \
                                      " was already serialized in this request, please remove this tag\n"
                            self.failed_tags.append({'tag_id': tag_id, 'status': message.replace('\n', '')})
                            if self.printing_lock is not None:
                                printing_func(str_to_print=message, logging_entity="serializationThread",
                                              lock_print=self.printing_lock, do_log=self.to_logging)
                            else:
                                print(message)
                            have_to_end_this_run = True
                if not all_tags_serialized_already:
                    # for the case serialization failed for the second time
                    if self.batch_dictionary['failed_already']:
                        message = '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n' \
                                  'Serialization failed!! you will need to end this run and restart it.\n' \
                                  'you will also need to register the following data manually:\n' + \
                                  str(self.batch_dictionary['upload_data']) + \
                                  '\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                        if self.printing_lock is not None:
                            printing_func(str_to_print=message, logging_entity="serializationThread",
                                          lock_print=self.printing_lock, do_log=self.to_logging)
                        else:
                            print(message)
                    else:
                        message = 'Serialization failed for data: ' + str(self.batch_dictionary['upload_data']) + \
                                  ' will try to do this serialization again when the user will press Stop\n'
                        if self.printing_lock is not None:
                            printing_func(str_to_print=message, logging_entity="serializationThread",
                                          lock_print=self.printing_lock, do_log=self.to_logging)
                        else:
                            print(message)
                    self.batch_dictionary['failed_already'] = True
                    self.kill_thread.set()
                    if have_to_end_this_run:
                        raise Exception('Serialization failed in a way that requires ending this run')


def check_serialization_exception_queues(serialization_threads_working, end_the_fails=False, printing_lock=None,
                                         to_logging=False):
    """
    checks if there is any response for any serialization thread, if it is good (success) will terminate the thread,
    else will raise exception
    :type serialization_threads_working: list of SerializationAPI
    :param serialization_threads_working: the Serialization process that needs to be monitored
    :type end_the_fails: bool
    :param end_the_fails: if True, kill all threads that had an exception
    :type printing_lock: threading.Lock
    :param printing_lock: printing lock
    :type to_logging: bool
    :param to_logging: if true, write to logging.debug the result of the upload
    """
    for thread in serialization_threads_working:
        tags_in_batch = []
        for i in range(len(thread.batch_dictionary['upload_data'])):
            tags_in_batch.append(thread.batch_dictionary['upload_data'][i]['tagId'])
        if not thread.exception_queue.empty():
            exception_details = thread.exception_queue.get()
            # using logging.warning that will be parsed to errors
            print_exception(exception_details, printing_lock=printing_lock)
            exc_type, exc_obj, exc_trace = exception_details
            if end_the_fails:
                thread.kill_thread.set()
                thread.join(timeout=0.5)
            raise Exception('Serialization failed for tags ' + str(tags_in_batch))


def check_serialization_response(serialization_threads_working, printing_lock=None, to_logging=False):
    """
    checks if there is any response for any serialization thread, if it is good (success) will terminate the thread,
    else will raise exception
    :type serialization_threads_working: list of SerializationAPI
    :param serialization_threads_working: the Serialization process that needs to be monitored
    :type printing_lock: threading.Lock
    :param printing_lock: printing lock
    :type to_logging: bool
    :param to_logging: if true, write to logging.debug the result of the upload
    """
    for thread in serialization_threads_working:
        response = thread.get_response()
        if 'uploaded Successfully' in response:
            thread.kill_thread.set()
            thread.join(timeout=0.5)
        else:
            pass


def close_all_serialization_processes_when_they_done(serialization_threads_working, try_serialize_again=None,
                                                     printing_lock=None, to_logging=False):
    """
    terminates all serialization threads when they are done
    :type serialization_threads_working: list of SerializationAPI
    :param serialization_threads_working: the Serialization process that needs to be monitored
    :type try_serialize_again: threading.Event
    :param try_serialize_again: if exists it will be set to set and it will make all
                                threads that failed for the first time to try again
    :type printing_lock: threading.Lock
    :param printing_lock: printing lock
    :type to_logging: bool
    :param to_logging: if true, write to logging.debug the result of the upload
    :return: list of dictionaries ({'tag_id': XXX, 'status': YYY}) of tags which have failed to serialize
    """
    if len(serialization_threads_working) > 0:
        message = 'please wait until all serialization processes end,\n' \
                  'will let you know when it is done (not more than a minute)'
        if printing_lock is not None:
            printing_func(str_to_print=message, logging_entity="serializationThread",
                          lock_print=printing_lock, do_log=to_logging)
        else:
            print(message)
    if try_serialize_again is not None:
        try_serialize_again.set()

    failed_tags = []
    # tmp_serialization_threads_working = copy.deepcopy(serialization_threads_working)
    while len(serialization_threads_working) > 0:
        locs_to_pop = []
        for loc, thread in enumerate(serialization_threads_working):
            thread.kill_thread.set()
            response = thread.get_response()
            tags_in_batch = []
            for i in range(len(thread.batch_dictionary['upload_data'])):
                tags_in_batch.append(thread.batch_dictionary['upload_data'][i]['tagId'])

            if thread.is_done:
                locs_to_pop.append(loc)
                failed_tags += thread.failed_tags

        for loc in reversed(locs_to_pop):
            serialization_threads_working[loc].kill_thread.set()
            serialization_threads_working[loc].join(timeout=0.5)
            serialization_threads_working.pop(loc)

    for thread in serialization_threads_working:
        thread.kill_thread.set()
        thread.join(timeout=0.5)

    time.sleep(0.5)

    # if len(serialization_threads_working) > 0:
    message = '\nAll serialization processes ended\n'
    if len(failed_tags) > 0:
        message += '\n-------------------------------------\n'
        message += 'failed tags in serialization process:\n'
        for i in range(len(failed_tags)):
            message += str(failed_tags[i]) + '\n'
        message += '-------------------------------------\n'
    else:
        message += 'serialization of all tags in files succeeded'

    if printing_lock is not None:
        printing_func(str_to_print=message, logging_entity="serializationThread",
                      lock_print=printing_lock, do_log=to_logging)
    else:
        print(message)

    return failed_tags

###########################################
#         Multiple Events Functions       #
###########################################


def or_set(self):
    """
    :param self: threading.Event()
    """
    self._set()
    self.changed()


def or_clear(self):
    """
    :param self: threading.Event()
    """
    self._clear()
    self.changed()


def orify(e, changed_callback):
    """
    combines the events
    :type e: threading.Event()
    :param e: the event to be combined into
    :type changed_callback: threading.Event()
    :param changed_callback: the event to be combined into
    """
    e._set = e.set
    e._clear = e.clear
    e.changed = changed_callback
    e.set = lambda: or_set(e)
    e.clear = lambda: or_clear(e)


def or_event_set(*events):
    """
    creates an event the combines multiple events
    :type threading.Event() list
    :return: the said event
    """
    or_event = threading.Event()

    def changed():
        """
        makes sure all of the events are clear when the orEvent is created
        """
        bools = [e.is_set() for e in events]
        if any(bools):
            or_event.set()
        else:
            or_event.clear()

    for e in events:
        orify(e, changed)
    changed()
    return or_event

###########################################
#               Post-Process              #
###########################################


def process_encrypted_tags_data(data, packet_threshold, tester_type=TesterName.OFFLINE, fail_this_tag=False,
                                is_debug_mode=False, packets_time_diff=None, adv_of_selected_tag=None):
    """
    :type data: list
    :param data: list of dict with tag_data
    :type packet_threshold: int
    :param packet_threshold: amount of packets for tag to pass
    :type tester_type: TesterName()
    :param tester_type: what tester uses this function
    :type fail_this_tag: bool
    :param fail_this_tag: indicates if 'status' field should be 'Failed' (in case of duplications)
    :type is_debug_mode: bool
    :param is_debug_mode: if True adds more columns to tags_data, if False will not add anything
                          (only in offline tester)
    :type packets_time_diff: dictionary
    :param packets_time_diff: packets time differences
    :type adv_of_selected_tag: string
    :param adv_of_selected_tag: add_address of the selected tag
    :rtype: dict
    :rvalue: dictionary with defined values
    """
    df = pd.DataFrame(data)
    adv_addr = df['advAddress'].iloc[0]
    tag_location = df['tagLocation'].iloc[0]
    common_run_name = df['commonRunName'].iloc[0]  # get first value (common value to all tags in run)
    received_packet_count = len(data)  # data is list of dicts where every dict is from one packet
    raw_data = df[['packet_time', 'raw_data']].to_json(orient="records")

    status = 'Failed'
    if received_packet_count >= packet_threshold and not fail_this_tag:
        status = 'Passed'

    if tester_type.value == 'offline':
        external_id = set_external_id(df['externalId'].iloc[0])
        ret_dict = {'advAddress': adv_addr,
                    'tagLocation': tag_location,
                    'externalId': external_id,
                    'status': status,
                    'commonRunName': common_run_name}

        if 'temperatureFromSensor' in df.columns:  # exists only if temperature sensor is enabled
            ret_dict['temperatureFromSensor'] = df['temperatureFromSensor'].iloc[0]
        good_df = df[df['packetStatus'].isin(['good', 'no singularity'])]
        try:
            good_df = good_df[good_df['advAddress'] == adv_of_selected_tag]
            ret_dict['Ttfgp'] = min(good_df['packet_time'])
        except Exception:
            ret_dict['Ttfgp'] = None
        if is_debug_mode:
            if 'temperatureFromSensor' in df.columns:  # exists only if temperature sensor is enabled
                ret_dict['temperatureFromSensor'] = df['temperatureFromSensor'].iloc[0]
            ret_dict['AdvAddressesInLocation'] = list(df['advAddress'].unique())
            if adv_of_selected_tag is not None:
                ret_dict['advAddress'] = adv_of_selected_tag
            raw_data = df[['packetStatus', 'packet_time', 'raw_data']].to_json(orient="records")
            if packets_time_diff is not None:
                ret_dict['packetsTimeDiff'] = packets_time_diff

        ret_dict['rawData'] = raw_data
        return ret_dict
    else:
        return {'advAddress': adv_addr,
                'tagLocation': tag_location,
                'status': status,
                'commonRunName': common_run_name,
                'rawData': raw_data}


def set_external_id(external_id=None):
    """
    returns external ID value to calling function (returns 'None' for unconverted tags)
    @type external_id: str (default is None)
    @param external_id: ID to print on tag
    @rtype: str
    @rvalue: 'None' (for unconverted) or external_id string
    """
    if external_id is not None:
        return external_id
    else:
        return 'None'

###########################################
#                   Log                   #
###########################################


def snake_to_camel(word):
    ret_val = ''.join(x.capitalize() or '_' for x in word.split('_'))
    ret_val = ret_val[:1].lower() + ret_val[1:] if ret_val else ''
    return ret_val


def collect_errors(log_path='', log_file_lines=''):
    """
    collect errors from logfile
    @type log_path: str
    @param log_path: log path file
    @type log_file_lines: str
    @param log_file_lines: if empty (''), read log file
    @rtype: list
    @rvalue: list of errors occurred in test
    """
    reel_data = {'tested': 0, 'passed': 0, 'includingUnderThresholdPassed': 0}
    errors = []
    if log_file_lines == '':
        log_file = open(file=log_path)
        log_file_lines = log_file.readlines()
    tag_data = {'tagLocation': None, 'externalId': None, 'status': None, 'packets': None}
    for line in log_file_lines:
        if 'User set up is:' in line:
            parts = [p for p in line.split("{")]
            # the dictionary from main window
            parts2 = [p for p in parts[1].split("}")]
            config_dict_from_user = ast.literal_eval('{' + parts2[0] + '}')
            # the dictionary from memory
            parts2 = [p for p in parts[2].split("}")]
            config_dict_from_memory = ast.literal_eval('{' + parts2[0] + '}')
            # the printing string dictionary
            try:
                parts3 = [p for p in parts[3].split("}")]
                printing_dict_from_memory = ast.literal_eval('{' + parts3[0] + '}')
            except Exception:
                printing_dict_from_memory = {}

            config_dict = {**config_dict_from_user, **config_dict_from_memory}
            config_dict = {**config_dict, **printing_dict_from_memory}
            for key, value in config_dict.items():
                reel_data[key] = value
            reel_data['tested'] = 0
        line = line.strip()
        if 'DEBUG' in line:
            if 'Duplication' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

            if 'Packet rssi is too high' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

            if 'Received packet that is too short' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

            if 'Exception happened:, exc_type = ' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

        if 'INFO' in line:
            parts = [p for p in line.split("INFO")]

            if 'Tag location is: ' in parts[1]:
                parts[1] = parts[1].strip('Tag location is: ')
                parts = [p for p in parts[1].split(',')]
                tag_data['tagLocation'] = int(parts[0])
                reel_data['tested'] = int(tag_data['tagLocation']) + 1  # locations starts from 0

        if 'WARNING ' in line:  # the space is here to ignore the 'Warnings' print from the printer
            tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
            parts = [p for p in line.split("WARNING ")]
            tmp['errorString'] = parts[1]
            errors.append(tmp)

    if len(errors) != 0:
        return errors
    return None


def update_json_field(path, key, value):
    """
    update json config file value
    :type path: string
    :param path: json config file path
    :type key: string
    :param key: key to change in json file
    :type value: string
    :param value: value to change @key to
    :return:
    """
    with open(path, "r+") as jsonFile:
        config_data = json.load(jsonFile)

        config_data[key] = value

        jsonFile.seek(0)
        json.dump(config_data, jsonFile)
        jsonFile.truncate()


class CsvLog:
    """
    Class for csv logs
    """

    def __init__(self, header_type, path, headers=None, tester_type=TesterName.NONE, temperature_sensor=False,
                 is_debug_mode=False):
        """
        :type header_type: HeaderType
        :param header_type:
        :param path:
        :param headers:
        :param tester_type:
        :type temperature_sensor: bool
        :param temperature_sensor: if True -> temperature sensor enabled -> add header. else: sensor is disabled
        :type is_debug_mode: bool
        :param is_debug_mode: if True adds more columns to tags_data, if False will not add anything
                              (only in offline tester)
        """
        self.tags_header = ['advAddress', 'tagLocation', 'status', 'commonRunName', 'rawData']

        self.run_header = ['testerStationName', 'commonRunName', 'batchName', 'testerType',
                           'comments', 'errors',
                           'timeProfile', 'txPower', 'energizingPattern', 'rssiThreshold', 'packetThreshold',
                           'tested', 'passed', 'includingUnderThresholdPassed', 'includingUnderThresholdYield', 'yield',
                           'yieldOverTime', 'yieldOverTimeInterval', 'yieldOverTimeOn',
                           'inlayType', 'inlay']

        self.packets_header = ['commonRunName', 'encryptedPacket', 'time']

        if header_type.value == HeaderType.TAG.value:
            self.header = self.tags_header
        elif header_type.value == HeaderType.RUN.value:
            self.header = self.run_header
        elif header_type.value == HeaderType.PACKETS.value:
            self.header = self.packets_header
        else:
            self.header = []
        self.path = path

        # add additional columns per tester:
        self.temperature_sensor_enable = temperature_sensor
        self.add_headers(headers, header_type, tester_type, is_debug_mode)

    def add_headers(self, headers=None, header_type=HeaderType.RUN, tester_type=TesterName.NONE, is_debug_mode=False):
        """
        added additional headers to output file according to file type and tester type
        :type headers:
        :param headers: additional headers for output file (determined by user)
        :type header_type: HeaderType
        :param header_type: determines if the file generated stores run data or tags data
        :type tester_type: TesterName
        :param tester_type: determines unique headers to add according to tester type
        :type is_debug_mode: bool
        :param is_debug_mode: if True adds more columns to tags_data, if False will not add anything
                              (only in offline tester)
        """
        if headers is None:
            if header_type.value == HeaderType.RUN.value:
                if tester_type.value == TesterName.OFFLINE.value:
                    added_headers = ['testTime', 'maxTtfp', 'converted', 'surface', 'tagGen',
                                     'toPrint', 'passJobName', 'printingFormat', 'stringBeforeCounter',
                                     'digitsInCounter', 'gwVersion', 'desiredPass',
                                     'desiredTags', 'firstPrintingValue', 'missingLabel', 'maxMissingLabels']
                    # TODO - add this list instead af the previous when cloud supports it
                    # added_headers = ['testTime', 'maxTtfp', 'converted', 'surface', 'tagGen',
                    #                  'toPrint', 'passJobName', 'printingFormat', 'stringBeforeCounter',
                    #                  'digitsInCounter', 'gwVersion', 'secondEnergizingPattern', 'desiredPass',
                    #                  'desiredTags', 'firstPrintingValue', 'missingLabel', 'maxMissingLabels',
                    #                  'temperatureSensorEnable', 'wiliotPackageVersion']

                elif tester_type.value == TesterName.TAL15K.value:
                    added_headers = ['testersGwVersion', 'chargerGwVersion', 'rowsNum', 'columnsNum',
                                     'numOfTesters', 'chargingTime', 'timePerTag']
                elif tester_type.value == TesterName.CONVERSION.value:
                    added_headers = []
                elif tester_type.value == TesterName.SAMPLE.value:
                    added_headers = ['testTime', 'maxTtfp', 'gwVersion', 'bleAttenuation', 'loraAttenuation',
                                     'antennaType']
                else:
                    added_headers = []
            elif header_type.value == HeaderType.TAG.value:
                if tester_type.value == TesterName.OFFLINE.value:
                    added_headers = ['externalId']
                    if self.temperature_sensor_enable:
                        added_headers.append('temperatureFromSensor')
                    if is_debug_mode:
                        added_headers.append('AdvAddressesInLocation')
                        added_headers.append('packetsTimeDiff')
                        added_headers.append('Ttfgp')
                elif tester_type.value == TesterName.SAMPLE.value:
                    added_headers = ['externalId']
                else:
                    added_headers = []
            elif header_type.value == HeaderType.PACKETS.value:
                added_headers = []
                if tester_type.value == TesterName.OFFLINE.value:
                    added_headers = ['externalId', 'tagLocation', 'packetStatus', 'chosenTagInLocation',
                                     'chosenTagStatus']
                    if self.temperature_sensor_enable:
                        added_headers.append('temperatureFromSensor')
                elif tester_type.value == TesterName.SAMPLE.value:
                    added_headers = ['externalId']
            else:
                added_headers = []
        else:
            added_headers = headers
        self.header += added_headers

    def open_csv(self):
        """
        create csv file if not exist
        """
        # dir_path = self.path[:(len(self.path) - (len(self.path.split('/')[-1])+1))]
        dir_path = dirname(self.path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if not os.path.isfile(self.path):
            with open(self.path, 'w', newline='') as write_obj:
                csv_writer = writer(write_obj)
                csv_writer.writerow(self.header)

    def append_dict_as_row(self, data_to_append):
        """
        append data list to existing csv
        @type data_to_append: list
        @param data_to_append: dictionary for each new row
        """
        # Open file in append mode
        with open(self.path, 'a+', newline='') as write_obj:
            # Create a dict writer object from csv module
            csv_writer = DictWriter(write_obj, fieldnames=self.header)
            # Add contents of list as last rows in the csv file
            csv_writer.writerows(data_to_append)

    def append_list_as_row(self, data_to_append):
        """
        append data list to existing csv
        @type data_to_append: list
        @param data_to_append: values to append to csv
        """
        # Open file in append mode
        with open(self.path, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(data_to_append)

    def append_table(self, data_table):
        """
        append data table to existing csv (using append_list_as_row)
        @type: data_table: list (list of lists)
        @param data_table: values to append to csv
        """
        col = 0  # the table has only 1 column
        for i in range(len(data_table)):
            self.append_list_as_row(self.dict_to_list(data_table[i][col]))

    def dict_to_list(self, data):
        """
        convert dict to list
        @type data: dict
        @param data:
        @rtype: list
        """
        res_list = []
        for title in self.header:
            if title in data.keys():
                res_list.append(data[title])
            else:
                res_list.append('')
        return res_list

    def override_run_data(self, run_data):
        """
        override run_data.csv at the end of run
        @type run_data: dict
        @param run_data: run configurations and results such as passed, tested, yield, etc.
        """
        with open(self.path, 'w', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(self.header)
            # self.append_list_as_row(self.path, self.dict_to_list(run_data))
            csv_writer.writerow(self.dict_to_list(run_data))


class colors:
    # Printing colors by log level:
    MESSAGE = '\033[36m'

    DEBUG = '\033[36m'
    INFO = '\033[30m'
    WARNING = '\033[35m'
    ERROR = '\033[91m'
    CRITICAL = '\033[31m'

    END = '\033[0m'


class CustomFormatter(logging.Formatter):

    format = "%(message)s"
    module = "Module: %(module)s"
    line = 'File "%(pathname)s", line %(lineno)s\n'
    exception = '%(exc_info)s\n'
#     moduleAndLine = module + "  " + line + " :\n"

    FORMATS = {
        logging.DEBUG: colors.DEBUG + format + colors.END,
        logging.INFO: colors.INFO + format + colors.END,
        logging.WARNING: colors.WARNING + format + colors.END,
        logging.ERROR: colors.ERROR + format + colors.END,
        logging.CRITICAL: colors.CRITICAL + format + colors.END
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def update_json_field(path, key, value):
    """
    update json config file value
    :type path: string
    :param path: json config file path
    :type key: string
    :param key: key to change in json file
    :type value: string
    :param value: value to change @key to
    :return:
    """
    with open(path, "r+") as jsonFile:
        config_data = json.load(jsonFile)

        config_data[key] = value

        jsonFile.seek(0)
        json.dump(config_data, jsonFile)
        jsonFile.truncate()


def setLogger(loggerName, log_level, outputFile=None):
    # Create the logger
    logger = logging.getLogger(loggerName)
    logger.setLevel(log_level)

    # Create stream handler
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(CustomFormatter())
    streamHandler.setLevel(getattr(logging, log_level))

    # Create file handler
    if outputFile is not None:
        fileHandler = logging.FileHandler(outputFile, 'w+')
        fileHandler.setLevel(logging.DEBUG)
        logger.addHandler(fileHandler)

    # Add the stream and file handler to the logger
    logger.addHandler(streamHandler)
    return logger


def changeFileHandler(logger, newHandlerFile):
    for hdlr in logger.handlers[:]:  # remove all old handlers
        if 'filehandler' in str(hdlr).lower():
            logger.removeHandler(hdlr)
    fileHandler = logging.FileHandler(newHandlerFile, 'w+')
    fileHandler.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)
    return logger


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


if __name__ == '__main__':
    pass
