# -*- coding: utf-8 -*-
#################################################
########   Device DRIVERS #######################
#################################################
#Studio Tecnico Pugliautomazione - Monopoli (BA)
# All rights reserved
# Copyright (c)
# v2.0 2020-07-22
# v2.1 2020-09-23
# v2.2 2020-09-30
# v2.3 2020-10-30
# v2.4 2020-11-01 sh1
# v2.5 2021-01-10 p32M6
# v2.6 2021-02-14 lv

import numpy as np
import logging
import time
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient as ModbusTCP
from pymodbus.client.sync import ModbusSerialClient as ModbusRTU
import threading

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


from susee.see_comm import  c_comm_devices


class c_driver_p32M7(c_comm_devices):


    def __init__(self, idDevices_pack, *args, **kwargs):
        super().__init__(idDevices_pack)

        # Set Address list
        self.addrList = {}
        self.addrList[1] = (1, 83)
        self.addrList[2] = (801, 837)


        #pDict
        self.paramDict()
    def paramDict(self):
        # Elaborazione registri - valori

        self.pDict = {}
        numPar = -1
        addrList=  self.addrList
        # 1  - 104 Tensione  L1L2


        # Calcolo parametri
        # 1  - 104 Tensione  L1L2
        # 2  - 107 Corrente L1
        # 3 - 108 Corrente L2
        # 4 - 109 Corrente L3
        # 5  - 113 Potenza L1
        # 6  - 114 Potenza L2
        # 7  - 115 Potenza L3
        # 8 132    Potenza Apparente totale
        # 9 133    Potenza attiva totale
        # 10 134    Potenza reattiva totale
        # 11 135    Fattore di potenza
        # 12 222    Energia attiva importata
        # 13 226    Energia reattiva  importata

        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 7 - (addrList[1][0] - 1),
            'idParam': 104,
            'k': 1,
            'offset':0,
            'words': 2,
            'type': 0,
        }

        # 2  - 107 Corrente L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 13 - (addrList[1][0] - 1),
            'idParam': 107,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 3 - 108 Corrente L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 15 - (addrList[1][0] - 1),
            'idParam': 108,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 4 - 109 Corrente L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 17 - (addrList[1][0] - 1),
            'idParam': 109,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 5  - 113 Potenza L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 25 - (addrList[1][0] - 1),
            'idParam': 113,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 6  - 114 Potenza L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 27 - (addrList[1][0] - 1),
            'idParam': 114,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 7  - 115 Potenza L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 29 - (addrList[1][0] - 1),
            'idParam': 115,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 8 132    Potenza Apparente totale
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 63 - (addrList[1][0] - 1),
            'idParam': 132,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }


        # 9 133    Potenza attiva totale
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 65 - (addrList[1][0] - 1),
            'idParam': 133,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }


        # 10 134    Potenza reattiva totale
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 67 - (addrList[1][0] - 1),
            'idParam': 134,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 11 135    Fattore di potenza
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 69 - (addrList[1][0] - 1),
            'idParam': 135,
            'k': 1,
            'offset': 0,
            'words': 2,
            'type': 0,
        }

        # 12 222    Energia attiva importata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 801 - (addrList[2][0] - 1),
            'idParam': 222,
            'k': 1,
            'offset': 0,
            'words': 4,
            'type': 0,
        }


        # 13 226    Energia reattiva  importata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 817 - (addrList[2][0] - 1),
            'idParam': 226,
            'k': 1,
            'offset': 0,
            'words': 4,
            'type': 0,
        }


class c_driver_sh2(c_comm_devices):
    # Driver for Schneider
    # v2.0 2020-09-30
    # v3.1 2021-01-26

    def __init__(self, idDevices_pack, *args, **kwargs):
        super().__init__(idDevices_pack)

        self.pDict = {}


        # Set Address list
        self.addrList = {}
        self.addrList[1] = (3000-1, 3036-1)
        self.addrList[2] = (3060-1, 3096-1)
        self.addrList[3] = (3204-1, 3224-1)
        self.paramDict()

    def paramDict(self):
        # Elaborazione registri - valori
        pDict = {}
        numPar = -1
        addrList = self.addrList


        # Calcolo parametri
        # 1  - 104 Tensione  L1L2
        numPar += 1
        shift_= 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 3020 - (addrList[1][0]+shift_),
            'idParam': 104,
            'k': 1.0,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 6,
        }

        # 2  - 105 Tensione  L2L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 3022 - (addrList[1][0]+shift_),
            'idParam': 105,
            'k': 1.0,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 6,
        }

        # 3  - 106 Tensione  L3L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 3024 - (addrList[1][0]+shift_),
            'idParam': 106,
            'k': 1.0,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 6,
        }

        # 4  - 107 Corrente L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 3000 - (addrList[1][0]+shift_),
            'idParam': 107,
            'k': 1.0,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 6,
        }

        # 5 - 108 Corrente L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 3002 - (addrList[1][0]+shift_),
            'idParam': 108,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        # 6 - 109 Corrente L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 3004 - (addrList[1][0]+shift_),
            'idParam': 109,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        # 7  - 135 fdp tot
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 3084 - (addrList[2][0]+shift_),
            'idParam': 135,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        # 8  - 119 fdp L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 3078 - (addrList[2][0]+shift_),
            'idParam': 119,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        # 9  - 120 fdp L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 3080 - (addrList[2][0]+shift_),
            'idParam': 120,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        #  10  - 121 fdp L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 3082 - (addrList[2][0]+shift_),
            'idParam': 121,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        #  11  - 133 P Attiva Tot
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 3060 - (addrList[2][0]+shift_),
            'idParam': 133,
            'k': 1000,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        # 12  - 134 P Reattiva Tot
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 3068 - (addrList[2][0]+shift_),
            'idParam': 134,
            'k': 1000,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 6,
        }

        # 13  - 222 Energia Attiva importata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 3,
            'addr': 3204 - (addrList[3][0]+shift_),
            'idParam': 222,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 4,
            'type': 3,
        }

        # 14  - 226 Energia Reattiva importata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 3,
            'addr': 3220 - (addrList[3][0]+shift_),
            'idParam': 226,
            'k': 1.0,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 4,
            'type': 3,
        }
class c_driver_duR(c_comm_devices):
    # Ducati
    # v1.0 2021-01-10

    def __init__(self, idDevices_pack, *args, **kwargs):
        super().__init__(idDevices_pack)

        self.pDict = {}


        # Set Address list
        self.addrList = {}
        self.addrList[1] = (1, 41)
        self.addrList[2] = (79, 121)
        self.paramDict()

    def paramDict(self):
        # Elaborazione registri - valori
        pDict = {}
        numPar = -1
        addrList = self.addrList


        # Calcolo parametri
        # 1  - 104 Tensione  L1L2
        numPar += 1
        shift_= 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 6 - (addrList[1][0]+shift_),
            'idParam': 104,
            'k': 1.0,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        # 2  - 105 Tensione  L2L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 8 - (addrList[1][0]+shift_),
            'idParam': 105,
            'k': 1.0,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        # 3  - 106 Tensione  L3L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 10 - (addrList[1][0]+shift_),
            'idParam': 106,
            'k': 1.0,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }
class c_driver_duT(c_comm_devices):
    # v1.0 2021-01-10


    def __init__(self, idDevices_pack, *args, **kwargs):
        super().__init__(idDevices_pack)

        self.pDict = {}


        # Set Address list
        self.addrList = {}
        self.addrList[1] = (0x1008, 0x1042)
        self.addrList[2] = (0x1046, 0x1048)
        self.paramDict()

    def paramDict(self):
        # Elaborazione registri - valori
        pDict = {}
        numPar = -1
        addrList = self.addrList


        # Calcolo parametri
        # 1  - 104 Tensione  L1L2
        numPar += 1
        shift_= 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 0x1008  - (addrList[1][0]+shift_),
            'idParam': 104,
            'k': 0.001,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        # 2  - 105 Tensione  L2L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 0x100A  - (addrList[1][0]+shift_),
            'idParam': 105,
            'k': 0.001,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        # 3  - 106 Tensione  L3L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 0x1010 - (addrList[1][0]+shift_),
            'idParam': 106,
            'k': 0.001,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }


class c_driver_lv(c_comm_devices):
    # LOvato
    # v1.0 2021-02-14

    def __init__(self, idDevices_pack, *args, **kwargs):
        super().__init__(idDevices_pack)

        self.pDict = {}


        # Set Address list
        self.addrList = {}
        self.addrList[1] = (0x1, 0x41)
        self.addrList[2] = (0x1A1F, 0x1A31) #6687 6705
        self.paramDict()

    def paramDict(self):
        # Elaborazione registri - valori
        '''
        Parametri                           Addr    k       u.m.
        IDPAR	Description	u.m.	DeviceType	Addr	Word/bit	Type
        107	Corrente L1	A	LV3	7	2	UlongSwap
        108	Corrente L2	A	LV3	9	2	UlongSwap
        109	Corrente L3	A	LV3	11	2	UlongSwap
        104	Tensione UL1-L2	V	LV3	13	2	UlongSwap
        105	Tensione UL2-L3	V	LV3	15	2	UlongSwap
        106	Tensione UL3-L1	V	LV3	17	2	UlongSwap
        113	Potenza attiva L1	W	LV3	19	2	LongSwap
        114	Potenza attiva L2	W	LV3	21	2	LongSwap
        115	Potenza attiva L3	W	LV3	23	2	LongSwap
        116	Potenza reattiva L1	Var	LV3	25	2	LongSwap
        117	Potenza reattiva L2	Var	LV3	27	2	LongSwap
        118	Potenza reattiva L3	Var	LV3	29	2	LongSwap
        110	Potenza apparente L1	VA	LV3	31	2	UlongSwap
        111	Potenza apparente L2	VA	LV3	33	2	UlongSwap
        112	Potenza apparente L3	VA	LV3	35	2	UlongSwap
        119	Fattore di potenza L1	na	LV3	37	2	LongSwap
        120	Fattore di potenza L2	na	LV3	39	2	LongSwap
        121	Fattore di potenza L3	na	LV3	41	2	LongSwap
        133	Potenza attiva totale	W	LV3	57	2	LongSwap
        134	Potenza reattiva totale	VAr	LV3	59	2	LongSwap
        132	Potenza apparente totale	VA	LV3	61	2	UlongSwap
        222	Energia attiva importata	Wh	LV3	6687	2	UlongSwap
        226	Energia Reattiva importata	VArh	LV3	6691	2	UlongSwap

        '''

        numPar = -1
        addrList = self.addrList

        # Calcolo parametri
        # 1  - 104 Tensione  L1L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 13  - addrList[1][0],
            'idParam': 104,
            'k': 0.01,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        # 2  - 105 Tensione  L2L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 15  - addrList[1][0],
            'idParam': 105,
            'k': 0.01,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        # 3  - 106 Tensione  L3L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 17  - addrList[1][0],
            'idParam': 106,
            'k': 0.01,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        #    - 107 Corrente L1    A
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 7 - addrList[1][0],
            'idParam': 107,
            'k': 0.0001,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        #    - 108 Corrente L2    A
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 9 - addrList[1][0],
            'idParam': 108,
            'k': 0.0001,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        #    - 109 Corrente L3    A
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 11 - addrList[1][0],
            'idParam': 109,
            'k': 0.0001,
            'offset': 0.0,
            'max'   : '',
            'min'   : '',
            'words': 2,
            'type': 1,
        }

        #    - 113 Potenza Attiva L1  W
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 19 - addrList[1][0],
            'idParam': 113,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        #    - 114 Potenza Attiva L2  W
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 21 - addrList[1][0],
            'idParam': 114,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        #    - 115 Potenza Attiva L3  W
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 23 - addrList[1][0],
            'idParam': 115,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }


        # - 116    Potenza reattiva L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 25 - addrList[1][0],
            'idParam': 116,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # - 117   Potenza reattiva L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 27 - addrList[1][0],
            'idParam': 117,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # - 118   Potenza reattiva L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 29 - addrList[1][0],
            'idParam': 118,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }


        # - 110    Potenza apparente L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 31 - addrList[1][0],
            'idParam': 110,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 1,
        }

        # - 111    Potenza apparente L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 33 - addrList[1][0],
            'idParam': 111,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 1,
        }

        # - 112    Potenza apparente L3
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 35 - addrList[1][0],
            'idParam': 112,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 1,
        }


        # - 119    Fattore di potenza L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 37 - addrList[1][0],
            'idParam': 119,
            'k': 0.0001,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # - 120    Fattore di potenza L2
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 39 - addrList[1][0],
            'idParam': 120,
            'k': 0.0001,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # - 121    Fattore di potenza L1
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 41 - addrList[1][0],
            'idParam': 121,
            'k': 0.0001,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # 1 132   Potenza Apparente totale
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 61 - addrList[1][0],
            'idParam': 132,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # 1 133    Potenza attiva totale
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 57 - addrList[1][0],
            'idParam': 133,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }
        # 2 134    Potenza reattiva totale
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 59 - addrList[1][0],
            'idParam': 134,
            'k': 0.01,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # 3 135    Fattore di potenza
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 1,
            'addr': 63 - addrList[1][0],
            'idParam': 135,
            'k': 0.0001,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 2,
        }

        # 4 222    Energia attiva importata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 6687 - addrList[2][0],
            'idParam': 222,
            'k': 10,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 1,
        }

        # 4 224    Energia attiva esportata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 6689 - addrList[2][0],
            'idParam': 224,
            'k': 10,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 1,
        }

        # 5 226    Energia reattiva  importata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 6691 - addrList[2][0],
            'idParam': 226,
            'k': 10,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 1,
        }

        # 5 228    Energia reattiva  importata
        numPar += 1
        self.pDict[numPar] = {
            'idAddrList': 2,
            'addr': 6693 - addrList[2][0],
            'idParam': 228,
            'k': 10,
            'offset': 0.0,
            'max': '',
            'min': '',
            'words': 2,
            'type': 1,
        }