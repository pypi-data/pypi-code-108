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
# import os
import sys
from os.path import exists, isfile, abspath, dirname, join
from os import environ
from shutil import copyfile
sys.path.append(abspath(dirname(join('..', '..', 'gateway_api'))))
from threading import Event
import logging
import PySimpleGUI as sg
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import pyqtgraph as pg
from serial.tools import list_ports
from wiliot.gateway_api.gateway import *
from wiliot.wiliot_testers.tester_utils import *
import threading
import pickle
import datetime
from time import sleep
from traceback import print_exc
from json import load
from wiliot.wiliot_testers.tester_utils import CsvLog

plt.switch_backend('agg')
import serial
# from wiliot_testers.conversion.R2R_utils import *

tested = 0
passed = {}
reel_name = ''
printingLock = threading.Lock()
loggingLock = threading.Lock()
passed_uniquesLock = threading.Lock()

PREAMBLE_BYTES = 5
NIBS_IN_BYTE = 2
ADV_ADDR_START = 7
ADV_ADDR_END = 13

WILIOT_APP_DATA = 'wiliot'
YIELD_TEST_DIR = 'yield'
YIELD_TEST_APP_DATA = join(environ['LOCALAPPDATA'], WILIOT_APP_DATA, YIELD_TEST_DIR)

if not exists(YIELD_TEST_APP_DATA):
    os.makedirs(YIELD_TEST_APP_DATA)

RESTORE_GW = 'Restore GW'
UPDATE_GW = 'Update GW'
CANCEL = 'Cancel'

GW_VERSIONS_FILE = '.gwVersions'


def get_ports_of_GWs():
    ports = list(list_ports.comports())
    GWs_ports = []
    for p in ports:
        print(p)
        if 'USB to UART Bridge' in str(p):
            GWs_ports.append(p.device)
            print(GWs_ports)
    return GWs_ports


def get_ports_of_arduino():
    ports = list(list_ports.comports())
    arduino_ports = []
    for p in ports:
        print(p)
        if 'USB Serial Device' in str(p) or 'Arduino NANO Every' in str(p):
            arduino_ports.append(p.device)
            print(arduino_ports)
    return arduino_ports


def saveScreen4Tester(unconverted_reel_tags_num, reel_name=''):
    filename = '.post_run_gui_inputs_do_not_delete.p'
    file_exists = isfile(join(YIELD_TEST_APP_DATA, filename))

    if file_exists:
        f = open(join(YIELD_TEST_APP_DATA, filename), "rb")
        js = pickle.load(f)
        f.close()

    default_values = {}
    # setting the values from previous runs
    try:
        if js['comments'] is not None:
            default_values['comments'] = js['comments']
        else:
            default_values['comments'] = ''
    except:
        default_values['comments'] = ''
    try:
        if js['reel_name'] is not None and reel_name == '':
            default_values['reel_name'] = js['reel_name']
        else:
            default_values['reel_name'] = reel_name
    except:
        default_values['reel_name'] = reel_name
    layout = [
        # [sg.Text('Would you like to upload this log to the cloud?'), sg.InputCombo(('Yes', 'No'), default_value="Yes", key='upload')],
        [sg.Text('Post run comments:')],
        [sg.InputText(default_values['comments'], key='comments')]]

    for ii in range(len(unconverted_reel_tags_num)):
        if ii == 1: ending = 'st'
        elif ii == 2: ending = 'nd'
        else: ending = 'th'
        layout.append([sg.Text('Unconverted reel tested ' + str(ii) + ending + ' tested tags number:')])
        layout.append([sg.InputText(default_values['reel_name'], key=str(ii) + 'reel_name')])

    layout.append([sg.Submit()])

    window = sg.Window('R2R', layout)
    event, values = window.read()
    window.close()
    pickle.dump(values, open(join(YIELD_TEST_APP_DATA, filename), "wb"))
    return values


def openSession(comPortObjs):
    guiInputsFile = '.IFT_gui_inputs_do_not_delete.p'

    js = {}
    file_exists = isfile(join(YIELD_TEST_APP_DATA, guiInputsFile))
    if file_exists:
        f = open(join(YIELD_TEST_APP_DATA, guiInputsFile), "rb")
        js = pickle.load(f)
        f.close()

    default_values = {}
    # setting the values from previous runs
    try:
        if js['reel_name'] is not None:
            default_values['reel_name'] = js['reel_name']
        else:
            default_values['reel_name'] = 'No'
    except:
        default_values['reel_name'] = 'No'
    try:
        if js['tags_num'] is not None:
            default_values['tags_num'] = js['tags_num']
        else:
            default_values['tags_num'] = '0'
    except:
        default_values['tags_num'] = '0'
    try:
        if js['inlay'] is not None:
            default_values['inlay'] = js['inlay']
        else:
            default_values['inlay'] = '076'
    except:
        default_values['inlay'] = '076'
    try:
        if js['rows'] is not None:
            default_values['rows'] = js['rows']
        else:
            default_values['rows'] = '1'
    except:
        default_values['rows'] = '1'

    gwOldVersions = {}
    if isfile(join(YIELD_TEST_APP_DATA, GW_VERSIONS_FILE)):
        gwOldVersions = pickle.load(open(join(YIELD_TEST_APP_DATA, GW_VERSIONS_FILE), "rb"))

    version = ''
    for port, gw in comPortObjs.items():
        curVer = gw['serial'].get_gw_version()[0]
        version = version if version != '' else curVer
        if version != curVer:
            gw_versions_popup()
            break

    layout = [
        [sg.Text('Reel Name when done:', font=4)],
        [sg.InputText(default_values['reel_name'], key='reel_name', font=4)],
        [sg.Text('Expected amount of tags:', font=4)],
        [sg.InputText(default_values['tags_num'], key='tags_num', font=4)],
        [sg.Text('Inlay:', font=4)],
        [sg.InputText(default_values['inlay'], key='inlay', font=4)],
        [sg.Text('Number of rows:', font=4)],
        [sg.InputText(default_values['rows'], key='rows', font=4)],
        [sg.Text('Dual/Single Band:', font=4)],
        [sg.Column([[sg.Combo(['Dual Band', 'Single Band'], key='band', font=4, default_value='Dual Band')]], vertical_alignment='center', justification='center', k='-C-')],
        [sg.Column([[sg.Button('Advanced', font=4)]], vertical_alignment='center', justification='center')],
        [sg.Submit()]]

    window = sg.Window('Settings', layout, keep_on_top=True)
    while True:
        event, values = window.read()
        if event == 'Advanced':
            update_gateway_popup(comPortObjs, gwOldVersions)
        elif event == 'Submit':
            break
        elif event == None:
            window.close()
            exit()
    window.close()
    new_path = join(YIELD_TEST_APP_DATA, 'logs', str(values['reel_name']))
    common_run_name = values['reel_name'] + str(time.time())
    tag_file_name = join(new_path, common_run_name + '@total_yield_tester@tags_data.csv')
    run_file_name = join(new_path, common_run_name + '@total_yield_tester@run_data.csv')
    log_path = join(new_path, common_run_name + '@total_yield_tester.log')
    packetsCsv = CsvLog(HeaderType.TAG, join(YIELD_TEST_APP_DATA, tag_file_name))
    packetsCsv.open_csv()
    runCsv = CsvLog(HeaderType.RUN, join(YIELD_TEST_APP_DATA, run_file_name))
    runCsv.open_csv()
    logging.basicConfig(filename=log_path, filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S', level=logging.DEBUG)
    pickle.dump(values, open(join(YIELD_TEST_APP_DATA, guiInputsFile), "wb"))
    values['common_run_name'] = common_run_name
    return values, packetsCsv, runCsv


def update_gateway_popup(comPortObjs, oldVersions):
    layout = []
    curVersions = {}
    for port, gw in comPortObjs.items():
        oldVersion = ''
        curVersions[port] = gw['serial'].get_gw_version()[0]
        if port in oldVersions.keys():
            oldVersion = oldVersions[port]
        latestVersion = gw['serial'].get_latest_version_number()[0]
        layout.append(
        [sg.Column([[sg.Text(f"Gateway Current version: {curVersions[port]}\nGateway Last version: {oldVersion}\nGateway Newest version: {latestVersion}", font=4)]], vertical_alignment='center', justification='center'),
        sg.Column([[sg.InputText('enter version', size=(15, 1), key=port + '_version', font=4)]], vertical_alignment='center', justification='center'),
        sg.Column([[sg.Button(UPDATE_GW, font=4, key=port)]], vertical_alignment='center', justification='center')])
    layout.append(
    [sg.Column([[sg.Button(CANCEL, font=4)]], vertical_alignment='center', justification='center')]
    )
    window = sg.Window('Settings', layout, keep_on_top=True)
    while True:
        event, values = window.read()
        if event != None and event != CANCEL:
            port = event
            version = values[port + '_version'].strip()
            updateGw = warning_popup(port, version)
            if updateGw:
                if version != curVersions[port]:
                    oldVersions[port] = curVersions[port]
                    print(f'Update GW on port {port} to version {version}')
                    # comPortObjs[port]['serial'].update_version(version)
        else:
            break
    pickle.dump(oldVersions, open(join(YIELD_TEST_APP_DATA, GW_VERSIONS_FILE), 'wb'))
    window.close()
    return event, values


def warning_popup(port, version):
    layout = [[
        sg.Column([[sg.Text(f"Are you sure you want to update Gateway {port} to version {version}?", font=4)]], vertical_alignment='center', justification='center')],
        [sg.Column([[sg.Button('No', font=4)]], vertical_alignment='center', justification='center'),
        sg.Column([[sg.Button('Yes', font=4)]], vertical_alignment='center', justification='center')
        ]]
    window = sg.Window('Settings', layout, keep_on_top=True)
    event, values = window.read()
    window.close()
    return event == 'Yes'


def gw_versions_popup():
    layout = [[
        sg.Column([[sg.Text(f"Gateways versions not identical, update via 'Advanced'.", font=4)]], vertical_alignment='center', justification='center')],
        [sg.Column([[sg.Button('Okay', font=4)]], vertical_alignment='center', justification='center')
        ]]
    window = sg.Window('Settings', layout, keep_on_top=True)
    event, values = window.read()
    window.close()


def conclusion(yield_):
    if yield_ > 20:
        layout = [
            [sg.Text('Yield = ' + str(yield_) + '%', font=4)],
            [sg.Text('Good job!!', font=4)],
            [sg.Exit()]]
        sg.ChangeLookAndFeel('Green')

    else:
        layout = [
            [sg.Text('Yield = ' + str(yield_) + '%', font=4)],
            [sg.Text('Please update Wiliot', font=4)],
            [sg.Exit()]]
        sg.ChangeLookAndFeel('DarkRed')

    window2 = sg.Window('Conclusion', layout)
    event, values = window2.read()
    window2.close()


class RunThread(threading.Thread):

    def __init__(self, comPortObj, port, baud, stop: Event, tags_num, reel_name, tester_name, passed_uniques, inlay, band='Dual Band', common_run_name='', tags_csv_log=None, run_csv_log=None):
        super(RunThread, self).__init__()
        self.comPortObj = comPortObj
        self.port = port
        self.baud = baud
        self.stop = stop
        self.tags_num = tags_num
        self.reel_name = reel_name
        self.tester_name = tester_name
        self.passed_uniques = passed_uniques
        self.inlay = inlay
        self.band = band
        self.common_run_name = common_run_name
        self.tags_csv_log = tags_csv_log
        self.run_csv_log = run_csv_log
        self.packets = []

        configs = self.get_configs(band)
        gwAppCmd = f"!gateway_app {configs['channel']} {configs['tTotal']} {configs['tOn']} {configs['energizingChannel']} {configs['numOfChannels']} {configs['rxChannel']}\r\n"
        self.GWconfig = bytes(gwAppCmd, encoding='utf-8')
        # self.GWconfig = b'!gateway_app 37 15 5 2480 0 2480\r\n'

    def get_configs(self, band):
        configs_file = join(YIELD_TEST_APP_DATA, '.default_configs.json')
        if not isfile(configs_file):
            copyfile(join('configs','.default_configs.json'), configs_file)
        with open(configs_file, 'r') as defJson:
            bandsDict = load(defJson)
            if bandsDict.get(band):
                configs = self.configs = bandsDict[band]
                return configs
            else:
                print(f'Error - {band} missing from configs file.')
                raise

    @pyqtSlot()
    def run(self):
        comPortObj = self.comPortObj
        time.sleep(0.5)
        comPortObj.write(b'!reset\r\n')
        time.sleep(1)
        comPortObj.write(b'!version\r\n')
        time.sleep(0.5)
        comPortObj.write(b'!pl_gw_config 0\r\n')
        time.sleep(0.5)
        comPortObj.write(b'!set_packet_filter_off\r\n')
        time.sleep(0.5)
        comPortObj.write(b'!set_pacer_interval 0\r\n')
        time.sleep(0.5)

        energizingCmd = f"!set_energizing_pattern {self.configs['pattern']}\r\n"
        comPortObj.write(bytes(energizingCmd, encoding='utf-8'))
        time.sleep(0.5)

        comPortObj.write(self.GWconfig)
        time.sleep(0.5)

        tag_id_dic = {}
        tag_id = ''
        tmp = ''
        prev_tag_id = ''
        with printingLock:
            print(str(self.tester_name) + ': Starting Multi-Tag System Test, from now on you can exit')
        with loggingLock:
            logging.info(str(self.tester_name) + ': Starting Multi-Tag System Test')
            logging.info(str(self.tester_name) + ': Reel Name = ' + str(self.reel_name) + ', number of tags in this test = ' + str(self.tags_num))
        global tested
        global all_packets

        comPortObj.run_packets_listener(do_process=True, tag_packets_only=False)

        while not self.stop.isSet():

            sleep(0.0001)
            if comPortObj.is_data_available():

                data = comPortObj.get_data(ActionType.CURRENT_SAMPLES, num_of_packets=1, data_type=DataType.RAW)
                if isinstance(data, dict):
                    data = [data]
                # print(data)

                if len(data) > 0:
                    for packet in data:
                        if packet.get('raw'):
                            try:
                                tmp = packet['raw']
                                if 'SW_VER' in tmp:
                                    # TODO remove next test when done
                                    with printingLock:
                                        print(str(self.tester_name) + ': tmp is: ' + str(tmp))
                                    Ver_Index = tmp.index('SW_VER') + 7
                                    GW_Ver = tmp[Ver_Index:]
                                    with printingLock:
                                        print(str(self.tester_name) + ': Detected GW BLE Chip SW Version: ' + GW_Ver)
                                        print(str(self.tester_name) + ': you can start!')

                            except Exception:
                                with printingLock:
                                    print(str(self.tester_name) + ': Warning: Could not decode ' + tmp)
                                with loggingLock:
                                    logging.debug(str(self.tester_name) + ': Warning: Could not decode ' + tmp)
                                continue

                            if tmp.startswith("process_packet"):
                                currentLocation = tested

                                tag_id = tmp.split('(')[1].split(')')[0].strip(' "')[:PREAMBLE_BYTES * NIBS_IN_BYTE]

                                try:
                                    # #todo remove next test (which exists to ignore not C0 tags)
                                    # if not 'D1D1' in tag_id:
                                    #     continue
                                    # new tag
                                    if not (tag_id in tag_id_dic.keys()):
                                        tag_id_dic[tag_id] = {}
                                        with passed_uniquesLock:
                                            if not tag_id in self.passed_uniques:
                                                self.passed_uniques.append(tag_id)

                                        with printingLock:
                                            print(str(self.tester_name) + ': ********** New Tag Detected: ' + tag_id + ' **********')
                                        with loggingLock:
                                            if prev_tag_id != '':  # for the first tag
                                                logging.info(str(self.tester_name) + ': previous tag data so far: ' + prev_tag_id + ' ' + str(tag_id_dic[prev_tag_id]))
                                            logging.info(str(self.tester_name) + ': ********** New Tag Detected: ' + tag_id + ' **********' + 'current counter value is: ' + str(currentLocation))

                                        tag_id_dic[tag_id] = {'packetData': [tmp], 'timeVec': [time.time()], 'currentLocation': [currentLocation]}

                                        global passed
                                        passed[self.tester_name] = len(tag_id_dic.keys())
                                        prev_tag_id = tag_id

                                        packet = tmp.split('(')[1].split(')')[0].strip(' "')
                                        tagRow = {'advAddress': packet[ADV_ADDR_START * NIBS_IN_BYTE:ADV_ADDR_END * NIBS_IN_BYTE], \
                                                  'tagLocation': currentLocation, \
                                                  'status': 'Passed', \
                                                  'commonRunName': self.common_run_name, \
                                                  'rawData': packet}
                                        self.tags_csv_log.append_list_as_row(tagRow.values())

                                    else:
                                        tag_id_dic[tag_id]['timeVec'].append(time.time())
                                        tag_id_dic[tag_id]['packetData'].append(tmp)
                                        tag_id_dic[tag_id]['currentLocation'].append(currentLocation)
                                except Exception:
                                    print_exc()
                                    print('the run thread crashed during processing of a packet')
                                    continue

                        else:
                            print(str(self.tester_name) + ': tmp is: ' + str(tmp))

        comPortObj.write(b'!reset\r\n')
        comPortObj.exit_gw_api()
        with printingLock:
            print(str(self.tester_name) + ": tag_id_dic is: " + str(tag_id_dic))
        with loggingLock:
            logging.info(str(self.tester_name) + ": tag_id_dic is: " + str(tag_id_dic))


class CounterThread(threading.Thread):

    def __init__(self, stop: Event, rows=1):
        super(CounterThread, self).__init__()
        self.stop = stop
        self.rows = int(rows)
        self.port = get_ports_of_arduino()
        if len(self.port) > 1:
            print("too many USB Serial Device connected, can't figure out which is the counter")
        elif len(self.port) < 1:
            print("No USB Serial Device connected, please connect the counter")
        else:  # there is only one port of usb that is not GW
            self.port = self.port[0]
        self.baud = '9600'
        self.comPortObj = serial.Serial(self.port, self.baud, timeout=0.1)

    @pyqtSlot()
    def run(self):
        buf = b''
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
                            tested += self.rows
                        # if tested % 10 == 0:
                        #     with printingLock:
                        #         print("Counter: " + str(tmp))
                        buf = b''
                    except Exception:
                        with printingLock:
                            print('Warning: Could not decode counter data')
                        with loggingLock:
                            logging.debug('Warning: Could not decode counter data')
                        buf = b''
                        continue

        self.comPortObj.close()


class MainWindow(QMainWindow):
    csv_header = ['raw', 'time']

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.comPortObjs = {}
        version = ''
        latestVersion = ''
        self.baud = 921600
        self.GWs_ports = get_ports_of_GWs()
        for port in self.GWs_ports:
            self.comPortObjs[port] = {}
            self.comPortObjs[port]['serial'] = comPortObj = WiliotGateway(baud=self.baud, port=port)
            self.comPortObjs[port]['version'] = portVersion = comPortObj.get_gw_version()[0]
        self.value, self.tags_csv_log, self.run_csv_log = openSession(self.comPortObjs)
        self.passed_every_50 = []
        self.last_tested_num = -1  # so the first position will be calculated
        self.last_passed_num = 0
        self.passed_uniques = []
        self.tags_num = int(self.value['tags_num'])
        self.reel_name = self.value['reel_name']
        self.band = self.value['band']
        self.rows = self.value['rows']
        self.inlay = self.value['inlay']
        self.common_run_name = self.value['common_run_name']
        self.yield_over_time = []
        self.calculate_interval = 10
        self.calculate_on = 50
        self.color = 'default'
        self.unconverted_reel_tags_num = [0]  # will be set to 0 when 'New Reel' button is pushed
        self.unconverted_reels_before_current_tags_num = 0

        self.stop = threading.Event()

        self.Counter_Thread = CounterThread(self.stop, rows=self.rows)
        self.Counter_Thread.start()

        self.low_yield_window_is_alive = threading.Event()
        self.run_thread = []
        for port in range(len(self.GWs_ports)):
            # if '5' in str(self.GWs_ports[port]):  # charger
            #     self.run_thread.append(
            #         RunThread(self.GWs_ports[port], self.baud, self.stop, self.tags_num, self.reel_name,
            #                    tester_name='tester' + str(port), passed_uniques=self.passed_uniques, listener=True))
            # else:
            # if '5' in str(self.GWs_ports[port]):# todo - delete the if
            self.run_thread.append(RunThread(self.comPortObjs[self.GWs_ports[port]]['serial'], self.GWs_ports[port], self.baud, self.stop, self.tags_num, self.reel_name,
                                             tester_name='tester' + str(port), passed_uniques=self.passed_uniques,
                                             inlay=self.value['inlay'], band=self.band,
                                             common_run_name=self.common_run_name, tags_csv_log=self.tags_csv_log))  # regular GW
            print('using the device connected to port ' + str(self.GWs_ports[port]))
        new_path = join(YIELD_TEST_APP_DATA, 'logs','conversion_testing', self.value['reel_name'])
        if not exists(new_path):
            os.makedirs(new_path)
        # self.log_path = new_path + '/' + self.reel_name + '_IFT_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.log'
        # logging.basicConfig(filename=self.log_path, filemode='a',
        #                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        #                     datefmt='%H:%M:%S', level=logging.DEBUG)
        self.openUI()
        for port in range(len(self.GWs_ports)):
            self.run_thread[port].start()

    def openUI(self):
        self.l = QLabel("If you want to end this run, press stop")
        self.cur_pass = QLabel("Currently Passed = 0")
        self.l.setStyleSheet('.QLabel {padding-top: 10px; font-size: 20px;}')
        self.cur_pass.setStyleSheet('.QLabel {padding-top: 10px; font-size: 20px;}')
        self.reel_label = QLabel("Reel Name: ")
        self.reel_label.setStyleSheet('.QLabel {padding-top: 10px; font-weight: bold; font-size: 25px; color:#005e5e;}')
        self.band_label = QLabel(f"Band: {self.band}")
        self.band_label.setStyleSheet('.QLabel {padding-top: 10px; font-weight: bold; font-size: 25px; color:#005e5e;}')
        self.tested = QLabel("Tested = 0, Passed = 0, Yield = -1%")
        self.tested.setStyleSheet('.QLabel {padding-top: 10px; font-size: 20px;}')

        layout = QVBoxLayout()

        self.new_unconverted_reel = QPushButton("New unconverted Reel")
        self.new_unconverted_reel.setStyleSheet("; font-size: 25px; background-color: teal")
        self.new_unconverted_reel.pressed.connect(self.new_reel_fn)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("font-weight: bold; font-size: 25px; background-color: red")
        self.stop_button.pressed.connect(self.stop_fn)

        self.graphWidget = pg.PlotWidget()
        self.x = []  # 0 time points
        self.y = []  # will contain the yield over time
        self.graphWidget.setBackground('w')
        # Add Title
        self.graphWidget.setTitle("Yield over time", color="b", size="30pt")
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidget.setLabel("left", "Yield for the last 50 tags [%]", **styles)
        self.graphWidget.setLabel("bottom", "Last tag location [x*" + str(self.calculate_interval) + "+" + str(self.calculate_on) + "]", **styles)
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        layout.addWidget(self.reel_label)
        layout.addWidget(self.band_label)
        layout.addWidget(self.l)
        layout.addWidget(self.new_unconverted_reel)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.cur_pass)
        layout.addWidget(self.tested)
        layout.addWidget(self.graphWidget)

        self.w = QWidget()
        self.w.setLayout(layout)
        self.setCentralWidget(self.w)
        self.show()

        if self.run_csv_log is not None:
            self.runRow = {
                'commonRunName': self.common_run_name, \
                'testerStationName': 'YieldTester', \
                'testerType': 'YieldTest', \
                'energizingPattern': self.run_thread[0].configs['pattern'], \
                'packetThreshold': 1, \
                'yieldOverTimeInterval': self.calculate_interval, \
                'yieldOverTimeOn': self.calculate_on, \
                'inlayType': self.band, \
                'inlay': self.inlay \
                }

        self.update_timer = QTimer()
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.recurring_timer)
        self.update_timer.start()

    ############################ GUI functions ##########################################################
    def new_reel_fn(self):
        with loggingLock:
            logging.info('---------------------------New unconverted reel added to this reel, ' + str(self.unconverted_reel_tags_num[-1]) + ' tags are in this reel----------------------------')
        with printingLock:
            print('---------------------------New unconverted reel added to this reel, ' + str(self.unconverted_reel_tags_num[-1]) + ' tags are in this reel----------------------------')
        self.unconverted_reels_before_current_tags_num += self.unconverted_reel_tags_num[-1]
        self.unconverted_reel_tags_num.append(0)

    def paint_background(self, color='default'):
        if color == 'red':
            self.w.setAutoFillBackground(True)
            p = self.w.palette()
            p.setColor(self.w.backgroundRole(), Qt.red)
            self.w.setPalette(p)
        if color == 'default':
            self.w.setAutoFillBackground(False)

    def stop_fn(self):
        global passed
        global tested
        logging.debug("Stopped by the operator.")
        last_values = saveScreen4Tester(self.unconverted_reel_tags_num, reel_name=self.reel_name)
        for i in range(len(self.unconverted_reel_tags_num)):
            name = str(i) + 'reel_name'
            if last_values[name] != '':
                logging.info(last_values[name] + ' had ' + str(self.unconverted_reel_tags_num[i]) + ' tags')
        with loggingLock:
            logging.info('Number of tags that were actually ran: ' + str(tested))
        # no counter option ( will take last user input on tested amount)
        # if last_values['tags_num'] != '':
        #     tag_num = int(last_values['tags_num'])
        # else:
        #     tag_num = int(self.value['tags_num'])
        # if tag_num != 0:
        #     with passed_uniquesLock: yield_= len(self.passed_uniques) / tag_num * 100
        if tested != 0:
            with passed_uniquesLock:
                yield_ = len(self.passed_uniques) / tested * 100
                yield_ = yield_ if yield_ <= 100 else 100
        else:
            yield_ = -1
        with loggingLock:
            logging.info(str(passed) + ' tags were passed')
            with passed_uniquesLock:
                logging.info(str(len(self.passed_uniques)) + ' unique tags passed in all of the testers')
            logging.info('Yield = ' + str(yield_) + '%')
            logging.info('yieldOverTime = ' + str(self.y))
            # logging.debug('Uploaded to cloud? ' + last_values['upload'])
            logging.info('Last words: ' + last_values['comments'])

        conclusion(yield_)
        self.exit_fn()

    def exit_fn(self):
        self.stop.set()
        # parts = [p for p in self.log_path.split("/")]
        # if last_values['upload'] == 'Yes':
        #     cloud_API(self.reel_name,parts[3])
        for port in range(len(self.GWs_ports)):
            self.run_thread[port].join()

        sys.exit(0)

    def recurring_timer(self):
        global tested
        global passed

        self.cur_pass.setText("Currently Passed = " + str(passed))

        if tested == 0:
            yield_ = -1
            self.reel_label.setText("Reel Name: " + self.reel_name)
        else:
            with passed_uniquesLock:
                yield_ = len(self.passed_uniques) / tested * 100
                yield_ = 100 if yield_ > 100 else yield_
            if tested > 500 and yield_ < 20 and self.color == 'default':
                self.color == 'red'
                self.w.setAutoFillBackground(True)
                p = self.w.palette()
                p.setColor(self.w.backgroundRole(), Qt.red)
                self.w.setPalette(p)
                self.reel_label.setText("Reel Name: " + self.reel_name + "\nYield is under 20%, STOP and look for errors!!!")
                self.stop_button.setStyleSheet("font-weight: bold; font-size: 25px; background-color: white")
                self.show()
                # self.low_yield_stop(yield_)
            elif self.color == 'red' and yield_ > 20:
                self.color == 'default'
                self.w.setAutoFillBackground(False)
                self.reel_label.setText("Reel Name: " + self.reel_name)
                self.stop_button.setStyleSheet("font-weight: bold; font-size: 25px; background-color: red")
                self.show()
        self.tested.setText('Tested = ' + str(tested) + ', Passed = ' + str(passed) + ', Yield = ' + '{0:.4g}'.format(yield_) + '%')
        # update the graph, if there was change in the tested amount
        # because passed and tested are been updated in different time we will check the passed of the prev tag => tested -1
        if tested > self.last_tested_num:
            if self.calculate_on >= tested > self.last_tested_num:
                with passed_uniquesLock:
                    self.passed_every_50.append(len(self.passed_uniques) - self.last_passed_num)
            elif tested > 0:
                del self.passed_every_50[0]
                with passed_uniquesLock:
                    self.passed_every_50.append(len(self.passed_uniques) - self.last_passed_num)
            if tested % self.calculate_interval == 1 and tested > self.calculate_on:
                # print('@@@@ self.passed_every_50 = ' + str(self.passed_every_50))
                # print('@@@@ self.last_passed_num = ' + str(self.last_passed_num))
                cur_yield = sum(self.passed_every_50) / self.calculate_on * 100
                cur_yield = cur_yield if cur_yield <= 100 else 100
                self.y.append(cur_yield)
                self.x = range(len(self.y))
                self.data_line.setData(self.x, self.y)  # Update the data.
                self.yield_over_time.append(int(cur_yield))
                if self.run_csv_log is not None:
                    runRow = {
                    'tested': tested, \
                    'passed': len(self.passed_uniques), \
                    'yield': yield_, \
                    'yieldOverTime': self.yield_over_time[-1], \
                        }
                    self.runRow.update(runRow)
                    self.run_csv_log.append_dict_as_row([self.runRow])
        # update the prev counters

        if tested > self.last_tested_num:
            self.last_tested_num += 1
            self.unconverted_reel_tags_num[-1] += 1
            with passed_uniquesLock:
                if len(self.passed_uniques) > self.last_passed_num:
                    self.last_passed_num += self.passed_every_50[-1]  # passed_every_50 might be more than 1 in a cell


app = QApplication([])
window = MainWindow()
app.exec_()
window.exit_fn()
