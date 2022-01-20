from wiliot.gateway_api.gateway import *

# ---------------------------------------
#              Multiple GW
# ---------------------------------------
# Multiple GW: connect to specific COM:
# Multiple GW: connect to all available COM:
ObjGW = WiliotGateway()
ObjGWs = []
for ind, port in enumerate(ObjGW.available_ports):
    ObjGWs.append(WiliotGateway(port=port))

ObjGWs[0].close_port()
ObjGWs[1].close_port()

# clean exit:
ObjGW.exit_gw_api()
