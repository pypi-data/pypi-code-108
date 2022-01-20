"""
This function assists to check Wiliot's tags response
"""
import argparse
from wiliot.gateway_api.gateway import *

# ------- setup the function variables ------------ #
# read from command line if applicable:
parser = argparse.ArgumentParser()
parser.add_argument('-e', action='store', dest='energy_pattern',
                    help='Energy Pattern - Please Consult Wiliot which pattern is the most suitable for your setup')
parser.add_argument('-p', action='store', dest='num_of_packet',
                    help='Packet number - The number of received packets to pass the test')
parser.add_argument('-t', action='store', dest='time_to_wait',
                    help='Time to wait - The maximum time in seconds to wait for the received packets')
args = vars(parser.parse_args())
energy_pattern = args['energy_pattern']
num_of_packet = args['num_of_packet']
time_to_wait = args['time_to_wait']

if energy_pattern is None:
    energy_pattern = 18
if num_of_packet is None:
    num_of_packet = 5
if time_to_wait is None:
    time_to_wait = 20

# --------- connect to the gateway ------------------ #
# Open GW connection
ObjGW = WiliotGateway(auto_connect=True)
is_connected, _, _ = ObjGW.get_connection_status()
if is_connected:
    print("gateway type:{}".format(ObjGW.hw_version))
    print("gateway version:{}".format(ObjGW.sw_version))

    # Config GW:
    ObjGW.config_gw(filter_val=False, pacer_val=0, energy_pattern_val=int(energy_pattern), time_profile_val=[5, 15],
                    beacons_backoff_val=0, received_channel=37, modulation_val=True)
    ObjGW.check_current_config()
    # acquire number of packets and process them:
    recv_data = ObjGW.run_packets_listener(max_packets=int(num_of_packet), max_time=int(time_to_wait), do_process=False)
    proc_data = ObjGW.run_process_packet(raw_data=recv_data)  # process
    if recv_data:
        print("time: {}".format(list(r['time'] for r in recv_data)))
        print("raw packets: {}".format(list(r['raw'] for r in recv_data)))
    if proc_data:
        for key in proc_data[0].keys():
            print("{} : {}".format(key, list(p[key] for p in proc_data)))

    # Close GW connection:
    ObjGW.close_port()
    ObjGW.exit_gw_api()

else:
    print("connection failed")
# clean exit:
ObjGW.exit_gw_api()
