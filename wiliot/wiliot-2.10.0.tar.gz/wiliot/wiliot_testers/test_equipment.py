'''
Created on Nov 30, 2021

@author: davidd
'''
from time import time, sleep
from sys import path
from os.path import join, dirname

import sys
import glob
import serial


class EquipmentError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        # print('calling str')
        if self.message:
            return 'EquipmentError: {msg}'.format(msg=self.message)
        else:
            return 'EquipmentError has been raised'


class Serial():

    def __init__(self):
        pass

    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


class Attenuator(object):
    '''
    Support class for:
    APITech Aeroflex Weinschel, 4205, 0, V1.30
    '''

    def __init__(self, ATTN_type, comport='AUTO'):
        if 'API' in ATTN_type:
            self._active_TE = Attenuator.API(comport)
        else:
            pass

    def GetActiveTE(self):
        return self._active_TE

    class API(object):

        def __init__(self, comport="AUTO"):
            self.baudrate = 9600
            if comport == "AUTO":
                ports_list = Serial().serial_ports()
                for port in ports_list:
                    self.comport = port
                    self.s = serial.Serial(self.comport, self.baudrate, timeout=0.5)
                    sleep(1)
                    # Turn the console off
                    self.s.write("CONSOLE DISABLE\r\n".encode())
                    # Flush the buffers
                    sleep(0.5)
                    self.s.flush()
                    self.s.flushInput()
                    self.s.flushOutput()

                    resp = self.Query("*IDN?\r\n")
                    self.model = resp
                    if ("Aeroflex" in resp):
                        print('Found ' + resp.strip('\r\n') + ' on port: ' + port)
                        break
                    elif '8311' in resp or '8331' in resp:
                        print('Found ' + resp.strip('\r\n') + ' on port: ' + port)
                    else:
                        pass
            else:
                self.s = serial.Serial(comport, self.baudrate, timeout=0.5)
                sleep(1)
                self.s.write("CONSOLE DISABLE\r\n".encode())
                # Flush the buffers
                self.s.flush()
                self.s.flushInput()
                self.s.flushOutput()
                resp = self.Query("*IDN?\r\n")
                self.model = resp
                if ("Aeroflex" in resp):
                    print('Found ' + resp.strip('\r\n') + ' on port: ' + comport)
                elif '8311' in resp or '8331' in resp:
                    print('Found ' + resp.strip('\r\n') + ' on port: ' + comport)
                else:
                    print('Aeroflex Attenuator not found on selected port, check connection', file=sys.stderr)

        def Write(self, cmd, wait=False):
            """Send the input cmd string via COM Socket"""
            if self.s.isOpen():
                pass
            else:
                self.s.open()
            self.s.flushInput()
            sleep(1)
            try:
                self.s.write(str.encode(cmd))
                sleep(0.5)  # Commands may be lost when writing too fast

            except:
                pass
            # self.s.close()

        def Query(self, cmd):
            """Send the input cmd string via COM Socket and return the reply string"""
            if self.s.isOpen():
                pass
            else:
                self.s.open()
                sleep(0.5)
            # self.s.flushInput()
            sleep(1)
            try:
                self.s.write(cmd.encode())
                # sleep(0.5)
                data = self.s.readline().decode("utf-8")
            except:
                data = ''
            # self.s.close()
            return data

        def close_port(self):
            if self.s is not None and self.s.isOpen():
                self.s.close()

        def is_open(self):
            if self.s is not None:
                return self.s.isOpen()
            return True

        def Setattn(self, attn):
            cmd = "ATTN {:.2f}\r\n".format(attn)
            self.Write(cmd)
            value = self.Getattn()
            return value

        def Getattn(self):
            cmd = "ATTN?\r\n"
            value = self.Query(cmd)
            return value


class Tescom:
    """
    Control TESCOM testing chambers
    """
    open_cmd = b'OPEN\r'
    close_cmd = b'CLOSE\r'
    com_port_obj = None
    models_list = ['TC-5064C', 'TA-7011AP', 'TC-5063A', 'TC-5970CP']

    def __init__(self, port=None):
        self.port = port
        try:
            if port is not None:
                self.connect(port)

        except Exception as e:
            print(e)
            print("Tescom - Connection failed")

    def connect(self, port):
        """
        :param port: com port to connect
        :return: com port obj
        """
        try:
            com_port_obj = self.com_port_obj = serial.Serial(port=port, baudrate=9600, timeout=1)
            if com_port_obj is not None:
                self.door_cmd = None
                self.com_port_obj.write(b'MODEL?\r')
                sleep(0.5)
                model = str(self.com_port_obj.read(14))
                parts = [p for p in model.split("'")]
                parts = [p for p in parts[1].split(" ")]
                self.model = parts[0]
                if len(self.model) > 0:
                    print("RF chamber connected to port " + str(port))
                    print("Tescom - Chamber model:", self.model)
                else:
                    print("Tescom - Error! No chamber found")
                    return
                if self.model in self.models_list:
                    self.door_cmd = b'DOOR?\r'
                else:
                    self.door_cmd = b'LID?\r'
            else:
                raise Exception
        except Exception as e:
            # print(e)
            print(("Tescom - Could not connect to port " + port))
            return None

    def close_port(self):
        """
        closes com port
        """
        try:
            self.com_port_obj.close()
            print("RF chamber disconnected from port: " + str(self.port))
        except Exception as e:
            print("Could not disconnect")

    def open_chamber(self):
        """
        opens chamber
        :return: "OK" if command was successful
        """
        if self.is_door_open():
            print("Chamber is open")
            return 'OK'
        try:
            print(f"Chamber {self.port} is opening")
            self.com_port_obj.reset_input_buffer()
            self.com_port_obj.reset_output_buffer()
            self.com_port_obj.write(self.open_cmd)
            res = ''
            wait_counter = 0
            while 'OK' not in res:
                if wait_counter >= 15:
                    raise Exception(f"Error in opening chamber {self.port}")
                res = self.com_port_obj.read(14).decode(
                    'utf-8').upper().rstrip('\r')
                if len(str(res)) > 0:
                    print(f'Chamber {self.port} status: ' + str(res))
                wait_counter += 1
                sleep(0.5)
            if not self.is_door_open():
                raise Exception(
                    f"{self.port} Door status doesn't match command sent!")
            print(f"Chamber {self.port} is open")
            return 'OK'
        except Exception as e:
            print(e)
            return "FAIL"

    def close_chamber(self):
        """
        closes chamber
        :return: "OK" if command was successful
        """
        if self.is_door_closed():
            print("Chamber closed")
            return 'OK'
        try:
            print(f"CHAMBER {self.port} IS CLOSING, CLEAR HANDS!!!")
            sleep(2)
            self.com_port_obj.write(self.close_cmd)
            res = ''
            wait_counter = 0
            while 'READY' not in res:
                if wait_counter >= 20:
                    raise Exception(f"Error in closing chamber {self.port}")
                res = self.com_port_obj.read(14).decode(
                    'utf-8').upper().rstrip('\r')
                if 'ERR' in res or 'READY' in res or 'OK' in res:
                    print(f'Chamber {self.port} status: ' + str(res))
                if 'ERR' in res:
                    return "FAIL"
                wait_counter += 1
                sleep(0.5)
            if not self.is_door_closed():
                raise Exception(
                    f"{self.port} Door status doesn't match command sent!")
            print(f"Chamber {self.port} closed")
            return 'OK'
        except Exception as e:
            print(f"Error in closing chamber {self.port}")
            print(e)
            return "FAIL"

    def is_connected(self):
        if self.com_port_obj is None:
            return False
        return self.com_port_obj.isOpen()

    def get_state(self):
        self.com_port_obj.reset_input_buffer()
        sleep(0.5)
        self.com_port_obj.write(self.door_cmd)
        sleep(0.5)
        state = self.com_port_obj.read(14).decode('utf-8').upper().rstrip('\r')
        return state

    def is_door_open(self):
        state = self.get_state()
        if 'OPEN' in state:
            return True
        return False

    def is_door_closed(self):
        state = self.get_state()
        if 'CLOSE' in state:
            return True
        return False


class BarcodeScanner(object):
    prefix = '~0000@'
    suffix = ';'
    com = ''
    serial = None

    def __init__(self, com=None, baud=115200, config=True, log_type='NO_LOG'):
        self.log_type = log_type
        if com != None:
            self.open_port(com, baud=baud, config=config)
        # else:
        #     self.serial = ser = Serial()

    def scan(self):
        # print("analog_trigger_setting")
        self.serial.write(b"\x1b\x31")
        sleep(0.1)
        # t = ser.read(ser.in_waiting)
        t = self.serial.read_all()
        # print(t)
        return t

    def scan_and_flush(self):
        self.serial.flushInput()
        self.serial.flushOutput()
        t = self.scan()
        self.serial.flushInput()
        self.serial.flushOutput()
        tClean = str(t).split('\\x')[-1]
        if tClean.startswith('06'):
            return str(t).split('\\x06')[-1].strip("'")
        else:
            print('Warning - not received ACK from barcode scanner.')
            return str(t).split('\\x')[-1]

    def scan_ext_id(self, scanDur=0.5, sleepDur=0.005):
        barcodeRead = ''
        startTime = time()
        while ((time() - startTime) < scanDur):
            barcodeRead = self.scan_and_flush()
            # barcodeRead = str(t)
            if len(barcodeRead) < 8:
                barcodeRead = ''
                continue

            fullData = curId = reelId = gtin = barcodeRead
            try:
                # fullData = barcodeRead.split('\\x')[-1]
                gtin = ')'.join(fullData.split(')')[:2]) + ')'
                tagData = fullData.split(')')[2]
                curId = tagData.split('T')[1].strip("' ").split('(')[0]
                reelId = tagData.split('T')[0].strip("' ")
                return fullData, curId, reelId, gtin
            except:
                pass
            return fullData, curId, reelId, gtin

        return None, None, None, None

    def auto_scan(self):
        # print("Automatic reading settings")
        self.serial.write(b"\x1b\x32")
        sleep(0.1)
        t = self.serial.read_all()
        # print(t)
        return t

    def trigger_stop_settings(self):
        # print("Trigger_stop_settings")
        # sleep(0.1)
        # t = ser.read(ser.in_waiting)
        sleep(0.1)
        t = self.serial.read_all()
        self.serial.flushInput()
        self.serial.flushOutput()
        sleep(0.1)
        # print(t)
        acks = str(t).split(';')[:-1]
        isSuccess = all([True if ack.endswith('\\x06')
                         else False for ack in acks])
        return isSuccess

    def open_port(self, com, baud=115200, config=True):
        if self.serial != None and self.serial.is_open():
            self.serial.closePort()
        self.serial = ser = serial.Serial(com, baud, timeout=0.5)
        if not self.check_com_port():
            print(f'{com} is not barcode scanner')
        if ser != None and self.log_type != 'NO_LOG':
            print(f'Barcode scanner ({com}) connected.')
        elif ser == None:
            print(f'Barcode scanner - Problem connecting {com}')
        self.com = com
        ser.timerout = 1  # read time out
        ser.writeTimeout = 0.5  # write time out.
        if config:
            self.configure()

    def close_port(self):
        if self.serial.isOpen():
            self.serial.close()

    def is_open(self):
        if self.serial is not None:
            return self.serial.isOpen()
        else:
            return False

    def configure(self, illScn='1', amlEna='0', grbEna='0', grbVll='2', atsEna='0', atsDur='36000', scnMod='0', pwbEna='1'):
        '''
        illScn - illumination:    0-off, 1-normal, 2-always on
        amlEna - aiming:          0-off, 1-normal, 2-always on
        pwbEna - power on beep    0-off, 1-on
        grbEna - good read beep   0-off, 1-on
        atsEna - auto sleep       0-disable, 1-enable
        atsDur - sleep duration   1-36000 [sec]
        scnMod - scan mode        0-level mode, 2-sense mode, 3-continuous mode, 7-batch mode
        '''
        sleep(0.1)
        params = {'ILLSCN': illScn, 'AMLENA': amlEna, 'GRBENA': grbEna, 'ATSENA': atsEna,
                  'GRBVLL': grbVll, 'ATSDUR': atsDur, 'SCNMOD': scnMod, 'PWBENA': pwbEna}
        params = [key + value for key, value in params.items()]
        configs = self.prefix + ';'.join(params) + self.suffix
        self.serial.write(str.encode(configs))
        # self.serial.write(b'ILLSCN2;AMLENA2;GRBENA0;ATSENA0,DUR0;SCNMOD0;')
        sleep(0.1)
        isSuccess = self.trigger_stop_settings()
        if isSuccess and self.log_type != 'NO_LOG':
            print(f'Barcode scanner ({self.com}) configured successfully.')
        elif not isSuccess:
            print(f'Barcode scanner ({self.com}) configuration failed.')

    def restore_all_factory_defaults(self):
        sleep(0.1)
        params = {'FACDEF': ''}
        params = [key + value for key, value in params.items()]
        configs = self.prefix + ';'.join(params) + self.suffix
        self.serial.write(str.encode(configs))
        sleep(0.1)
        isSuccess = self.trigger_stop_settings()
        if isSuccess and self.log_type != 'NO_LOG':
            print(f'Barcode scanner ({self.com}) restored factory default successfully.')
        elif not isSuccess:
            print(f'Barcode scanner ({self.com}) restored factory default failed.')

    def manual_configure(self, params):
        sleep(0.1)
        configs = self.prefix + ';'.join(params) + self.suffix
        self.serial.write(str.encode(configs))
        sleep(0.1)
        t = self.serial.read_all()
        # print(t)
        return t

    def find_and_open_port(self, baud=115200, config=True):
        com = self.find_com_port(baud)
        if com is not None:
            self.open_port(com, baud, config)
            return True
        return False

    def find_com_port(self, baud=115200):
        comPorts = [
            s.device for s in serial.tools.list_ports.comports()]
        if len(comPorts) == 0:
            comPorts = comPorts = [
                s.name for s in serial.tools.list_ports.comports()]

        coms = []
        for com in comPorts:
            if self.check_com_port(com, baud):
                coms.append(com)
                if len(coms) > 1:
                    print(
                        'Warning - more than one barcode scanner found, using the first barcode scanner.')

        if len(coms) > 0:
            return coms[0]
        else:
            print('Error - could not find barcode scanner.')
            return None

    def check_com_port(self, com=None, baud=115200):
        is_bar_scan = True
        close_port = False
        if not self.is_open() and com is not None:
            close_port = True
            self.serial = serial.Serial(com, baud, timeout=0.5)
        elif not self.is_open():
            print('BarcodeScanner - check_com_port: Missing com port')
            return False
        res = self.manual_configure(['QRYPDN'])
        if not 'NLS-N1' in str(res):
            is_bar_scan = False
        if close_port:
            self.serial.close()
            self.serial = None

        return is_bar_scan
