import logging
import threading
from ftdi_serial import Serial
from vapourtec.errors import VapourtecError
import atexit


class SF10:
    """
    The SF10 pump should have firmware v1.8 installed on it. Remote control must also be enabled on the pump. To check
    this, use some software to communicate with the pump with RS-232. During development the program Termite was
    used.
    Connect to the pump in the program and send the following command to enable remote control of the pump:
    REMOTEEN vtec 1
    You should receive an "OK" back from the pump if successful. This only has to be done once.
    Once this is done, you can send the GV command to check the firmware version on the pump, and send REMOTEEN again
    to check that remote control is enabled

    Connection settings according to the manual are
    +----------------------+---------------------------------------------+
    | Parameter            | Comment                                     |
    +----------------------+---------------------------------------------+
    | Baud rate            | 9600                                        |
    +----------------------+---------------------------------------------+
    | Parity               | Not specified in manual, None is used       |
    +----------------------+---------------------------------------------+
    | Handshaking          | Not specified in manual, None is used       |
    +----------------------+---------------------------------------------+
    | Data bits            |  Not specified in manual, 8 is used         |
    +----------------------+---------------------------------------------+
    | Stop bits            |  Not specified in manual, 1 is used         |
    +----------------------+---------------------------------------------+
    | Physical connection  | Connect from PC to SF10 with a serial cable |
    |                      | A straight, RS232, 9 pin serial cable will  |
    |                      | be required. (Female to Female)             |
    |                      | Use a USB to serial converter if the PC     |
    |                      | has no built in serial connector.           |
    |                      | Your PC will allocate a COM port number to  |
    |                      | the serial port or the converter (if used). |
    +----------------------+---------------------------------------------+
    | Message Terminators  | Not specified in the manual, <CR> is used   |
    +----------------------+---------------------------------------------+

    Protocols are:
    If a recognized command was sent to the pump OK will be sent back. OK will still be sent back even if numerical
    parameters are out of range and sent to the pump, even though the pump may not change to the set value.
    Note that setting a value out of range causes the default parameter to be used.
    +---------------+-------------------------+-----------------------------------+
    | Sent by PC    | Parameter               | Description                       |
    +---------------+-------------------------+-----------------------------------+
    | START         |                         | Start pump                        |
    +---------------+-------------------------+-----------------------------------+
    | STOP          |                         | Stop pump                         |
    +---------------+-------------------------+-----------------------------------+
    | VALVE x       | x is A or B             | Select valve position x,          |
    |               |                         | e.g. VALVE A, VALVE B             |
    +---------------+-------------------------+-----------------------------------+
    | MODE x        | x is FLOW or REG or     | Select pump mode x,               |
    |               | DOSE or GAS or RAMP     | e.g. MODE FLOW, MODE REG          |
    +---------------+-------------------------+-----------------------------------+
    | SETFLOW x     | x is the flow rate in   | Sets flow rate to x mL/min, used  |
    |               | mL/min                  | by FLOW and DOSE modes,           |
    |               |                         | e.g. SETFLOW 5.0                  |
    +---------------+-------------------------+-----------------------------------+
    | SETGASFLOW x  | x is the gas flow       | Sets gas flow rate to x ssc/min,  |
    |               | rate  in ssc/min        | used by GAS modes,                |
    |               |                         | e.g. SETGASFLOW 50.0              |
    +---------------+-------------------------+-----------------------------------+
    | SETREG X      | x is the pressure in    | Sets regulator mode pressure to   |
    |               | bar                     | x bar, used by REGULATOR mode     |
    |               |                         | e.g. SETREG 4.0                   |
    +---------------+-------------------------+-----------------------------------+
    | SETDOSE X     | x is the dose volume    | Sets dose volume in mL/min,used   |
    |               | in mL/min               | by DOSE mode,                     |
    |               |                         | e.g. SETDOSE 20.0                 |
    +---------------+-------------------------+-----------------------------------+
    | SETRAMP x y z | x is the start speed    | Sets ramp speed from x mL/min to  |
    |               | in mL/min, y is the     | y mL/min over z minutes,          |
    |               | final speed in mL/min,  | e.g. SETRAMP 1 2 10               |
    |               | z is time in minutes    |                                   |
    +---------------+-------------------------+-----------------------------------+


    """
    CONNECTION_SETTINGS = {'baudrate': 9600, 'data_bits': Serial.DATA_BITS_8, 'stop_bits': Serial.STOP_BITS_1}
    # hex command characters for data transmission
    CR_HEX = "\x0d"  # carriage return
    LINE_ENDING = CR_HEX  # each individual command and each response are terminated with CR
    LINE_ENDING_ENCODED = LINE_ENDING.encode()

    # constants for protocols and responses
    _FIRMWARE = "GV"
    _REMOTE_CONTROL_SETTING = 'REMOTEEN'
    _SET_RC_ENABLED = 'REMOTEEN vtec 1'
    _RC_ENABLED = 'Remote Control is enabled'  # response back from SL10 for REMOTEEN command if remote control is
    # enabled
    _START = 'START'
    _STOP = 'STOP'
    _SET_VALVE = 'VALVE'
    _SET_MODE = 'MODE'
    _SET_FLOW_RATE = 'SETFLOW'
    _SET_GAS_FLOW_RATE = 'SETGASFLOW'
    _SET_REGULATOR_PRESSURE = 'SETREG'
    _SET_DOSE_VOLUME = 'SETDOSE'
    _SET_RAMP = 'SETRAMP'
    # response back from SL10 if a recognized command was sent to the pump, but we strip the \n from the front of all
    # responses
    # _COMMAND_SENT_RESPONSE = '\nOK'
    _COMMAND_SENT_RESPONSE = 'OK'  # so use this instead

    VALVE_A = 'A'
    VALVE_B = 'B'
    _VALVES = [VALVE_A, VALVE_B]

    MODE_FLOW = 'FLOW'
    MODE_REGULATOR = 'REG'
    MODE_DOSE = 'DOSE'
    MODE_GAS = 'GAS'
    MODE_RAMP = 'RAMP'
    _MODES = [MODE_FLOW, MODE_REGULATOR, MODE_DOSE, MODE_GAS, MODE_RAMP]

    def __init__(self,
                 device_port: str,
                 safe_connect: bool = False,
                 ):
        """

        :param device_port: port to connect to the pump
        :param safe_connect: if True, then on connection stop the pump and set the pump mode and the values for each
            mode to default values. doing this allows the class to know the state of the pump once connected
        """
        self._device_port = device_port
        self.ser: Serial = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # keep track of important properties here since the pump cannot be queried for these values
        self._safe_connect = safe_connect
        self._running: bool = False if safe_connect is True else None
        self._valve: str = self.VALVE_A if safe_connect is True else None
        self._mode: str = self.MODE_FLOW if safe_connect is True else None
        self._flow_rate: float = 1.0 if safe_connect is True else None
        self._gas_flow_rate: float = 1.0 if safe_connect is True else None
        self._dose_flow_rate: float = 1.0 if safe_connect is True else None
        self._dose_volume: float = 1.0 if safe_connect is True else None
        self._regulator_pressure: float = 1.0 if safe_connect is True else None
        self._ramp_initial_rate: float = 0.5 if safe_connect is True else None
        self._ramp_final_rate: float = 1.0 if safe_connect is True else None
        self._ramp_time: float = 1.0 if safe_connect is True else None

        self.connect()

    @property
    def device_port(self) -> str:
        return self._device_port

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, value: bool) -> None:
        self._running = value

    @property
    def valve(self) -> str:
        return self._valve

    @valve.setter
    def valve(self, value: str) -> None:
        self._valve = value

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value) -> None:
        self._mode = value

    @property
    def flow_rate(self) -> float:
        return self._flow_rate

    @flow_rate.setter
    def flow_rate(self, value: float) -> None:
        self._flow_rate = value

    @property
    def gas_flow_rate(self) -> float:
        return self._gas_flow_rate

    @gas_flow_rate.setter
    def gas_flow_rate(self, value: float) -> None:
        self._gas_flow_rate = value

    @property
    def dose_flow_rate(self) -> float:
        return self._dose_flow_rate

    @dose_flow_rate.setter
    def dose_flow_rate(self, value: float) -> None:
        self._dose_flow_rate = value

    @property
    def dose_volume(self) -> float:
        return self._dose_volume

    @dose_volume.setter
    def dose_volume(self, value: float) -> None:
        self._dose_volume = value

    @property
    def regulator_pressure(self) -> float:
        return self._regulator_pressure

    @regulator_pressure.setter
    def regulator_pressure(self, value: float) -> None:
        self._regulator_pressure = value

    @property
    def ramp_initial_rate(self) -> float:
        return self._ramp_initial_rate

    @ramp_initial_rate.setter
    def ramp_initial_rate(self, value: float) -> None:
        self._ramp_initial_rate = value

    @property
    def ramp_final_rate(self) -> float:
        return self._ramp_final_rate

    @ramp_final_rate.setter
    def ramp_final_rate(self, value: float) -> None:
        self._ramp_final_rate = value

    @property
    def ramp_time(self) -> float:
        return self._ramp_time

    @ramp_time.setter
    def ramp_time(self, value: float) -> None:
        self._ramp_time = value

    def connect(self):
        """Connect to the SF10"""
        try:
            if self.ser is None:
                cn = Serial(device_port=self.device_port,
                            **self.CONNECTION_SETTINGS,
                            )
                self.ser = cn
            else:
                self.ser.connect()
            # Turn remote control on
            response = self._send_and_receive(self._SET_RC_ENABLED)
            # Check firmware version
            response = self._send_and_receive(self._FIRMWARE)
            # Check that remote control is enabled
            response = self._send_and_receive(self._REMOTE_CONTROL_SETTING)
            if response != self._RC_ENABLED:
                self.disconnect()
                raise VapourtecError()
            else:
                # Ensure that the serial port is closed on system exit
                self.logger.debug('Connected to SF10')
                if self._safe_connect is True:
                    # set default settings to match hard-coded values in initializer for properties to track
                    self.stop()
                    self.set_valve(self.VALVE_A)
                    self.set_mode(self.MODE_FLOW)
                    self.set_flow_rate(1.0)
                    self.set_gas_flow_rate(1.0)
                    self.set_dose_volume(1.0)
                    self.set_ramp(0.5, 1.0, 1.0)
                atexit.register(self.disconnect)
        except Exception as e:
            self.logger.warning("Could not connect to an SF10, make sure the right port was selected and that remote "
                                "control is enabled")
            raise VapourtecError("Could not connect to an SF10, make sure the right port was selected and that remote "
                                 "control is enabled")

    def disconnect(self):
        """Disconnect from the SL10 and switch to local mode, doesnt turn it off"""
        if self.ser is None:
            # if SF10 is already disconnected then self.ser is None
            return
        try:
            self.ser.disconnect()
            self.ser = None
            self.logger.debug('Disconnected from SF10')
        except Exception as e:
            self.logger.warning("Could not disconnect from SF10")

    def start(self) -> bool:
        """
        :return: True if command was sent, False otherwise
        """
        response = self._send_and_receive(self._START)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug('Start SF10')
            self.running = True
            return True
        else:
            self.logger.warning('SF10 failed to start')
            return False

    def stop(self) -> bool:
        """
        :return: True if command was sent, False otherwise
        """
        response = self._send_and_receive(self._STOP)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug('Stop SLF10')
            self.running = False
            return True
        else:
            self.logger.warning('SF10 failed to stop')
            return False

    def set_valve(self, valve: str) -> bool:
        """
        :param str, valve: either A or B, valve position to select

        :return: True if command was sent, False otherwise
        """
        if valve not in self._VALVES:
            self.logger.warning(f'Valve position must be one of "{SF10.VALVE_A}" or "{SF10.VALVE_B}"')
            return False
        command = self._SET_VALVE + f' {valve}'
        response = self._send_and_receive(command)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug(f'Valve position set to {valve}')
            self.valve = valve
            return True
        else:
            self.logger.warning(f'Valve position failed to be set to {valve}')
            return False

    def set_mode(self, mode: str) -> bool:
        """
        Select pump mode

        :param str, mode: one of FLOW, REG, DOSE, GAS, or RAMP

        :return: True if command was sent, False otherwise
        """
        if mode not in self._MODES:
            self.logger.warning(f"Valve position must be one of '{SF10.MODE_FLOW}',"
                                f" '{SF10.MODE_REGULATOR}', '{SF10.MODE_DOSE}', "
                                f"'{SF10.MODE_GAS}', or '{SF10.MODE_RAMP}'")
            return False
        command = self._SET_MODE + f' {mode}'
        response = self._send_and_receive(command)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug(f'Pump mode set to {mode}')
            self.mode = mode
            return True
        else:
            self.logger.warning(f'Pump mode failed to be set to {mode}')
            return False

    def set_flow_rate(self, flow_rate: float) -> bool:
        """
        :param float, flow_rate: flow rate in mL/min for FLOW and DOSE modes

        :return: True if command was sent, False otherwise
        """
        if type(flow_rate) == str:
            flow_rate = float(flow_rate)
        if type(flow_rate) != float and type(flow_rate) != int:
            self.logger.warning('Flow rate must be a numerical value')
            return False
        flow_rate = float(round(flow_rate, 3))
        command = self._SET_FLOW_RATE + f' {str(flow_rate)}'
        response = self._send_and_receive(command)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug(f'Flow rate set to {flow_rate} mL/min')
            self.flow_rate = flow_rate
            return True
        else:
            self.logger.warning(f'Flow rate failed to be set to {flow_rate} mL/min')
            return False

    def set_gas_flow_rate(self, flow_rate: float) -> bool:
        """
        :param float, flow_rate: gas flow rate in ssc/min for GAS mode

        :return: True if command was sent, False otherwise
        """
        if type(flow_rate) == str:
            flow_rate = float(flow_rate)
        if type(flow_rate) != float and type(flow_rate) != int:
            self.logger.warning('Gas flow rate must be a numerical value')
            return False
        command = self._SET_GAS_FLOW_RATE + f' {str(flow_rate)}'
        response = self._send_and_receive(command)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug(f'Gas flow rate set to {flow_rate} ssc/min')
            self.gas_flow_rate = flow_rate
            return True
        else:
            self.logger.warning(f'Gas flow rate failed to be set to {flow_rate} ssc/min')
            return False

    def set_regulator_pressure(self, pressure: float) -> bool:
        """
        :param float, pressure: pressure in bar for REGULATOR mode

        :return: True if command was sent, False otherwise
        """
        if type(pressure) == str:
            pressure = float(pressure)
        if type(pressure) != float and type(pressure) != int:
            self.logger.warning('Pressure must be a numerical value')
            return False
        command = self._SET_REGULATOR_PRESSURE + f' {str(pressure)}'
        response = self._send_and_receive(command)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug(f'Regulator pressure set to {pressure} bar')
            self.regulator_pressure = pressure
            return True
        else:
            self.logger.warning(f'Regulator pressure failed to be set to {pressure} bar')
            return False

    def set_dose_volume(self, volume: float) -> bool:
        """
        :param float, volume: volume in mL for DOSE mode

        :return: True if command was sent, False otherwise
        """
        if type(volume) == str:
            volume = float(volume)
        if type(volume) != float and type(volume) != int:
            self.logger.warning('Volume must be a numerical value')
            return False
        command = self._SET_DOSE_VOLUME + f' {str(volume)}'
        response = self._send_and_receive(command)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.debug(f'Dose volume set to {volume} mL')
            self.dose_volume = volume
            return True
        else:
            self.logger.warning(f'Dose volume failed to be set to {volume} mL')
            return False

    def set_ramp(self, initial: float, final: float, t: float) -> bool:
        """
        Set the ramp in RAMP mode

        :param float, initial: initial ramp speed in mL/min
        :param float, final: final ramp speed in mL/min
        :param float, t: time to go from the initial to final ramp speed in minutes

        :return: True if command was sent, False otherwise
        """
        if type(initial) == str:
            initial = float(initial)
        if type(final) == str:
            final = float(final)
        if type(t) == str:
            t = float(t)
        if type(initial) != float and type(initial) != int:
            self.logger.warning('Initial must be a numerical value')
            return False
        if type(final) != float and type(final) != int:
            self.logger.warning('Final must be a numerical value')
            return False
        if type(t) != float and type(t) != int:
            self.logger.warning('Time must be a numerical value')
            return False
        command = self._SET_RAMP + f' {str(initial)}' + f' {str(final)}' + f' {str(t)}'
        response = self._send_and_receive(command)
        if response == self._COMMAND_SENT_RESPONSE:
            self.logger.warning(f'Ramp set to go from {initial} mL/min to {final} mL/min in {t} minutes')
            self.ramp_final_rate = final
            self.ramp_initial_rate = initial
            self.ramp_time = t
            return True
        else:
            self.logger.warning(f'Ramp failed to be set to go from {initial} mL/min to {final} mL/min in {t} '
                                f'minutes')
            return False

    def _send_and_receive(self,
                          command: str,
                          ) -> str:
        """
        Send a command, get a response back, and return the response
        :param str, command: the command to send to the SF10

        :return:
        """
        with self._lock:
            # format the command to send so that it terminates with the line ending (CR)
            formatted_command: str = command + self.LINE_ENDING
            formatted_command_encoded = formatted_command.encode()
            # this is the response, and the return string
            response_string = self.ser.request(data=formatted_command_encoded,
                                               line_ending=self.LINE_ENDING_ENCODED,
                                               ).decode()
            # sometimes for some cables/communicating with a raspberry pi, '/n' is the first part of a
            # response back from the pump, so strip that out
            if response_string.count('\n') == 1:
                response_string = response_string.strip('\n')
            return response_string

