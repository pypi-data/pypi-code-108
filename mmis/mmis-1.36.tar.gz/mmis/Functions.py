
import struct
import spidev 
import RPi.GPIO as GPIO
import time
import warnings
warnings.filterwarnings("ignore") # Ignores all the warnings

spi = spidev.SpiDev()       
spi.open(0,0)             # (bus, device)
spi.max_speed_hz = 300000 # spi bus frequency


class StrtoHexList(list):
    def __repr__(self):
        """
	    Converts the String number for e.g. '234.5' to list of hexadecimals

	    Returns
	    -------
	    list : hex list 
	        list of hexadecimals.
	    
        """
        return '['+','.join("0x%X"%x if type(x) is int else repr(x) for x in self)+']'

class bytestofloat:
    def __init__(self, byte):
        """
        Converts four bytes to floating point number

        Parameters
        ----------
        byte : list
            The parameter is a list containing 4 bytes.

        Returns
        -------
        self.Float : Float point number
            The parameter is not returned but stored as a local variable self.Float

        """
        List = byte
        List.reverse()
        Join_Chars = ''.join(chr(i) for i in List)
        #print (Join_Chars)
        self.Float = struct.unpack(">f", bytes(Join_Chars, 'latin-1'))

class SETTransactions:
				   
    def __init__(self, Register, Data, ChipSelect, Interrupt):
        """
        Set the parameters to the modules PIC microcontroller

        Parameters
        ----------
        Register : Hexadecimal
            Address of the register.
        Data : list
            list of hexadecimals.
        ChipSelect : uint
            GPIO pin number of Chipselect.
        Interrupt : uint
            GPIO pin number of Interrupt.

        Returns
        -------
        None.

        """
        to_send = StrtoHexList(bytearray(Data, 'ascii'))
        #print (to_send)
        GPIO.output(ChipSelect, 0)
        Dummy1 = spi.xfer2([Register])
        Dummy2 = spi.xfer2(to_send)
        Dummy3 = spi.xfer2([0X2A])
        GPIO.output(ChipSelect, 1)
        self.Received = []
        time.sleep(0.005)
        while GPIO.input(Interrupt):
                GPIO.output(ChipSelect, 0)
                x = spi.readbytes(1)
                GPIO.output(ChipSelect, 1)
                self.Received.append(x[0])
                time.sleep(0.00002)         # Sleep functionality used

class GETTransactions:
    
    
    def __init__(self, Register, ChipSelect, Interrupt):
        """
        Get all the parameters from the modules PIC microcontroller

        Parameters
        ----------
        Register : Hexadecimal
            Address of the register.
        ChipSelect : uint8
            GPIO pin number of Chipselect.
        Interrupt : uint8
            GPIO pin number of Interrupt.

        Returns
        -------
        The parameters are not returned but stored as local variables. Depending on what is requested, 
        accordingly the following variables are assigned with results
        
        self.Float : 4 bytes
            The requested data is a floating point number
        self.Float : 3 bytes
        self.Character: 1 byte
            A character is received
        self.String : >5 bytes
            Strings of text are requested (for e.g. name of the module)
        self.Version : 5 bytes
            Version number of the software is requested

        """
        GPIO.output(ChipSelect, 0)
        Dummy4 = (spi.xfer2([Register]))
        Dummy5 = (spi.xfer2([0X2A]))
        if Dummy4[0] > 127:
                self.Alarm = 1
        else:
                self.Alarm = 0
        
        GPIO.output(ChipSelect, 1)
        self.Received = []
        GPIO.output(ChipSelect, 0)
        runs = 0
        situation = True
        while situation:
            runs = runs+1
            time.sleep(0.005)
            if (GPIO.input(Interrupt) or (runs == 10)):
                situation = False
                
        while GPIO.input(Interrupt):
                x = spi.readbytes(1)
                self.Received.append(x[0])
                time.sleep(0.00002)         
        GPIO.output(ChipSelect, 1)    
        if len(self.Received)==4:
                self.Float = bytestofloat(self.Received)
    
        if len(self.Received)==3: # for Dual Heater
                #print (self.Received)
                self.Float = self.Received[2]+self.Received[1]*255+self.Received[0]*255*255

        elif len(self.Received)==1:
                #print ("1 byte received")
                self.Character = chr(self.Received[0])

        elif len(self.Received) > 5:
                #print ("more bytes received")
                self.String = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])
                #spi.close()

        elif len(self.Received)==5:
                #print ("5 byte received")
                self.Version = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])
            

                        
                        
