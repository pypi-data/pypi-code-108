# ---------------------------------------
#               run in real time:
# ---------------------------------------
from wiliot.gateway_api.gateway import *
import threading
import time

continue_until_empty = False


def recv_data_handler(action_type, data_type):
    """

    :type action_type:ActionType
    :type data_type: DataType
    :return:
    """
    print("DataHandlerProcess Start")
    while True:
        time.sleep(0)  # important for the processor - keep it for fast performance
        # check if there is data to read
        if ObjGW.is_data_available():
            # get data
            data_in = ObjGW.get_data(action_type=action_type, num_of_packets=1, data_type=data_type)
            if not data_in:
                continue
            if data_type.value == 'raw':
                print("{} : {}".format(data_in['raw'], data_in['time']))
            elif data_type.value == 'processed':
                for key, element in data_in.items():
                    print("{} : {}".format(key, element))
        else:  # no available data
            if continue_until_empty:
                # stop the analysis process
                ObjGW.stop_processes(packet_analysis_process=True)
                return


# Open GW connection
ObjGW = WiliotGateway(auto_connect=True)
is_connected, _, _ = ObjGW.get_connection_status()
if is_connected:
    # Config GW:
    ObjGW.config_gw(filter_val=False, pacer_val=0, energy_pattern_val=20, time_profile_val=[5, 15],
                    beacons_backoff_val=2, received_channel=37, modulation_val=True)
    ObjGW.check_current_config()
    # acquiring and processing in real time
    ObjGW.run_packets_listener(do_process=True)
    # or running both functions:
    #       ObjGW.run_packets_listener()
    #       ObjGW.run_process_packet()

    dataHandlerListener = threading.Thread(target=recv_data_handler, args=(ActionType.FIRST_SAMPLES,
                                                                           DataType.PROCESSED))
    dataHandlerListener.start()

    # stop all process due to event:
    time.sleep(10)
    ObjGW.stop_processes(packet_listener_process=True, packet_analysis_process=False)

    # complete acquiring data:
    time.sleep(0.1)
    continue_until_empty = True

    # Close GW connection:
    ObjGW.close_port(is_reset=True)

else:
    print("connection failed")

# clean exit:
ObjGW.exit_gw_api()