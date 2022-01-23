from wiliot.gateway_api.gateway import *

# ---------------------------------------
#             Basic Example
# ---------------------------------------
# Open GW connection
ObjGW = WiliotGateway(auto_connect=True)
is_connected, _, _ = ObjGW.get_connection_status()
if is_connected:
    print("gateway type:{}".format(ObjGW.hw_version))
    print("gateway version:{}".format(ObjGW.sw_version))

    # Check GW Version and update if needed:
    ObjGW.update_version()

    # Config GW:
    ObjGW.config_gw(filter_val=False, pacer_val=0, energy_pattern_val=20, time_profile_val=[5, 15],
                    beacons_backoff_val=0, received_channel=37, modulation_val=True)
    ObjGW.check_current_config()
    # acquire number of packets and process them:
    recv_data = ObjGW.run_packets_listener(max_packets=10, max_time=20, do_process=False)  # acquire
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
