#!/tools/common/pkgs/python/3.6.3/bin/python3.6
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
     nor are you named on the U.S. Treasury Department's list of Specially Designated
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
'''
Created on Oct 24, 2021

@author: davidd
'''
import logging
import pickle
from numpy.core._multiarray_umath import arange
from urllib.parse import quote
import jwt
import numpy
import requests
from os import _exit, makedirs, mkdir, environ
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pygubu
from threading import Thread, Lock
from time import sleep
import time
import csv
import datetime
from ConfigsGui import ConfigsGui, DEFAULT_CONFIG
from ComConnect import ComConnect, GO, CONTINUE, CONNECT_HW, READ, popup_message
from traceback import print_exc
from json import load, dump, loads
import argparse
import http.client
import sys
from os.path import isfile, abspath, dirname, join, isdir, basename
sys.path.append(abspath(dirname(join('..', '..', '..', '..', 'pywiliot_internal'))))
from pywiliot_internal.wiliot.wiliot_testers.tester_utils \
    import setLogger, changeFileHandler, CsvLog, HeaderType, TesterName, StreamToLogger
from pywiliot_internal.wiliot.packet_data_tools.process_encrypted_packets import estimate_diff_packet_time

LOG_LEVEL = 'DEBUG'

logger = setLogger('__main__', LOG_LEVEL, outputFile=join(abspath(dirname(__file__)), 'SampleTest.log'))
sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)

addToDictMutex = Lock()
calibMutex = Lock()
recvDataMutex = Lock()
timerMutex = Lock()

RAW = 'raw'
TIME = 'time'

DEF_NUM_OF_TAGS = 2

PREAMBLE_BYTES = 10
NIBS_IN_BYTE = 2
ADV_ADDR_START = 0
ADV_ADDR_END = 6
CRC_START = 29
# PAYLOAD_START = 8
PAYLOAD_START = 8

CLOUD_TIMEOUT = 10

CSV_FILE_NAME = 'packets.csv'
OUTPUT_DIR = join(abspath(dirname(__file__)), 'logs')

# CONNECT_HW = 'Connect Hw'
# GO = 'Go'
# CONTINUE = 'Continue'

CSV_COLUMNS = ['raw', 'time']
ID_CSV_COLUMNS = ['ext_id', 'chamber']
CSV_DATABASE_COLUMNS = ['timestamp', 'tested', 'passed', 'responding[%]', 'packets', 'testTime[sec]',
                        'ttfpAvg[sec]', 'ttfpStd[sec]', 'ttfpMin[sec]', 'ttfpMax[sec]', 'tbpAvg[sec]',
                        'tbpStd[sec]', 'tbpMin[sec]', 'tbpMax[sec]', 'channel', 'energizing', 'antennaType',
                        'attenBle[db]', 'attenLoRa[db]', 'externalId', 'numberOfChambers', 'gwVersion']

TOKEN_FILE_NANE = '.token.pkl'


class SampleTest(object):
    goButtonState = CONNECT_HW
    comConnect = None
    configsGui = None
    comTtk = None
    configsTtk = None
    testBarcodesThread = None
    finishThread = None
    closeChambersThread = None
    gatewayDataReceive = None
    token = None
    claimSet = None
    timerThread = None
    testFinished = True
    wiliotTags = False
    forceCloseRequested = False
    postState = False
    closeRequested = False
    debug_mode = False
    testGo = False
    testStop = False
    stopTimer = False
    reel_id = ''
    testDir = ''
    owner = ''
    station_name = ''
    testTime = 0
    tagsCount = 0
    packetsCount = 0
    testStartTime = 0
    sleep = 0
    cur_atten = 0
    defaultDict = {}
    packet_dict = {}
    packets_dict = {}
    dataBaseDict = {}
    runDataDict = {}
    params = {}
    barcodesRead = {}
    tagsFinished = {}
    badPreambles = []
    numOfTags = DEF_NUM_OF_TAGS

    def __init__(self, debug_mode=False, calib=None, low=None, high=None, step=None):

        self.calib = calib
        self.low = low
        self.high = high
        self.step = step

        if isfile(join('configs', '.defaults.json')):
            with open(join('configs', '.defaults.json'), 'r') as defaultComs:
                self.defaultDict = load(defaultComs)

        self.check_token()
        self.popup_login()
        self.update_data()
        # self.get_token()

        self.builder = builder = pygubu.Builder()
        self.debug_mode = debug_mode

        self.comConnect = ComConnect(top_builder=builder)
        self.configsGui = ConfigsGui(top_builder=builder)

    def gui(self):
        self.set_gui()

        self.ttk.mainloop()

    def set_gui(self):
        uifile = join(abspath(dirname(__file__)), 'utils', 'sample_test.ui')
        self.builder.add_from_file(uifile)

        img_path = join(abspath(dirname(__file__)), '.')
        self.builder.add_resource_path(img_path)
        img_path = join(abspath(dirname(__file__)), 'utils')
        self.builder.add_resource_path(img_path)

        missing_com_port = self.comConnect.choose_com_ports(self.defaultDict)

        if missing_com_port:
            popup_message('Default com ports not available, check connections.', title='Warning', log='warning')

        self.ttk = Tk()

        self.ttk.eval('tk::PlaceWindow . center')
        self.ttk.title("Wiliot Sample Test")
        self.mainWindow = self.builder.get_object('mainwindow', self.ttk)
        self.ttk.protocol("WM_DELETE_WINDOW", self.close)
        self.builder.connect_callbacks(self)

        configs = self.configsGui.get_configs()
        self.builder.get_object('test_config')['values'] = \
            [key for key, item in configs.items() if isinstance(item, dict)]

        self.set_gui_defaults()

    def go(self):
        if self.finishThread is not None and self.finishThread.is_alive():
            self.finishThread.join()
        self.goButtonState = goButtonState = self.builder.tkvariables.get('go').get()
        self.builder.get_object('go')['state'] = 'disabled'
        self.builder.get_object('forceGo')['state'] = 'disabled'
        self.builder.get_object('stop')['state'] = 'disabled'
        if goButtonState == CONNECT_HW:
            self.connectThread = Thread(target=self.comConnect.connect_all, args=([False]))
            self.connectThread.start()
            # self.comConnect.connect_all(gui=False)
        elif goButtonState == READ:
            if self.tagsCount == 0:
                self.comConnect.reset_test_barcodes()
            indexes = self.get_missing_ids_chambers()
            self.testBarcodesThread = Thread(target=self.comConnect.read_scanners_barcodes, args=([indexes]))
            self.testBarcodesThread.start()
        elif goButtonState == GO:
            self.numOfPackets = 0
            self.total_num_of_unique = 0
            self.avg_unique = 1
            self.badPreambles = []
            self.packets_dict = {}
            self.change_params_state(state='disabled')
            self.barcodesRead = self.comConnect.get_barcodes()
            self.packetsCount = 0
            self.numOfTags = int(self.builder.tkvariables.get('numTags').get())
            self.testId = testId = time.time()
            if not isdir(OUTPUT_DIR):
                makedirs(OUTPUT_DIR)
            self.testDir = testDir = datetime.datetime.fromtimestamp(testId).strftime('%d%m%y_%H%M%S')
            mkdir(join(OUTPUT_DIR, testDir))
            self.common_run_name = common_run_name = self.reel_id + '_' + testDir
            changeFileHandler(logger, join(OUTPUT_DIR, testDir, f'{common_run_name}.log'))
            self.update_params()
            self.testStartTime = time.time()
            if self.calib is not None and self.calib.lower() in ['ble', 'lora']:
                self.calibModeThread = Thread(target=self.calib_mode, args=())
                self.calibModeThread.start()
            else:
                self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
                self.sendCommandThread.start()

        elif goButtonState == CONTINUE:
            self.barcodesRead = self.comConnect.get_barcodes()
            self.change_params_state(state='disabled')
            self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
            self.sendCommandThread.start()

    def get_missing_ids_chambers(self):
        last_barcodes = self.comConnect.get_barcodes()
        indexes = list(range(self.comConnect.get_num_of_barcode_scanners()))
        if len(last_barcodes) > 0:
            used_indexes = list(last_barcodes.values())
            indexes = [index for index in indexes if index not in used_indexes]
        return indexes

    def force_go(self):
        """
        enable go in the GUI even if some of the chambers are empty
        """
        if self.builder.get_variable('forceGo').get() == '1':
            indexes = self.get_missing_ids_chambers()
            self.closeChambersThread = Thread(target=self.comConnect.close_chambers, args=([indexes]))
            self.closeChambersThread.start()
            self.closeChambersThread.join()
            self.builder.tkvariables.get('go').set(GO)
        else:
            self.comConnect.update_go_state()

    def calib_mode(self):
        self.testFinished = False
        attenuations = arange(float(self.low), float(self.high) + float(self.step), float(self.step))
        for i in attenuations:
            calibMutex.acquire()
            self.total_num_of_unique = 0
            self.avg_unique = 1
            self.packet_dict = {}
            self.cur_atten = i
            self.packetsCount = 0
            self.tagsFinished = {}
            self.testGo = True
            if self.calib.lower() == 'ble':
                self.params['attenBle'] = self.cur_atten
                self.dataBaseDict['attenBle[db]'] = self.cur_atten
            elif self.calib.lower() == 'lora':
                self.dataBaseDict['attenLoRa[db]'] = self.cur_atten
                self.params['attenLoRa'] = self.cur_atten
            self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
            self.sendCommandThread.start()
            self.sendCommandThread.join()
            sleep(self.sleep)

        calibMutex.acquire()
        self.calib_mode_post_process()
        self.comConnect.open_chambers()
        self.builder.tkvariables.get('numTags').set(self.numOfTags)
        self.builder.tkvariables.get('go').set(READ)
        self.comConnect.reset_test_barcodes()
        self.builder.get_object('connect')['state'] = 'enabled'
        self.builder.get_object('read_qr')['state'] = 'enabled'
        calibMutex.release()
        popup_message('Sample Test - Calib Mode Finished running.', log='info')

    def calib_mode_post_process(self):

        common_run_name = self.reel_id + '_' + self.testDir
        unique_valid = []
        full_test_dir = join(OUTPUT_DIR, self.testDir)
        with open(join(full_test_dir, f'{common_run_name}@packets_data_calib_mode.csv'), 'w+', newline='') as newCsv, \
             open(join(full_test_dir, f'{common_run_name}@unique_data.csv'), 'w+', newline='') as new_tagsCsv:
            writer = csv.DictWriter(newCsv, fieldnames=['advAddress', 'status', 'rawData', 'attenuation'])
            writer.writeheader()
            for atten, runData in self.packets_dict.items():
                for preamble, data in runData.items():
                    if len(data['packets']) > 0:
                        for packet in data['packets']:
                            packet_raw = packet['raw'].split('(')[1].split(')')[0].strip(' "')
                            tag_row = {
                                       'advAddress':
                                           packet_raw[ADV_ADDR_START * NIBS_IN_BYTE:ADV_ADDR_END * NIBS_IN_BYTE],
                                       'status': 'PASSED',
                                       'rawData': packet,
                                       'attenuation': atten
                                       }
                            writer.writerows([tag_row])

                    unique_valid.append({
                                         'preamble': preamble,
                                         'tbp': data['tbp'],
                                         'ttfp': data['ttfp'],
                                         'ext ID': data['ext ID'],
                                         'reel': data['reel'],
                                         'attenuation': atten
                                         })

            writer = csv.DictWriter(new_tagsCsv, fieldnames=unique_valid[0].keys())
            writer.writeheader()
            writer.writerows(unique_valid)

    def stop(self):
        """
        stop the test and run post process
        """
        if self.testGo:
            self.forceCloseRequested = True
            recvDataMutex.acquire()
            self.forceCloseRequested = False
            recvDataMutex.release()
        if not self.testFinished:
            self.builder.get_object('go')['state'] = 'disabled'
            self.builder.get_object('stop')['state'] = 'disabled'
            self.finishThread = Thread(target=self.finished, args=([True]))
            self.finishThread.start()

    def add(self):
        """
        add manually tag to the list
        """
        self.barcodesRead = self.comConnect.get_barcodes()
        new_tag = self.builder.tkvariables.get('addTag').get()
        if not new_tag.split(',')[0].strip() in self.barcodesRead.keys():
            # self.builder.get_object('scanned').insert(END, new_tag)
            # self.barcodesRead[new_tag.split(',')[0].strip()] = new_tag.split(',')[1].strip()
            # self.comConnect.set_barcodes(self.barcodesRead)
            if len(new_tag.split(',')) < 2:
                popup_message(f'Missing chamber index, add chamber index after a comma.', title='Error', log='error')
                return
            cur_id = new_tag.split(',')[0].strip()
            scan_index = int(new_tag.split(',')[1].strip())
            if (scan_index + 1) > self.comConnect.get_num_of_barcode_scanners():
                popup_message(f'Chamber number {scan_index} not exists.', title='Error', log='error')
                return

            barcodes = self.builder.get_object('scanned').get(0, END)
            if any([barcode for barcode in barcodes if int(barcode.split()[1].strip()) == scan_index]):
                popup_message(f'Chamber {scan_index} tag already scanned.', title='Error', log='error')
                return
            # logger.info(scan_index)

            self.builder.tkvariables.get('addTag').set('')
            popup_thread = Thread(target=popup_message, args=('Chambers are closing!!\nWatch your hands!!!',
                                                              'Warning', ("Helvetica", 18), 'warning'))
            popup_thread.start()
            popup_thread.join()
            self.comConnect.add_tag_to_test(cur_id, self.reel_id, scan_index, close_chamber=True)

        self.comConnect.update_go_state()

    def remove(self):
        """
        remove tag read from the list
        """
        self.barcodesRead = self.comConnect.get_barcodes()
        tag = self.builder.get_object('scanned').get(ACTIVE)
        tags = list(self.builder.get_object('scanned').get(0, END))
        tag_index = tags.index(tag)
        self.builder.get_object('scanned').delete(tag_index, tag_index)
        tags.pop(tag_index)
        self.builder.tkvariables.get('addTag').set(tag)
        self.barcodesRead.pop(tag.split(',')[0].strip())
        self.comConnect.set_barcodes(self.barcodesRead)
        self.comConnect.open_chambers(indexes=[int(tag.split(',')[1].strip())])
        self.comConnect.update_go_state()

    def change_params_state(self, state='disabled'):
        self.builder.get_object('connect')['state'] = state
        self.builder.get_object('configs')['state'] = state
        self.builder.get_object('reelId')['state'] = state
        self.builder.get_object('test_config')['state'] = state
        self.builder.get_object('numTags')['state'] = state if state == 'disabled' else 'normal'
        self.builder.get_object('go')['state'] = state
        self.builder.get_object('add')['state'] = state
        self.builder.get_object('remove')['state'] = state
        self.builder.get_object('read_qr')['state'] = state
        self.builder.get_object('addTag')['state'] = state if state == 'disabled' else 'normal'

    def set_gui_defaults(self):
        self.builder.tkvariables.get('numTags').set(DEF_NUM_OF_TAGS)
        if self.token is None:
            self.builder.get_variable('sendToCloud').set('0')
        else:
            self.builder.get_variable('sendToCloud').set('1')

    def open_configs(self):
        """
        open Configs GUI
        """
        if self.configsGui is not None and not self.configsGui.is_gui_opened():
            self.configsTtk = Toplevel(self.ttk)
            self.ttk.eval(f'tk::PlaceWindow {str(self.configsTtk)} center')
            self.configsGui.gui(self.configsTtk)

    def test_config(self, *args):
        """
        update the configs in Configs module according to the main GUI
        """
        self.configsGui.config_set(self.builder.get_object('test_config').get())

    def open_com_ports(self):
        """
        open ComConnect GUI
        """
        if self.comConnect is not None and not self.comConnect.is_gui_opened():
            self.comTtk = Toplevel(self.ttk)
            self.ttk.eval(f'tk::PlaceWindow {str(self.comTtk)} center')
            self.comConnect.gui(self.comTtk)

    def read_qr(self):
        barcode, reel = self.comConnect.read_barcode()
        # logger.info(barcode)
        if barcode is not None:
            tag_type = self.builder.tkvariables.get('tagType')
            tag_type.set(barcode)
        else:
            read_qr_thread = Thread(target=popup_message, args=(
                [f'Error reading external ID, try repositioning the tag.', 'Error', ("Helvetica", 10), 'error']))
            read_qr_thread.start()
            read_qr_thread.join()
            if self.calib is None:
                return
        if reel is not None:
            reel_id = self.builder.tkvariables.get('reelId')
            reel_id.set(reel)
            self.reel_id = reel
        # self.testId = (barcode[-9:])
        self.tagType = DEFAULT_CONFIG
        self.builder.get_object('test_config').set(self.tagType)
        self.configsGui.set_default_config(self.tagType)
        self.configsGui.set_params(self.tagType)
        self.change_params_state(state='enabled')
        self.builder.get_object('forceGo')['state'] = 'enabled'

    def update_params(self):
        self.params = params = self.configsGui.get_params()
        antenna_type = self.builder.get_object('test_config').get()
        antenna_type = 'TIKI' if 'TIKI' in antenna_type.upper() else 'TEO'
        self.runDataDict['antennaType'] = antenna_type
        self.dataBaseDict['antennaType'] = antenna_type
        self.dataBaseDict['timestamp'] = datetime.datetime.fromtimestamp(self.testId).strftime('%d/%m/%y %H:%M:%S')
        self.dataBaseDict['tested'] = self.builder.get_object('numTags').get()
        self.dataBaseDict['attenBle[db]'] = self.runDataDict['bleAttenuation'] = params['attenBle']
        self.dataBaseDict['attenLoRa[db]'] = self.runDataDict['loraAttenuation'] = params['attenLoRa']
        self.dataBaseDict['channel'] = params['channel']
        # self.dataBaseDict['total time'] = params['tTotal']
        # self.dataBaseDict['on time'] = params['tOn']
        self.dataBaseDict['energizing'] = self.runDataDict['energizingPattern'] = params['pattern']
        self.dataBaseDict['testTime[sec]'] = self.runDataDict['testTime'] = params['testTime']
        # self.dataBaseDict['reel'] = self.builder.tkvariables.get('reelId').get()
        self.dataBaseDict['externalId'] = self.comConnect.get_gtin()
        self.dataBaseDict['numberOfChambers'] = self.comConnect.get_num_of_barcode_scanners()
        self.dataBaseDict['gwVersion'] = self.comConnect.get_gw_version()
        if 'sleep' in params.keys():
            self.sleep = int(params['sleep'])
        else:
            self.sleep = 0
        self.testTime = float(params['testTime'])

    def send_gw_commands(self):
        """
        send commands to the GW and start the packet listener
        """
        if self.sleep > 0:
            for i in range(self.sleep):
                sleep(1)
                if i % 3 == 0:
                    print('.', end='')
            print()
        self.gatewayDataReceive = Thread(target=self.recv_data_from_gw, args=())
        self.gatewayDataReceive.start()
        try:
            self.comConnect.send_gw_app(self.params)
        except:
            print_exc()
        self.testFinished = False

    def recv_data_from_gw(self):
        self.packet_dict = {}
        self.tagsFinished = {}
        self.testGo = True
        self.sendCommandThread.join()
        self.startTime = self.comConnect.get_gw_time()
        last_time = time.time()
        self.targetTime = last_time + self.testTime
        if self.timerThread is not None:
            self.timerThread.join()
        self.timerThread = Thread(target=self.timer_count_down, args=())
        self.timerThread.start()
        add_to_dict_threads = []
        packets_list = []
        recvDataMutex.acquire()
        while time.time() < self.targetTime:
            sleep(0.001)
            try:
                if self.closeRequested or self.forceCloseRequested or not self.comConnect.is_gw_serial_open():
                    logger.info("DataHandlerProcess Stop")
                    self.closeRequested = False
                    break

                if self.comConnect.is_gw_data_available():

                    gw_data = self.comConnect.get_data()

                    if isinstance(gw_data, dict):
                        gw_data = [gw_data]

                    for packet in gw_data:
                        if 'process_packet' in packet['raw']:
                            self.packetsCount += 1
                            packets_list.append(packet)
                            cur_time = time.time()
                            if cur_time - last_time > 2 and len(packets_list) > 0:
                                temp_thread = Thread(target=self.add_to_packet_dict, args=([packets_list.copy()]))
                                temp_thread.start()
                                add_to_dict_threads.append(temp_thread)
                                packets_list = []
                                last_time = cur_time

            except BaseException:
                print_exc()
                pass
            
        timerMutex.acquire()
        self.stopTimer = True
        timerMutex.release()
        self.tagsCount += len(self.barcodesRead.keys())
        for thread in add_to_dict_threads:
            thread.join()
        recvDataMutex.release()
        if self.calib is None and not self.forceCloseRequested:
            self.builder.get_object('stop')['state'] = 'disabled'
            self.finishThread = Thread(target=self.finished, args=())
            self.finishThread.start()
        elif self.calib is not None:
            self.comConnect.cancel_gw_commands()
            self.post_process_iteration()
            self.packets_dict[self.cur_atten] = {}
            self.packets_dict[self.cur_atten].update(self.packet_dict)
            calibMutex.release()

    def timer_count_down(self):
        """
        count down the test time
        """
        while time.time() < self.targetTime:
            if self.stopTimer:
                timerMutex.acquire()
                self.stopTimer = False
                timerMutex.release()
                break
            timer = int(self.targetTime - time.time())
            update_timer_thread = Thread(target=self.update_timer, args=([timer]))
            update_timer_thread.start()
            update_timer_thread.join()
            sleep(1)
        self.builder.tkvariables.get('testTime').set(str(self.testTime))

    def update_timer(self, timer):
        """
        update timer value in the GUI
        :type timer: int
        :param timer: remaining time to the test
        """
        self.builder.tkvariables.get('testTime').set(str(timer))

    def add_to_packet_dict(self, packets):
        addToDictMutex.acquire()
        for packet in packets:
            packet_raw = packet['raw'].split('(')[1].split(')')[0].strip(' "')
            preamble = packet_raw[:PREAMBLE_BYTES * NIBS_IN_BYTE]
            self.numOfPackets += 1
            if preamble not in self.packet_dict.keys() and preamble not in self.badPreambles:
                cur_id = None
                reel_id = None
                full_data = None
                if self.token is not None:
                    full_data, cur_id, reel_id, gtin = self.get_packet_ext_id(packet, owner=self.owner)

                if self.token is not None and (cur_id is not None or self.debug_mode is not None)\
                        and full_data not in self.comConnect.get_barcodes().keys():
                    logger.info(
                        f'Tag with preamble {preamble} and external ID {cur_id} detected but not belong to the test.')
                    self.badPreambles.append(preamble)
                    addToDictMutex.release()
                    return

                logger.info(f'New Tag detected with preamble: {preamble}')

                self.packet_dict[preamble] = {}
                self.packet_dict[preamble]['packets'] = []
                self.packet_dict[preamble]['ttfp'] = -1
                self.packet_dict[preamble]['tbp'] = -1
                self.packet_dict[preamble]['ext ID'] = cur_id
                self.packet_dict[preamble]['reel'] = reel_id
                self.packet_dict[preamble]['unique'] = {}

            if preamble in self.badPreambles:
                continue

            else:
                if not packet_raw[:-5] in self.packet_dict[preamble]['unique'].keys():
                    self.packet_dict[preamble]['unique'][packet_raw[:-5]] = []
                self.packet_dict[preamble]['unique'][packet_raw[:-5]].append(packet)
                self.packet_dict[preamble]['packets'].append(packet)

                if len(self.packet_dict[preamble]['unique'][packet_raw[:-5]]) > 3:
                    self.tagsFinished[preamble] = True

                if len(self.tagsFinished.keys()) >= self.comConnect.get_num_of_barcode_scanners():
                    self.closeRequested = True
        addToDictMutex.release()

    def finished(self, force_finish=False):
        self.testGo = False
        self.comConnect.add_to_test_barcodes(self.barcodesRead)
        self.comConnect.cancel_gw_commands()
        self.comConnect.open_chambers()
        avg_unique, avg_tbp, avg_ttfp = self.post_process_iteration()
        self.packets_dict.update(self.packet_dict)

        if self.tagsCount < self.numOfTags and not force_finish:
            self.builder.tkvariables.get('go').set(READ)
            self.builder.tkvariables.get('numTags').set(self.numOfTags - self.tagsCount)
            self.builder.get_object('go')['state'] = 'enabled'
            self.builder.get_object('add')['state'] = 'enabled'
            self.builder.get_object('remove')['state'] = 'enabled'
            self.builder.get_object('addTag')['state'] = 'normal'
            self.builder.get_object('stop')['state'] = 'enabled'
            self.builder.get_object('forceGo')['state'] = 'enabled'
            self.builder.tkvariables.get('addTag').set('')
            if len(self.packet_dict.keys()) > 0:
                popup_message(f'Average TTFP: {avg_ttfp:.2f}\n'
                              f'Average Unique: {avg_unique:.2f}\n'
                              f'Average TBP: {avg_tbp:.2f}\n'
                              f'Replace tags and click on "Read"',
                              title='info', log='info')
        else:
            self.finishThread = Thread(target=self.finish_test, args=())
            self.finishThread.start()

    def post_process_iteration(self):
        total_num_of_unique = 0
        avg_unique = 1
        for preamble, packets in self.packet_dict.items():
            for raw, data in packets['unique'].items():
                times_list = []
                packets_list = []
                tbp_list = []
                sorted_packets = sorted(data, key=lambda d: d['time'])
                last_time = 0
                # logger.info(preamble)
                num_unique = 1
                for packet in sorted_packets:
                    packets_list.append(packet['raw'])
                    times_list.append(packet['time'])
                    cur_time = float(packet['time'])
                    tbp = cur_time - last_time
                    if last_time != 0:
                        # logger.info(f'{tbp}')
                        num_unique += 1
                        tbp_list.append(float_precision(tbp))

                    last_time = cur_time

                    if self.packet_dict[preamble]['ttfp'] > cur_time or self.packet_dict[preamble]['ttfp'] == -1:
                        self.packet_dict[preamble]['ttfp'] = cur_time

                if num_unique >= 4 and self.packet_dict[preamble]['tbp'] == -1:
                    if not self.comConnect.gw_tbp_version():
                        tbp = min(tbp_list)
                        self.packet_dict[preamble]['tbp'] = tbp
                    else:
                        tbp = estimate_diff_packet_time(packets_list, times_list)
                        if len(tbp) > 1:
                            self.packet_dict[preamble]['tbp'] = min(tbp[1:]) * (10 ** (-3))

                avg_unique = ((avg_unique * total_num_of_unique) + num_unique) / (total_num_of_unique + 1)
                total_num_of_unique += 1

        if self.total_num_of_unique == 0 and total_num_of_unique == 0:
            self.avg_unique = -1
        else:
            self.avg_unique = (((self.avg_unique * self.total_num_of_unique) + (avg_unique * total_num_of_unique)) /
                               (self.total_num_of_unique + total_num_of_unique))
        self.total_num_of_unique = self.total_num_of_unique + total_num_of_unique

        avg_tbp = 0
        average_ttfp = 0
        tbp_count = 0
        count = 0
        for preamble, data in self.packet_dict.items():
            count += 1
            if data['tbp'] != -1:
                tbp_count += 1
                avg_tbp = ((avg_tbp * (tbp_count - 1) + data['tbp']) / tbp_count)
            average_ttfp = ((average_ttfp * (count - 1)) + data['ttfp']) / count

        return avg_unique, avg_tbp, average_ttfp

    def finish_test(self):
        unique_valid = self.post_process(self.packets_dict)

        test_barcodes = self.comConnect.get_test_barcodes()
        pass_fail = ((len(self.packets_dict.keys()) / len(test_barcodes.keys())) * 100) >= \
                    int(self.params['respondingMu'])
        bg_color = 'green' if pass_fail else 'red'
        pass_fail = 'Passed' if pass_fail else 'Failed'

        avg_ttfp = self.dataBaseDict['ttfpAvg[sec]']
        avg_tbp = self.dataBaseDict['tbpAvg[sec]'] if 'tbpAvg[sec]' in self.dataBaseDict.keys() else -1

        self.files_and_cloud(unique_valid)

        self.tagsCount = 0
        self.builder.tkvariables.get('numTags').set(self.numOfTags)
        self.builder.tkvariables.get('go').set(READ)
        self.comConnect.reset_test_barcodes()
        self.builder.get_object('connect')['state'] = 'enabled'
        self.builder.get_object('read_qr')['state'] = 'enabled'
        self.builder.get_object('forceGo')['state'] = 'disabled'
        self.builder.get_object('stop')['state'] = 'disabled'
        self.builder.get_object('go')['state'] = 'disabled'
        self.testFinished = True
        popup_message(f'Test has {pass_fail}\n' +
                      f'Average TTFP: {avg_ttfp} [sec]\n' +
                      f'Average unique packets: {self.avg_unique:.2f} [packets]\n' +
                      f'Average time between packets: {avg_tbp} [sec]', title='Finished test', bg=bg_color, log='info')

    def files_and_cloud(self, unique_valid):
        self.runDataDict['testerStationName'] = self.station_name
        self.runDataDict['commonRunName'] = self.common_run_name
        self.runDataDict['testerType'] = 'sample'
        self.runDataDict['gwVersion'] = self.comConnect.get_gw_version()

        run_data_path = abspath(join(OUTPUT_DIR, self.testDir, f'{self.common_run_name}@run_data.csv'))
        run_csv = CsvLog(HeaderType.RUN, run_data_path, tester_type=TesterName.SAMPLE)
        run_csv.open_csv()
        run_csv.append_dict_as_row([self.runDataDict])

        post_run_success = self.post_data(run_data_path, destination='runs-indicators')

        tags_data_path = abspath(join(OUTPUT_DIR, self.testDir, f'{self.common_run_name}@packets_data.csv'))
        packets_csv = CsvLog(HeaderType.PACKETS, tags_data_path, tester_type=TesterName.SAMPLE)
        packets_csv.open_csv()

        for preamble, data in self.packets_dict.items():
            if len(data['packets']) > 0:
                for packet in data['packets']:
                    tag_row = {'commonRunName': self.common_run_name,
                               'encryptedPacket': packet['raw'],
                               'time': packet['time'],
                               'externalId': data['ext ID']}
                    packets_csv.append_dict_as_row([tag_row])

        if post_run_success:
            post_tags_success = self.post_data(tags_data_path, destination='packets-indicators')
            if not post_tags_success:
                popup_message(f'Failed uploading tags data, Upload manually:\n' +
                              f'{self.common_run_name}@packets_data.csv.', log='warning')
        else:
            popup_message(f'Failed uploading run and tags data, Upload manually:\n' +
                          f'{self.common_run_name}@run_data.csv\n' +
                          f'{self.common_run_name}@packets_data.csv', log='warning')

        if len(unique_valid) > 0:
            with open(join(OUTPUT_DIR, self.testDir, f'{self.common_run_name}@tags_data.csv'), 'w+', newline='')\
                    as newCsv:
                writer = csv.DictWriter(newCsv, fieldnames=unique_valid[0].keys())
                writer.writeheader()
                writer.writerows(unique_valid)

        with open(join(OUTPUT_DIR, self.testDir, f'{self.common_run_name}@configs_data.csv'), 'w+', newline='')\
                as newCsv:
            writer = csv.DictWriter(newCsv, fieldnames=CSV_DATABASE_COLUMNS)
            writer.writeheader()
            writer.writerows([self.dataBaseDict])

        with open(join(OUTPUT_DIR, self.testDir, f'{self.common_run_name}@ext_ids_data.csv'), 'w+', newline='')\
                as newCsv:
            writer = csv.DictWriter(newCsv, fieldnames=ID_CSV_COLUMNS)
            writer.writeheader()
            ids_dict = self.comConnect.get_test_barcodes()
            temp_dict = []
            for tagId, chamber in ids_dict.items():
                temp_dict.append({'ext_id': tagId, 'chamber': chamber})
            writer.writerows(temp_dict)

    def get_packet_ext_id(self, packet, owner='wiliotmnf'):
        """
        get external ID of a tag by sending an example packet to the cloud.
        :type packet: dict
        :param packet: contains the raw and time of the packet.
        :type owner: string
        :param owner: owner of the tag (wiliot, wiliotmnf, wiliot-ops).
        :return: external ID of the tag, and the external ID parsed when it's wiliot tag.
        """
        conn = http.client.HTTPSConnection("api.wiliot.com")

        packet_time = packet['time']
        packet_raw = packet['raw'].split('(')[1].split(')')[0].strip(' "')
        packet_payload = packet_raw[PAYLOAD_START * NIBS_IN_BYTE:]
        packet_payload = packet_payload[: CRC_START * NIBS_IN_BYTE]
        # logger.info(packet_raw)
        # logger.info(packet_payload)

        payload = '{\"gatewayType\":\"Manufacturing\",\"gatewayId\":\"manufacturing-gateway-id\",\"timestamp\":'\
                  + str(time.time())\
                  + ',\"packets\":[{\"timestamp\":'\
                  + str(packet_time * (10 ** 6))\
                  + ',\"payload\":\"'\
                  + packet_payload\
                  + '\"}]}'

        headers = {
            'accept': "application/json",
            'authorization': "Bearer " + self.token + "",
            'content-type': "application/json"
        }

        conn.request("POST", f"/v1/owner/{owner}/resolve", payload, headers)

        res = conn.getresponse()
        data = res.read()

        data = loads(data.decode("utf-8"))
        # logger.info(data)

        cur_id = reel_id = gtin = full_data = None

        if 'externalId' in data['data'][0].keys() and data['data'][0]['externalId'] != 'unknown':
            full_data = data['data'][0]['externalId']
            cur_id = reel_id = gtin = full_data
            # try:
            #     gtin = ')'.join(full_data.split(')')[:2]) + ')'
            #     tag_data = full_data.split(')')[2]
            #     cur_id = tag_data.split('T')[1].strip("' ")
            #     reel_id = tag_data.split('T')[0].strip("' ")
            # except:
            #     pass
        return full_data, cur_id, reel_id, gtin

    def post_data(self, file_path, destination, environment='test'):
        """
        post file to the cloud
        :type file_path: string
        :param file_path: the path to the uploaded file
        :type destination: string
        :param destination: the destination in the cloud (runs-indicators, packets-indicators)
        :type environment: string
        :param environment: the environment in the cloud (dev, test, prod, etc.)
        :return: bool - True if succeeded, False otherwise
        """
        try:
            if self.token is not None:
                url = f'https://api.wiliot.com/{environment}' \
                      f'/v1/manufacturing/upload/testerslogs/sample-test/{destination}'
                payload = {}
                files = [
                  ('file', (basename(file_path), open(file_path, 'rb'), 'text/csv'))
                ]
                headers = {
                  'Authorization': f'Bearer {self.token}'
                }
                response = requests.request("POST", url, headers=headers, data=payload, files=files,
                                            timeout=CLOUD_TIMEOUT)
                logger.info(response.text)
                data = loads(response.text)
                if 'data' not in data.keys() or 'success' not in data['data']:
                    self.postState = False
                self.postState = True
                return self.postState
        except:
            return False

    def post_process(self, packets_dict):
        num_of_answered = len(packets_dict.keys())
        self.dataBaseDict['packets'] = self.numOfPackets
        self.dataBaseDict['tested'] = self.runDataDict['tested'] = self.tagsCount
        self.dataBaseDict['passed'] = self.runDataDict['passed'] = num_of_answered
        self.dataBaseDict['responding[%]'] = self.runDataDict['yield'] = f'{int((num_of_answered/self.tagsCount)*100)}'\
                                                                         + '%'

        ttfp_arr = [packet['ttfp'] for packet in packets_dict.values()]
        avg_ttfp = sum(ttfp_arr) / num_of_answered if num_of_answered > 0 else -1
        ttfp_arr = ttfp_arr if len(ttfp_arr) > 0 else [-1]
        self.dataBaseDict['ttfpStd[sec]'] = f'{numpy.std(ttfp_arr):.2f}'
        self.dataBaseDict['ttfpAvg[sec]'] = f'{avg_ttfp:.2f}'
        self.dataBaseDict['ttfpMin[sec]'] = f'{min(ttfp_arr):.2f}'
        self.dataBaseDict['ttfpMax[sec]'] = self.runDataDict['maxTtfp'] = f'{max(ttfp_arr):.2f}'

        tbp_arr = []
        unique_valid = []
        for preamble, packet in packets_dict.items():
            if packet['tbp'] != -1:
                tbp_arr.append(packet['tbp'])
            unique_valid.append({'preamble': preamble,
                                 'tbp': f"{ packet['tbp']:.2f}",
                                 'ttfp': f"{packet['ttfp']:.2f}",
                                 'ext ID': f"{packet['ext ID']}",
                                 'reel': f"{packet['reel']}"})
        if len(tbp_arr) > 0:
            self.dataBaseDict['tbpStd[sec]'] = f'{numpy.std(tbp_arr):.2f}'
            avg_tbp = sum(tbp_arr) / len(tbp_arr)
            self.dataBaseDict['tbpAvg[sec]'] = f'{avg_tbp:.2f}'
            self.dataBaseDict['tbpMin[sec]'] = f'{min(tbp_arr):.2f}'
            self.dataBaseDict['tbpMax[sec]'] = f'{max(tbp_arr):.2f}'
        return unique_valid

    def reset(self):
        """
        reset the tester (fully available only when running from bat file)
        """
        if popup_yes_no():
            self.ttk.destroy()
            _exit(1)
        else:
            pass

    def close(self):
        """
        close the gui and destroy the test
        """
        self.ttk.destroy()
        _exit(0)

    def update_data(self):
        """
        update station name and owner in json file, for future usage.
        """
        temp_coms = {}
        if isfile(join('configs', '.defaults.json')):
            with open(join('configs', '.defaults.json'), 'r') as defaultComs:
                temp_coms = load(defaultComs)
        if self.station_name.strip() != '':
            temp_coms['stationName'] = self.station_name
        if self.owner.strip() != '':
            temp_coms['owner'] = self.owner
        with open(join('configs', '.defaults.json'), 'w+') as defaultComs:
            dump(temp_coms, defaultComs, indent=4)

    def popup_login(self):
        """
        popup to insert fusion auth credentials, and choosing owner.
        """
        default_font = ("Helvetica", 10)
        popup = Tk()
        popup.eval('tk::PlaceWindow . center')
        popup.wm_title('Login')

        def quit_tester():
            popup.destroy()
            _exit(0)

        popup.protocol("WM_DELETE_WINDOW", quit_tester)

        def update_owner():
            owners = list(self.claimSet['owners'].keys())
            c1['values'] = owners
            c1['state'] = 'enabled'
            if 'owner' in self.defaultDict.keys() and self.defaultDict['owner'] in owners:
                def_owner = self.defaultDict['owner']
            else:
                def_owner = owners[0]
            c1.set(def_owner)
            b3['state'] = 'active'

        def login():
            logger.info('Requesting token...')
            username = e1.get()
            password = e2.get()
            if username.strip() != '' and password.strip() != '':
                environ['FUSION_AUTH_USER'] = username
                environ['FUSION_AUTH_PASSWORD'] = password
                # logger.info(username)
                # logger.info(password)
            self.get_token()
            if self.token is not None:
                update_owner()
            # popup.destroy()

        def ok():
            self.owner = c1.get()
            self.station_name = e3.get()
            popup.destroy()

        if self.token is None:
            l1 = Label(popup, text='Enter FusionAuth User-Name and Password:', font=default_font)
            l1.grid(row=1, column=0, padx=10, pady=10, columnspan=3)
            l2 = Label(popup, text='Username:', font=default_font)
            l2.grid(row=2, column=0, padx=10, pady=10)
            e1 = Entry(popup)
            e1.grid(row=2, column=1, padx=10, pady=5)
            l3 = Label(popup, text='Password:', font=default_font)
            l3.grid(row=3, column=0, padx=10, pady=10)
            e2 = Entry(popup, show='*')
            e2.grid(row=3, column=1, padx=10, pady=5)
            b1 = Button(popup, text="Quit", command=quit_tester, height=1, width=10)
            b1.grid(row=4, column=0, padx=10, pady=10)
            b2 = Button(popup, text="Login", command=login, height=1, width=10)
            b2.grid(row=4, column=2, padx=10, pady=10)
        else:
            l1 = Label(popup, text='Choose owner and station name:', font=default_font)
            l1.grid(row=1, column=0, padx=10, pady=10, columnspan=3)
        l4 = Label(popup, text='Owner:', font=default_font)
        l4.grid(row=5, column=0, padx=10, pady=10)
        c1 = ttk.Combobox(popup, state='disabled')
        c1.grid(row=5, column=1, padx=10, pady=15)
        l5 = Label(popup, text='Station Name:', font=default_font)
        l5.grid(row=6, column=0, padx=10, pady=10)
        e3 = Entry(popup)
        if 'stationName' in self.defaultDict.keys():
            e3.insert(0, self.defaultDict['stationName'])
        e3.grid(row=6, column=1, padx=10, pady=5)
        b3 = Button(popup, text="OK", command=ok, height=1, width=10)
        b3.grid(row=7, column=1, padx=10, pady=10)

        if self.claimSet is not None:
            update_owner()

        popup.mainloop()

    def get_token(self):
        """
        get new token using username and password stored in environment variables
        :return: the new token
        """
        try:
            username = environ.get('FUSION_AUTH_USER')
            username = quote(username)
            password = environ.get('FUSION_AUTH_PASSWORD')
            password = quote(password)
            conn = http.client.HTTPSConnection("api.wiliot.com")
            headers = {'accept': "application/json"}
            conn.request("POST", "/v1/auth/token?password=" + password + "&username=" + username, headers=headers)
            res = conn.getresponse()
            data = res.read()
            tokens = loads(data.decode("utf-8"))
            # logger.info(tokens)
            self.token = token = tokens['access_token']
            self.claimSet = jwt.decode(token, options={"verify_signature": False})
            self.save_token(tokens)
            logger.info('Token received successfully.')
            # logger.info(token)
        except:
            self.token = None
            logger.error('Could not generate token, check username and password.')
            token = None
        return token

    def check_token(self):
        """
        upload the last token from pickle file, check its status
        if the token is outdated and the refresh token still alive, refresh the token.
        """
        if isfile(join('configs', TOKEN_FILE_NANE)):
            f = open(join('configs', TOKEN_FILE_NANE), "rb")
            token = pickle.load(f)
            f.close()
            if (datetime.datetime.now() - token['issue_date']).days < 1\
                    and (datetime.datetime.now() - token['issue_date']).seconds < 6 * 60 * 60:
                self.token = token['access_token']
                self.claimSet = jwt.decode(token['access_token'], options={"verify_signature": False})
                logger.info('Token loaded successfully.')
            elif (datetime.datetime.now() - token['issue_date']).days < 7:
                self.refresh_token(token['refresh_token'])

    def refresh_token(self, refresh_token):
        """
        refresh the token if the token is less than week old.
        :type refresh_token: string
        :param refresh_token: the refresh token of the last token generated.
        :return: the new token
        """
        try:
            conn = http.client.HTTPSConnection("api.wiliot.com")
            headers = {'accept': "application/json"}
            conn.request("POST", "/v1/auth/refresh?refresh_token=" + refresh_token, headers=headers)
            res = conn.getresponse()
            data = res.read()
            tokens = loads(data.decode("utf-8"))
            self.save_token(tokens)
            # logger.info(tokens)
            self.token = token = tokens['access_token']
            self.claimSet = jwt.decode(token, options={"verify_signature": False})
            logger.info('Token refreshed successfully.')
            # logger.info(token)
        except:
            # print_exc()
            self.token = None
            logger.info('Could not refresh token.')
            token = None
        return token

    def save_token(self, token):
        token['issue_date'] = datetime.datetime.now()
        pickle.dump(token, open(join('configs', TOKEN_FILE_NANE), "wb"))


def popup_yes_no():
    root = Tk()
    root.wm_withdraw()
    result = messagebox.askquestion("Sample Test", "Reset Sample Test?", icon='warning')
    root.destroy()
    if result == 'yes':
        return True
    else:
        return False


def float_precision(num, prec=2):
    dot_pos = str(num).index('.')
    first_idx = [i for i in range(len(str(num))) if str(num)[i] != '0' and str(num)[i] != '.']
    first_idx = first_idx[0] if first_idx[0] > 0 else first_idx[0] + 1
    after_dot = first_idx - dot_pos + prec
    if after_dot > 0:
        eval_str = '{:.%sf}' % (str(first_idx - dot_pos + prec))
    else:
        eval_str = '{:.0f}'
    return float(eval_str.format(num))


if __name__ == '__main__':
    calib = None
    low = None
    high = None
    step = None

    parser = argparse.ArgumentParser(description='Run PixieParser')
    parser.add_argument('-d', '--debug', action='store_true', default='False', help='Debug mode')
    parser.add_argument('-c', '--calib', help='Calibration mode, attenuator type')
    parser.add_argument('-low', '--low', help='lower value of attenuation')
    parser.add_argument('-high', '--high', help='higher value of attenuation')
    parser.add_argument('-step', '--step', help='attenuation step')
    args = parser.parse_args()
    if args.calib is not None and (args.calib is None or args.low is None or args.high is None or args.step is None):
        logger.info('Warning - Missing values for calibration mode.')
    # Run the UI
    app_folder = abspath(join(dirname(__file__), '..'))
    try:
        sampleTest = SampleTest(debug_mode=args.debug, calib=args.calib, low=args.low, high=args.high, step=args.step)
        sampleTest.gui()
    except BaseException:
        print_exc()
    sys.exit(0)
