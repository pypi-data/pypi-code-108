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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import pyqtgraph as pg
import serial.tools.list_ports
from queue import Queue
import serial
from datetime import datetime
from wiliot.gateway_api.gateway import *
from wiliot.wiliot_testers.tester_utils import *
from tal15k_utils import *

plt.switch_backend('agg')

tested = 0
passed = 0
run_data_dict = {}
run_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
wafer_name = ''
tags_data_log = None
run_data_log = None
run_data_path = ''
tags_data_path = ''

printingLock = threading.Lock()
transmitted_uniquesLock = threading.Lock()


class LoopThread(threading.Thread):
    """
    Thread that have the main loop that tells the other threads to work or wait

    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type time_per_tag: int
        @param time_per_tag: test time per tag
        @type charging_time: int
        @param charging_time: charge time at the begging of each batch
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
            program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:
        @except Exception('error in compute_location')

    Events:
        listen/ waits on:
            events.done => user pressed stop
            events.testers_good[] => tag passed
            events.test_time_is_over => testing time is over (been set by internal timer)
            events.stop => tells operator to stop this run
            events.continue_ => continue after duplication happened

        sets:
            events.charge_between_tags => signal charger to start charging cw
            events.charge_at_new_batch => signal charger to start charging pattern 27
            events.stop_charge => signal charger to stop transmitting

    Logging:
        the logging from this thread will be to logging.info(), logging.debug()
    """

    def __init__(self, events, time_per_tag, charging_time, ports_and_guis):
        super(LoopThread, self).__init__()
        self.events = events
        self.ports_and_guis = ports_and_guis
        self.exception_queue = Queue()
        self.time_per_tag = time_per_tag
        self.charging_time = charging_time
        self.gui_values = self.ports_and_guis.value
        self.timer_is_done = False
        self.is_first_after_new_batch = True  # to make sure first location will be [x, 0, 0]

        if len(self.events.testers_good) == 1:
            self.gw_events_or = or_event_set(self.events.done, self.events.testers_good[0],
                                             self.events.test_time_is_over)
        elif len(self.events.testers_good) == 2:
            self.gw_events_or = or_event_set(self.events.done, self.events.testers_good[0],
                                             self.events.testers_good[1], self.events.test_time_is_over)
        else:
            with printingLock:
                print(
                    'code does not support more than 2 testers,\n\
                    if you want to use more please add support in GPIO component')

        self.good = []
        for i in range(len(self.events.testers_good)):
            self.good.append(False)

    def run(self):
        """
        runs the thread
        """
        with printingLock:
            print('LoopThread: I am ready')
        logging.info('LoopThread: I am ready')
        state = ''
        die = False
        is_first_run = True  # to make sure we start the run with "new batch" (otherwise we can't know the location)
        global tested

        try:
            while not die:
                time.sleep(0)
                if self.events.done.isSet():
                    with printingLock:
                        print("PC send done to GPIO, will exit GPIO thread")
                    die = True
                    continue

                # will keep trying to read the lines as long as the user did not intervene
                with printingLock:
                    print("LoopThread: waiting to data to arrive from TAL15K, time = " + str(time.time()))
                logging.info("LoopThread: waiting to data to arrive from TAL15K")

                while not self.events.done.isSet() and not self.events.stop.isSet():
                    time.sleep(0)
                    state = self.ports_and_guis.gpio_read()
                    if state is None:
                        state = ''
                        continue
                    if 'Completed Successfully' in state:
                        continue
                    else:
                        break

                if self.events.pause.isSet():
                    self.stop_charging()
                    self.stop_all_gws()
                    self.events.continue_.wait()
                    continue  # to avoid reading the state (= None)
                if self.events.continue_.isSet():
                    for i in range(len(self.events.testers_work)):
                        self.events.testers_work[i].clear()
                    is_location_in_batch_is_good = self.compute_location()
                    if not is_location_in_batch_is_good:
                        raise Exception('compute_location() failed')
                    self.events.charge_between_tags.set()
                    for i in range(len(self.good)):
                        if not self.good[i]:
                            self.ports_and_guis.gpio_command('bad' + str(i))
                        else:  # reset the testers results
                            self.good[i] = False
                    continue  # to avoid reading the state (= None)

                # for us to know that the tester is ready to start
                if is_first_run:
                    if 'new batch' in state:
                        is_first_run = False
                        self.is_first_after_new_batch = True
                        self.new_batch()
                        continue  # need to start the while again

                    # we should not get this value for first message (only new batch)
                    # otherwise we will not know the location
                    else:
                        self.bad_answer_from_gpio(state)
                        if 'start test' in state:
                            with printingLock:
                                print("LoopThread: this return value is illegal for first location.\n\
                                     will pause this run, "
                                      "if you will press Continue this batch locations might be wrong")

                            logging.debug("LoopThread: this return value is illegal for first location.\n\
                                 will pause this run, if you will press Continue this batch locations might be wrong")

                # not first run #####################
                else:
                    if 'new batch' in state:
                        self.is_first_after_new_batch = True
                        self.new_batch()
                        continue  # need to start the while again

                    elif 'start test' in state:
                        if not self.is_first_after_new_batch:
                            self.stop_charging()
                        tested += 1
                        with printingLock:
                            print("LoopThread: 'start test' received from TAL15K, time = " + str(time.time()))
                        logging.info("LoopThread: 'start test' received from TAL15K")
                        for i in range(len(self.events.testers_work)):
                            if not self.events.testers_work[i].isSet():
                                self.events.testers_work[i].set()

                        # start tag testing loop
                        self.timer_is_done = False
                        self.timer = threading.Timer(float(self.time_per_tag), self.end_of_time)
                        self.timer.start()

                        all_tags_are_good = False  # a flag to indicate all tags passed and we should continue
                        while not self.timer_is_done and not die:
                            time.sleep(0)
                            try:
                                self.gw_events_or.wait()
                                if self.events.done.isSet():
                                    with printingLock:
                                        print("LoopThread: PC send done to GPIO, will exit GPIO thread")
                                    die = True
                                else:
                                    for i in range(len(self.good)):
                                        if self.events.testers_good[i].isSet():
                                            self.good[i] = True
                                            self.events.testers_good[i].clear()
                                    all_tags_are_good = True
                                    for i in range(len(self.good)):
                                        if not self.good[i]:
                                            all_tags_are_good = False

                                if self.events.test_time_is_over.isSet() or all_tags_are_good:
                                    self.events.test_time_is_over.clear()
                                    break
                            except Exception:
                                exception_details = sys.exc_info()
                                self.exception_queue.put(exception_details)

                        self.timer.cancel()  # end of tags testing loop

                        for i in range(len(self.events.testers_work)):
                            self.events.testers_work[i].clear()
                        is_location_in_batch_is_good = self.compute_location()
                        if not is_location_in_batch_is_good:
                            raise Exception('compute_location() failed')

                    else:
                        self.stop_charging()
                        self.bad_answer_from_gpio(state)

                self.events.charge_between_tags.set()
                for i in range(len(self.good)):
                    if not self.good[i]:
                        self.ports_and_guis.gpio_command('bad' + str(i))
                    else:  # reset the testers results
                        self.good[i] = False
                        self.ports_and_guis.gpio_command('good' + str(i))

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
        finally:
            with printingLock:
                print("LoopThread: done")
            logging.info("LoopThread: done")

    def new_batch(self):
        with printingLock:
            print("LoopThread: 'new batch' received from TAL15K")
        logging.info("LoopThread: 'new batch' received from TAL15K")
        self.ports_and_guis.location_in_batch[1] = 0  # (0-columns_num-1)
        self.ports_and_guis.location_in_batch[2] = 0  # (0-rows_num-1)
        for i in range(len(self.events.testers_work)):
            self.events.testers_work[i].clear()

        self.events.charge_at_new_batch.set()
        time.sleep(float(self.charging_time))
        self.stop_charging()
        self.ports_and_guis.gpio_command('end of charge')
        self.ports_and_guis.location_in_batch[0] += 1

    def stop_charging(self):
        # turn off the charger
        if self.events.charge_at_new_batch.isSet():
            self.events.charge_at_new_batch.clear()
        if self.events.charge_between_tags.isSet():
            self.events.charge_between_tags.clear()
        self.events.stop_charge.set()

    def bad_answer_from_gpio(self, state):
        with printingLock:
            print("LoopThread: state = " +
                  str(state.strip('\n\r')) + " , this return value is illegal. will pause this run")
        logging.debug("LoopThread: state = " +
                      str(state.strip('\n\r')) + " , this return value is illegal. will pause this run")
        self.events.pause.set()
        self.stop_all_gws()
        self.events.continue_.wait()

    def end_of_time(self):
        """
        puts self.timer_is_done = True
        """
        self.timer_is_done = True
        self.events.test_time_is_over.set()

    def stop_all_gws(self):
        """
        stops all gws (testers and charger) from transmitting
        """
        # to avoid deadlock in testers thread, when done is set, the threads will close GWs by themselves
        if self.events.done.isSet():
            return
        for i in range(len(self.events.testers_work)):
            self.events.testers_work[i].clear()
        self.events.charge_at_new_batch.clear()
        self.events.charge_between_tags.clear()
        self.events.stop_charge.set()

    def compute_location(self):
        """
        change self.ports_and_guis.location_in_batch to its next location
        @except: Exception('error in compute_location')
        @return: True for success, False otherwise
        """
        if len(self.good) == 1:
            if self.is_first_after_new_batch:
                self.is_first_after_new_batch = False
            # outside of the testing area - we should never get here (new batch should be received before)
            elif self.ports_and_guis.location_in_batch[1] > (int(self.gui_values['columns_num']) - 1) or \
                    self.ports_and_guis.location_in_batch[2] > (int(self.gui_values['rows_num']) - 1) or \
                    self.ports_and_guis.location_in_batch[1] < 0 or self.ports_and_guis.location_in_batch[2] < 0:
                with printingLock:
                    print('error in calculating location (self.ports_and_guis.location_in_batch = ' + str(
                        self.ports_and_guis.location_in_batch) + ', we must end this run. please press STOP')
                logging.debug('error in calculating location (self.ports_and_guis.location_in_batch = ' + str(
                    self.ports_and_guis.location_in_batch) + ', we must end this run. please press STOP')
                self.stop_all_gws()
                self.events.stop.set()
                return False
            else:  # legal values
                # top row
                if self.ports_and_guis.location_in_batch[2] == int(self.gui_values['rows_num']) - 1:
                    if self.ports_and_guis.location_in_batch[1] % 2 == 0:  # will move left
                        self.ports_and_guis.location_in_batch[1] += 1
                    else:
                        self.ports_and_guis.location_in_batch[2] -= 1  # will move down
                # bottom row
                elif self.ports_and_guis.location_in_batch[2] == 0:
                    if self.ports_and_guis.location_in_batch[1] % 2 == 1:  # will move left
                        self.ports_and_guis.location_in_batch[1] += 1
                    else:
                        self.ports_and_guis.location_in_batch[2] += 1  # will move up
                elif self.ports_and_guis.location_in_batch[1] % 2 == 0:  # will move up
                    self.ports_and_guis.location_in_batch[2] += 1
                else:
                    self.ports_and_guis.location_in_batch[2] -= 1  # will move down

        else:
            with printingLock:
                print('need to learn the testing route for this amount of testers in order to compute location.\
                     please press STOP')
            logging.debug('need to learn the testing route for this amount of testers in order to compute location.\
                 please press STOP')
            self.stop_all_gws()
            self.events.stop.set()
            return False
        if self.is_legal_location():
            return self.ports_and_guis.location_in_batch
        else:
            self.events.pause.set()
            with printingLock:
                print('error in compute_location')
            logging.debug('error in compute_location')
            raise Exception('error in compute_location')

    def is_legal_location(self):
        """

        @return: True for legal location, False otherwise
        """
        if len(self.good) == 1:
            if self.ports_and_guis.location_in_batch[1] > int(self.gui_values['columns_num']) - 1:
                return False
            if self.ports_and_guis.location_in_batch[2] > int(self.gui_values['rows_num']) - 1:
                return False
            if self.ports_and_guis.location_in_batch[1] < 0:
                return False
            if self.ports_and_guis.location_in_batch[2] < 0:
                return False
        else:
            with printingLock:
                print('LoopThread: need to learn the testing route for this amount of testers '
                      'in order to compute location. please press STOP')
            logging.debug('LoopThread: need to learn the testing route for this amount of testers'
                          ' in order to compute location. please press STOP')
            self.stop_all_gws()
            self.events.stop.set()
            return False

        with printingLock:
            print('LoopThread: Current location is ' + str(self.ports_and_guis.location_in_batch))
        logging.debug('LoopThread: Current location is ' + str(self.ports_and_guis.location_in_batch))
        return True


class ChargerThread(threading.Thread):
    """
    Thread that controls charger gw

    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
              program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Events:
        listen/ waits on:
        events.done=> user pressed stop
        events.charger_event_or => event that equals to (events.charge_at_new_batch OR events.stop_charge OR
                                    events.charge_between_tags)
        events.charge_at_new_batch => start charging with the pattern in between batches (27)
        events.charge_between_tags => start charging with the pattern in between tags (cw)
        events.stop_charge => stop transmitting
        events.testers_are_silent => notify when testers ended testing

        sets:
        None

    Logging:
        the logging from this thread will be to logging.info()
        """

    def __init__(self, events, ports_and_guis):
        super(ChargerThread, self).__init__()
        self.ports_and_guis = ports_and_guis
        self.events = events
        self.exception_queue = Queue()
        self.ports_and_guis.charger_config()

    def run(self):
        """
        runs the thread
        """
        try:
            with printingLock:
                print('Charger: I am ready')
            logging.info('Charger: I am ready')
            while not self.events.done.isSet():
                time.sleep(0)
                self.events.charger_event_or.wait()
                if self.events.charge_at_new_batch.isSet():
                    self.events.charge_at_new_batch.clear()
                    for i in range(len(self.events.testers_are_silent)):
                        self.events.testers_are_silent[i].wait()
                        self.events.testers_are_silent[i].clear()
                    self.ports_and_guis.charger_work(charging_type='new batch')
                    with printingLock:
                        print('Charger: start charging after new batch, time = ' + str(time.time()))
                    logging.info('Charger: start charging after new batch')
                elif self.events.charge_between_tags.isSet():
                    self.events.charge_between_tags.clear()
                    self.ports_and_guis.charger_work(charging_type='between tags')
                    with printingLock:
                        print('Charger: start charging between tags, time = ' + str(time.time()))
                    logging.info('Charger: start charging between tags')
                elif self.events.stop_charge.isSet():
                    self.events.stop_charge.clear()
                    self.ports_and_guis.charger_shutup()
                    with printingLock:
                        print('Charger: stopped charging, time = ' + str(time.time()))
                    logging.info('Charger: stopped charging')

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
        finally:
            try:
                self.ports_and_guis.charger_shutup()
                self.ports_and_guis.charger_close()
            except Exception:
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
            with printingLock:
                print("Charger: done")
            logging.info("Charger: done")


class TesterThread(threading.Thread):
    """
    Thread that controls tester gw (can be use more than one time)

    Parameters:
        @type port: serial.tools.list_ports.comports()[x].device()
        @param port: what port the tester of this thread connected to
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
            program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type tester_num: int
        @param tester_num: number of the tester [0...(<number of testers> -1)]
        @type transmitted_uniques: global list (use transmitted_uniquesLock to use it)
        @param transmitted_uniques: contains all tags transmitted in this run


    Exceptions:
        @except Exception: 'duplication happened'

    Events:
        listen/ waits on:
            events.done=> user pressed stop
            events.testers_work[self.tester_num] => start testing
            events.continue_ => continue after duplication happened

        sets:
            events.testers_good[self.tester_num] => the current tag passed

    Logging:
        the logging from this thread will be to logging.info(), logging.debug() and logging.warning()
        """

    def __init__(self, port, ports_and_guis, events, tester_num, transmitted_uniques):
        super(TesterThread, self).__init__()
        self.port = port  # name of the port this tester is connected to
        self.ports_and_guis = ports_and_guis
        self.events = events
        self.transmitted_uniques = transmitted_uniques
        self.tester_num = tester_num
        self.gui_values = self.ports_and_guis.value
        self.exception_queue = Queue()
        self.ports_and_guis.tester_config(tester_num=self.tester_num)

    def run(self):
        """
        runs the thread
        """
        try:
            duplication_at_location = ''
            prev_adv_address = ''
            with printingLock:
                print('Tester' + str(self.tester_num) + ': I am ready')
            logging.info('Tester' + str(self.tester_num) + ': I am ready')
            prev_batch_num = self.ports_and_guis.location_in_batch[0]
            while not self.events.done.isSet():
                time.sleep(0)
                self.events.testers_work[self.tester_num].wait()
                # to reconfigure GW to tester mode after charging time
                self.events.charger_is_silent.wait()
                self.ports_and_guis.tester_run_packets_listener(tester_num=self.tester_num)
                self.ports_and_guis.tester_work(tester_num=self.tester_num)
                with printingLock:
                    print('Tester' + str(self.tester_num) + ': start testing, time = ' + str(time.time()))
                logging.debug('Tester' + str(self.tester_num) + ': start testing, time = ' + str(time.time()))
                # check if we started new batch
                if prev_batch_num < self.ports_and_guis.location_in_batch[0]:
                    duplication_at_location = ''
                    prev_batch_num = self.ports_and_guis.location_in_batch[0]

                tag_data_list = []
                # once every location
                while self.events.testers_work[self.tester_num].isSet() and not self.events.done.isSet():
                    time.sleep(0)  # to prevent run slowdown by gateway_api
                    self.cur_tag_adv_addr = ''
                    self.cur_tag_min_rssi = 1000
                    if self.ports_and_guis.tester_is_data_available(self.tester_num):
                        gw_answer = self.ports_and_guis.tester_get_data(self.tester_num)
                        if gw_answer and not gw_answer['is_valid_tag_packet']:
                            with printingLock:
                                print('Tester' + str(self.tester_num) + ': non packet msg received: ' + str(gw_answer))
                            logging.debug('Tester' + str(self.tester_num) + ': non packet msg received: ' +
                                          str(gw_answer))
                        elif gw_answer and gw_answer['is_valid_tag_packet']:
                            # in packet decoder we will decide the correct way to decode the packet
                            try:
                                global wafer_name
                                packet_raw_data = encrypted_packet_decoder(gw_answer)
                                self.adv_addr = packet_raw_data['advAddress']
                                packet_raw_data['tagLocation'] = self.ports_and_guis.location_in_batch
                                packet_raw_data['commonRunName'] = wafer_name + run_start_time
                                with printingLock:
                                    print('Tester' + str(self.tester_num) +
                                          ': encrypted_packet_decoder result is: ' + str(packet_raw_data))
                                logging.info('Tester' + str(self.tester_num) +
                                             ': encrypted_packet_decoder result is: ' + str(packet_raw_data))
                            except Exception:
                                msg = 'Tester' + str(self.tester_num) + \
                                      'Warning: encrypted_packet_decoder could not decode packet, will skip it'
                                with printingLock:
                                    print(msg)
                                logging.warning(msg)
                                continue
                            try:
                                # this will make sure that we do not have any duplication
                                # count when there are two new tags simultaneously
                                self.is_good_packet, need_to_switch, need_to_pause = \
                                    self.encrypted_packet_filter(packet_raw_data)
                                if self.is_good_packet:
                                    if self.cur_tag_adv_addr == '':
                                        self.cur_tag_adv_addr = self.adv_addr
                                    if self.cur_tag_min_rssi > packet_raw_data['rssi']:
                                        self.cur_tag_min_rssi = packet_raw_data['rssi']

                                # we will take no risk for now, and will pause no matter where the duplication came from
                                if need_to_pause or need_to_switch:
                                    print('Due to current settings, the run will pause. '
                                          'If you wish to continue the run anyway press Continue')
                                    logging.debug('Due to current settings, the run will pause. '
                                                  'If you wish to continue the run anyway press Continue')
                                    if duplication_at_location == '':
                                        duplication_at_location = [packet_raw_data]
                                    else:
                                        duplication_at_location.append(packet_raw_data)
                                    logging.debug(
                                        'Tester' + str(self.tester_num) + ': duplication at location ' + str(
                                            self.ports_and_guis.location_in_batch)
                                        + ', duplication data = ' + str(duplication_at_location[-1]))
                                    raise Exception('duplication happened')

                                if not self.is_good_packet:
                                    continue

                                transmitted_uniquesLock.acquire()  # to avoid double write to the transmitted_uniques
                                if packet_raw_data['advAddress'] not in self.transmitted_uniques:
                                    self.transmitted_uniques.append(packet_raw_data['advAddress'])
                                    transmitted_uniquesLock.release()
                                    with printingLock:
                                        print('Tester' + str(self.tester_num) + ': ********** New Tag Detected: ' +
                                              packet_raw_data['advAddress'] + ' **********')

                                    logging.info('Tester' + str(self.tester_num) +
                                                 ': ********** New Tag Detected: ' +
                                                 packet_raw_data['advAddress'] + ' **********')

                                    prev_adv_address = packet_raw_data['advAddress']

                                    # break if reached packet threshold
                                    tag_data_list.append(packet_raw_data)
                                    if len(tag_data_list) >= int(self.gui_values['packet_threshold']):
                                        self.events.testers_good[self.tester_num].set()
                                        global passed
                                        passed += 1
                                        self.events.testers_work[self.tester_num].clear()
                                        break  # remember there might be other tester working..

                                # more packets from the tag tested
                                elif prev_adv_address is not '' and \
                                        packet_raw_data['advAddress'] == prev_adv_address:
                                    transmitted_uniquesLock.release()
                                    with printingLock:
                                        print('Tester' + str(self.tester_num) + ': packet found from tag ' +
                                              packet_raw_data['advAddress'] + ' **********')
                                    logging.info('Tester' + str(self.tester_num) + ': packet found from tag '
                                                 + packet_raw_data['advAddress'] +
                                                 ', raw packet = ' + str(packet_raw_data['raw_data']))

                            except Exception:
                                exception_details = sys.exc_info()
                                exc_type, exc_obj, exc_trace = exception_details
                                self.exception_queue.put(exception_details)
                                if 'duplication happened' in str(exc_obj):
                                    with printingLock:
                                        print('Tester' + str(self.tester_num) + ' duplication happened')
                                    self.events.continue_.wait()
                                else:
                                    with printingLock:
                                        print('Tester' + str(self.tester_num) +
                                              ' run thread crashed during processing of a packet')
                                    continue

                            finally:
                                # just to make sure there will be no deadlock
                                try:
                                    transmitted_uniquesLock.release()
                                except Exception:
                                    pass

                # make the tester silent
                self.ports_and_guis.tester_shutup(self.tester_num)
                with printingLock:
                    print('Tester' + str(self.tester_num) + ': stopped transmitting, time = ' + str(time.time()))
                logging.debug('Tester' + str(self.tester_num) + ': stopped transmitting, time = ' + str(time.time()))
                self.ports_and_guis.tester_clean_buffer(self.tester_num)
                if len(tag_data_list) > 0:
                    data = process_encrypted_tags_data(data=tag_data_list,
                                                       packet_threshold=int(self.gui_values['packet_threshold']),
                                                       tester_type=TesterName.TAL15K)
                    global tags_data_log
                    if tags_data_log is None:
                        tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                               tester_type=TesterName.TAL15K)
                        tags_data_log.open_csv()
                        print("tags_data log file has been created")
                    tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))

                    try:
                        with printingLock:
                            print('Tester' + str(self.tester_num) + ': tag ' + data['advAddress'] + ', data = ' + str(
                                data))
                        logging.info('Tester' + str(self.tester_num) + ': tag ' + data['advAddress'] + ', data = ' +
                                     str(data))
                    except Exception:
                        with printingLock:
                            print('Tester' + str(self.tester_num) + ': could not print the tag data')
                        logging.info('Tester' + str(self.tester_num) + ': could not print the tag data')

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
            print_exception(exception_details, printingLock)

        finally:
            try:
                self.ports_and_guis.tester_shutup(self.tester_num)
                self.ports_and_guis.tester_close(self.tester_num)
            except Exception:
                pass
            finally:
                with printingLock:
                    print('Tester' + str(self.tester_num) + ": done")
                logging.info('Tester' + str(self.tester_num) + ": done")

    def encrypted_packet_filter(self, raw_data):
        """
        checks if the packet is good in terms of RSSI, tag UID
        @param raw_data: raw data of the tags (return value from packet_listener)
        @return: is_good_packet - is the packet legal,
                    need_to_switch - the tag that is currently in test is not the correct tag
                     and you should switch to the tag that sent this packet,
                     need_to_pause - you should pause the run due to Duplication
        """
        try:
            # check if the RSSI is good
            if int(raw_data['rssi']) > 90:  # todo - change to value from config file
                msg = str(raw_data['raw_data']) + " - Packet rssi is too high and wasn't accounted for"
                logging.debug(msg)
                print(msg)
                return False, False, False

            # check if the tag was already caught in the GW
            with transmitted_uniquesLock:
                if str(raw_data['advAddress']) in self.transmitted_uniques:
                    msg = str(raw_data['raw_data']) + " - Duplication from a tag we have seen before (advAddress = " \
                          + raw_data['advAddress'] + ")"
                    logging.debug(msg)
                    print(msg)
                    return False, False, True

            # check if this packet is from new tag
            if self.cur_tag_adv_addr != raw_data['advAddress'] and self.cur_tag_min_rssi != 1000:
                if raw_data['rssi'] >= self.cur_tag_min_rssi:
                    msg = str(raw_data['raw_data']) + " - Duplication from new tag (advAddress = " + \
                          str(raw_data['advAddress']) \
                          + ") we have not seen before (new tag rssi = " + str(raw_data['rssi']) \
                          + ', current tag rssi = ' + str(self.cur_tag_min_rssi) + ')'
                    logging.debug(msg)
                    print(msg)
                    return False, False, True
                else:
                    msg = str(raw_data['raw_data']) + " - Duplication with smaller RSSI, need to change tag " \
                                                      "(to advAddress = " + str(raw_data['advAddress']) + \
                          ") (new tag rssi = " + str(raw_data['rssi']) \
                          + ', current tag rssi = ' + str(self.cur_tag_min_rssi) + ')'
                    logging.debug(msg)
                    print(msg)
                    return False, True, True
            return True, False, False
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
            print_exception(exception_details, printingLock)
            return False, False, False


class PortsAndGuis:
    """
    holds all of the out side communication (gui or comports)
    class which holds all of the out side communication (GUI or comports)

    Parameters:
        @type value: dictionary
        @param value: output of open_session() (start GUI)
        @type testers_ports: list of serial.tools.list_ports.comports()[x].device()
        @param testers_ports: contains all GWs connected to PC except the charger
        @type charger_port: serial.tools.list_ports.comports()[x].device()
        @param charger_port: charger GW
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads

    Exceptions:
        @except Exception('No Arduino ports was found'): no Wiliot Arduino was found
        @except Exception("illegal gpio_command sent to gpio"): the command sent to Arduino was not 'end of charge',
            'bad<x>' or 'good<x>'  (<x> is tester number)

    Events:
        sets:
            events.testers_are_silent[tester_num] => tester <tester_num> stopped transmitting
            events.charger_is_silent => charger stopped transmitting

    Logging:
        logging.info() and logging.debug()
    """

    def __init__(self, value, testers_ports, charger_port, events):
        self.exception_queue = Queue()
        try:
            self.gpio_baud = '1000000'
            self.events = events
            # will be updated by loop thread, will be used by testers threads [batch, column, row]
            # loop thread is starting by adding 1 to location 0 -> batch starts from -1
            self.location_in_batch = [-1, 0, 0]  # [0-inf, 0-columns_num-1, 0-rows_num-1]
            self.init_config_values()
            self.testers_ports = testers_ports
            # for Charger thread ###########
            self.charger_port = charger_port
            # for Main thread ###########
            # run values
            self.value = value

            # check if the system variable exist
            assert ('TESTER_STATION_NAME' in os.environ), 'TESTER_STATION_NAME is missing from PC environment variables'
            self.tester_station_name = os.environ['TESTER_STATION_NAME']
            # todo write the station name to log and data frame
            # for Testers thread ###########
            self.testers_comPortObj = []
            # will have some empty parts, but will be more comfortable to read
            for i in range(len(self.testers_ports)):
                self.testers_comPortObj.append(WiliotGateway())
            # for GPIO thread ###########
            self.read_and_write_time_out_gpio = 0.5
            self.gpio_find_and_open_port()
            self.gw_lock = threading.Lock()

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def init_config_values(self):
        """
        initialize the config values for the run
        """
        self.dir_config = 'configs'
        self.configs_for_tester_values_path = self.dir_config + '/defaults_for_tester_values.json'
        self.configs_for_charger_values_path = self.dir_config + '/defaults_for_charger_values.json'
        config_defaults = ConfigDefaults()
        self.configs_for_tester = open_json(self.dir_config, self.configs_for_tester_values_path,
                                            config_defaults.get_tester_defaults())
        self.configs_for_charger = open_json(self.dir_config, self.configs_for_charger_values_path,
                                             config_defaults.get_charger_defaults())

    def tester_config(self, tester_num):
        """config for tester GW
        @type tester_num: int
        @param tester_num: The tester number (set by main)
        """
        with self.gw_lock:
            self.testers_comPortObj[tester_num] = WiliotGateway(port=self.testers_ports[tester_num],
                                                                lock_print=printingLock, logger_name='root')
            self.testers_comPortObj[tester_num].update_version(versions_path='gateway_versions')
            self.testers_comPortObj[tester_num].config_gw(energy_pattern_val=self.
                                                          configs_for_tester['energizingPattern'],
                                                          time_profile_val=self.
                                                          configs_for_tester['silenceTimeProfile'],
                                                          received_channel=39, filter_val=False, pacer_val=0,
                                                          max_wait=1)

            sw_version, _ = self.testers_comPortObj[tester_num].get_gw_version()
        self.events.testers_are_silent[tester_num].set()
        global run_data_dict
        run_data_dict['testersGwVersion']['tester' + str(tester_num)] = sw_version

    def tester_shutup(self, tester_num):
        """makes tester GW be silent
        @type tester_num: int
        @param tester_num: The tester number (set by main)
        """
        # this should shut him up ;)
        with self.gw_lock:
            self.testers_comPortObj[tester_num].config_gw(time_profile_val=self.
                                                          configs_for_tester['silenceTimeProfile'], max_wait=1)
        self.events.testers_are_silent[tester_num].set()

    def tester_work(self, tester_num):
        """makes tester GW work again
        @type tester_num: int
        @param tester_num: The tester number (set by main)
        """
        with self.gw_lock:
            self.testers_comPortObj[tester_num].config_gw(time_profile_val=self.
                                                          configs_for_tester['workTimeProfile'], max_wait=1)

    def tester_clean_buffer(self, tester_num):
        """makes tester GW clear its buffer from previous packets
        @type tester_num: int
        @param tester_num: The tester number (set by main)
        """
        # run_packet_listener will restart the listening at the start of the next iteration
        with self.gw_lock:
            self.testers_comPortObj[tester_num].stop_processes()
            self.testers_comPortObj[tester_num].reset_buffer()  # to clean the buffer of the GW

    def tester_close(self, tester_num):
        """makes tester GW be silent and closes the port
        @type tester_num: int
        @param tester_num: The tester number (set by main)
        """
        try:
            if type(self.testers_comPortObj[tester_num]) is not bool:
                with self.gw_lock:
                    self.testers_comPortObj[tester_num].close_port(is_reset=True)
        except Exception:
            pass

    def tester_run_packets_listener(self, tester_num):
        """
        runs packets listener function
        :type tester_num: int
        :param tester_num: The tester number (set by main)
        """
        with self.gw_lock:
            self.testers_comPortObj[tester_num].run_packets_listener(tag_packets_only=True, do_process=True)

    def tester_is_data_available(self, tester_num):
        """
        checks if there is any data available at the tester
        :type tester_num: int
        :param tester_num: The tester number (set by main)
        :rtype bool
        :return: True if data is available tp get, False otherwise
        """
        with self.gw_lock:
            return self.testers_comPortObj[tester_num].is_data_available()

    def tester_get_data(self, tester_num):
        """
        gets data from packet listener
        :type tester_num: int
        :param tester_num: The tester number (set by main)
        :rtype
        :return: a list with all the extracted packets or processed data
        """
        with self.gw_lock:
            return self.testers_comPortObj[tester_num].get_data(action_type=ActionType.FIRST_SAMPLES, num_of_packets=1,
                                                                data_type=DataType.PROCESSED)

    def charger_config(self):
        """config for charger GW
        """
        # TODO config GW patterns by what decided (flow and charge/calib)

        with self.gw_lock:
            self.Charger_comPortObj = WiliotGateway(port=self.charger_port, lock_print=printingLock,
                                                    logger_name='root')
            self.Charger_comPortObj.update_version(versions_path='gateway_versions')
            self.Charger_comPortObj.config_gw(energy_pattern_val=self.configs_for_charger['energizingPattern'],
                                              time_profile_val=self.configs_for_charger['silenceTimeProfile'],
                                              received_channel=38,
                                              filter_val=False, pacer_val=0, max_wait=1)  # todo - add support for sub1g

            sw_version, _ = self.Charger_comPortObj.get_gw_version()
        self.events.charger_is_silent.set()
        global run_data_dict
        run_data_dict['chargerGwVersion'] = sw_version

    def charger_shutup(self):
        """makes charger GW be silent
        """
        with self.gw_lock:
            self.Charger_comPortObj.config_gw(time_profile_val=self.configs_for_charger['silenceTimeProfile'],
                                              max_wait=1)
        self.events.charger_is_silent.set()

    def charger_work(self, charging_type):
        """
        makes charger GW transmit again
        :type charging_type: string
        :param charging_type: what energizing pattern to use ('new batch', 'between tags')
        """
        self.events.charger_is_silent.clear()
        if charging_type == 'new batch':
            # 7,15 because the beacon takes ~7 mili and the tag needs time of silent in between
            with self.gw_lock:
                self.Charger_comPortObj.config_gw(time_profile_val=self.configs_for_charger['workTimeProfile'],
                                                  max_wait=0)
        elif charging_type == 'between tags':
            # cw charging in between tags to make sure it has enough energy until the end
            # not using patter 27 to avoid calibration over the metal plate
            self.Charger_comPortObj.write("!start_tx_carrier 2480\r\n")

    def charger_close(self):
        """
        makes charger GW be silent and closes the port
        """
        try:
            if type(self.Charger_comPortObj) is not bool:
                with self.gw_lock:
                    self.Charger_comPortObj.close_port(is_reset=True)
        except Exception:
            pass

    def gpio_find_and_open_port(self):
        """
        @return: none
        """
        arduino_found = False
        self.gpio_port = None
        try:
            ports_list = list(serial.tools.list_ports.comports())
            for port in ports_list:
                self.comport = port
                if 'Arduino' not in str(port):
                    continue
                try:
                    self.gpio_port = serial.Serial(self.comport.device, self.gpio_baud,
                                                   timeout=self.read_and_write_time_out_gpio,
                                                   write_timeout=self.read_and_write_time_out_gpio)
                    if self.gpio_port.isOpen():
                        pass
                    else:
                        self.gpio_port.open()
                    response = ''
                    self.gpio_port.flushInput()
                    try:
                        self.gpio_port.write(str.encode("*IDN?"))
                        time.sleep(0.4)
                        data = self.gpio_port.readline()
                        response = data.decode("utf-8")
                        # Cut the last character as the device returns a null terminated string
                        with printingLock:
                            print('gpio unit response = ' + str(response))
                    except Exception:
                        with printingLock:
                            print(datetime.datetime.now().time(), "Sent: ", "*IDN?")
                            print(datetime.datetime.now().time(), "Recv: ", str(response))
                        exception_details = sys.exc_info()
                        self.exception_queue.put(exception_details)
                        return False

                    if "Wiliot Tester GPIO unit" in response:
                        with printingLock:
                            print('Found ' + response)
                        self.gpio_port.flushInput()
                        arduino_found = True
                        break
                    else:
                        self.gpio_port.close()
                except Exception:
                    with printingLock:
                        print('failed to open the gpio port')
                    exception_details = sys.exc_info()
                    self.exception_queue.put(exception_details)
                    print_exception(exception_details, printingLock)
            if not arduino_found:
                with printingLock:
                    print('No Arduino port was found. please connect the Arduino or call for support')
                raise Exception('No Arduino ports was found')
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def gpio_is_cmd_legal(self, cmd):
        """
        checks if the arduino will be able to handle the cmd
        :type cmd: str
        :param cmd: gpio_command to arduino, the legal commands are: "end of charge", "good#", "bad#"
                    (# = number of tester)
        :rtype: bool
        :return: True if legal, False otherwise
        """
        if cmd == 'end of charge':
            return True
        elif cmd[0:3] == 'bad' and len(cmd) == 4:
            try:
                int(cmd[3])
                return True
            except Exception:
                return False
        elif cmd[0:4] == 'good' and len(cmd) == 5:
            try:
                int(cmd[4])
                return True
            except Exception:
                return False
        else:
            return False

    def gpio_command(self, cmd=''):
        """
        Send the input cmd string via COM Socket and return the reply string
        :type cmd: str
        :param cmd: gpio_command to arduino ("end of charge", "good#", "bad#") # = number of tester
        :rtype: bool
        :return: True if successful, False otherwise
        """
        if not self.gpio_is_cmd_legal(cmd):
            raise Exception("illegal gpio_command sent to gpio")

        if self.gpio_port.isOpen():
            pass
        else:
            self.gpio_port.open()
            self.gpio_port.flushInput()

        try:
            self.gpio_port.write(str.encode(cmd))
            with printingLock:
                print("GPIO: sent to arduino = '" + str(cmd) + "'")
            logging.debug("GPIO: sent to arduino = '" + str(cmd) + "'")
            return True
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
            with printingLock:
                print(datetime.datetime.now().time(), "Sent: ", cmd)
            logging.debug("Sent: ", cmd)
            return False

    def gpio_read(self):
        """
        Send the input cmd string via COM Socket and return the reply string
        :rtype: string
        :return: the string that were received from GPIO unit, after .decode("utf-8").strip('\n\r') or
        None if something failed or timer ended
        """
        if self.gpio_port.isOpen():
            pass
        else:
            self.gpio_port.open()
        try:
            buf = b''

            # should exit the gpio_read line if the response was not received
            # until self.read_and_write_time_out_gpio secs
            data = self.gpio_port.readline()

            # for a case only part of the line was gpio_read
            if data.__len__() > 0:
                buf += data
                if b'\n' not in buf:
                    data = self.gpio_port.readline()
                    buf += data

            if len(buf) > 0:
                with printingLock:
                    print('GPIO: new data from tal15k = ' + str(buf.decode().strip('\n\r')))
                logging.info('GPIO: new data from tal15k = ' + str(buf.decode().strip('\n\r')))
                self.gpio_port.flushInput()
                if len(buf) > 0:
                    value = buf.decode().strip('\t\n\r')
                else:
                    value = None
            else:
                value = None
        except Exception:
            value = None
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

        return value

    def gpio_close(self):
        if self.gpio_port is not None:
            self.gpio_port.close()
        with printingLock:
            print("GPIO: done")
        logging.info("GPIO: done")


class MainEvents:
    """
    Contains events that connect between all threads
    Events are set or cleared by threads
    Events are divided to four primary groups:
        1. LoopThread events
        2. MainWindow events
        3. ChargerThread events
        4. TesterThread events

    Parameters:
        @type num_of_testers: int
        @param num_of_testers: number of testers for this run
    Exceptions: None
    Events: None
    Logging: None
    """

    def __init__(self, num_of_testers):
        self.done = threading.Event()
        self.stop = threading.Event()  # need to end this run because an severe error happened
        self.pause = threading.Event()
        self.continue_ = threading.Event()

        self.test_time_is_over = threading.Event()

        self.charge_at_new_batch = threading.Event()
        self.charge_between_tags = threading.Event()
        self.stop_charge = threading.Event()
        self.charger_is_silent = threading.Event()  # to make sure the testers will not start until the charger is done
        self.charger_event_or = or_event_set(self.charge_at_new_batch, self.stop_charge, self.charge_between_tags)

        # testers threads will only turn those signals off and will not turn them on
        self.testers_work = []
        self.testers_are_silent = []  # to make sure the charger will not start until all testers are done
        self.testers_good = []  # turned on by the tester thread
        self.testers_bad = []
        for i in range(int(num_of_testers)):
            self.testers_work.append(threading.Event())
            self.testers_are_silent.append(threading.Event())
            self.testers_good.append(threading.Event())
            self.testers_bad.append(threading.Event())


class MainWindow(QMainWindow):
    """
    Thread that opens and controls the GUI, opens all threads, sets/clears timers for all threads and handles exceptions
    This class will call for upload to cloud

    Parameters:
        values set by user in Offline Tester GUI:
            @wafer_name: str
            @rows_num: how many rows (reels) are in the sheet - int
            @columns_num: how many tags being tested in each batch (x axis, machine direction) - int
            @num_of_testers: how many testers are being used - int
            @packet_threshold: how many packets tag needs to pass - int
            @inlay_type: dropdown list with inlay types (e.g. "Dual Band") - string
            @charging_time: time in seconds for charging at the begging of each run - float
            @time_per_tag: time in seconds for testing each tag (tag will be fail if it did not response before - float

    Exceptions:
        @except Exception('No GW ports was found')
        @except Exception('No Tester port was found')
        @except Exception('No Charger port was found')

    Events:
        listen/ waits on:
            None
        sets:
            events.done => user pressed stop
            events.pause => user pressed Pause
            events.continue_ => continue after duplication happened
            events.stop_charge.set() => only at end of run, to avoid deadlock
            events.charge_at_new_batch => only at end of run, to avoid deadlock
            events.charger_is_silent => only at end of run, to avoid deadlock
            events.testers_work => only at end of run, to avoid deadlock
            events.testers_are_silent => only at end of run, to avoid deadlock

    Logging:
        configuration, logging to logging.debug(), logging.exception() and logging.info()
    """

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        try:
            self.exception_queue = Queue()
            self.value = open_session()
            self.events = MainEvents(self.value['num_of_testers'])
            self.passed_every_batch = []
            self.last_tested_num = -1  # so the first position will be calculated
            self.last_passed_num = 0
            self.transmitted_uniques = []
            self.wafer_name = self.value['wafer_name']
            self.yield_over_time = []
            self.errors = []
            self.batch_size = int(self.value['rows_num']) * int(self.value['columns_num'])

            self.color = 'default'
            self.unconverted_reel_tags_num = [0]  # will be set to 0 when 'New Reel' button is pushed
            self.unconverted_reels_before_current_tags_num = 0

            new_path = 'logs/' + self.value['wafer_name']
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            self.log_path = new_path + '/' + self.wafer_name + '_assembly_' + datetime.datetime.now().strftime(
                "%Y%m%d_%H%M%S") + '.log'
            logging.basicConfig(filename=self.log_path, filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S', level=logging.DEBUG)
            logging.debug("operator configuration is: " + str(self.value))

            global wafer_name
            global run_data_log, run_data_path, tags_data_path
            wafer_name = self.value['wafer_name']

            tags_data_path = new_path + '/' + wafer_name + '@' + \
                             datetime.datetime.utcnow().isoformat() + '_tags_data.csv'
            tags_data_path = tags_data_path.replace(':', '-')
            run_data_path = new_path + '/' + wafer_name + '@' + datetime.datetime.utcnow().isoformat() + '_run_data.csv'
            run_data_path = run_data_path.replace(':', '-')

            if run_data_log is None:
                run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.TAL15K)
                run_data_log.open_csv()
                with printingLock:
                    print("run_data log file has been created")

            self.testers_ports = []  # is updated in self.get_ports_of_gws()
            self.charger_port = ''  # is updated in self.get_ports_of_gws()
            self.get_ports_of_gws()
            self.ports_and_guis = PortsAndGuis(value=self.value, testers_ports=self.testers_ports,
                                               charger_port=self.charger_port, events=self.events)

            # update run data
            global run_data_dict
            run_data_dict['yieldOverTimeInterval'] = self.batch_size
            run_data_dict['yieldOverTimeOn'] = self.batch_size
            for key in self.value:
                if snake_to_camel(key) in run_data_log.header:
                    run_data_dict[snake_to_camel(key)] = self.value[key]
            run_data_dict['commonRunName'] = wafer_name + run_start_time
            run_data_dict['testerType'] = 'tal15k'
            run_data_dict['testerStationName'] = self.ports_and_guis.tester_station_name
            run_data_dict['testersGwVersion'] = {}
            run_data_log.override_run_data(run_data_dict)

            self.tester_threads = []

            self.loop_thread = LoopThread(events=self.events,
                                          time_per_tag=self.value['time_per_tag'],
                                          charging_time=self.value['charging_time'], ports_and_guis=self.ports_and_guis)
            if len(self.testers_ports) == 0 and self.charger_port == '':
                with printingLock:
                    print('No GW port was found. please connect the GWs or call for support')
                raise Exception('No GW ports was found')
            else:
                for port in range(len(self.testers_ports)):
                    self.tester_threads.append(
                        TesterThread(port=self.testers_ports[port], ports_and_guis=self.ports_and_guis,
                                     events=self.events,
                                     tester_num=port, transmitted_uniques=self.transmitted_uniques))
                    with printingLock:
                        print('using the device connected to port ' + str(self.testers_ports[port]))
                # charger  #TODO make sure it is the charger port
                self.charger_thread = ChargerThread(events=self.events, ports_and_guis=self.ports_and_guis)

            self.open_ui()
            logging.info('main: Wafer Name = ' + str(self.wafer_name))

            for port in range(len(self.testers_ports)):
                self.tester_threads[port].start()
            self.charger_thread.start()
            self.loop_thread.start()

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
            self.look_for_exceptions()

    def open_ui(self):
        """
        opens the run GUI
        """
        self.stop_label = QLabel("If you want to end this run, press stop")
        self.cont_label = QLabel("If you want to skip and fail this location, press Continue")
        self.reel_label = QLabel("Reel Name: ")
        self.reel_label.setStyleSheet('.QLabel {padding-top: 10px; font-weight: bold; font-size: 25px; color:#ff5e5e;}')
        self.tested = QLabel("Tested = 0, Passed = 0, Yield = -1%")
        self.last_pass = QLabel("No tag has passed yet :(")
        layout = QVBoxLayout()

        self.continue_ = QPushButton("Continue")
        self.continue_.setStyleSheet("background-color: green")
        self.continue_.pressed.connect(self.continue_fn)

        self.pause = QPushButton("Pause")
        self.pause.setStyleSheet("background-color: orange")
        self.pause.pressed.connect(self.pause_fn)

        self.stop = QPushButton("Stop")
        self.stop.setStyleSheet("background-color: red")
        self.stop.pressed.connect(self.stop_fn)

        self.graphWidget = pg.PlotWidget()
        self.x = []  # 0 time points
        self.y = []  # will contain the yield over time
        self.graphWidget.setBackground('w')
        # Add Title
        self.graphWidget.setTitle("Yield over time", color="b", size="30pt")
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidget.setLabel("left", "Yield for the last batch [%]", **styles)
        self.graphWidget.setLabel("bottom", "Last tag location [(x+1)*" + str(self.batch_size) + "]", **styles)
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        layout.addWidget(self.reel_label)
        layout.addWidget(self.cont_label)
        layout.addWidget(self.continue_)
        layout.addWidget(self.pause)
        layout.addWidget(self.stop_label)
        layout.addWidget(self.stop)
        layout.addWidget(self.last_pass)
        layout.addWidget(self.tested)
        layout.addWidget(self.graphWidget)

        self.w = QWidget()
        self.w.setLayout(layout)
        self.setCentralWidget(self.w)
        self.show()

        self.update_timer = QTimer()
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.recurring_timer)
        self.update_timer.start()

    # GUI functions ##########################################################
    def paint_background(self, color='default'):
        """
        will change the run GUI to red or back to regular
        @param color: will indicate what color to change to (default or red)
        """
        if color == 'red':
            self.w.setAutoFillBackground(True)
            p = self.w.palette()
            p.setColor(self.w.backgroundRole(), Qt.red)
            self.w.setPalette(p)
        if color == 'default':
            self.w.setAutoFillBackground(False)

    def stop_fn(self):
        """
        will end the run (end the threads, upload to cloud)
        """
        self.events.done.set()

        global tested
        global passed
        logging.debug("Stopped by the operator.")
        last_values = self.save_screen_4_tester()
        logging.info('Number of tags that were actually ran: ' + str(tested))
        if tested != 0:
            with transmitted_uniquesLock:
                yield_ = len(self.transmitted_uniques) / tested * 100
        else:
            yield_ = -1
        logging.info(str(passed) + ' tags were passed')
        with transmitted_uniquesLock:
            logging.info(str(len(self.transmitted_uniques)) + ' unique tags passed in all of the testers')
        logging.info('Yield = ' + str(yield_) + '%')
        logging.info('yieldOverTime = ' + str(self.y))
        logging.info('Last words: ' + last_values['comments'])

        conclusion(yield_)
        # to avoid deadlock
        self.events.continue_.set()
        self.events.stop_charge.set()
        self.events.charge_at_new_batch.set()
        self.events.charger_is_silent.set()

        for tester_num in range(len(self.testers_ports)):
            self.events.testers_work[tester_num].set()
            self.events.testers_are_silent[tester_num].set()

        parts = [p for p in self.log_path.split("/")]
        # if last_values['upload'] == 'Yes':
        #     #TODO add cloud API
        #     return_val = cloud_API(self.wafer_name,parts[3])
        #     logging.debug('Uploaded to cloud? ' + return_val)

        for port in range(len(self.testers_ports)):
            self.tester_threads[port].join()
        self.charger_thread.join()
        self.loop_thread.join()

        global run_data_log
        global run_data_dict
        global run_data_path

        if run_data_log is None:
            run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.TAL15K)
            run_data_log.open_csv()

        run_data_dict['passed'] = passed
        run_data_dict['tested'] = tested
        if tested > 0:  # avoid division by zero
            run_data_dict['yield'] = passed / tested
        if tested == 0:
            run_data_dict['yield'] = -1
        run_data_dict['yieldOverTime'] = self.yield_over_time
        run_data_dict['errors'] = self.errors
        run_data_dict['comments'] = last_values['comments']
        run_data_dict['includingUnderThresholdPassed'] = len(self.transmitted_uniques)
        if tested > 0:  # avoid division by zero
            run_data_dict['includingUnderThresholdYield'] = run_data_dict['includingUnderThresholdPassed'] / tested
        run_data_log.override_run_data(run_data_dict)

        sys.exit(0)

    def continue_fn(self):
        """
        will make the run continue (after exception or pause), triggered by Continue button.
        last location will be fail
        """
        self.look_for_exceptions()
        if not self.events.continue_.isSet():
            logging.debug("Continued by the operator after tester has stopped.")
            with printingLock:
                print("user pressed Continue, the tester will advance now (the last spot will be fail)")

            # self.look_for_exceptions()
            if self.events.pause.isSet():
                self.events.pause.clear()
            self.events.continue_.set()

    def pause_fn(self):
        """
        will make the run pause, triggered by Pause button
        """
        if not self.events.pause.isSet():
            logging.debug("Paused by the operator.")
            with printingLock:
                print("user pressed Pause, the tester will pause now (the current spot will be fail)")
            self.events.pause.set()

    def recurring_timer(self):
        """
        runs all the time: updates the run GUI data, trigger the look_for_exceptions
        @return: none
        """
        global tested
        if self.events.pause.isSet() or self.events.done.isSet():
            self.look_for_exceptions()
            return
        if tested == 0:
            yield_ = -1
            self.reel_label.setText("Wafer Name: " + self.wafer_name)
        else:
            with transmitted_uniquesLock:
                yield_ = len(self.transmitted_uniques) / tested * 100
            if tested > 200 and yield_ < 20 and self.color == 'default':
                self.color == 'red'
                self.w.setAutoFillBackground(True)
                p = self.w.palette()
                p.setColor(self.w.backgroundRole(), Qt.red)
                self.w.setPalette(p)
                self.reel_label.setText(
                    "Wafer Name: " + self.wafer_name + "\nYield is under 20%, STOP and look for errors!!!")
                self.stop_button.setStyleSheet("font-weight: bold; font-size: 25px; background-color: white")
                self.show()
            elif self.color == 'red' and yield_ > 20:
                self.color == 'default'
                self.w.setAutoFillBackground(False)
                self.reel_label.setText("Wafer Name: " + self.wafer_name)
                self.stop_button.setStyleSheet("font-weight: bold; font-size: 25px; background-color: red")
                self.show()
        self.tested.setText('Tested = ' + str(tested) + ', Passed = ' + str(passed) + ', Yield = ' + str(yield_) + '%')
        # update the graph, if there was change in the tested amount
        # because passed and tested are been updated in different time we will check the passed of the prev tag =>
        # tested -1
        if tested > self.last_tested_num:
            if self.batch_size >= tested > self.last_tested_num:
                with transmitted_uniquesLock:
                    self.passed_every_batch.append(len(self.transmitted_uniques) - self.last_passed_num)
            elif tested > 0:
                del self.passed_every_batch[0]
                with transmitted_uniquesLock:
                    self.passed_every_batch.append(len(self.transmitted_uniques) - self.last_passed_num)
            if tested % self.batch_size == 1 and tested > self.batch_size:
                self.y.append(sum(self.passed_every_batch) / self.batch_size * 100)
                self.x = range(len(self.y))
                self.data_line.setData(self.x, self.y)  # Update the data.
                self.yield_over_time.append(int(sum(self.passed_every_batch) / self.batch_size * 100))
        # update the prev counters
        if not self.events.pause.isSet():
            self.look_for_exceptions()

        if tested > self.last_tested_num:
            self.last_tested_num += 1
            self.unconverted_reel_tags_num[-1] += 1
            with transmitted_uniquesLock:
                if len(self.transmitted_uniques) > self.last_passed_num:
                    self.last_passed_num += self.passed_every_batch[
                        -1]  # passed_every_batch might be more than 1 in a cell

    def get_ports_of_gws(self):
        """
        finds and updates self.charger_port and self.testers_ports
        Exceptions:
            'No Tester port was found', 'No Charger port was found'
        """
        ports = list(serial.tools.list_ports.comports())
        charger_found = False
        tester_num = 0
        for p in ports:
            with printingLock:
                print(p)
            if 'USB to UART Bridge' in str(p):
                if 'COM3' in str(p):  # charger  #TODO make sure it is the charger port
                    charger_found = True
                    self.charger_port = p.device
                else:
                    self.testers_ports.append(p.device)
                    tester_num += 1
                with printingLock:
                    print('using the device connected to port ' + str(p))
        if tester_num == 0:
            with printingLock:
                print('No Tester port was found. please connect the Tester GW or call for support')
            raise Exception('No Tester port was found')
        elif not charger_found:
            with printingLock:
                print('No Charger port was found. please connect the Charger GW or call for support')
            raise Exception('No Charger port was found')

    def save_screen_4_tester(self):
        """
        opens last GUI after STOP is pressed
        @return: dict {"upload", "comments"}
        """
        layout = [
            [sg.Text('Would you like to upload this log to the cloud?'),
             sg.InputCombo(('Yes', 'No'), default_value="Yes", key='upload')],
            [sg.Text('Post run comments:')],
            [sg.InputText('', key='comments')],
            [sg.Submit()]]

        window = sg.Window('TAL15K tester closing window', layout)
        event, values = window.read()
        window.close()
        return values

    def look_for_exceptions(self):
        """
        goes over all of the exception queues in all of the threads and looks for exceptions that happened.
        """
        testers_has_exceptions = False
        for port in range(len(self.testers_ports)):
            if not self.tester_threads[port].exception_queue.empty():
                testers_has_exceptions = True
        if testers_has_exceptions or not self.charger_thread.exception_queue.empty() or \
                not self.loop_thread.exception_queue.empty() or not \
                self.exception_queue.empty():
            with printingLock:
                print('!!!!!!!!!!!!!!!! EXCEPTION FOUND !!!!!!!!!!!!!!!!!!!!!!!!!')
            self.handle_tester_exception()
            if not self.events.pause.isSet():
                logging.exception("Paused because an exception happened")
                with printingLock:
                    print("Paused because an exception happened, the tester will pause now")
                self.events.pause.set()
            with printingLock:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    def handle_tester_exception(self):
        """
        handles the exception that were caught by the look_for_exception
        - currently only prints the exceptions
        """

        for port in range(len(self.testers_ports)):
            if not self.tester_threads[port].exception_queue.empty():
                exception_details = self.tester_threads[port].exception_queue.get()
                exc_type, exc_obj, exc_trace = exception_details
                with printingLock:
                    print('tester_threads[' + str(port) + '] got an Exception:')
                logging.exception('tester_threads[' + str(port) + '] got an Exception:')
                print_exception(exception_details, printingLock)
                self.errors.append((self.ports_and_guis.location_in_batch, str(exc_obj)))
        if not self.charger_thread.exception_queue.empty():
            exception_details = self.charger_thread.exception_queue.get()
            exc_type, exc_obj, exc_trace = exception_details
            with printingLock:
                print('charger_thread got an Exception:')
            logging.exception('charger_thread got an Exception:')
            print_exception(exception_details, printingLock)
            self.errors.append((self.ports_and_guis.location_in_batch, str(exc_obj)))
        if not self.exception_queue.empty():  # for main thread
            exception_details = self.exception_queue.get()
            exc_type, exc_obj, exc_trace = exception_details
            with printingLock:
                print('main_thread got an Exception:')
            logging.exception('main_thread got an Exception:')
            print_exception(exception_details, printingLock)
            self.errors.append((self.ports_and_guis.location_in_batch, str(exc_obj)))
        if not self.loop_thread.exception_queue.empty():
            exception_details = self.loop_thread.exception_queue.get()
            exc_type, exc_obj, exc_trace = exception_details
            with printingLock:
                print('loop_thread got an Exception:')
            logging.exception('loop_thread got an Exception:')
            print_exception(exception_details, printingLock)
            self.errors.append((self.ports_and_guis.location_in_batch, str(exc_obj)))


app = QApplication([])
window = MainWindow()
app.exec_()
