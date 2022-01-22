# -*- coding: utf-8 -*-
###############################################
###########  COMMUNICATION FUNCTIONS  #########
###############################################
#2020-09-23
#2021-01-31  v3.0
#2021-02-03  v3.1
#2021-02-15  v3.2
#2021-03-11  v3.3  rs485 try connection
#2021-03-18  v3.4  stop thread option

from susee.see_functions import time_utc, build_param
from susee.see_dict import err_code
import time
from pymodbus.client.sync import ModbusSerialClient as ModbusRTU
from pymodbus.client.sync import ModbusTcpClient as ModbusTCP
import threading

from datetime import datetime

import logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def write_register(idComm,addrReg,value):
    #ver. 4.0 - 2019-08-23
    #ver. 4.1 - 2020-11-27  added stopbits, parity
    #Variabili locali
    codeError_rr	= 0 
    rr              = 0 

    if   idComm['method'] =='rtu':

        #
        #Connessione RTU
        #
        idAddr          = idComm['idAddr']
        COMport         = idComm['ipAddr_COM']
        baudrate        = idComm['baudrate']
        timeout         = idComm['timeout']
        StopBits        = idComm['StopBits']
        parity          = idComm['parity']
         
        client = ModbusRTU(	method		='rtu', 
						    port        = COMport , 
						    baudrate    = baudrate, 
						    timeout     = timeout,
                            stopbits    = StopBits,
                            parity      = parity
                               )

    elif idComm['method'] =='tcp':

        ipAddr  = idComm['ipAddr_COM']
        timeout = idComm['timeout']
        idAddr  = idComm['idAddr']
        idPort  = idComm['Port']
   
        client = ModbusTCP(  ipAddr, port=  idPort)
        client.timeout = timeout

    else:
        exit
    
    if client.connect():

        rr = client.write_register(addrReg,value,unit=idAddr)
        try:
            if rr.function_code > 0x80:
                codeError_rr+= err_code['err_register']
        except:
            pass
        try:
            if rr.string:
                codeError_rr+= err_code['err_register']
        except:
            pass
        client.close()
    else:
            codeError_rr  += err_code['err_connection']

    return rr, codeError_rr, time_utc()

def write_registers(idComm, addrReg, value):
    # ver. 1.0 - 2020-0518
    # ver 2.0   - 2020-07-06

    codeError_rr = 0
    rr = 0

    if idComm['method'] == 'rtu':

        #
        # Connessione RTU
        #
        idAddr = idComm['idAddr']
        COMport = idComm['ipAddr_COM']
        baudrate = idComm['baudrate']
        timeout = idComm['timeout']
        StopBits = idComm['StopBits']
        parity = idComm['parity']

        client = ModbusRTU(method	='rtu',
                           port        = COMport ,
                           baudrate    = baudrate,
                           timeout     = timeout,
                            stopbits = StopBits,
                            parity = parity,)


    elif idComm['method'] =='tcp':

        ipAddr  = idComm['ipAddr_COM']
        timeout = idComm['timeout']
        idAddr  = idComm['idAddr']
        idPort  = idComm['Port']

        client = ModbusTCP(ipAddr, port= idPort)
        client.timeout = timeout

    else:
        exit

    if client.connect():

        rr = client.write_registers(addrReg, value, unit=idAddr)
        try:
            if rr.function_code > 0x80:
                codeError_rr += err_code['err_register']
        except:
            pass
        try:
            if rr.string:
                codeError_rr += err_code['err_register']
        except:
            pass
        client.close()
    else:
        codeError_rr  += err_code['err_connection']
    now_ = time_utc()
    return rr, codeError_rr, now_

#Read devices
def read_registers(idComm, addrReg):
    # ver. 4.0 - 2019-08-23
    # ver 2.0   - 2020-07-06
    # ver 2.1   - 2020-11-27

    codeError_rr = [0] * len(addrReg)
    rr = [{} for x in range(len(addrReg))]

    if idComm['method'] == 'rtu':
        #
        # Connessione RTU
        #
        idAddr = idComm['idAddr']
        COMport = idComm['ipAddr_COM']
        baudrate = idComm['baudrate']
        timeout = idComm['timeout']
        StopBits = idComm['StopBits']
        parity = idComm['parity']

        client = ModbusRTU(method	='rtu',
                               port        = COMport ,
                               baudrate    = baudrate,
                               timeout     = timeout,
                               stopbits     =StopBits,
                               parity       =parity,
                           )

    elif idComm['method'] =='tcp':
        #
        # Connessione TCP
        #
        ipAddr  = idComm['ipAddr_COM']
        timeout = idComm['timeout']
        idAddr  = idComm['idAddr']
        idPort  = idComm['Port']

        client = ModbusTCP(ipAddr, port=  idPort)
        client.timeout = timeout
    else:
        return '', 'nok conn tyoe', time_utc()

    if client.connect():
        for x in range(len(addrReg)):
            AddrStart = [*addrReg.items()][x][1][0]
            AddrNum  =  [*addrReg.items()][x][1][1] - AddrStart

            rr[x] = client.read_holding_registers(address  = AddrStart,
                                                  count = AddrNum,
                                                  unit = idAddr)
            try:
                if rr[x].function_code > 0x80:
                    codeError_rr[x]+= err_code['err_register']
            except:
                pass
            try:
                if rr[x].string:
                    codeError_rr[x]+= err_code['err_register']
            except:
                pass
    else:
        for x in range(len(addrReg)):
            codeError_rr[x]  += err_code['err_connection']

    try:
        client.close()
    except:
        pass

    return rr, codeError_rr, time_utc()

def internet_(host,port, time):
    import os
    #host = "8.8.8.8"
    t= os.system('ping   192.168.1.13 ')
    #"ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', host), shell=True)
    #"ping " + ("-n 1 " if  sys.platform().lower()=="win32" else "-c 1 ") + host)
    
    if t:
        return True
    else:
        return False

def internet2():
    # v2.0 2020-03-22
    # check if host/port is open
    # https://stackoverflow.com/questions/3764291/checking-network-connection

    import socket
    ipaddress = socket.gethostbyname(socket.gethostname())
    if ipaddress == "127.0.0.1":
       return False
    else:
        return True

def internet(host, port, timeout):
    #v1.0 2018-07-2-18
    #check if host/port is open 
    import socket
    #socket.create_connection().shutdown(0)

    try:
        socket.create_connection((host,port),timeout)
        socket.create_connection((host, port)).close()
        errorID = 1
        return errorID
    except socket.error: # as err :
        errorID = -1
        return errorID

class c_read_registers_old:
    # Read Registers Class
    # v1.0 2020-09-25
    # v1.2 2020-09-30
    # v1.3 2020-11-27 Parity Stopbits

    def __init__(self, idDevPack):
        self.idDevPack = idDevPack

    def open(self):
        if self.idDevPack['method'] == 'rtu':
            #
            # Connessione RTU
            #
            idAddr = self.idDevPack['idAddr']
            COMport = self.idDevPack['ipAddr_COM']
            baudrate = self.idDevPack['baudrate']
            timeout = self.idDevPack['timeout']
            Parity = self.idDevPack['parity']   # 'N': none; 'E': even; 'O': odd; default: N
            Stopbits = self.idDevPack['StopBits'] # 1

            client = ModbusRTU(method='rtu',
                               port=COMport,
                               baudrate=baudrate,
                               timeout=timeout,
                               parity= Parity,
                               Bytesize= 8,
                               Stopbitss=Stopbits,
                               )
            #client.write_register()
        elif self.idDevPack['method'] == 'tcp':
            #
            # Connessione TCP
            #
            ipAddr = self.idDevPack['ipAddr_COM']
            timeout = self.idDevPack['timeout']
            idAddr = self.idDevPack['idAddr']
            idPort = self.idDevPack['Port']

            client = ModbusTCP(ipAddr, port=idPort)
            client.timeout = timeout

        return client

    def read_rr(self, addrReg):
        # read_holding_registers
        # ver. 4.0 - 2019-08-23
        # ver 2.0   - 2020-07-06
        # ver 2.1 - 2020-09-23 - out rr_time
        # ver 3.0 2020-09-25

        n_rr = len(addrReg)
        codeError_rr = [0] *  n_rr
        rr = [{} for x in range(n_rr)]
        rr_dtime = [0] * n_rr

        if self.client.connect():
            for x in range(n_rr):
                AddrStart = [*addrReg.items()][x][1][0]
                AddrNum = [*addrReg.items()][x][1][1] - AddrStart

                t0_=time.time_ns()
                rr[x] = self.client.read_holding_registers(address=AddrStart,
                                                      count=AddrNum,
                                                      unit=self.idDevPack['idAddr'])
                rr_dtime[x] = time.time_ns() - t0_
                try:
                    if rr[x].function_code > 0x80:
                        codeError_rr[x] += err_code['err_register']
                except:
                    pass
                try:
                    if rr[x].string:
                        codeError_rr[x] += err_code['err_register']
                except:
                    pass
        else:
            for x in range(n_rr):
                codeError_rr[x] += err_code['err_connection']
        return rr, codeError_rr, rr_dtime

    def read_ir(self, addrReg):
        # read_input_registers
        # ver 1.0 2020-10-17

        n_rr = len(addrReg)
        codeError_rr = [0] *  n_rr
        rr = [{} for x in range(n_rr)]
        rr_dtime = [0] * n_rr

        if self.client.connect():
            for x in range(n_rr):
                AddrStart = [*addrReg.items()][x][1][0]
                AddrNum = [*addrReg.items()][x][1][1] - AddrStart +1

                t0_=time.time_ns()
                rr[x] = self.client.read_input_registers(   address=AddrStart,
                                                            count=AddrNum,
                                                            unit=self.idDevPack['idAddr'])
                rr_dtime[x] = time.time_ns() - t0_
                try:
                    if rr[x].function_code > 0x80:
                        codeError_rr[x] += err_code['err_register']
                except:
                    pass
                try:
                    if rr[x].string:
                        codeError_rr[x] += err_code['err_register']
                except:
                    pass
        else:
            for x in range(n_rr):
                codeError_rr[x] += err_code['err_connection']
        return rr, codeError_rr, rr_dtime

    def write_reg(self, addrReg, value):
        codeWrite_err =0

        rr = self.client.write_register(addrReg, value, unit=self.idDevPack['idAddr'])
        try:
            if rr.function_code > 0x80:
                codeWrite_err = err_code['err_register']
        except:
            pass
        try:
            if rr.string:
                codeWrite_err = err_code['err_register']
        except:
            pass
        return codeWrite_err


    def close(self):
        try:
            self.client.close()
        except:
            pass

#2021-01-31 - v3.0 - threads
class c_comm_devices(threading.Thread):
    #Base comm class
    # ver 3.1 2021-01-26
    # ver 3.2 2021-01-31

    def __init__(self, idDevPack, *args, **kwargs):
        super(c_comm_devices, self).__init__(*args, **kwargs)

        self.idDevPack = idDevPack
        self.time_ = [0] * 6
        logger.info(f"__init__ {self.idDevPack['Port']}")
        self.client = None
        self.addrList = {}
        self.num=0
        self.read_en = False
        self.sync_ = True
        self.stop = False

    def setup(self):
        self.n_rr = len(self.addrList)
        self.codeError_rr = [0] * self.n_rr
        self.rr = [{} for x in range(self.n_rr)]
        self.rr_dtime = [0] * self.n_rr
        self.rr_delay = [0] * self.n_rr

    def open_conn(self):
        if self.idDevPack['method'] == 'rtu':
            #
            # Connessione RTU
            #
            idAddr = self.idDevPack['idAddr']
            COMport = self.idDevPack['ipAddr_COM']
            baudrate = self.idDevPack['baudrate']
            timeout = self.idDevPack['timeout']
            Parity = self.idDevPack['parity']   # 'N': none; 'E': even; 'O': odd; default: N
            Stopbits = self.idDevPack['StopBits'] # 1

            self.client = ModbusRTU(method='rtu',
                               port=COMport,
                               baudrate=baudrate,
                               timeout=timeout,
                               parity= Parity,
                               Bytesize= 8,
                               Stopbitss=Stopbits,
                               )

        elif self.idDevPack['method'] == 'tcp':
            #
            # Connessione TCP
            #
            ipAddr = self.idDevPack['ipAddr_COM']
            timeout = self.idDevPack['timeout']
            idAddr = self.idDevPack['idAddr']
            idPort = self.idDevPack['Port']

            self.client = ModbusTCP(ipAddr, port=idPort)
            self.client.timeout = timeout

        try:
            logger.info(f"{self.idDevPack['idDev']} --- OPEN connnection result: {self.client.connect()}")
        except:
            logger.info(f"{self.idDevPack['idDev']} --- OPEN connnection WRONG self.client {self.client}!")

        self.time_[1] = time.time_ns()  # time after connection

        #Setup regs
        self.setup()

    def close_conn(self):
        try:
            self.client.close()
            logger.info(f"{self.idDevPack['idDev']} --- CLOSE connnection result: {self.client.connect()}")
        except:
            pass
            logger.info(f"{self.idDevPack['idDev']} --- CLOSE connnection NOK   !!!!!!!!!!!!!!")

    def read_regs(self, type_):

        for x in range(self.n_rr):
            self.codeError_rr[x] = 0
            self.rr_dtime[x] = 0
            self.rr_delay[x] = 0

        if self.client.connect():
            for x in range(self.n_rr):
                AddrStart = self.addrList[x+1][0]  #[*self.addrList.items()][x][1][0]
                AddrNum =   self.addrList[x+1][1] - AddrStart #[*self.addrList.items()][x][1][1] - AddrStart

                t0_ = time.time_ns()
                if type_ == 'rr':
                    try:
                        self.rr[x] = self.client.read_holding_registers(address=AddrStart,
                                                                   count=AddrNum,
                                                                   unit=self.idDevPack['idAddr'])
                    except:
                        self.codeError_rr[x] += err_code['err_connection']

                if type_ == 'ir':
                    try:
                        self.rr[x] = self.client.read_input_registers(address=AddrStart,
                                                               count=AddrNum,
                                                               unit=self.idDevPack['idAddr'])
                    except:
                        self.codeError_rr[x] += err_code['err_connection']

                trr_ = time.time_ns()
                self.rr_dtime[x] = trr_ - t0_  # time to read registers
                self.rr_delay[x] = trr_ - self.TimeStamp_ns
                logger.info(f"{self.idDevPack['idDev']}:{x} --- READ REGS lenght:{self.rr[x]}  --- delay {float(self.rr_dtime[x])/1000.0} ms")

                try:
                    if self.rr[x].function_code > 0x80:
                        self.codeError_rr[x] += err_code['err_register']
                except:
                    pass
                try:
                    if self.rr[x].string:
                        self.codeError_rr[x] += err_code['err_register']
                except:
                    pass
        else:
            logger.info(f"{self.idDevPack['idDev']}: NOT READ REGS !!!!!!!!!!!!!!!!!!!!!!!!!1")
            for x in range(self.n_rr):
                self.rr_delay[x] = time.time_ns() - self.TimeStamp_ns
                self.codeError_rr[x] += err_code['err_connection']

    def read_regs_fast(self, type_):
        if self.client.connect():
            for x in range(self.n_rr):

                self.rr[x] = self.client.read_holding_registers(address=self.addrList[x + 1][0],
                                                                    count=self.addrList[x + 1][1] -self.addrList[x + 1][0] ,
                                                                    unit=self.idDevPack['idAddr'])
        else:
            logger.info(f"{self.idDevPack['idDev']}: NO CONNECTION ACTIVE READ REGS !!!!!!!!!!!!!!!!!!!!!!!!!1")
            for x in range(self.n_rr):
                self.rr_delay[x] = time.time_ns() - self.TimeStamp_ns
                self.codeError_rr[x] += err_code['err_connection']

    def run(self, *args):
        while True:
            if self.read_en:
                self.time_[2] = time.time_ns()  # time before read registers
                self.read_regs('rr')
                self.time_[3] = time.time_ns()  # time After read registers
                if self.sync_:
                    self.read_en = False
            if self.stop:
                break

    def run_once(self, *args):
        self.time_[2] = time.time_ns()  # time before read registers
        self.read_regs('rr')
        self.time_[3] = time.time_ns()  # time After read registers
        self.read_en = False

    def build_values(self):
        # From regs data to values - out as dictionary
        # v1.0 2020-09-27
        # v2.0 2021-01-26
        # v3.0 2021-01-26

        self.time_[4] = time.time_ns()  # time BEFORE data format

        self.param_list = {}
        #TimeStamp_us = time.mktime(self.TimeStamp.timetuple()) + self.TimeStamp.microsecond * 1e-6
        #self.Delay = self.time_[3] * 10 **-9 - TimeStamp_us  # [s]
        #self.Delay = (self.time_[3] - self.TimeStamp_ns)*10**-9

        #k_ = 1000
        #self.Delay = self.Delay * k_  # [ms]

        for x in range(len(self.pDict)):
            self.param_list[x] = build_param(self.pDict[x],
                                             self.idDevPack['idDev'],
                                             self.rr[self.pDict[x]['idAddrList'] - 1],
                                             self.codeError_rr[self.pDict[x]['idAddrList'] - 1],
                                             self.TimeStamp.strftime('%Y-%m-%d %H:%M:%S.%f'),
                                             self.rr_delay[self.pDict[x]['idAddrList']-1]*10**-6)

        self.time_[5] = time.time_ns()  # time AFTER data format

