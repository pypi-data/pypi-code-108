import RPi.GPIO as GPIO
import time
from time import sleep
import subprocess
from datetime import datetime
import sys
import datetime
import shlex
import urllib.request
from subprocess import check_output
from socket import timeout

GPIO.setmode(GPIO.BOARD)

# change these as desired
clockpin = 36
mosipin = 29
misopin = 32
cspin = 31

# set up the SPI interface pins
GPIO.setup(mosipin, GPIO.OUT)
GPIO.setup(misopin, GPIO.IN)
GPIO.setup(clockpin, GPIO.OUT)
GPIO.setup(cspin, GPIO.OUT)

# read SPI data from MCP3002 chip, 2 possible adc's (0 thru 1)
def readrtc(commandout):
    """
    SPI bitbang protocol to read from the real time clock 

    Parameters
    ----------
    commandout : Byte
        Registers to read the data.

    Returns
    -------
    RTCout : Bytes
        Requested data from the real time clock.

    """
    RTCout = 0
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    for i in range(8):
            if (commandout & 0x80):
                    GPIO.output(mosipin, True)
            else:
                    GPIO.output(mosipin, False)
            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(8):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            RTCout <<= 1
            if (GPIO.input(misopin)):
                    RTCout |= 0x1

    GPIO.output(cspin, True)

    return RTCout

def writertc(address, value):
    """
    SPI bitbang protocol to write to the real time clock

    Parameters
    ----------
    address : Byte
        Register address to write to.
    value : Bytes
        Values to write to the address.

    Returns
    -------
    None.

    """
    command = address*256+value
    RTCout = 0
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    for i in range(16):
            if (command & 0x8000):
                    GPIO.output(mosipin, True)
            else:
                    GPIO.output(mosipin, False)
            command <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

    GPIO.output(cspin, True)

def writeseconds(value):
    """
    Sets the seconds value to the real time clock

    Parameters
    ----------
    value : Byte
        Seconds value.

    Returns
    -------
    None.

    """
    a = (value%10)
    b = ((value//10)<<4)
    c = (a|b)
    writertc(int(0x80), c)
    #print (c)

def writeminutes(value):
    """
    Sets the minutes value to the real time clock

    Parameters
    ----------
    value : Byte
        Minutes value.

    Returns
    -------
    None.

    """
    a = (value%10)
    b = ((value//10)<<4)
    c = (a|b)
    writertc(int(0x81), c)
    #print (c)

def writehours(value):
    """
    Sets the hours value to the real time clock

    Parameters
    ----------
    value : Byte
        Hours value.

    Returns
    -------
    None.

    """
    a = (value%10)
    b = ((value//10)<<4)
    c = (a|b)
    writertc(int(0x82), c)
    #print (c)

def writedate(value):
    """
    Sets the Day number value to the real time clock

    Parameters
    ----------
    value : Byte
        Day number value.

    Returns
    -------
    None.

    """
    a = (value%10)
    b = ((value//10)<<4)
    c = (a|b)
    writertc(int(0x84), c)
    #print (c)

def writemonth(value):
    """
    Sets the Month number value to the real time clock

    Parameters
    ----------
    value : Byte
        Month value.

    Returns
    -------
    None.

    """
    a = (value%10)
    b = ((value//10)<<4)
    c = (a|b)
    writertc(int(0x85), c)
    #print (c)

def writeyear(value):
    """
    Sets the Year value to the real time clock

    Parameters
    ----------
    value : Byte
        Year value.

    Returns
    -------
    None.

    """
    a = (value%10)
    b = ((value//10)<<4)
    c = (a|b)
    writertc(int(0x86), c)
    #print (c)

def seconds():
    """
    Reads the seconds value from the real time clock

    Returns
    -------
    second : Byte
        Second's value.

    """
    a = readrtc(0x00)
    b = 128
    x = bin(a|b)
    ones = int(x[6:],2)
    tens = int(x[3:6],2)
    second = tens*10+ones
    return second

def minutes():
    """
    Reads the minutes value from the real time clock

    Returns
    -------
    minute : Byte
        Minute's value.

    """
    a = readrtc(0x01)
    b = 128
    x = bin(a|b)
    ones = int(x[6:],2)
    tens = int(x[3:6],2)
    #sleep(1)
    minute = tens*10+ones
    return minute

def hours():
    """
    Reads the hours value from the real time clock

    Returns
    -------
    hours : Byte
        Hours value.

    """
    a = readrtc(0x02)
    b = 128
    x = bin(a|b)
    ones = int(x[6:],2)
    tens = int(x[4:6],2)
    #sleep(1)
    hours = tens*10+ones
    return hours

def day():
    """
    Reads the day number of the week value from the real time clock

    Returns
    -------
    day : Byte
        day number of the week value.

    """
    a = readrtc(0x03)
    b = 128
    x = bin(a|b)
    day = int(x[7:],2)
    return day

def date():
    """
    Reads the days value from the real time clock

    Returns
    -------
    date : Byte
        Day's value.

    """
    a = readrtc(0x04)
    b = 128
    x = bin(a|b)
    ones = int(x[6:],2)
    tens = int(x[4:6],2)
    #sleep(1)
    date = tens*10+ones
    return date

def month():
    """
    Reads the month value from the real time clock

    Returns
    -------
    month : Byte
        Months value.

    """
    a = readrtc(0x05)
    b = 128
    x = bin(a|b)
    ones = int(x[6:],2)
    tens = int(x[5],2)
    #sleep(1)
    month = tens*10+ones
    return month

def year():
    """
    Reads the year value from the real time clock

    Returns
    -------
    year : Byte
        Year value.

    """
    a = readrtc(0x06)
    b = 256
    x = bin(a|b)
    ones = int(x[7:],2)
    tens = int(x[3:7],2)
    #sleep(1)
    year = tens*10+ones
    return year
# Note that bitbanging SPI is incredibly slow on the Pi as its not
# a RTOS - reading the ADC takes about 30 ms (~30 samples per second)
# which is awful for a microcontroller but better-than-nothing for Linux

def SET_TIME(time_str):
    """
    Sets the time of the raspberry pis system clock

    Parameters
    ----------
    time_str : string
        strign with time and date

    Returns
    -------
    None.

    """
    x = subprocess.call(shlex.split("sudo timedatectl set-ntp false"))
    sleep(1)
    y = subprocess.call(shlex.split("sudo timedatectl set-time '%s'"%time_str))
    sleep(1)
    z = subprocess.call(shlex.split("sudo hwclock -w"))
    #print (x,y,z)

def Reset_Network_Time():
    """
    Resets the network time of raspberry pi 

    Returns
    -------
    None.

    """
    x = subprocess.call(shlex.split("sudo /etc/init.d/ntp stop"))
    sleep(5)
    y = subprocess.call(shlex.split("sudo ntpd -q -g"))
    sleep(5)
    z = subprocess.call(shlex.split("sudo /etc/init.d/ntp start"))
    print (x,y,z)

def Check_Connection():
    """
    Checks weather there is a internete connection for the raspberry pi
    if connected: syncs the raspberry pis clock with the network time
    if not connected: syncs the raspberry pi clock with the time from real time clock

    Returns
    -------
    None.

    """
        
    ip = check_output(['hostname', '-I'])
    #print (ip)
    
    try:
            urllib.request.urlopen("http://www.google.com")
            status = "Connected"
    except:
            status = "Not connected"

    print (status)

    if status == "Connected":
        x = subprocess.call(shlex.split("sudo timedatectl set-ntp true"))
        #print ("reading time for ntp server")
        time = str(datetime.datetime.now())
        var1 = time.find(" ")
        Date = time[:var1]
        Time = time[var1+1:var1+9]
        
        Year = int(Date[2:4])
        writeyear(Year)
        Month = int(Date[5:7])
        writemonth(Month)
        Day = int(Date[8:10])
        writedate(Day)
        Hour = int(Time[:2])
        writehours(Hour)
        Minute = int(Time[3:5])
        writeminutes(Minute)
        Second = int(Time[6:8])
        writeseconds(Second)
        Total = str(Day)+'-'+str(Month)+'-'+str(Year)+' '+str(Hour)+':'+str(Minute)+':'+str(Second)
        #print (Total)
            
    else:

        #print ("read time from the real time clock and set the raspberry pi hardware clock")
        Century = '20'
        Year = str(year())
        Month = str(month())
        Day = str(date())
        Hour = str(hours())
        Minute = str(minutes())
        Second = str(seconds())
        #print (Second)
        total = Century+Year+'-'+Month+'-'+Day+' '+Hour+':'+Minute+':'+Second
        print (total)
        SET_TIME(total)

def NTPservertoRTC():
    """
    Syncs the NTP server time to real time clock of raspberry pi

    Returns
    -------
    status : string

    """
    ip = check_output(['hostname', '-I'])
    #print (ip)
    
    try:
            #print ("yes")
            urllib.request.urlopen("http://www.google.com")
            status = "Connected"
    except:
            status = "Not connected"

    #print (status)

    if status == "Connected":
        x = subprocess.call(shlex.split("sudo timedatectl set-ntp true"))
        #print ("reading time for ntp server")
        sleep(15)
        time = str(datetime.datetime.now())
        var1 = time.find(" ")
        Date = time[:var1]
        Time = time[var1+1:var1+9]
        
        Year = int(Date[2:4])
        writeyear(Year)
        Month = int(Date[5:7])
        writemonth(Month)
        Day = int(Date[8:10])
        writedate(Day)
        Hour = int(Time[:2])
        writehours(Hour)
        Minute = int(Time[3:5])
        writeminutes(Minute)
        Second = int(Time[6:8])
        writeseconds(Second)
        Total = str(Day)+'-'+str(Month)+'-'+str(Year)+' '+str(Hour)+':'+str(Minute)+':'+str(Second)

    return status

def RTCtoSystemClock():
    """
    Programs the raspberry pi system clock with the time from RTC

    Returns
    -------
    None.

    """
    Century = '20'
    Year = str(year())
    Month = str(month())
    Day = str(date())
    Hour = str(hours())
    Minute = str(minutes())
    Second = str(seconds())
    #print (Second)
    total = Century+Year+'-'+Month+'-'+Day+' '+Hour+':'+Minute+':'+Second
    print (total)
    SET_TIME(total)
                
def RTCTime():
    """
    Reads the time and date from real time clock

    Returns
    -------
    total : TYPE
        DESCRIPTION.

    """
    Century = '20'
    Year = str(year())
    Month = str(month())
    Day = str(date())
    Hour = str(hours())
    Minute = str(minutes())
    Second = str(seconds())
    #print (Second)
    total = Month+'/'+Day+'/'+Year+' '+Hour+':'+Minute+':'+Second
    return total
