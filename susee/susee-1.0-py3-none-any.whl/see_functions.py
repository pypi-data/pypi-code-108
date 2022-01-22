# -*- coding: utf-8 -*-
##############################
##### Functions  #############
##############################
#Studio Tecnico Pugliautomazione - Monopoli (BA)
# Copyright (c)
# v2.0 2020-07-22
# v2.1 2020-12-29   swap_convert()
# v2.2 2020-12-29   fixed offset
# v2.3 2021-04-23
# v2.4 2021-0515


import struct, os, pytz
from datetime import datetime
from susee.see_dict import err_code

##############################
###  Format Conversions ######
##############################
#Converte due word in un numero intero - swap on
def ulongswap_convert(hexa, hexb):
    hh = hexa * 16 ** 4 + hexb
    #print('hexa,hexb, hh, int(hh): {} {} {} {} '.format(hexa,hexb, hh, int(hh) ))
    return int(hh)
    
def longswap_convert(hexa, hexb):
    hh = hexa * 16 ** 4 + hexb
    if hh > 0x7fffffff:
        hh = hh-16**8 +1
    return int(hh)

def swap_convert(hexa):
    hh = hexa
    if hh > 0x7fff:
        hh = hh-16**4 +1
    return int(hh)

#Converte due word in float - swap on  
def float_convert(hex_a, hex_b):
    #import struct
    hh = hex_a * 16 ** 4 + hex_b
    return float('{0:.2f}'.format(struct.unpack('!f',struct.pack('>I',hh))[0]))
    
#Converte quattro word in float - swap on   
def double_convert(hex_a,hex_b,hex_c,hex_d):
    #import struct
    hex_double = hex_a * 16 ** 12 + hex_b * 16 ** 8 + hex_c * 16 ** 4 + hex_d
    return float('{0:.2f}'.format(struct.unpack('!d',struct.pack('>Q',hex_double))[0]))

#Converte quattro word in integer 4 bytes
def int_double_convert(hex_a,hex_b,hex_c,hex_d):
    #import struct
    hex_double = hex_a * 16 ** 12 + hex_b * 16 ** 8 + hex_c * 16 ** 4 + hex_d
    return int(hex_double)

#Check: numero � NaN
def isNaN(num):
    return num != num

## Drivers support functions


def build_param(pDict, # self.pDict[x],
                idDev, # self.idDevPack['idDev'],
                list_name, # self.rr[self.pDict[x]['idAddrList'] - 1],
                codeError, # self.codeError_rr[self.pDict[x]['idAddrList'] - 1],
                TimeStamp, # self.TimeStamp.strftime('%Y-%m-%d %H:%M:%S.%f'),
                Delay, #self.Delay)
                 ):

    # print('addr, idParam,list_name: {} {} {}'.format(addr, idParam,list_name))
    # v.2.9 - 2018-11-05
    # v.3.0 - 2020-06-30
    # v.3.1 - 2020-10-29
    # v.3.2 - 2020-12-03  offset
    # v.3.3 - 2021-01-21
    # v.3.4 - 2021-04-23

    # Estrae il valore del parametro dai registri e restituisce in formato 'dizionario'
    # list_name : array dei registri
    # addr        : indirizzo del valore nel registro
    # k            : fattore moltiplicativo
    # idDev        : identificativo del device
    # idParam    : identificativo del parametro
    # codeError : codice di errore in caso di mancata lettura del registro
    # numwords    : numero di words di cui � composto il valore

    # Tipi di conversione
    # numwords ==1
    #    type =0 no conversion
    #
    # numwords == 2
    #     type =0 float_converter   {-1, 0}
    #     type =1 ulongswap_convert {0 , 1}
    #     type =2 longswap_convert  {0 , 1}
    #     type =3 long_convert      {+1, 0}
    #     type =4 ulong_convert     {+1, 0}
    #     type = 5  float_converter {+1, 0}
    # numwords == 4
    #      type =0 double_convert   { -1, 0 , +1 , +2 }
    #      type =1 double_convert   {  0, +1 , +2, +3 }
    #      type =2 int_double_convert   { -1, 0 , +1 , +2 }
    #
    # return    : dizionario come da Dict_Generate

    num_type = pDict['type']
    list_name = list_name
    addr = pDict['addr']
    k = pDict['k']
    offset = pDict['offset']
    idParam = pDict['idParam']
    codeError = codeError
    numwords = pDict['words']
    TimeStamp =TimeStamp
    Delay = Delay

    value_ = 0
    try:
        len_list = len(list_name.registers)
    except:
        len_list = 0
        codeError += err_code['lenreg_zero']

    if len_list > 1:
        if numwords == 1:
            if num_type == 0:
                value_ = list_name.registers[addr] * k + offset

            if num_type == 1:
                value_ = swap_convert(list_name.registers[addr]) * k + offset

        elif numwords == 2:
            if num_type == 0:
                value_ = float_convert(list_name.registers[addr - 1],
                                       list_name.registers[addr]) * k + offset
            elif num_type == 1:
                value_ = ulongswap_convert(list_name.registers[addr],
                                           list_name.registers[addr + 1]) * k + offset
            elif num_type == 2:
                value_ = longswap_convert(list_name.registers[addr],
                                          list_name.registers[addr + 1]) * k + offset
            elif num_type == 3:
                value_ = longswap_convert(list_name.registers[addr + 1],
                                          list_name.registers[addr]) * k + offset
            elif num_type == 4:
                value_ = ulongswap_convert(list_name.registers[addr + 1],
                                           list_name.registers[addr]) * k + offset
            elif num_type == 5:
                value_ = float_convert(list_name.registers[addr + 1],
                                       list_name.registers[addr]) * k + offset
            elif num_type == 6:
                value_ = float_convert(list_name.registers[addr],
                                       list_name.registers[addr+1]) * k + offset

        elif numwords == 4:
            if num_type == 0:
                value_ = double_convert(list_name.registers[addr - 1],
                                        list_name.registers[addr],
                                        list_name.registers[addr + 1],
                                        list_name.registers[addr + 2]) * k + offset
            elif num_type == 1:
                value_ = double_convert(list_name.registers[addr],
                                        list_name.registers[addr + 1],
                                        list_name.registers[addr + 2],
                                        list_name.registers[addr + 3]) * k + offset
            elif num_type == 2:
                value_ = int_double_convert(list_name.registers[addr - 1],
                                            list_name.registers[addr],
                                            list_name.registers[addr + 1],
                                            list_name.registers[addr + 2]) * k + offset
            elif num_type == 3:
                value_ = int_double_convert(list_name.registers[addr    ],
                                        list_name.registers[addr + 1],
                                        list_name.registers[addr + 2],
                                        list_name.registers[addr + 3]) * k + offset
    else:
        value_ = 0
    if isNaN(value_):
        value_ = 0
        codeError += err_code['value_NaN']
    return Dict_Generate(idDev, idParam, value_ , codeError, TimeStamp, Delay)

def Dict_Generate(idDevice,idParam,Value,Code, TimeStamp,Delay):
        #Genera un dizionario dati
        return dict(idDevice  = str(idDevice),
                    idParam   = str(idParam),
                    Date      = TimeStamp,
                    Value     = float(Value),
                    Delay     = Delay,
                    Code      = Code
                    ) 
        
def push_log(stringa):
    #salva su file - config_log{}
    #con datetime

    filedatetime = '{:%Y%m%d}'.format(time_utc())
    filename    =  filedatetime + 'log_file.log'
    stringa     = '{:%Y-%m-%d %H:%M:%S}'.format(time_utc()) + ' - ' + stringa + '\n'
    topstring   = '---------------  susee Log file ------------------ ' + '\n'
    f=[]
    file_ok = True
    if os.path.isfile(filename):
        try:
            f=open(filename,'a')
        except os.error:# as err:
            file_ok = False
        else:
            f.write(stringa)
            f.close()
    else:
        try:
            f=open(filename,'w')
        except os.error: # as err:
            file_ok = False
            print('Impossibile creare il file:',filename)
        else:
            f.write(topstring)
            f.write(stringa)
            f.close()
            file_ok = True
    return  file_ok   

#Gestione Threads
import  threading
class MyThread(threading.Thread):
    #v2.0 2020-09-21
    def _init__(self, group, func , name, *args): #, **kwargs):
        threading.Thread.__init__(self)
        self.name = name    
        self.func = func
        self.args = args if args is not None else []
        #self.kwargs = kwargs if kwargs is not None else {}
        self._stop_event = threading.Event()
        #print('-> name: {}, func: {} ,args: {}'.format(name, func,args ))

    def run(self, *args):
        try:
            self.res = self.func(*self.args, *args)
        except:
            pass

    def getResults(self):
        try:
            return self.res
        except:
            return {}, 1, datetime.now()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


#Web Server sockets
def MyWebServer():
    print('Starting web server ....')
    import http.server
    import socketserver
    PORT = 8001
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("m597 webserver serving at port", PORT)
        httpd.serve_forever()  

def push_webfile(testo):
    #testo  multiriga
    #Moduli
    filename    = 'index.htm'
    f=[]
    file_ok = True
    stringa=[]
    
    TimeNow =str(time_utc())
    stringa.append('<html>')
    stringa.append('<body>'+'<br />')
    stringa.append('Lettura strumenti sistema di monitoraggio - '+TimeNow +' - '+'<br />')
    stringa.append('-'*150+'<br />'+'<br />')    
    for i in range(len(testo)):
        stringa.append(testo[i]+'<br />')
    
    stringa.append('<body>')
    stringa.append('<html>')


    if os.path.isfile(filename) | 1:
        try:
            f=open(filename,'w')
        except os.error: # as err:
            file_ok = False
            print('Impossibile creare il file:',filename)
        else:
            for i in range(len(stringa)):
                f.write(stringa[i])
            f.close()
            file_ok = True

    return  file_ok

#tools
def time_utc():
    UTC = pytz.utc
    dt = datetime.now(UTC)
    return dt

def time_local(tZone):
    #Time zone accordint to the timeZone
    #v1.0 2020-07-26

    IST = pytz.timezone(tZone)
    dt = datetime.now(IST)
    return dt

def utctime_to_tZone(utc_str_date, tZone):
    #v3.0 2019-01-02 - timezone
    #v3.1 2021-05-15

    tz = pytz.timezone(tZone)
    
    if  'time' in str(type(utc_str_date)):
        try:
            utc_str_date = utc_str_date.replace(tzinfo=pytz.timezone('utc')).astimezone(tz=tz).strftime('%Y-%m-%d %H:%M:%S')
            utc_str_date = datetime.strptime(str(utc_str_date).split('+')[0], '%Y-%m-%d %H:%M:%S')
            return utc_str_date
        except :
            print('nok_time utctime_to_tZone. utc_time:', utc_str_date)
            return utc_str_date

    if  'str' in str(type(utc_str_date)):
        try:
            utc_str_date = datetime.strptime(utc_str_date, '%Y-%m-%d %H:%M:%S' )
            utc_str_date = utc_str_date.replace(tzinfo=pytz.timezone('utc')).astimezone(tz=tz).strftime('%Y-%m-%d %H:%M:%S')
            return utc_str_date
        except :
            print('nok_str utctime_to_tZone. utc_time:', utc_str_date)
            return utc_str_date


def tZone_to_utctime(str_date, tZone):
    # Convert a UTC time to local time
    # v1.0 2020-04-25 - from timezone to utc
    # v2.0 2021-05-15
    # n.b.  pytz.timezone('Europe/Rome')  --> <DstTzInfo 'Europe/Rome' LMT+0:50:00 STD>
    #


    local_now = datetime.now()
    diff_local_utc = utctime_to_tZone(local_now, tZone) - local_now

    if 'time' in str(type(str_date)):
        try:
            #str_date = str_date.replace(tzinfo=pytz.timezone(tZone)).astimezone(tz=tz).strftime('%Y-%m-%d %H:%M:%S')
            #str_date = datetime.strptime(str(str_date).split('+')[0], '%Y-%m-%d %H:%M:%S')
            str_date = str_date - diff_local_utc
            return str_date.strftime( '%Y-%m-%d %H:%M:%S')
        except:
            print('[msg] nok_time utctime_to_tZone. utc_time:', str_date)
            return str_date

    if 'str' in str(type(str_date)):
        try:
            str_date = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
            #str_date = str_date.replace(tzinfo=pytz.timezone(tZone)).astimezone(tz=tz).strftime( '%Y-%m-%d %H:%M:%S')
            str_date = str_date - diff_local_utc
            return str_date.strftime( '%Y-%m-%d %H:%M:%S')
        except:
            print('> nok_str utctime_to_tZone. utc_time:', str_date)
            return str_date

def datetime_to_F123(date_):
    #Categorize a date according to F1,F2, F3 time period
    #and quaterly of hour
    #2020-04-27
    #v1.0
    #date_ = datetime()

    if 'str' in str(type(date_)):
        date_ = datetime.strptime(date_, '%Y-%m-%d %H:%M:%S')

    dateYear    =   date_.year
    dateMonth   =   date_.month
    dateDay     =   date_.day
    #0= sunday
    dateWeekDay = date_.isoweekday()
    dateHour    = date_.hour
    date_YMD =   datetime(dateYear, dateMonth, dateDay)

    x = dateYear
    noWdays =  [datetime(x,1,1)]
    noWdays += [datetime(x,1,6) ]
    noWdays += [datetime(x,4,25) ]
    noWdays += [datetime(x,5,1) ]
    noWdays += [datetime(x,6,2) ]
    noWdays += [datetime(x,8,15) ]
    noWdays += [datetime(x,11,1) ]
    noWdays += [datetime(x,12,8) ]
    noWdays += [datetime(x,12,25) ]
    noWdays += [datetime(x,12,26)]
    noWdays += [datetime(2020,4,21), datetime(2020,4,22)]
    noWdays += [datetime(2021,4,4), datetime(2021,4,25)]

    period_F123 = 'F1'

    condF2  = (dateWeekDay == 6 and dateHour in range(7,22)) or \
              (date_YMD not in noWdays) and (dateHour in [7, 19, 20, 21, 22])

    condF3 = (date_YMD in noWdays) or \
             dateWeekDay == 7 or \
             (dateHour in [23, 0, 1, 2, 3, 4, 5, 6])

    if condF2:
        period_F123 = 'F2'

    if condF3:
        period_F123 = 'F3'

    #index quaterly of hour since 1= 00.00 to 96 = 23:45
    #format
    p_ = divmod(dateHour * 60 + date_.minute, 15) #period 0..95
    pp_= divmod(p_[0],4) #periods in hours
    qHTime =  str(pp_[0])+ ':'+str('{:02d}'.format(pp_[1]*15))  #hh:mm
    qH =    p_[0] + 1   #0...14

    #Turno orario lavorativo
    #wp1 da 6 a 14
    #wp2 da 14 a 22
    #wp3 da 22 a 6

    if (dateHour in range(6,14)) :
        wPeriod_ = 1
    if (dateHour in range(14,22)):
        wPeriod_ = 2
    if (dateHour in [22,23,0,1,2,3,4,5]):
        wPeriod_ = 3

    return period_F123,  qH, qHTime, wPeriod_
