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
from datetime import datetime

import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import pyqtgraph as pg
from queue import Queue
from wiliot.gateway_api.gateway import *
from wiliot.wiliot_testers.tester_utils import *
from wiliot.wiliot_testers.offline.offline_utils import *
import time
import os
import threading
import json
from datetime import timedelta
from importlib_metadata import version
import copy
from numpy import mean

# a global variable which will be in the log_file name that says the R2R code version
R2R_code_version = '12'
# running parameters
tested = 0
passed = 0
under_threshold = 0
missing_labels = 0
black_list_size = 0
last_pass_string = 'No tag has passed yet :('

desired_pass_num = 999999999  # this will be set to the desired pass that we want to stop after
desired_tags_num = 999999999  # this will be set to the desired tags that we want to stop after
reel_name = ''
common_run_name = ''
log_path = ''
run_data_path = ''
tags_data_path = ''
debug_tags_data_path = ''
packets_data_path = ''
is_debug_mode = True
debug_tags_data_log = None
packets_data_log = None
tags_data_log = None
run_data_log = None
temperature_sensor_enable = False
problem_in_locations_hist = None
run_data_list = []
run_data_dict = {}
run_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
failed_tags = None  # tags that failed in serialization (updated at the end of the run)

external_id_for_printer = 999999999
yield_over_time = 0
calculate_interval = 10
calculate_on = 50

lock_print = threading.Lock()


class Printer(threading.Thread):
    """
    thread that turns printer on, checks that the print was successful after every tag,

    Parameters:
    @type start_value: int
    @param start_value: first external ID to print on first tag
    @type pass_job_name: str
    @param pass_job_name: the printer pass job name
    @type events: class MainEvents (costume made class that has all of the Events of the program threads)
    @param events: has all of the Events of the program threads
    @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
                        program threads)
    @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:
    @except PrinterNeedsResetException: means that we need to close the program:
            'The printer initialization process has failed in command:...',
            'Printer failed to switch to running mode',
            'The printer over-all-state is Shutdown',
            'The printer over-all-state is Starting up',
            'The printer over-all-state is Shutting down',
            'The printer over-all-state is Offline',
            'reopen_sock() failed'
    @except Exception: operate according to the description:
            'The printer error-state is Warnings present',
            'The printer error-state is Faults present',
            'The printer printed Fail to the previous tag',
            'The printer have not printed on the last tag'

    Events:
        listen/ waits on:
            events.r2r_ready_or_done2tag    => user pressed Stop (end the program)
            events.done_to_printer_thread             => user pressed Stop (end the program) - to avoid deadlock
            events.cont_to_printer_thread             => continue was pressed by user
            events.r2r_ready                => printing was made
            events.was_pass_to_printer      => the last printing was pass
        sets:
            events.printer_error            => the last print was not successful, will cause pause to this run
                                                (and will trigger exception according to the situation)
            events.printer_success          => the last print was successful

    Logging:
        the logging from this thread will be also to logging.debug()
    """

    def __init__(self, start_value, pass_job_name, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(Printer, self).__init__()
        try:
            self.ports_and_guis = ports_and_guis
            self.TCP_BUFFER = self.ports_and_guis.configs_for_printer_values['TCP_BUFFER']
            self.job_name = ''
            self.line_number = ''
            self.sgtin = 'sgtin'
            self.reel_num = 'reel_num'
            self.first_tag_counter = 'tag_number'
            self.pass_counter = 0
            self.fail_counter = 0
            self.printer_response_timeout = 1  # time in seconds for printer to answer with updated printing value
            self.timer_is_done = False
            self.exception_queue = Queue()
            self.printing_format = self.ports_and_guis.Tag_Value['printingFormat']
            self.roll_sgtin = self.ports_and_guis.Tag_Printing_Value['stringBeforeCounter']
            self.events = events
            self.r2r_ready_or_done2tag_or_done_to_printer_thread = or_event_set(events.r2r_ready_or_done2tag,
                                                                                events.done_to_printer_thread)
            self.start_value = start_value
            self.cur_value = 0
            self.pass_job_name = pass_job_name
            self.fail_job_name = self.ports_and_guis.Tag_Printing_Value['failJobName']

            # open the socket & config the printer
            self.initialization()

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def initialization(self, use_current_value=False):
        """
        Initialize Constants and socket
        @param use_current_value: will indicate that this is not the first initialization at this run
                                    (make the next print to continue from the last printed value)
        """
        try:
            cmds = []
            self.ports_and_guis.open_printer_socket()  # will open and connect the socket
            self.set_printer_to_running()
            # after printer crash - make sure the continue will be from a the old counter
            if use_current_value:
                global external_id_for_printer
                config_start_value = external_id_for_printer
            else:
                config_start_value = self.start_value
            # initialization protocol
            if self.printing_format == 'Test':
                cmds = ['CAF\r\n', 'CQI\r\n', 'CLN|1|\r\n', 'CLN|2|\r\n',
                        'LAS|' + str(self.pass_job_name) + '|2|' + str(self.sgtin) + '=' +
                        str(self.roll_sgtin[:18]) + '|' + str(self.reel_num) + '=' + str(self.roll_sgtin[18:26]) +
                        'T' + '|' + str(self.first_tag_counter) + '=' + str(config_start_value) + '|\r\n']
                if self.fail_job_name == self.pass_job_name:
                    cmds.append('LAS|' + str(self.fail_job_name) + '|1|' + str(self.sgtin) + '=' +
                                str(self.roll_sgtin[:18]) + '|' + str(self.reel_num) + '=' +
                                str(self.roll_sgtin[18:26]) + 'T' + '|' + str(self.first_tag_counter) + '=' +
                                str(config_start_value) + '|\r\n')
                else:
                    cmds.append('LAS|' + self.fail_job_name + '|1|\r\n')
            elif self.printing_format == 'SGTIN':
                # SGTIN_QR has field for reel_num + 'T' and field for sgtin,
                # SGTIN_only acts the same (the QR will not be in the sticker itself)
                if self.pass_job_name == 'SGTIN_QR' or self.pass_job_name == 'SGTIN_only' or \
                        self.pass_job_name == 'devkit_TEO' or self.pass_job_name == 'devkit_TIKI' \
                        or self.pass_job_name == 'empty':
                    cmds = ['CAF\r\n', 'CQI\r\n', 'CLN|1|\r\n', 'CLN|2|\r\n',
                            'LAS|' + str(self.pass_job_name) + '|2|' + str(self.sgtin) + '=' + str(
                                self.roll_sgtin[:18]) + '|'
                            + str(self.reel_num) + '=' + str(self.roll_sgtin[18:26]) + 'T' + '|'
                            + str(self.first_tag_counter) + '=' + str(config_start_value) + '|\r\n']
                    if self.fail_job_name == self.pass_job_name:
                        cmds.append('LAS|' + str(self.fail_job_name) + '|1|' + str(self.sgtin) + '=' +
                                    str(self.roll_sgtin[:18]) + '|' + str(self.reel_num) + '=' +
                                    str(self.roll_sgtin[18:26]) + 'T' + '|' + str(self.first_tag_counter) + '=' +
                                    str(config_start_value) + '|\r\n')
                    else:
                        cmds.append('LAS|' + self.fail_job_name + '|1|\r\n')

            else:
                printing_func('The print Job Name inserted is not supported at the moment, You will need to press Stop',
                              'PrinterThread', lock_print, logger_type='debug')

            for cmd in cmds:
                value = self.query(cmd)
                time.sleep(0.1)
                # check if the return value is good, if not retry again for 10 times
                counter = 0
                while counter < 10:
                    # 'CQI' fails if the queue is empty
                    if value == 'ERR' and 'CQI' not in cmd:
                        counter += 1
                        time.sleep(0.1)
                        value = self.query(cmd)
                    else:
                        break
                if counter >= 10:
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer initialization process has failed in command: ' + cmd)
            # get the current counter value
            value = self.query(self.get_state_request())
            if value == 'ERR':
                self.events.printer_error.set()
                raise PrinterNeedsResetException(
                    'The printer initialization process has failed in command: ' + self.get_state_request())
            else:
                parts = [p for p in value.split("|")]
                self.cur_value = int(parts[5])

            if not self.events.printer_error.isSet():
                printing_func('printer thread is ready after initialization',
                              'PrinterThread', lock_print, logger_type='debug')
                self.events.printer_success.set()
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def set_printer_to_running(self):
        """
        sets the printer to running mode
        Zipher Text Communications Protocol
        printer state machine:
           0 -> 1                      shutdown
           1 -> 4 (automatically)      starting-up
           2 -> 0 (automatically)      shutting-down
           3 -> 2, 4                   running
           4 -> 2, 3                   offline
        @except: PrinterNeedsResetException('Printer failed to switch to running mode')
        @return: None
        """
        res = self.query(self.get_state_request())
        parts = [p for p in res.split("|")]
        if parts[1] == '0':  # (Shut down)
            res = self.query(self.set_state_command('1'))
            if res == 'ACK':
                while True:
                    time.sleep(1)
                    res = self.query(self.set_state_command('3'))
                    if res == 'ACK':
                        return
        elif parts[1] == '3':  # (Running)
            return
        elif parts[1] == '4':  # (Offline)
            res = self.query(self.set_state_command('3'))
            if res == 'ACK':
                return

        self.events.printer_error.set()
        raise PrinterNeedsResetException('Printer failed to switch to running mode')

    def run(self):
        """
        runs the thread
        """
        global passed
        # this flag will tell the printer to restart its run() (for a case of connectionError)
        do_the_thread_again = True
        while do_the_thread_again:
            do_the_thread_again = False
            logging.debug('starts printer inner loop')
            while not self.events.done_to_printer_thread.isSet():
                try:
                    self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                    if self.events.done_to_printer_thread.isSet():
                        break

                    # for a case of pause - the printing test should not happen (printing should not happen)
                    if self.events.pause_to_tag_thread.isSet():
                        self.events.cont_to_printer_thread.wait()

                    # to avoid wrong counter in edge cases of printer crash
                    if self.events.cont_to_printer_thread.isSet():
                        self.events.cont_to_printer_thread.clear()
                        # get the current counter value
                        value = self.query(self.get_state_request())
                        if value == 'ERR':
                            self.events.printer_error.set()
                            raise PrinterNeedsResetException(
                                'The printer initialization process has failed in command: ' + self.get_state_request())
                        else:
                            parts = [p for p in value.split("|")]
                            self.cur_value = int(parts[5])

                    self.events.r2r_ready.wait()
                    self.events.r2r_ready.clear()
                    self.cur_value += 1

                    self.printing_happened_as_expected()

                except Exception:
                    exception_details = sys.exc_info()
                    self.exception_queue.put(exception_details)
                    exc_type, exc_obj, exc_trace = exception_details
                    self.events.printer_error.set()  # to avoid deadlocks
                    # ConnectionResetError => exc_obj = 'An existing connection was forcibly closed by the remote host'
                    if isinstance(exc_obj, PrinterNeedsResetException):
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                        break
                    elif isinstance(exc_obj, ConnectionResetError):
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                        try:
                            self.reopen_sock()
                            do_the_thread_again = True
                            self.events.done_to_printer_thread.clear()
                            continue
                        except Exception:
                            printing_func('self.reopen_sock() in printer thread failed, will end this run',
                                          'PrinterThread', lock_print, logger_type='debug')
                            exception_details = sys.exc_info()
                            self.exception_queue.put(exception_details)
                            exc_type, exc_obj, exc_trace = exception_details
                            self.events.printer_error.set()  # to avoid deadlocks
                            if isinstance(exc_obj, PrinterNeedsResetException):
                                self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                                break
                    else:
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()

        self.closure()
        printing_func("Exited the while loop of printer thread", 'PrinterThread', lock_print, logger_type='debug')
        return

    def printing_happened_as_expected(self):
        """
        checks if the printing value matches the values registered to the logs
        should be called only after self.events.r2r_ready was set
        Exceptions:
            @except Exception('The printer printed Pass to the previous tag'):
                    printer printed pass while it should have been print fail
            @except Exception('The printer printed Fail to the previous tag')
                    printer printed fail while it should have been print pass
            @except Exception('The printer have not printed on the last tag')
                    printer did not print while it should have been
        """

        self.timer = threading.Timer(self.printer_response_timeout, self.end_of_time)
        self.timer.start()
        printing_on_last_tag_happened = False

        time.sleep(0.15)  # Empiric tests have shown the answer will not be received until 150ms have passed

        # will try to get the printing status until timer will end
        while not self.timer_is_done and not self.events.done_to_printer_thread.isSet() and\
                not printing_on_last_tag_happened:
            res = self.query(self.get_state_request())
            parts = [p for p in res.split("|")]
            if parts[1] != '3':
                self.timer.cancel()
                self.timer_is_done = False
                if parts[1] == '0':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Shutdown')
                if parts[1] == '1':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Starting up')
                if parts[1] == '2':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Shutting down')
                if parts[1] == '4':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Offline')
            if parts[2] != '0':
                self.timer.cancel()
                self.timer_is_done = False
                if parts[2] == '1':
                    self.events.printer_error.set()
                    raise Exception('The printer error-state is Warnings present')
                if parts[2] == '2':
                    self.events.printer_error.set()
                    raise Exception('The printer error-state is Faults present')
                self.events.printer_error.set()
                break

            # the counter is correct
            if int(parts[5]) == self.cur_value:
                printing_on_last_tag_happened = True
                # the prev tag passed
                if self.events.was_pass_to_printer.isSet():
                    self.events.was_pass_to_printer.clear()
                    # pass was printed
                    if parts[3] == self.pass_job_name:
                        self.events.printer_success.set()
                    else:
                        self.timer.cancel()
                        self.timer_is_done = False
                        self.events.printer_error.set()
                        raise Exception('The printer printed Fail to the previous tag')

                    self.ports_and_guis.update_printer_gui_inputs()  # will add one to last printing value

                # the prev tag failed
                else:
                    self.events.was_fail_to_printer.clear()
                    # fail was printed
                    if parts[3] == self.fail_job_name:
                        self.events.printer_success.set()
                    else:
                        self.timer.cancel()
                        self.timer_is_done = False
                        self.events.printer_error.set()
                        raise Exception('The printer printed Pass to the previous tag')

            time.sleep(0.05)

        self.timer.cancel()
        self.timer_is_done = False

        if not printing_on_last_tag_happened:
            self.events.printer_error.set()
            raise Exception('The printer have not printed on the last tag')

    def end_of_time(self):
        """
        is triggered at the end of timer
        """
        self.timer_is_done = True

    def query(self, cmd, print_and_log=True):
        """Send the input cmd string via TCPIP Socket
        @type cmd: string
        @param cmd: command to send to printer
        @type print_and_log: bool
        @param print_and_log: if true print and log the communication
        @return: the reply string
        """
        if print_and_log:
            msg = "Sent command to printer: " + cmd.strip('\r\n')
            printing_func(msg, 'PrinterThread', lock_print, logger_type='debug')
        self.ports_and_guis.Printer_socket.send(cmd.encode())
        data = self.ports_and_guis.Printer_socket.recv(int(self.TCP_BUFFER))
        value = data.decode("utf-8")
        # Cut the last character as the device returns a null terminated string
        value = value[:-1]
        if print_and_log:
            msg = "Received answer from printer: " + str(value.strip('\r\n'))
            printing_func(msg, 'PrinterThread', lock_print, logger_type='debug')

        return value

    def closure(self):
        """
        set printer to shutting down and close the socket
        """
        try:
            self.query(self.set_state_command('2'))  # for regular closure (not when connection error happens)
            self.ports_and_guis.Printer_socket.close()
        except Exception:
            try:
                self.ports_and_guis.Printer_socket.close()
            except Exception:
                printing_func('s.close() failed', 'PrinterThread', lock_print, logger_type='warning')
                pass

    def reopen_sock(self):
        """
        close and reopens the printer sock
        """
        try:
            self.closure()
            time.sleep(1)  # to make sure the socket is closed when we start the reopen
            self.initialization()
        except Exception:
            printing_func('reopen_sock() failed, please end this run', 'PrinterThread',
                          lock_print, logger_type='warning')
            raise (PrinterNeedsResetException('reopen_sock() failed'))

    def line_assigment(self, job_name, line_number, field_name, field_value):
        """
        builds the command to send to printer for configuration of the printing format
        @param job_name: (string) what is the job name (should be the same as in the printer)
        @param line_number: what is the line to assign to (2 = pass, 1 = fail)
        @param field_name: field name in the printer
        @param field_value: what to put in this field
        @return: the cmd to send to printer
        """
        # Send Line Assignment Command: job name + line number+starting value
        cmd = 'LAS|' + str(job_name) + '|' + str(line_number) + '|' + str(field_name) + '=' + str(
            field_value) + '|\r\n'
        # changing to bytes
        return cmd

    def clear_line(self, line_number):
        """
        builds the command to send to printer for clearing a line
        @param line_number: the line to clear
        @return: the cmd to send to printer
        """
        # On success, returns the default success response (ACK). On failure, returns the default failure response (ERR)
        cmd = 'CLN|' + str(line_number) + '|\r\n'
        return cmd

    def set_state_command(self, desired_state):
        """
        builds the command to send to printer for setting a printer state
        @param desired_state: the state to enter to, according to the following description
        0 Shut down
        1 Starting up
        2 Shutting down
        3 Running
        4 Offline
        @return: the cmd to send to printer
        """
        cmd = 'SST|' + str(desired_state) + '|\r\n'
        return cmd

    def get_job_name(self):
        """
        gets the last job that were used by the printer
        @return: the name of the current job in the printer in the following format:
            JOB|<job name>|<line number>|<CR>
        """
        cmd = 'GJN\r\n'
        return cmd

    def get_state_request(self):
        """
        gets the situation of the printer
        @return: the situation in the printer in the following format:
            STS|<overallstate>|<errorstate>|<currentjob>|<batchcount>|<totalcount>|<
        """
        cmd = 'GST\r\n'
        return cmd


class TagThread(threading.Thread):
    """
    Thread that controls the gateway, tests each tag and saves data to csv output file
    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
                            program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:
        @except Exception: 'Exception happened in Tag thread initialization. need to kill this run'
                means that connecting to GW or temperature sensor failed, the run will pause and wait for
                stop button from user

        @except Exception: 'tag_checker_thread got an Exception, press Continue or Stop'
                exception details will be printed

        @except (OSError, serial.SerialException):
                Problems with GW connection, requires user to press "Stop" and end the run

        @except Exception: exception occurred while testing a tag (inside new_tag function)

        @except Exception('R2R moved before timer ended') :
                Either R2R moved before or received packet is not valid tag packet
                The run will pause

        @except Exception: 'Warning: packet_decoder could not decode packet, will skip it'
                In case encrypted_packet_decoder() failed in decoding packet, packet is skipped and
                threads waits for next packet.
                Run won't pause in that case. If tag reaches timeout, it will marked as fail

    Events:
        listen/ waits on:
            events.r2r_ready_or_done2tag => user pressed Stop (end the program) or r2r has finished to write the command
            events.done_or_printer_event => waits for printer event or for done_to_tag_thread (closes TagThread)
            events.done_to_tag_thread => closes TagThread at the end of the run
            events.cont_to_tag_thread => wait for continue from MainWindow thread
            events.pause_to_tag_thread => pauses thread if exception happened of user pressed Pause
            events.printer_error => the last print was not successful, will cause pause to this run
                                                (and will trigger exception according to the situation)

        sets:
            events.cont_to_main_thread => send continue from TagThread to MainWindow thread
            events.tag_thread_is_ready_to_main => notifies MainWindow thread TagThread is ready
            events.pause_to_tag_thread => pauses thread if exception happened of user pressed Pause
            events.was_pass_to_printer => tag has passed. report "Pass" to printer
            events.was_fail_to_printer => tag has failed. report "Fail" to printer
            events.disable_missing_label_to_r2r_thread => if set, the run will pause if missing label is detected
            events.enable_missing_label_to_r2r_thread => if set, the run will not pause if missing label is detected
                                                        (up to maxMissingLabels set by user)
            events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
            events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception
            events.pass_to_r2r_thread => notify if current tag passed. if set, send pulse on "Pass" GPIO line,
                                         The R2R will advance to next tag
            events.fail_to_r2r_thread => notify if current tag failed. if set, send pulse on "Fail" GPIO line,
                                         The R2R will advance to next tag

    Logging:
        logging to logging.debug(), logging.info() and logging.warning()
    """
    def __init__(self, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(TagThread, self).__init__()
        self.ports_and_guis = ports_and_guis
        self.events = events
        self.test_times_up = False
        self.r2r_response_times_up = False
        self.ttfp_times_up = False
        self.duplication_handling_timer_is_done = False
        self.ttfgp_list = []
        self.tag_list_len = 5000  # TODO - decide how many tags to use here
        self.adv_addr = ''
        self.time_for_duplication_handling = 20  # time in seconds for duplication handling procedure
        # variables for using serialization API
        self.num_of_tags_per_upload_batch = 10
        self.serialization_data_for_all_run = []  # list of data_to_upload lists
        # the tags that have not been started the upload yet
        self.next_batch_to_serialization = {'response': '', 'upload_data': [], 'failed_already': False}
        self.serialization_threads_working = []  # the actual threads that do the serialization
        self.get_new_token = True  # flag to indicate if a new token is needed
        self.time_delta_for_new_token = timedelta(hours=1)  # will generate new token after this time
        self.last_time_token_was_generated = None

        self.pass_job_name = ''  # will be set inside config
        self.to_print = False
        self.printing_value = {'passJobName': None, 'stringBeforeCounter': None, 'digitsInCounter': 10,
                               'firstPrintingValue': '0'}  # will be set in config()
        self.done_or_printer_event = or_event_set(self.events.done_to_tag_thread, events.printer_event)
        self.fetal_error = False
        self.exception_queue = Queue()

        try:
            self.GwObj, self.t = self.config()
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
            printing_func('Exception happened in Tag thread initialization. need to kill this run',
                          'TagThread', lock_print, logger_type='warning')
            # to pause the run if exception happens
            self.events.cont_to_tag_thread.wait()
            self.events.cont_to_tag_thread.clear()
            self.events.pause_to_tag_thread.clear()
            self.events.cont_to_main_thread.set()

        self.time_out_to_missing_label = float(self.value['testTime']) + 10
        self.r2r_timer = ''
        self.timer = ''
        self.timer_for_ttfp = ''
        self.printed_external_id = ''
        self.timer_for_duplication_handling = ''

        self.tag_location = 0
        self.events.tag_thread_is_ready_to_main.set()
        file_path, user_name, password, owner_id, is_successful = check_user_config_is_ok()

    @pyqtSlot()
    def run(self):
        """
        runs the thread
        """
        if self.value['missingLabel'] == 'No':
            self.events.disable_missing_label_to_r2r_thread.set()
            self.is_missing_label_mode = False
        elif self.value['missingLabel'] == 'Yes':
            self.events.enable_missing_label_to_r2r_thread.set()
            self.is_missing_label_mode = True

        self.events.tag_thread_is_ready_to_main.set()
        die = False
        self.missing_labels_in_a_row = 0

        while not die:
            try:
                if self.ports_and_guis.do_serialization:
                    check_serialization_exception_queues(self.serialization_threads_working, printing_lock=lock_print)
                self.events.r2r_ready_or_done2tag.wait()
                if self.events.done_to_tag_thread.is_set():
                    die = True
                else:  # the r2r_ready event happened , done_or_printer_event.wait will happen after start GW
                    # start of tags loop ###########################
                    # the long timer (will cause +1 missing label)
                    self.r2r_response_times_up = False
                    # will wait 10 seconds after the tag timer should have ended
                    # and then will enforce a start_r2r & fail_r2r
                    self.r2r_timer = threading.Timer(self.time_out_to_missing_label, self.end_of_time,
                                                     ['r2r is stuck'])
                    self.r2r_timer.start()
                    if self.ports_and_guis.do_serialization:
                        # check if the serialization process so far are OK
                        check_serialization_exception_queues(self.serialization_threads_working,
                                                             printing_lock=lock_print)
                        check_serialization_response(self.serialization_threads_working)
                    # new_tag will set the events (pass_to_r2r_thread, fail_to_r2r_thread)
                    result = self.new_tag(self.t)
                    if result == 'Exit':
                        die = True
                    self.tag_location += 1
                    # end of tags loop ###############################
                # will upload a batch at the end of the run or after self.num_of_tags_per_upload_batch
                if (len(self.next_batch_to_serialization['upload_data']) ==
                    self.num_of_tags_per_upload_batch or
                    (die and len(self.next_batch_to_serialization['upload_data']) > 0)) \
                        and self.to_print and self.ports_and_guis.do_serialization:

                    self.serialization_data_for_all_run.append(self.next_batch_to_serialization)
                    self.next_batch_to_serialization = {'response': '', 'upload_data': [], 'failed_already': False}
                    check_serialization_exception_queues(self.serialization_threads_working, printing_lock=lock_print)
                    # check when was the last time we generate a new token
                    get_new_token = True
                    if self.last_time_token_was_generated is not None:
                        if self.last_time_token_was_generated - datetime.datetime.now() < \
                                self.time_delta_for_new_token:
                            get_new_token = False
                    else:
                        self.last_time_token_was_generated = datetime.datetime.now()
                    self.serialization_threads_working.append(
                        SerializationAPI(batch_dictionary=self.serialization_data_for_all_run[-1], to_logging=True,
                                         get_new_token=get_new_token,
                                         try_serialize_again=self.events.try_serialize_again, printing_lock=lock_print))
                    self.serialization_threads_working[-1].start()

            except (OSError, serial.SerialException):
                if self.events.done_to_tag_thread.is_set():
                    die = True
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                printing_func("Problems with gateway serial connection - click on Stop and exit the app",
                              'TagThread', lock_print, logger_type='warning')
                self.fetal_error = True
            except Exception:
                if self.events.done_to_tag_thread.is_set():
                    die = True
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                # wait until user press Continue
                if not self.r2r_timer == '':
                    self.r2r_timer.cancel()

                if not die:
                    self.events.cont_to_tag_thread.wait()
                self.events.cont_to_tag_thread.clear()
                self.events.pause_to_tag_thread.clear()
                self.events.cont_to_main_thread.set()
        self.closure_fn()

    def end_of_time(self, kind):
        """
        sets the correct flag to True when a timer is done
        @param kind: the kind of the timer
        """
        if kind == 'tag':
            self.test_times_up = True
            printing_func("Tag reached Time-Out",
                          'TagThread', lock_print, logger_type='debug')
        if kind == 'r2r is stuck':
            self.r2r_response_times_up = True
            printing_func("R2R is stuck, Tag reached Time-Out",
                          'TagThread', lock_print, logger_type='debug')
            logging.debug("R2R is stuck, Tag reached Time-Out")
        if kind == 'no packet arrived':  # ttfp timer
            self.ttfp_times_up = True
            printing_func("First packet did not arrive for more than " + self.value['maxTtfp'] + " seconds",
                          'TagThread', lock_print, logger_type='debug')
        if kind == 'duplication handling':
            self.duplication_handling_timer_is_done = True
            printing_func("Duplication handling timer is over",
                          'TagThread', lock_print, logger_type='debug')

    def config(self):
        """
        configuration of GW, logging and run_data
        @return:  Gw's Com port Obj, temperature sensor
        """
        self.value = self.ports_and_guis.Tag_Value
        if self.value['comments'] == '':
            self.value['comments'] = None

        self.internal_value = self.ports_and_guis.configs_for_gw_values

        self.tags_handling = TagsHandling(self.tag_list_len, lock_print=lock_print,
                                          rssi_threshold=self.internal_value['rssiThreshold'],
                                          logging_thread='TagThread', only_add_tags_after_location_ends=True,
                                          add_to_black_list_after_locations=int(self.value['blackListAfter']))
        # for the case we do not print
        self.externalId = 0
        self.pass_job_name = ''
        global problem_in_locations_hist
        problem_in_locations_hist = self.tags_handling.problem_in_locations_hist
        if self.value['toPrint'] == 'Yes':
            self.to_print = True
            self.printing_value, is_OK = self.ports_and_guis.Tag_Printing_Value, self.ports_and_guis.Tag_is_OK
            self.externalId = int(self.printing_value['firstPrintingValue'])
            self.pass_job_name = self.printing_value['passJobName']

        # setting up the global variables ###################################################
        global desired_pass_num
        global desired_tags_num
        desired_tags_num = int(self.value['desiredTags'])
        desired_pass_num = int(self.value['desiredPass'])

        # config GW, temp sens and classifier ###############################################
        self.GwObj = self.ports_and_guis.GwObj
        # +30 to let us see the high rssi packets in the PC (will be captured in the encrypted_packet_filter())
        self.GwObj.write('!set_energizing_pattern 52')
        time.sleep(0.1)
        self.GwObj.write('!set_energizing_pattern 51')
        time.sleep(0.1)
        self.GwObj.write('!set_tester_mode 1')
        time.sleep(0.1)
        self.GwObj.write('!pl_gw_config 1')
        time.sleep(0.1)
        config_gw(self.GwObj, rssi_threshold=(int(self.internal_value['rssiThreshold']) + 30),
                  energizing_pattern=self.internal_value['energizingPattern'],
                  tx_power=self.internal_value['txPower'], time_profile='0,6',
                  filter_val=False, pacer_val=0, received_channel=37, modulation_val=True,
                  set_interrupt=True, pl_delay=self.internal_value['plDelay'])
        # self.GwObj.check_current_config()  # for debugging
        global temperature_sensor_enable
        if temperature_sensor_enable:
            t = self.ports_and_guis.Tag_t
        else:
            t = None
        self.internal_value['testerStationName'] = self.ports_and_guis.tag_tester_station_name

        global run_data_list
        run_data_list.append(self.value)
        run_data_list.append(self.internal_value)
        run_data_list.append(self.printing_value)
        # run_data_list.append(self.ports_and_guis.test_configs)             # TODO - add this field to run_data
        # run_data_list.append({'wiliotPackageVersion': version('wiliot')})  # TODO - add this field to run_data
        printing_func("wiliot's package version = " + str(version('wiliot')), 'TagThread', lock_print=lock_print,
                      do_log=True)
        global run_start_time
        logging.info('Start time is: ' + run_start_time + ', User set up is: %s, %s, %s',
                     self.value, self.internal_value, self.printing_value)
        global run_data_dict
        global run_data_log

        if run_data_log is None:
            run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.OFFLINE)
            run_data_log.open_csv()
            printing_func("run_data log file has been created",
                          'TagThread', lock_print, logger_type='debug')
        for dic in run_data_list:
            for key in dic.keys():
                if key in run_data_log.header:
                    run_data_dict[key] = dic[key]

        run_data_dict['commonRunName'] = common_run_name
        run_data_dict['testerType'] = 'offline'
        sw_version, _ = self.GwObj.get_gw_version()
        run_data_dict['gwVersion'] = sw_version
        global yield_over_time
        global calculate_interval
        global calculate_on
        global passed
        global tested
        run_data_dict['yieldOverTime'] = yield_over_time
        run_data_dict['yieldOverTimeInterval'] = calculate_interval
        run_data_dict['yieldOverTimeOn'] = calculate_on
        run_data_dict['passed'] = passed
        run_data_dict['tested'] = tested
        if tested > 0:  # avoid division by zero
            run_data_dict['yield'] = passed / tested
        if tested == 0:
            run_data_dict['yield'] = -1.0
            run_data_dict['includingUnderThresholdPassed'] = -1
            run_data_dict['includingUnderThresholdYield'] = -1.0
        run_data_log.append_list_as_row(run_data_log.dict_to_list(run_data_dict))
        return self.GwObj, t

    def new_tag(self, t):
        """
        will run a loop to count the packets for 1 tag and decide pass/fail
        @param t: temperature sensor
        """
        global tags_data_log, debug_tags_data_log, tags_data_path, debug_tags_data_path
        global packets_data_log, packets_data_path
        global under_threshold, missing_labels, temperature_sensor_enable
        global is_debug_mode
        chosen_tag_data_list = []
        debug_chosen_tag_data_list = []
        self.timer, self.timer_for_ttfp, raw_data = '', '', ''
        self.timer_for_duplication_handling = ''
        self.start_GW_happened = False  # will say if the r2r is in place, if not -> busy wait in the while loop
        self.test_times_up = False
        self.ttfp_times_up = False
        self.duplication_handling_timer_is_done = False
        temperature_from_sensor = 0
        self.tag_appeared_before = False

        self.need_to_check_tbp = False
        self.did_change_pattern = False

        def clear_timers():
            if not self.timer == '':
                self.timer.cancel()
                self.test_times_up = False
            if not self.timer_for_ttfp == '':
                self.timer_for_ttfp.cancel()
                self.ttfp_times_up = False
            if not self.r2r_timer == '':
                self.r2r_timer.cancel()
                self.r2r_response_times_up = False
            if not self.timer_for_duplication_handling == '':
                self.timer_for_duplication_handling.cancel()
                self.duplication_handling_timer_is_done = False
        printing_func('************ new tag test ************', 'TagThread',
                      lock_print, logger_type='debug')

        self.GwObj.reset_buffer()
        config_gw(self.GwObj,
                  energizing_pattern=self.internal_value['energizingPattern'],
                  time_profile=self.internal_value['timeProfile'])  # starting to transmit
        # self.GwObj.check_current_config()  # for debugging
        printing_func('Changed the GW duty cycle to ' + str(self.internal_value['timeProfile']), 'TagThread',
                      lock_print, logger_type='debug')

        try:
            clear_timers()
        except Exception as e:
            pass
        current_tag_is_certain = True
        # look for packets as long as user not interrupts AND
        # (test not over OR duplication handling procedure happening)
        while (len(chosen_tag_data_list) < int(self.value['packetThreshold']) and not self.test_times_up and
                not self.r2r_response_times_up and not self.ttfp_times_up or not current_tag_is_certain) and \
                not self.duplication_handling_timer_is_done and \
                not self.events.pause_to_tag_thread.is_set() and \
                not self.events.cont_to_tag_thread.is_set() and not self.events.done_to_tag_thread.is_set():
            time.sleep(0)  # to prevent run slowdown by gateway_api
            if temperature_sensor_enable:
                temperature_from_sensor = t.get_currentValue()

            if not self.start_GW_happened:
                # wait until the GPIO is triggered /max time is done. ignore all packets until done
                gw_answer = self.GwObj.read_specific_message(msg="Start Production Line GW",
                                                             read_timeout=self.time_out_to_missing_label)
                if gw_answer == '':
                    self.r2r_response_times_up = True  # will be treated as missing label
                    break
                # resets the counters
                self.GwObj.reset_buffer()
                self.GwObj.run_packets_listener(tag_packets_only=False, do_process=True)
                printing_func(gw_answer, 'TagThread', lock_print, logger_type='info')
                global tested
                tested += 1
                self.printed_external_id, is_OK = get_printed_value(self.printing_value['stringBeforeCounter'],
                                                                    self.printing_value['digitsInCounter'],
                                                                    str(self.externalId),
                                                                    self.value['printingFormat'])
                if not is_OK:
                    msg = 'printing counter reached a value that is bigger than the counter possible space.' \
                          ' the program will exit now'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                    sys.exit(0)
                msg = "----------------- Tag location: " + str(self.tag_location) + \
                      " ----------------- expected tag external ID is: " + str(self.printed_external_id)
                printing_func(msg, 'TagThread', lock_print, logger_type='info')

                chosen_tag_data_list = []
                debug_chosen_tag_data_list = []

                msg = "New Tag timer started (" + self.value['testTime'] + " secs)"
                printing_func(msg, 'TagThread', lock_print, logger_type='debug')

                # set timer for new tag
                self.timer = threading.Timer(float(self.value['testTime']), self.end_of_time, ['tag'])
                self.timer.start()
                self.timer_for_ttfp = threading.Timer(float(self.value['maxTtfp']), self.end_of_time,
                                                      ['no packet arrived'])
                self.timer_for_ttfp.start()
                self.start_GW_happened = True
                self.tags_handling.set_new_location()
                global black_list_size
                black_list_size = self.tags_handling.get_black_list_size()

            # if we received a packet we will process it and add it to the tag data list
            if self.GwObj.is_data_available():
                gw_answer = self.GwObj.get_data(action_type=ActionType.FIRST_SAMPLES, num_of_packets=1,
                                                data_type=DataType.PROCESSED)
                if gw_answer and \
                        not gw_answer['is_valid_tag_packet'] and "Start Production Line GW" in gw_answer['packet']:
                    if self.start_GW_happened:
                        msg = "gw answer is:" + str(gw_answer)
                        printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                        clear_timers()  # verify times are cleared before next tag
                        raise Exception('R2R moved before timer ended')
                elif gw_answer and gw_answer['is_valid_tag_packet']:
                    # for the tag to keep running until the end of main timer if there was any packet
                    self.timer_for_ttfp.cancel()
                    # in packet decoder we will decide the correct way to decode the packet
                    try:
                        raw_data = encrypted_packet_decoder(gw_answer)
                        self.adv_addr = raw_data['advAddress']
                        raw_data['tagLocation'] = self.tag_location
                        raw_data['commonRunName'] = common_run_name
                        raw_data['externalId'] = self.printed_external_id
                        logging.info('packet_decoder result is: ' + str(raw_data))
                    except Exception:
                        msg = 'Warning: packet_decoder could not decode packet, will skip it'
                        printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                        continue
                    # this will make sure that we do not have any duplication
                    # count when there are two new tags simultaneously
                    self.is_good_packet, self.need_to_check_tbp, packet_status = \
                        self.tags_handling.encrypted_packet_filter(gw_answer)

                    if temperature_sensor_enable:
                        logging.info('%s' % gw_answer + ', temperatureFromSensor = ' + str(temperature_from_sensor))
                        raw_data['temperatureFromSensor'] = t.get_currentValue()

                    # to open longer timer for understanding what is the current tag
                    if self.need_to_check_tbp and current_tag_is_certain:
                        current_tag_is_certain = False
                        clear_timers()
                        self.timer_for_duplication_handling = threading.Timer(self.time_for_duplication_handling,
                                                                              self.end_of_time,
                                                                              ['duplication handling'])
                        self.timer_for_duplication_handling.start()
                        msg = "Need more time to decide what tag is transmitting (due to duplication/ " \
                              "no singularization issue) will open a long timer (" +\
                              str(self.time_for_duplication_handling) + " seconds) for this location and " \
                                                                        "will proceed when it is done"
                        printing_func(msg, 'TagThread', lock_print, do_log=True, logger_type='warning')

                    raw_data['packetStatus'] = packet_status
                    if is_debug_mode:
                        debug_raw_data = copy.deepcopy(raw_data)
                        debug_raw_data['packetStatus'] = packet_status
                        debug_chosen_tag_data_list.append(debug_raw_data)

                    if not self.is_good_packet:
                        continue
                    chosen_tag_data_list.append(raw_data)
                    if 'advAddress' in raw_data.keys():
                        msg = "------- Tag location: " + str(self.tag_location) + " -------" + \
                              "------- Tag advAddress: " + str(raw_data['advAddress']) + " -------"
                        printing_func(msg, 'TagThread', lock_print, do_log=True, logger_type='info')

                    printing_func(str(gw_answer), 'TagThread', lock_print, do_log=True, logger_type='debug')
                    # make the GW do only 900MHz energy pattern in order to test
                    # sub1G harvester (after calibration from first packet)
                    if 'Dual' in self.value['inlayType'] and not self.did_change_pattern:
                        self.did_change_pattern = True
                        config_gw(self.GwObj,
                                  energizing_pattern=self.internal_value['secondEnergizingPattern'],
                                  time_profile='0,6')
                        # self.GwObj.check_current_config()  # for debugging
                        # in order to clean all previous packets
                        sleep(0.005)  # the max amount of time per rdr (end of energy until transmission)
                        self.GwObj.reset_buffer()
                        config_gw(self.GwObj,
                                  energizing_pattern=self.internal_value['secondEnergizingPattern'],
                                  time_profile=self.internal_value['timeProfile'])
                        # restart the timer of ttfp
                        # the long timers will continue to count from the beginning of this test
                        if self.timer_for_ttfp is not '':
                            self.timer_for_ttfp.cancel()
                        self.ttfp_times_up = False
                        # to make sure the duplication handling will not end in the middle
                        if self.timer_for_duplication_handling is not '':
                            self.timer_for_ttfp = threading.Timer(float(self.value['maxTtfp']), self.end_of_time,
                                                                  ['no packet arrived'])
                            self.timer_for_ttfp.start()

        # end of packet loop ########################################

        # close packets listeners:
        self.GwObj.stop_processes()  # run_packet_listener will restart the listening at the start of the next iteration
        self.GwObj.reset_buffer()
        packets_time_diff = None

        # stop transmitting energy:
        if 'Dual' in self.value['inlayType'] and self.did_change_pattern:
            self.did_change_pattern = False  # double check
            config_gw(self.GwObj,
                      energizing_pattern=self.internal_value['energizingPattern'],
                      time_profile='0,6')
            # self.GwObj.check_current_config()  # for debugging
            printing_func('Changed the GW duty cycle to 0,6 and energizing pattern back to '
                          + str(self.internal_value['energizingPattern']), 'TagThread',
                          lock_print, logger_type='debug')
        else:
            config_gw(self.GwObj, time_profile='0,6')
            # self.GwObj.check_current_config()  # for debugging
            printing_func('Changed the GW duty cycle to 0,6 - stop transmitting', 'TagThread',
                          lock_print, logger_type='debug')

        # to resolve what is the tag that was tested
        if not current_tag_is_certain:
            self.adv_addr, self.tag_appeared_before, packets_time_diff = \
                self.tags_handling.get_estimated_tag_in_location()
            # for the case of no packet was received
            if self.adv_addr is None:
                chosen_tag_data_list = []
            else:
                # this will pass tags that transmitted enough packets even if it was received after the timer ended
                # this is a temporary fix so the post-process will not collapse
                df_chosen_tag_data_list = pd.DataFrame(chosen_tag_data_list)
                chosen_tag_data_list = (df_chosen_tag_data_list.loc[df_chosen_tag_data_list['advAddress'] ==
                                                                    self.adv_addr]).to_dict('records')
        # adding the packets from this location to packets_data_log
        if packets_data_log is None:
            packets_data_log = CsvLog(header_type=HeaderType.PACKETS, path=packets_data_path,
                                      tester_type=TesterName.OFFLINE,
                                      temperature_sensor=temperature_sensor_enable)
            packets_data_log.open_csv()
            printing_func("packets_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
        desired_keys = ['externalId', 'tagLocation', 'packetStatus', 'temperatureFromSensor', 'commonRunName',
                        'encryptedPacket', 'time']
        chosen_tag_in_location = None
        if len(chosen_tag_data_list) > 0:
            packets_data = process_encrypted_tags_data(data=chosen_tag_data_list,
                                                       packet_threshold=int(self.value['packetThreshold']),
                                                       fail_this_tag=self.tag_appeared_before,
                                                       adv_of_selected_tag=self.adv_addr)
            chosen_tag_status = packets_data['status']
            chosen_tag_in_location = chosen_tag_data_list[0]['advAddress']
        else:
            chosen_tag_status = 'Failed'

        for i in range(len(debug_chosen_tag_data_list)):
            tmp_packet_dict = {'chosenTagInLocation': chosen_tag_in_location,
                               'chosenTagStatus': chosen_tag_status}

            for key in debug_chosen_tag_data_list[i]:
                if key == 'packet_time':
                    tmp_packet_dict['time'] = debug_chosen_tag_data_list[i][key]
                if key == 'raw_data':
                    tmp_packet_dict['encryptedPacket'] = debug_chosen_tag_data_list[i][key]
                elif key in desired_keys:
                    tmp_packet_dict[key] = debug_chosen_tag_data_list[i][key]
            packets_data_log.append_list_as_row(packets_data_log.dict_to_list(tmp_packet_dict))

        # for the previous tag print - make sure the last tag was printed:
        if self.to_print:
            self.done_or_printer_event.wait()

        # run several checks before moving to the next tag:
        # ------------------------------------------------
        # check if the stop button was pressed:
        if self.events.done_to_tag_thread.is_set():
            clear_timers()
            self.events.was_fail_to_printer.set()  # to avoid deadlock
            logging.info("The User pressed STOP")
            logging.debug('stop pressed after start GW happened. the last tag will be ignored')
            return 'Exit'
        # check if the pause button was pressed:
        elif self.events.pause_to_tag_thread.isSet():
            if self.events.done_to_tag_thread.isSet():
                clear_timers()
                return
            else:
                clear_timers()
                self.events.cont_to_tag_thread.wait()
                self.events.cont_to_tag_thread.clear()
                self.events.pause_to_tag_thread.clear()
                self.events.cont_to_main_thread.set()
        # check if the continue button was pressed:
        elif self.events.cont_to_tag_thread.isSet():
            # for the case that the Button was pressed after a long time (the token expires)
            # check when was the last time we generate a new token
            get_new_token = True
            if self.last_time_token_was_generated is not None:
                if self.last_time_token_was_generated - datetime.datetime.now() < \
                        self.time_delta_for_new_token:
                    get_new_token = False
            else:
                self.last_time_token_was_generated = datetime.datetime.now()
            if get_new_token:
                if not get_new_token_api():
                    printing_func('get_new_token_api() failed', 'TagThread', lock_print, logger_type='warning')

            self.events.cont_to_tag_thread.clear()
            self.events.pause_to_tag_thread.clear()
            self.events.cont_to_main_thread.set()
        # check if we received enough packets to pass the current tag:
        elif len(chosen_tag_data_list) >= int(self.value['packetThreshold']) and not self.tag_appeared_before:
            self.missing_labels_in_a_row = 0
            printing_func('Tag reached packet Threshold', 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
            data = packets_data
            if tags_data_log is None:
                tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                       tester_type=TesterName.OFFLINE,
                                       temperature_sensor=temperature_sensor_enable)
                tags_data_log.open_csv()
                printing_func("tags_data log file has been created", 'TagThread',
                              lock_print, do_log=False, logger_type='debug')
            tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))

            if is_debug_mode:
                debug_data = process_encrypted_tags_data(data=debug_chosen_tag_data_list,
                                                         packet_threshold=int(self.value['packetThreshold']),
                                                         fail_this_tag=self.tag_appeared_before,
                                                         is_debug_mode=True,
                                                         packets_time_diff=packets_time_diff,
                                                         adv_of_selected_tag=self.adv_addr)
                if debug_tags_data_log is None:
                    debug_tags_data_log = CsvLog(header_type=HeaderType.TAG, path=debug_tags_data_path,
                                                 tester_type=TesterName.OFFLINE,
                                                 temperature_sensor=temperature_sensor_enable,
                                                 is_debug_mode=is_debug_mode)
                    debug_tags_data_log.open_csv()
                    printing_func("debug_tags_data log file has been created", 'TagThread',
                                  lock_print, do_log=False, logger_type='debug')
                debug_tags_data_log.append_list_as_row(debug_tags_data_log.dict_to_list(debug_data))

            printing_func("The data to the classifier is: " + str(data), 'TagThread',
                          lock_print, do_log=False, logger_type='info')            # the tag is good
            self.printed_external_id, is_OK = get_printed_value(self.printing_value['stringBeforeCounter'],
                                                                self.printing_value['digitsInCounter'],
                                                                str(self.externalId), self.value['printingFormat'])
            if not is_OK:
                clear_timers()
                msg = 'printing counter reached a value that is bigger than the counter possible space.' \
                      ' the program will exit now'
                printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                sys.exit(0)
            if temperature_sensor_enable:
                try:
                    msg = "*****************Tag with advAddress " + str(raw_data['advAddress']) + \
                          " has passed, tag location is " + str(self.tag_location) + ' , ' + \
                          str({'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                               'temperatureFromSensor': data['temperatureFromSensor']}) + '*****************'
                    printing_func(msg, 'TagThread', lock_print, logger_type='info')

                except Exception:
                    clear_timers()
                    msg = "*****************Tag with advAddress " + str(raw_data['advAddress']) + \
                          " has passed, tag location is " + str(self.tag_location) + ' , ' + \
                          str({'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                               'temperatureFromSensor': data['temperatureFromSensor']}) + '*****************'
                    printing_func(msg, 'TagThread', lock_print, logger_type='info')
            else:
                try:
                    msg = "*****************Tag with advAddress " + str(raw_data['advAddress']) + \
                          " has passed, tag location is " + str(self.tag_location) + ' , ' + \
                          str({'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id}) +\
                          '*****************'
                    printing_func(msg, 'TagThread', lock_print, logger_type='info')

                except Exception:
                    clear_timers()
                    msg = "*****************Tag with advAddress " + str(raw_data['advAddress']) + \
                          " has passed, tag location is " + str(self.tag_location) + ' , ' + \
                          str({'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id}) +\
                          '*****************'
                    printing_func(msg, 'TagThread', lock_print, logger_type='info')

            if not self.to_print:
                self.events.r2r_ready.clear()
            self.events.pass_to_r2r_thread.set()
            global passed
            passed += 1
            global last_pass_string
            last_pass_string = 'last pass tag\nadvAddress: ' + str(self.adv_addr) + ', tag location: ' + str(
                self.tag_location) + ', external ID: ' + self.printed_external_id
            if self.to_print:
                self.events.was_pass_to_printer.set()
                self.externalId += 1

                payload = raw_data['raw_data']
                if self.ports_and_guis.do_serialization:
                    if len(self.next_batch_to_serialization['upload_data']) == 0:
                        self.next_batch_to_serialization = {'response': '',
                                                            'upload_data': [{"payload": payload,
                                                                             "tagId": self.printed_external_id}],
                                                            'writing_lock': threading.Lock(), 'failed_already': False}
                    else:
                        self.next_batch_to_serialization['upload_data'].append({"payload": payload,
                                                                                "tagId": self.printed_external_id})
            else:
                self.externalId += 1
            if packets_data['Ttfgp'] is not None:
                self.ttfgp_list.append(float(packets_data['Ttfgp']))

        # tag did not transmit for too long (self.value['maxTtfp']
        elif self.ttfp_times_up:
            if self.start_GW_happened:
                self.missing_labels_in_a_row = 0
            logging.debug("Tag has failed! did not transmit for {} seconds".format(str(self.value['maxTtfp'])))

            if not self.to_print:
                self.events.r2r_ready.clear()
            self.events.fail_to_r2r_thread.set()
            if self.to_print:
                self.events.was_fail_to_printer.set()
        # time is up  - tag failed
        elif self.start_GW_happened:
            self.missing_labels_in_a_row = 0
            logging.debug("Tag time is over.")
            # write the data of the tag in case it failed with packets
            if len(chosen_tag_data_list) > 0:
                data = packets_data
                under_threshold += 1
                if tags_data_log is None:
                    tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                           tester_type=TesterName.OFFLINE,
                                           temperature_sensor=temperature_sensor_enable)
                    tags_data_log.open_csv()
                    printing_func("tags_data log file has been created", 'TagThread',
                                  lock_print, do_log=False, logger_type='debug')
                tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))
                printing_func("The data to the classifier is: " + str(data), 'TagThread',
                              lock_print, do_log=False, logger_type='info')

            if is_debug_mode and len(debug_chosen_tag_data_list) > 0:
                adv_of_selected_tag = None
                if len(chosen_tag_data_list) > 0:
                    df = pd.DataFrame(chosen_tag_data_list)
                    adv_of_selected_tag = df['advAddress'].iloc[0]

                debug_data = process_encrypted_tags_data(data=debug_chosen_tag_data_list,
                                                         packet_threshold=int(self.value['packetThreshold']),
                                                         fail_this_tag=True,
                                                         is_debug_mode=True,
                                                         packets_time_diff=packets_time_diff,
                                                         adv_of_selected_tag=adv_of_selected_tag)
                if debug_tags_data_log is None:
                    debug_tags_data_log = CsvLog(header_type=HeaderType.TAG, path=debug_tags_data_path,
                                                 tester_type=TesterName.OFFLINE,
                                                 temperature_sensor=temperature_sensor_enable,
                                                 is_debug_mode=is_debug_mode)
                    debug_tags_data_log.open_csv()
                    printing_func("debug_tags_data log file has been created", 'TagThread',
                                  lock_print, do_log=False, logger_type='debug')
                debug_tags_data_log.append_list_as_row(debug_tags_data_log.dict_to_list(debug_data))

            # write the log if there were any packets.
            if len(chosen_tag_data_list) > 0:
                if 'tag_id' in raw_data.keys():
                    logging.info("Tag {} has failed!".format(str(raw_data['tag_id'])))
                elif 'advAddress' in raw_data.keys():
                    logging.info("Tag with advAddress {} has failed!".format(str(raw_data['advAddress'])))
            if not self.to_print:
                self.events.r2r_ready.clear()
            self.events.fail_to_r2r_thread.set()
            if self.to_print:
                self.events.was_fail_to_printer.set()
        # missing label
        elif self.r2r_response_times_up:
            self.start_GW_happened = False

            msg = 'R2R has not move for ' + str(self.time_out_to_missing_label) +\
                  ' seconds , enforce a start_r2r & fail_r2r (the last spot will be fail)'
            printing_func(msg, 'TagThread', lock_print, logger_type='debug')
            missing_labels += 1

            # will take care of the missing labels in a row situation
            if self.missing_labels_in_a_row > 0:
                self.missing_labels_in_a_row += 1
            else:
                self.missing_labels_in_a_row = 1

            if self.events.done_to_tag_thread.isSet():
                clear_timers()
                return
            else:
                if not self.is_missing_label_mode:
                    msg = 'missing label has been detected. The R2R will stop now'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                    printing_func('Please check the reel is OK and press Continue', 'TagThread', lock_print,
                                  do_log=False, logger_type='warning')
                    self.events.stop_to_r2r_thread.set()
                    self.events.cont_to_tag_thread.wait()
                    self.missing_labels_in_a_row = 0
                    self.events.cont_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                elif self.missing_labels_in_a_row > int(self.value['maxMissingLabels']):
                    msg = str(self.missing_labels_in_a_row) \
                          + ' missing labels in a row has been detected. The R2R will stop now'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                    printing_func('Please check the reel is OK and press Continue', 'TagThread', lock_print,
                                  do_log=False, logger_type='warning')
                    self.events.stop_to_r2r_thread.set()
                    self.events.cont_to_tag_thread.wait()
                    self.missing_labels_in_a_row = 0
                    self.events.cont_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                else:
                    msg = str(self.missing_labels_in_a_row) + ' missing labels in a row has been detected'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                    if not self.to_print:
                        self.events.r2r_ready.clear()
                    self.events.start_to_r2r_thread.set()
        # check if printer error occurs:
        elif self.to_print:  # will use it only before self.start_GW_happened
            self.done_or_printer_event.wait()
            if self.events.done_to_tag_thread.isSet():
                clear_timers()
                return
            # to make sure that the tag thread will not proceed if an error occur
            if self.events.printer_error.isSet():
                if self.events.done_to_tag_thread.isSet():
                    clear_timers()
                    return
                else:
                    self.events.cont_to_tag_thread.wait()
                    self.events.cont_to_tag_thread.clear()
                    self.events.pause_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                    self.events.printer_error.clear()
            else:
                self.events.printer_success.clear()

        # doing it last for the case of printer crash in the middle of the new_tag()
        global external_id_for_printer
        external_id_for_printer = self.externalId
        clear_timers()

    def closure_fn(self):
        """
           turn off the GW (reset) and closes the GW Comport
           Logging:
               'User pressed Stop!'
           """
        global failed_tags, run_data_dict, problem_in_locations_hist
        # for the case that the Button was pressed after a long time (the token expires)
        if not get_new_token_api():
            printing_func('get_new_token_api() failed', 'TagThread', lock_print, logger_type='warning')
        if self.ports_and_guis.do_serialization:
            failed_tags = close_all_serialization_processes_when_they_done(
                self.serialization_threads_working, to_logging=True, printing_lock=lock_print,
                try_serialize_again=self.events.try_serialize_again)
            # run_data_dict['TagsFaildSerialization'] = failed_tags  # TODO add this lines to save tags that failed serialization
        problem_in_locations_hist = self.tags_handling.problem_in_locations_hist
        self.GwObj.stop_processes()
        self.GwObj.reset_buffer()
        self.GwObj.write('!reset')
        self.GwObj.close_port(is_reset=True)
        printing_func("TagThread is done", 'TagThread',
                      lock_print, logger_type='debug')


class R2RThread(threading.Thread):
    """
    Thread that controls R2R machine

    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
              program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:

    @except Exception: 'r2r_thread got an Exception, press Continue or Stop'
            exception details will be printed
            Exception might be either:
                1. Send GPIO pulse failed
                2. GPIO pulse was sent twice

    Events:
        listen/ waits on:
        events.done_or_stop => event that equals to (events.done_to_r2r_thread OR events.stop_to_r2r_thread)
        events.done_to_r2r_thread => kills R2R thread main loop if set
        events.pass_to_r2r_thread => notify if current tag passed. if set, send pulse on "Pass" GPIO line
        events.fail_to_r2r_thread => notify if current tag failed. if set, send pulse on "Fail" GPIO line
        events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
        events.enable_missing_label_to_r2r_thread => notify if missing label mode is enabled
            (skips current tag location in case of missing label up to maxMissingLabels set by user)


        sets:
        events.r2r_ready => notify if R2R in ready for movement
        events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception

    Logging:
        the logging from this thread will be to logging.debug()
        """
    def __init__(self, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(R2RThread, self).__init__()

        self.exception_queue = Queue()
        self.events = events
        self.done_or_stop = or_event_set(self.events.done_to_r2r_thread, self.events.stop_to_r2r_thread)
        self.r2r_events_or = or_event_set(self.events.pass_to_r2r_thread, self.events.fail_to_r2r_thread,
                                          self.events.start_to_r2r_thread, self.done_or_stop,
                                          self.events.enable_missing_label_to_r2r_thread)
        self.en_missing_label = False
        self.ports_and_guis = ports_and_guis

        self.my_gpio = self.ports_and_guis.R2R_myGPIO

    @pyqtSlot()
    def run(self):
        """
        runs the thread
        """
        die = False
        while not die:
            try:
                self.r2r_events_or.wait()
                if self.done_or_stop.is_set():
                    self.my_gpio.gpio_state(3, "OFF")
                    msg = "PC send stop to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.events.stop_to_r2r_thread.clear()
                    if self.events.done_to_r2r_thread.isSet():
                        die = True
                if self.events.pass_to_r2r_thread.is_set():
                    self.my_gpio.pulse(1, 50)
                    msg = "^^^^^^^^^^^^^^^^^^ PC send pass to R2R ^^^^^^^^^^^^^^^^^^"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.events.pass_to_r2r_thread.clear()
                    self.events.r2r_ready.set()
                if self.events.fail_to_r2r_thread.is_set():
                    self.my_gpio.pulse(2, 50)
                    msg = "PC send fail to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.events.fail_to_r2r_thread.clear()
                    self.events.r2r_ready.set()
                if self.events.start_to_r2r_thread.is_set():
                    if self.en_missing_label:
                        self.my_gpio.gpio_state(3, "OFF")
                        time.sleep(0.5)  # just to be on the safe side
                    self.my_gpio.gpio_state(3, "ON")
                    time.sleep(0.5)  # just to be on the safe side
                    self.my_gpio.pulse(2, 50)
                    if self.en_missing_label:
                        msg = "PC send stop + start + fail to R2R"
                        printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    else:
                        msg = "PC send start + fail to R2R"
                        printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.events.start_to_r2r_thread.clear()
                    self.events.r2r_ready.set()
                if self.events.enable_missing_label_to_r2r_thread.is_set():
                    self.my_gpio.gpio_state(4, "ON")
                    msg = "PC send 'enable missing label' to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.events.enable_missing_label_to_r2r_thread.clear()
                    self.en_missing_label = True
                if self.events.disable_missing_label_to_r2r_thread.is_set():
                    self.my_gpio.gpio_state(4, "OFF")
                    msg = "PC send 'disable missing label' to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.events.disable_missing_label_to_r2r_thread.clear()
                    self.en_missing_label = False
            except Exception:
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                self.events.stop_to_r2r_thread.set()  # to avoid from the run to continue printing in this case
                self.events.cont_to_tag_thread.wait()


class MainEvents:
    """
    Contains events that connect between all threads
    Events are set or cleared by threads
    Events are divided to four primary groups:
        1. TagThread events
        2. MainWindow events
        3. R2R (reel to reel machine) events
        4. Printer events

    Parameters: None
    Exceptions: None
    Events: None
    Logging: None
    """
    def __init__(self):
        """
        Initialize the events for the entire run
        """

        # set by tag_checker
        self.pass_to_r2r_thread = threading.Event()
        self.fail_to_r2r_thread = threading.Event()
        # set by main
        self.start_to_r2r_thread = threading.Event()
        self.stop_to_r2r_thread = threading.Event()
        self.cont_to_tag_thread = threading.Event()
        # only to be sure we initialize the counters to the printer counter
        self.cont_to_printer_thread = threading.Event()
        self.cont_to_main_thread = threading.Event()
        self.pause_to_tag_thread = threading.Event()
        self.enable_missing_label_to_r2r_thread = threading.Event()
        self.disable_missing_label_to_r2r_thread = threading.Event()
        self.done_to_tag_thread = threading.Event()
        self.done_to_printer_thread = threading.Event()
        self.done2r2r_ready = threading.Event()
        self.done_to_r2r_thread = threading.Event()
        self.tag_thread_is_ready_to_main = threading.Event()
        self.try_serialize_again = threading.Event()

        # set by r2r
        # both printer and tag thread will wait on it. only printer will .clear() it (in printing mode)
        self.r2r_ready = threading.Event()

        # printer events
        self.was_pass_to_printer = threading.Event()
        self.was_fail_to_printer = threading.Event()
        self.printer_success = threading.Event()
        self.printer_error = threading.Event()
        self.printer_event = or_event_set(self.printer_success, self.printer_error)

        # being used in printer thread too
        self.r2r_ready_or_done2tag = or_event_set(self.r2r_ready, self.done2r2r_ready)


class PortsAndGuis:
    """
    class which is responsible for initializing peripheral's ports and get data from run GUIs

    Parameters: None
    Exceptions: None
    Events: None
    Logging: None
    """
    def __init__(self):
        """
        Initialize the runs ports and gets data from the guis
        """

        # run values (1st GUI)
        self.Tag_Value = open_session()

        # Getting the config values
        self.init_config_values()

        # for Tag thread ###########

        # printing values (2nd GUI)
        self.do_serialization = False
        if self.Tag_Value['toPrint'] == 'Yes':
            self.to_print = True
            self.do_serialization = True
            if self.Tag_Value['printingFormat'] == 'Test':
                self.Tag_Printing_Value, self.Tag_is_OK = printing_test_window()
                if not self.Tag_is_OK:
                    msg = 'Impossible printing values entered by the user, the program will exit now'
                    printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
                    sys.exit(0)
                self.do_serialization = False
            elif self.Tag_Value['printingFormat'] == 'SGTIN':
                self.Tag_Printing_Value, self.Tag_is_OK = printing_sgtin_window()
                if not self.Tag_is_OK:
                    msg = 'user exited the program'
                    printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
                    sys.exit(0)
            else:
                msg = 'user chose unsupported printing format!!!'
                printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
        # path for log file
        new_path = 'logs/' + str(self.Tag_Value['batchName'])
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        global log_path, R2R_code_version
        global run_start_time, common_run_name
        global reel_name
        reel_name = self.Tag_Value['batchName']
        common_run_name = reel_name + run_start_time
        self.Tag_pathForLog = new_path + '/' + common_run_name + '@ver=' + R2R_code_version + '.log'
        self.Tag_pathForLog = self.Tag_pathForLog.replace(':', '-')
        log_path = self.Tag_pathForLog
        # save the reel & log name for upload to the cloud at the end

        logging.basicConfig(filename=log_path, filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S', level=logging.DEBUG)
        self.auto_attenuator_enable = False

        self.config_equipment(temperature_sensor=True, attenuator=True)

        # check if the system variable exist
        assert ('testerStationName' in os.environ), 'testerStationName is missing from PC environment variables, ' \
                                                    'please add it in the following convention:' \
                                                    ' <company name>_<tester number>'
        self.tag_tester_station_name = os.environ['testerStationName']
        # serial for GW
        self.GwObj = WiliotGateway(auto_connect=True, logger_name='root', lock_print=lock_print)
        ver, __ = self.GwObj.get_gw_version()
        assert (int(ver.split('.')[0]) >= 2 and int(ver.split('.')[1]) >= 5 and int(ver.split('.')[2][0]) >= 1), \
            'GW version should be at least 2.5.1 to support accurate timing measurement'
        # for Printer thread ###########
        self.Printer_socket = ''  # will only be opened by the thread
        if self.Tag_Value['printingFormat'] == 'Test':
            self.filename = 'gui_printer_inputs_4_Test_do_not_delete.json'
        elif self.Tag_Value['printingFormat'] == 'SGTIN':
            self.filename = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'

        else:
            msg = 'The print Job Name inserted is not supported at the moment, You will need to press Stop'
            printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')

        # check printing configs and save it locally
        folder_path = 'configs'
        self.data_for_printing = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, self.filename),
                                           default_values=DefaultGUIValues(
                                               self.Tag_Value['printingFormat']).default_gui_values)

        # create log filenames
        global run_data_path, tags_data_path, packets_data_path, debug_tags_data_path
        self.tags_data_path = new_path + '/' + common_run_name + '@offline_tester@tags_data' + \
                                                                 '@ver=' + R2R_code_version + '.csv'
        self.tags_data_path = self.tags_data_path.replace(':', '-')
        self.debug_tags_data_path = new_path + '/' + common_run_name + '@offline_tester@debug_tags_data' + \
                                                                       '@ver=' + R2R_code_version + '.csv'
        self.debug_tags_data_path = self.debug_tags_data_path.replace(':', '-')
        self.run_data_path = new_path + '/' + common_run_name + '@offline_tester@run_data' + \
                                                                '@ver=' + R2R_code_version + '.csv'
        self.run_data_path = self.run_data_path.replace(':', '-')
        self.packets_data_path = new_path + '/' + common_run_name + '@offline_tester@packets_data@ver=' + \
                                                                    R2R_code_version + '.csv'
        self.packets_data_path = self.packets_data_path.replace(':', '-')
        run_data_path = self.run_data_path
        tags_data_path = self.tags_data_path
        debug_tags_data_path = self.debug_tags_data_path
        packets_data_path = self.packets_data_path
        # create log files
        global tags_data_log, debug_tags_data_log, is_debug_mode, packets_data_log
        if tags_data_log is None:
            tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path, tester_type=TesterName.OFFLINE,
                                   temperature_sensor=temperature_sensor_enable)
            tags_data_log.open_csv()
            printing_func("tags_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
        if is_debug_mode and debug_tags_data_log is None:
            debug_tags_data_log = CsvLog(header_type=HeaderType.TAG, path=debug_tags_data_path,
                                         tester_type=TesterName.OFFLINE,
                                         temperature_sensor=temperature_sensor_enable,
                                         is_debug_mode=is_debug_mode)
            debug_tags_data_log.open_csv()
            printing_func("debug_tags_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
        if packets_data_log is None:
            packets_data_log = CsvLog(header_type=HeaderType.PACKETS, path=packets_data_path,
                                      tester_type=TesterName.OFFLINE, temperature_sensor=temperature_sensor_enable)
            packets_data_log.open_csv()
            printing_func("packets_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
        # for R2R thread ###########
        self.R2R_myGPIO = R2rGpio()

    def open_printer_socket(self):
        """
        opens the printer socket
        """
        self.Printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Printer_socket.connect((self.configs_for_printer_values['TCP_IP'],
                                     int(self.configs_for_printer_values['TCP_PORT'])))

    def update_printer_gui_inputs(self):
        """
        save the last pass value for crash support.
        passed global variable will be updated at tag Thread and should be correct here
        """
        self.data_for_printing['firstPrintingValue'] = str(int(self.data_for_printing['firstPrintingValue']) + 1)
        file_path = os.path.join('configs', self.filename)
        json.dump(self.data_for_printing, open(file_path, "w"))

    def init_config_values(self):
        """
        initialize the config values for the run
        """
        self.dir_config = 'configs'
        self.configs_for_gw_file_values_path = self.dir_config + '/configs_for_gw_values.json'
        self.configs_for_gw_file_values_path_dual_band = self.dir_config + '/configs_for_gw_values_dual_band.json'
        config_defaults = ConfigDefaults()
        if 'Dual' in self.Tag_Value['inlayType']:
            self.configs_for_gw_values = open_json(self.dir_config, self.configs_for_gw_file_values_path_dual_band,
                                                   config_defaults.get_dual_band_gw_defaults())
        else:
            self.configs_for_gw_values = open_json(self.dir_config, self.configs_for_gw_file_values_path,
                                                   config_defaults.get_single_band_gw_defaults())

        self.configs_for_printer_file_values_path = self.dir_config + '/configs_for_printer_values.json'
        self.configs_for_printer_values = open_json(self.dir_config, self.configs_for_printer_file_values_path,
                                                    config_defaults.get_printer_defaults())

    def config_attenuator(self):
        """
        configs attenuator for this run
        :Return: True if configuration found and attenuator was configured successfully, False otherwise
        """
        if not self.auto_attenuator_enable:
            msg = "according to configs.test_configs (AutoAttenuatorEnable) automatic attenuator is not connected, " \
                  "or should not be used."
            printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                          do_log=True, logger_type='debug')
            try:
                attn = set_calibration_attn(set_optimal_attn=False)
                if attn is None:
                    msg = "failed to set attenuation"
                else:
                    msg = 'Attenuation is set (' + str(attn) + "dB)"
            except EquipmentError:
                msg = 'was not able to open port to Attenuator, will continue this run without attenuator configuration'

            except Exception:
                msg = 'was not able to open json with attenuator config data, will continue this run without ' \
                      'attenuator configuration'
        else:
            try:
                tmp_path = os.path.join('..', 'config/equipment_config.json')
                attn = set_calibration_attn(set_optimal_attn=True, config_path=tmp_path)
                if attn is None:
                    msg = "failed to set attenuation, you will need to press Stop"
                    printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                                  do_log=True, logger_type='debug')
                    raise Exception("AutoAttenuatorEnable=Yes but failed to set attenuation")
                else:
                    msg = 'Attenuation is set (' + str(attn) + "dB)"
            except EquipmentError:
                msg = 'was not able to open port to Attenuator, you will need to press Stop\n' \
                      'if you want to restart run without using auto attenuator please change the field ' \
                      '"AutoAttenuatorEnable" in configs.test_config.json to "No"'
                printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                              do_log=True, logger_type='debug')
                raise Exception("AutoAttenuatorEnable=Yes but could not open port to Attenuator")
            except Exception:
                msg = 'was not able to open json with attenuator config data, will continue this run without ' \
                      'attenuator configuration'

        printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                      do_log=True, logger_type='debug')

    def config_equipment(self, temperature_sensor=True, attenuator=True):
        """
        :type temperature_sensor: bool
        :param temperature_sensor: if True will config temperature sensor
        :type attenuator: bool
        :param attenuator: if True will config attenuator
        configs equipment that needed for the run
        """
        # temperature sensor and auto attenuator
        global temperature_sensor_enable
        temperature_sensor_enable = False
        folder_path = 'configs'
        cfg_file_name = 'test_configs.json'
        # if file or folder doesn't exist will create json file with temperatureSensorEnable = 'No' and raise exception
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, cfg_file_name)
            if os.path.exists(file_path):
                self.test_configs = open_json(folder_path=folder_path,
                                              file_path=os.path.join(folder_path, cfg_file_name))
            else:
                msg = "Config file doesn't exist\n Creating test_config.json"
                printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
                with open(file_path, 'w') as cfg:
                    json.dump({"temperatureSensorEnable": "No", "AutoAttenuatorEnable": "No"}, cfg)
                raise Exception('test_config.json was created\n Temperature sensor is disabled\n'
                                'You will need to press Stop')
        else:
            msg = "'configs' directory doesn't exist\n Creating directory and test_config.json"
            printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
            os.mkdir(folder_path)
            file_path = os.path.join(folder_path, cfg_file_name)
            with open(file_path, 'w') as cfg:
                json.dump({"temperatureSensorEnable": "No", "AutoAttenuatorEnable": "No"}, cfg)
            raise Exception('test_config.json was created\n Temperature sensor and Auto Attenuator is disabled\n'
                            'You will need to press Stop')
        if temperature_sensor:
            if 'temperatureSensorEnable' not in self.test_configs.keys() or \
                    'AutoAttenuatorEnable' not in self.test_configs.keys():
                with open(file_path, 'w') as cfg:
                    json.dump({"temperatureSensorEnable": "No", "AutoAttenuatorEnable": "No"}, cfg)
                raise Exception('test_config.json missing some values, will return it to default values\n'
                                'You will need to press Stop')
            if self.test_configs['temperatureSensorEnable'].upper() == 'NO':
                temperature_sensor_enable = False
            elif self.test_configs['temperatureSensorEnable'].upper() == 'YES':
                temperature_sensor_enable = True
            else:  # illegal inputs will be ignored
                raise Exception("Valid values for temperatureSensorEnable are 'Yes' or 'No'\n "
                                "You will need to press Stop")
            if temperature_sensor_enable:
                self.Tag_t = set_temperature()
            else:
                self.Tag_t = None
        if attenuator:
            if self.test_configs['AutoAttenuatorEnable'].upper() == 'NO':
                self.auto_attenuator_enable = False
            elif self.test_configs['AutoAttenuatorEnable'].upper() == 'YES':
                self.auto_attenuator_enable = True
            else:  # illegal inputs will be ignored
                raise Exception("Valid values for AutoAttenuatorEnable are 'Yes' or 'No'\n You will need to press Stop")
            self.config_attenuator()


class MainWindow(QMainWindow):
    """
    Thread that opens and controls the GUI, opens all threads, sets/clears timers for all threads and handles exceptions
    This class will call for upload to cloud

    Parameters:
        values set by user in Offline Tester GUI:
            @Allow multiple missing label in row: dropdown list "Yes"/"No"
                If set to "No" the run will pause when a missing label is detected
            @Max missing labels in a row: int
                In case this number of missing label in row is reached, the run will pause
            @To print?: dropdown list "Yes"/"No"
                Enable/Disable printer. If set to "Yes" printing GUI will be opened after user pressed "Submit"
            @What is the printing job format?: dropdown list "SGTIN"/"Test"
            @Reel_name: str
            @Tags Generation: dropdown list with tags generation (e.g. "D2")
            @Inlay type: dropdown list with inlay types (e.g. "Dual Band")
            @Inlay serial number (3 digits): serial number for given inlay type
            @Test time [sec] (reel2reel controller->delay between steps = 999): max time before R2R moves to next tag
            @Fail if no packet received until [sec]: Max time TagThread will wait for first packet from tag
            @PacketThreshold: minimum amount of valid received packets from tag to pass
            @Desired amount of tags (will stop the run after this amount of tags): int.
                The run will pause after the amount written is reached. The user can choose to stop the run or continue.
            @Desired amount of pass (will stop the run after this amount of passes): int
                The run will pause after the amount written is reached in tags that passed.
                The user can choose to stop the run or continue.
            @Surface: dropdown list with various testing surfaces with given dielectric constant (Er)
            @Is converted?: dropdown list "Yes"/"No"  => if tag is converted or not
            @comments: text box for user comments

    Exceptions:
        @except Exception: exception occurred in one of the threads => calls look_for_exceptions()
            look_for_exceptions() will call handle_r2r_exception() which prints and handles the exception if possible

    Events:
        listen/ waits on:
            events.tag_thread_is_ready_to_main => event from TagThread. if set, TagThread is ready
            events.printer_event => wait for response from printer (printer_success or printer_error)
            events.printer_success => the last print was successful
            events.cont_to_main_thread => continue response received from TagThread
            events.r2r_ready => notify if R2R in ready for movement

        sets:
            events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
            events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception
            events.pause_to_tag_thread => pauses TagThread if exception happened of user pressed Pause
            events.done_to_tag_thread => closes TagThread at the end of the run
            events.cont_to_tag_thread => send continue to paused TagThread after user pressed continue
            events.done2r2r_ready => closes R2RThread
            events.done_to_r2r_thread => kills R2R thread main loop if set
            events.done_to_printer_thread => user pressed Stop (end the program) - to avoid deadlock
            events.cont_to_printer_thread => send continue to PrinterThread after Continue pressed by user


    Logging:
        logging to logging.debug() and logging.info()
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the runs threads and classes
        """
        try:
            super(MainWindow, self).__init__(*args, **kwargs)
            self.events = MainEvents()
            self.passed_every_50 = []
            self.last_tested_num = 0
            self.last_passed_num = 0
            self.yield_over_time = []
            self.calculate_interval = 10
            self.to_print = False
            global calculate_interval
            calculate_interval = self.calculate_interval
            self.calculate_on = 50
            global calculate_on
            calculate_on = self.calculate_on
            self.first_reached_to_desired_passes = False
            self.first_reached_to_desired_tags = False
            self.yield_drop_happened = False
            self.yield_was_high_lately = True
            self.prev_y_len = 0
            self.waiting_for_user_to_press_stop_because_printer = False

            self.ports_and_guis = PortsAndGuis()

            self.r2r_thread = R2RThread(self.events, self.ports_and_guis)
            self.tag_checker_thread = TagThread(self.events, self.ports_and_guis)

            self.events.tag_thread_is_ready_to_main.wait()
            self.events.tag_thread_is_ready_to_main.clear()

            self.pass_job_name = self.tag_checker_thread.printing_value['passJobName']  # will be set inside config
            self.to_print = self.tag_checker_thread.to_print
            self.start_value = int(self.tag_checker_thread.printing_value['firstPrintingValue'])

            # printer set-up ####################################################################
            # happens here so we will wait less until the printer will start up (will happen in the background)
            if self.to_print:
                self.printer = Printer(self.start_value, self.pass_job_name, self.events, self.ports_and_guis)
                self.look_for_exceptions()

            self.open_ui()  # starts recurring_timer() that starts look_for_exceptions()

            self.r2r_thread.start()
            self.tag_checker_thread.start()
            self.events.tag_thread_is_ready_to_main.wait()
            self.events.tag_thread_is_ready_to_main.clear()
            if self.to_print:
                self.printer.start()
                self.events.printer_event.wait()
                if self.events.printer_success.isSet():
                    self.events.printer_success.clear()
                    msg = 'Printer is ready to start'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')

            self.events.start_to_r2r_thread.set()
        except Exception:
            exception_details = sys.exc_info()
            msg = 'Exception detected during initialization:'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            print_exception(exception_details, printing_lock=lock_print)
            self.look_for_exceptions()

        # done will be raised from stop_fn (user pressed done)

    def open_ui(self):
        """
        opens the run main GUI that will present the run data and gives to the user ability to Stop/Continue/Pause
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
        self.graphWidget.setLabel("left", "Yield for the last 50 tags [%]", **styles)
        self.graphWidget.setLabel("bottom", "Last tag location [x*" + str(self.calculate_interval) + "+" +
                                  str(self.calculate_on) + "]", **styles)
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

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()

        # updates the GUI and stops all if exception happened
        self.update_timer = QTimer()
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.recurring_timer)
        self.update_timer.start()

    # GUI functions ##########################################################
    def stop_fn(self):
        """
        will be triggered by the Stop button and will end the run.
        will upload run's data to cloud and close the threads.
        """
        global tested, passed, missing_labels
        global last_pass_string, under_threshold, problem_in_locations_hist
        if tested == 0:
            yield_ = -1.0
        else:
            yield_ = passed / tested * 100
        self.events.pause_to_tag_thread.set()
        self.update_timer.stop()
        self.close()
        ttfgp_avg = None
        if len(self.tag_checker_thread.ttfgp_list) > 0:
            ttfgp_avg = mean(self.tag_checker_thread.ttfgp_list)
        self.events.done_to_tag_thread.set()
        self.events.done_to_printer_thread.set()
        self.events.done2r2r_ready.set()
        self.events.cont_to_tag_thread.set()  # to avoid deadlock
        self.events.done_to_r2r_thread.set()

        values = save_screen(tested=tested, passed=passed, yield_=yield_, missing_labels=missing_labels,
                             problem_in_locations_hist_val=problem_in_locations_hist, ttfgp_avg=ttfgp_avg)

        msg = "Stopped by the operator.\n" + 'Reels yield_over_time is: |' + str(self.yield_over_time) + \
              '| interval: |' + str(self.calculate_interval) + '|, on: |' + str(self.calculate_on) + \
              '\nLast words: ' + values['comments'] + '\nTested = ' + str(tested) + ', Passed = ' + str(passed) + \
              ', Yield = ' + str(yield_) + '%' + ', Missing labels = ' + str(missing_labels)
        printing_func(msg, 'MainWindow', lock_print, logger_type='info')

        self.r2r_thread.join()
        # save last printed value, also being done after every pass by the printer thread (for crash support):
        if self.to_print:
            if self.tag_checker_thread.value['printingFormat'] == 'SGTIN':
                filename = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'
                printing_format = 'SGTIN'
            else:
                filename = 'gui_printer_inputs_4_Test_do_not_delete.json'
                printing_format = 'Test'

            folder_path = 'configs'
            data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, filename),
                             default_values=DefaultGUIValues(printing_format).default_gui_values)
            data['firstPrintingValue'] = str(int(data['firstPrintingValue']) + 1)
            f = open(os.path.join(folder_path, filename), "w")
            json.dump(data, f)
            f.close()

        global run_data_log, log_path, run_data_dict, run_data_path
        if run_data_log is None:
            run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.OFFLINE)
            run_data_log.open_csv()
        run_data_dict['passed'] = passed
        run_data_dict['tested'] = tested
        if tested > 0:  # avoid division by zero
            run_data_dict['yield'] = passed / tested
        if tested == 0:
            run_data_dict['yield'] = -1.0
        run_data_dict['yieldOverTime'] = self.yield_over_time
        run_data_dict['includingUnderThresholdPassed'] = under_threshold + passed
        if tested > 0:  # avoid division by zero
            run_data_dict['includingUnderThresholdYield'] = run_data_dict['includingUnderThresholdPassed'] / tested
        run_data_dict['errors'] = collect_errors(log_path)
        run_data_log.override_run_data(run_data_dict)

        global reel_name, tags_data_path
        res = None
        if values['upload'] == 'Yes':
            parts1 = [i for i in run_data_path.split('/')]
            parts2 = [i for i in tags_data_path.split('/')]
            try:
                res = upload_to_cloud_api(batch_name=reel_name, tester_type='offline', run_data_csv_name=parts1[-1],
                                          tags_data_csv_name=parts2[-1], to_logging=True)
            except Exception:
                exception_details = sys.exc_info()
                print_exception(exception_details=exception_details, printing_lock=lock_print)
                res = False

            if not res:
                msg = 'Upload to cloud failed!!!!!!!!!\ngot an error while uploading to cloud'
                printing_func(msg, 'MainWindow', lock_print, logger_type='warning')
            else:
                logging.debug('Uploaded to cloud? ' + values['upload'])
        else:
            logging.debug('Uploaded to cloud? No')

        self.tag_checker_thread.join()
        if self.to_print and not self.waiting_for_user_to_press_stop_because_printer:
            self.printer.join()

        global failed_tags
        if res is not None:
            upload_conclusion(failed_tags=failed_tags, succeeded_csv_uploads=res)
        sys.exit(0)

    def continue_fn(self):
        """
        will be triggered by the Continue button and will resume the run after Pause/ run got stuck if possible.
        """
        if not self.events.cont_to_tag_thread.isSet() and not self.waiting_for_user_to_press_stop_because_printer\
                and not self.tag_checker_thread.fetal_error:
            msg = "user pressed Continue, the R2R will advance now (the last spot will be fail)"
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            self.look_for_exceptions()
            self.events.cont_to_tag_thread.set()
            self.events.cont_to_printer_thread.set()
            self.events.cont_to_main_thread.wait()
            self.events.cont_to_main_thread.clear()
            self.events.start_to_r2r_thread.set()

    def pause_fn(self):
        """
        will be triggered by the Pause button and will pause the run if possible.
        """
        if not self.events.pause_to_tag_thread.isSet() and not self.waiting_for_user_to_press_stop_because_printer\
                and not self.tag_checker_thread.fetal_error:
            msg = "user pressed Pause, the R2R will pause now (the current spot will be fail)"
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            self.events.stop_to_r2r_thread.set()
            self.events.pause_to_tag_thread.set()

    def recurring_timer(self):
        """
        update the runs main GUI, checks that the other threads are OK (no exceptions)
        """
        global tested, passed, missing_labels, black_list_size
        global last_pass_string, reel_name

        if tested == 0:
            yield_ = -1.0
            self.reel_label.setText("Reel Name: " + reel_name)
        else:
            yield_ = passed / tested * 100
        self.tested.setText('Tested = ' + str(tested) + ', Passed = ' + str(passed) + ', Yield = ' +
                            '{0:.4g}'.format(yield_) + '%' + '\nMissing labels = ' + str(missing_labels) +
                            ', black list size = ' + str(black_list_size))
        self.last_pass.setText(last_pass_string)
        # update the graph, if there was change in the tested amount
        # because passed and tested are been updated in different times
        # we will check the passed of the prev tag => tested -1
        if tested > self.last_tested_num:
            if self.calculate_on >= tested > self.last_tested_num:
                if passed - self.last_passed_num > 0:
                    self.passed_every_50.append(1)
                else:
                    self.passed_every_50.append(0)
            elif tested > 0:
                del self.passed_every_50[0]
                if passed - self.last_passed_num > 0:
                    self.passed_every_50.append(1)
                else:
                    self.passed_every_50.append(0)

            if len(self.passed_every_50) > self.calculate_on:
                msg = 'self.passed_every_50 length is too long (self.passed_every_50 = ' + \
                      str(self.passed_every_50) + ')'
                printing_func(msg, 'MainWindow', lock_print, logger_type='warning')

            if tested % self.calculate_interval == 1 and tested > self.calculate_on:
                self.y.append(sum(self.passed_every_50) / self.calculate_on * 100)
                self.x = range(len(self.y))
                self.data_line.setData(self.x, self.y)  # Update the data.
                self.yield_over_time.append(int(sum(self.passed_every_50) / self.calculate_on * 100))
            if 0 < len(self.y) != self.prev_y_len and self.yield_was_high_lately:
                self.prev_y_len = len(self.y)
                if self.y[-1] == 0:  # 50 fails in a row => Pause the run
                    msg = 'There are 50 fails in a row, please make sure everything is OK and press Continue'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                    self.yield_drop_happened = True
                    self.yield_was_high_lately = False
                    if not self.events.pause_to_tag_thread.isSet():
                        self.events.stop_to_r2r_thread.set()
                        self.events.pause_to_tag_thread.set()
                elif self.y[-1] < 40 and len(self.y) > 15:  # under 40% yield-over-time for 200 tags => Pause the run
                    self.yield_drop_happened = True
                    for ii in range(1, 15):
                        if self.y[-ii] < 40:
                            continue
                        else:
                            self.yield_drop_happened = False
                            break
                    if self.yield_drop_happened:
                        msg = str('*' * 100) + '\nThe yield-over-time of the last 200 tags is below 40%,'\
                                               ' waiting to operator to press Continue\n' + str('*' * 100)
                        printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                        self.yield_was_high_lately = False
                        if not self.events.pause_to_tag_thread.isSet():
                            self.events.stop_to_r2r_thread.set()
                            self.events.pause_to_tag_thread.set()
                elif self.y[-1] > 50 and len(self.y) > 15:
                    self.yield_was_high_lately = True
            global yield_over_time
            yield_over_time = self.yield_over_time
            # update the prev counters
            self.last_tested_num += 1
            if passed > self.last_passed_num:
                self.last_passed_num += 1

        if tested == desired_tags_num and not self.first_reached_to_desired_tags:
            msg = '---------------------------Desired tags have reached (' + str(tested) + \
                  ') , If you wish to proceed, press Continue---------------------------'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            self.first_reached_to_desired_tags = True
            self.pause_fn()
        if passed == desired_pass_num and not self.first_reached_to_desired_passes:
            msg = '---------------------------Desired passes have reached (' + str(passed) + \
                  ') , If you wish to proceed, press Continue---------------------------'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            self.first_reached_to_desired_passes = True
            self.pause_fn()
        if not self.waiting_for_user_to_press_stop_because_printer:
            self.look_for_exceptions()

    def look_for_exceptions(self):
        """
        search for exceptions in the threads Exceptions Queues.
        """
        if self.to_print:
            if not self.printer.exception_queue.empty() or not self.tag_checker_thread.exception_queue.empty() or \
                    not self.r2r_thread.exception_queue.empty():
                if not self.events.pause_to_tag_thread.isSet():
                    msg = "Paused because an exception happened, the R2R will pause now "\
                          "(the current spot will be fail)"
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                    self.events.stop_to_r2r_thread.set()
                    self.events.pause_to_tag_thread.set()
                self.handle_r2r_exception()
        elif not self.tag_checker_thread.exception_queue.empty() or not self.r2r_thread.exception_queue.empty():
            if not self.events.pause_to_tag_thread.isSet():
                msg = "Paused because an exception happened, the R2R will pause now (the current spot will be fail)"
                printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                self.events.stop_to_r2r_thread.set()
                self.events.pause_to_tag_thread.set()
            self.handle_r2r_exception()

    def handle_r2r_exception(self):
        """
        handle the exception if possible. prints the exception to screen and log
        """
        if self.to_print:
            if not self.printer.exception_queue.empty():
                exception_details = self.printer.exception_queue.get()
                msg = 'Printer got an Exception:'
                printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                # using logging.warning that will be parsed to errors
                print_exception(exception_details, printing_lock=lock_print)
                exc_type, exc_obj, exc_trace = exception_details
                # ConnectionResetError => exc_obj = 'An existing connection was forcibly closed by the remote host'
                if isinstance(exc_obj, PrinterNeedsResetException):
                    msg = 'please press Stop and start a new run'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                    self.waiting_for_user_to_press_stop_because_printer = True
                    self.events.printer_error.set()  # to avoid deadlock when printer thread crashed before
                elif isinstance(exc_obj, ConnectionResetError):
                    self.events.done_to_printer_thread.set()
                    msg = 'Will close socket to Printer and restart it, please wait...'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                    self.events.printer_event.wait()
                else:
                    if self.events.r2r_ready.isSet():
                        self.events.r2r_ready.clear()
                    msg = 'Please check everything is OK and press Continue'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')

        if not self.tag_checker_thread.exception_queue.empty():
            exception_details = self.tag_checker_thread.exception_queue.get()
            msg = 'tag_checker_thread got an Exception, waiting for an operator to press Continue or Stop'
            exc_type, exc_obj, exc_trace = exception_details
            if 'R2R moved before timer ended' in str(exc_obj):
                msg = 'R2R moved before timer ended, please check in r2r controller\n' \
                      'Menu -> Motors setup -> DELAY BETWEEN STEPS\n' \
                      'is set to 999'
                printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                print_exception(exception_details, printing_lock=lock_print)
                pop_up_window(msg)
            else:
                printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                print_exception(exception_details, printing_lock=lock_print)

        if not self.r2r_thread.exception_queue.empty():
            exception_details = self.r2r_thread.exception_queue.get()
            msg = 'r2r_thread got an Exception, waiting for an operator to press Continue or Stop'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            print_exception(exception_details, printing_lock=lock_print)


# --------  main code:  ---------- #
app = QApplication([])
window = MainWindow()
app.exec_()
