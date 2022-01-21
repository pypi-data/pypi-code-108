"""
Basic test of the SF10
"""
import time
import logging
from vapourtec.sf10 import SF10
from vapourtec.errors import VapourtecError


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    port = 'COM4'
    safe_connect = False
    sf10 = SF10(device_port=port, safe_connect=safe_connect)

    sf10.set_valve(SF10.VALVE_A)
    time.sleep(0.5)
    sf10.set_valve(SF10.VALVE_B)
    time.sleep(0.5)
    sf10.set_valve('C')  # should not work, there is no valve C
    time.sleep(0.5)

    sf10.set_mode(SF10.MODE_FLOW)
    sf10.set_flow_rate(5)  # mL/min
    time.sleep(0.5)

    sf10.start()
    time.sleep(2)
    sf10.stop()

    sf10.set_mode(SF10.MODE_GAS)
    sf10.set_gas_flow_rate(50)  # ssc/min
    time.sleep(0.5)

    sf10.set_mode(SF10.MODE_REGULATOR)
    sf10.set_regulator_pressure(4)  # bar
    time.sleep(0.5)

    sf10.set_mode(SF10.MODE_DOSE)
    sf10.set_flow_rate(10)  # mL/min
    sf10.set_dose_volume(20)  # mL
    time.sleep(0.5)

    sf10.set_mode(SF10.MODE_RAMP)
    sf10.set_ramp(1, 2, 3)  # from 1 mL/min to 2 mL/min over 3 minutes
    time.sleep(0.5)

    sf10.disconnect()
