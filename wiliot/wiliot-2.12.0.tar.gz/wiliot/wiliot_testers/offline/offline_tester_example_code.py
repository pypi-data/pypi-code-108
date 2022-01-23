"""
The code below shows a simplified example of using Wiliot's gateway API.
An example of a system is a printer or other machine that moves a reel of tags so that only one tag is tested
and transmitted at a time. The system  is controlled by a class called Printer
TagThread tests each tag and decides whether it has passed or failed the test. Depending on whether or not the
tag was successful, an addition mechanism could be implemented (such as printing a QR code).

The full working code on Wiliot's testing system can be found in offline_tester.py
"""

from wiliot.gateway_api.gateway import *
from wiliot.wiliot_testers.tester_utils import *
import queue
import time
import threading

# global queues for communications:
to_printer_command = queue.Queue()
from_printer_command = queue.Queue()
to_tag_command = queue.Queue()
from_tag_command = queue.Queue()


class Printer(threading.Thread):
    """
    The printer handler
    Todo: add all communication, printing, movement,error etc. here
    """
    def __init__(self):
        super(Printer).__init__()
        self.stop_all = False

        # start listening to commands:
        self.run()

    def run(self):
        while True:
            try:
                cmd = to_printer_command.get(timeout=0.050)
                if cmd == 'move to the next tag':
                    self.move()
                elif cmd == 'exit':
                    self.stop_all = True
                    self.exit()
                    return
                # todo: add more commands and cases
            except queue.Empty:
                pass
            except Exception as e:
                raise e

    def move(self):
        # todo: build a code that moves the tags reel so the next tag will be close to the antenna
        if self.stop_all:
            return
        time.sleep(5)  # todo: replace it with the real printer movement process
        from_printer_command.put('in_place')
        print("new tag is in place")

    def error_handling(self):
        # todo: build a function that handles exceptions and error
        from_printer_command.put('raised_error')

    def exit(self):
        # todo: add closing printer connection and other relevant processes
        return


class TagThread(threading.Thread):
    """
    Tag tester handler
    based on offline_tester.py
    this example contains all the main building blocks but lack the specific details and conditions
    that are important for different application
    """
    def __init__(self):
        super(TagThread).__init__()
        # init management:
        self.stop_all = False
        # init GW:
        self.GwObj = WiliotGateway(auto_connect=True)
        is_connected, _, _ = self.GwObj.get_connection_status()
        if is_connected:
            # Config GW:
            self.GwObj.config_gw(filter_val=False, pacer_val=0, energy_pattern_val=20, time_profile_val=[5, 15],
                                 beacons_backoff_val=0, received_channel=37, modulation_val=True)
            self.GwObj.check_current_config()
        # init test parameters:
        # TODO: change to the relevant parameters according to your test and tag type
        self.packet_threshold = 3  # packets for success
        self.max_test_time = 10.0  # seconds, the maximum time for each test tag
        self.max_time_for_first_packet = 5.0  # seconds, the maximum time for the first packet to arrive
        self.rssi_threshold = 70  # the power reduction(lower number -> stronger signal)
        # init timers:
        self.test_timer = None
        self.first_packet_timer = None
        self.is_test_time_up = False
        self.is_first_packet_time_up = False
        # init data:
        self.tag_list = []

        # start listening to commands:
        self.run()

    def run(self):
        while True:
            try:
                cmd = to_tag_command.get(timeout=0.050)
                if cmd == 'test new tag':
                    self.new_tag_arrived()
                elif cmd == 'exit':
                    self.stop_all = True
                    self.exit()
                    return
                # todo: add more commands and cases
            except queue.Empty:
                pass
            except Exception as e:
                raise e

    def new_tag_arrived(self):

        def clear_timers():
            if not self.test_timer == '':
                self.test_timer.cancel()
                self.is_test_time_up = False
            if not self.first_packet_timer == '':
                self.first_packet_timer.cancel()
                self.is_first_packet_time_up = False

        def end_of_time(timer_type):
            if timer_type == 'test':
                self.is_test_time_up = True
                print("Tag reached Time-Out")
            if timer_type == 'first packet':
                self.is_first_packet_time_up = True
                print("First packet did not arrive for more than " + str(self.max_time_for_first_packet) + " seconds")

        def packet_filter(data_to_filter):
            # check if the RSSI is good
            if str(data_to_filter['rssi']) > str(self.rssi_threshold):
                print('packet signal is too weak')
                return False

            # check if the tag was already caught in the GW
            if str(data_to_filter['adv_address']) in self.tag_list:
                print('Duplication from a tag we have seen before')
                return False

            # TODO: add more conditions

            return True

        def processing_good_tag(data_for_process):
            # TODO: write your processing function or use one of the tester_utils functions
            #  (e.g. process_encrypted_tags_data)
            return data_for_process

        def save_to_csv(data_to_save):
            # TODO: write your processing function or use one of the tester_utils functions (e.g. CSVLog)
            pass

        # init - GW:
        self.GwObj.reset_buffer()  # clean buffer
        self.GwObj.config_gw(time_profile_val=[5, 15])  # starting to transmit
        # init - timers:
        self.test_timer = threading.Timer(float(self.max_test_time), end_of_time, ['test'])
        self.test_timer.start()
        self.first_packet_timer = threading.Timer(float(self.max_time_for_first_packet), end_of_time, ['first packet'])
        self.first_packet_timer.start()
        # init - timers flags:
        self.is_test_time_up = False
        self.is_first_packet_time_up = False
        # init data:
        data_in = None
        tag_data_list = []
        clear_timers()
        # start listening:
        self.GwObj.run_packets_listener(tag_packets_only=True, do_process=True)

        while len(tag_data_list) < int(self.packet_threshold) and not self.is_test_time_up and \
                not self.is_first_packet_time_up and not self.stop_all:
            time.sleep(0)  # 0 seconds to allow the cpu to recover
            # read data:
            if self.GwObj.is_data_available():
                data_in = self.GwObj.get_data(action_type=ActionType.FIRST_SAMPLES, num_of_packets=1,
                                              data_type=DataType.PROCESSED)
                if data_in and data_in['is_valid_tag_packet']:
                    print('valid packet')
                    self.first_packet_timer.cancel()
                    is_good_packet = packet_filter(data_in)
                    if is_good_packet:
                        tag_data_list.append(data_in)
                        for key, element in data_in.items():
                            print("{} : {}".format(key, element))
                    else:
                        print("valid packet but didn't pass the packet filter")
                else:
                    print("invalid packet")

        self.GwObj.stop_processes()
        self.GwObj.reset_buffer()
        self.GwObj.config_gw(time_profile_val=[0, 6])  # stop transmitting
        print("stop listening")

        # check if the tag pass or failed:
        if len(tag_data_list) == int(self.packet_threshold):
            clear_timers()
            self.tag_list.append(data_in['adv_address'])
            # process data:
            processed_data = processing_good_tag(data_in)
            # save to csv:
            save_to_csv(processed_data)
        elif self.is_first_packet_time_up:
            print("Tag has failed! did not transmit for {} seconds".format(self.max_time_for_first_packet))
        elif self.is_test_time_up:
            print("Tag has failed! did not transmit {} packets".format(self.packet_threshold))

        # end of tag test
        from_tag_command.put('test_is_done')

    def error_handling(self):
        # todo: build a function that handles exceptions and error
        from_tag_command.put('raised_error')

    def exit(self):
        self.GwObj.exit_gw_api()
        # todo: add closing file for csv and other relevant processes
        return


##########################################
#            main code                   #
###########################################
printer = threading.Thread(target=Printer, args=())
printer.start()
tag = threading.Thread(target=TagThread, args=())
tag.start()

# test parameters:
number_of_packets_to_test = 1000
tested_packets = 0
max_running_time = 30  # seconds

# start
to_printer_command.put('move to the next tag')
time_start = datetime.datetime.now()

# command holder
while True:
    dt_run = datetime.datetime.now() - time_start
    if tested_packets >= number_of_packets_to_test:
        print("completed the test")
        to_tag_command.put('exit')
        to_printer_command.put('exit')
        break
    if dt_run.total_seconds() > max_running_time:
        print("The running time is up")
        to_tag_command.put('exit')
        to_printer_command.put('exit')
        break
    # read commands from printer
    cmd_printer = ''
    try:
        cmd_printer = from_printer_command.get(timeout=0.050)
    except queue.Empty:
        pass
    except Exception as e:
        print(e)
    # check printer command
    if cmd_printer == 'in_place':
        print("test new tag")
        to_tag_command.put('test new tag')
    elif cmd_printer == 'raised_error':
        print("printer raised error")
        to_tag_command.put('exit')
        to_printer_command.put('exit')
        break

    # read commands from tag
    cmd_tag = ''
    try:
        cmd_tag = from_tag_command.get(timeout=0.050)
    except queue.Empty:
        pass
    except Exception as e:
        print(e)
    # check printer command
    if cmd_tag == 'test_is_done':
        print("move to the next tag")
        to_printer_command.put('move to the next tag')
        tested_packets += 1
    elif cmd_tag == 'raised_error':
        print("tag analysis raised error")
        to_tag_command.put('exit')
        to_printer_command.put('exit')
        break

tag.join()
printer.join()
