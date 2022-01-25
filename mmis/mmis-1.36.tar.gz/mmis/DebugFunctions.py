

import struct
import spidev
import RPi.GPIO as GPIO
import time
spi = spidev.SpiDev()
spi.open(0,0)
#spi.max_speed_hz = 50000
#GPIO.setmode(GPIO.BOARD)

""" String to List of Hexa decimal conversion"""
""" call bytearray('234.5') in the list"""
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
        GPIO.output(ChipSelect, 0)
        Dummy1 = spi.xfer2([Register])
        Dummy2 = spi.xfer2(to_send)
        Dummy3 = spi.xfer2([0X2A])
        GPIO.output(ChipSelect, 1)
        self.Received = []
        while GPIO.input(Interrupt):
                GPIO.output(ChipSelect, 0)
                x = spi.readbytes(1)
                GPIO.output(ChipSelect, 1)
                self.Received.append(x[0])
                time.sleep(0.00002)         # Sleep functionality used

class GETTransactions:
    def __init__(self, Register, ChipSelect, Interrupt, wait_time):
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
        Dummy1 = spi.xfer2([Register])
        Dummy2 = spi.xfer2([0X2A])
        time.sleep(0.002)                    # Sleep functionality used
        GPIO.output(ChipSelect, 1)
        self.Received = []
        time.sleep(wait_time)
        while GPIO.input(Interrupt):
                GPIO.output(ChipSelect, 0)
                x = spi.readbytes(1)
                print (x)
                GPIO.output(ChipSelect, 1)
                self.Received.append(x[0])
                time.sleep(0.00002)         # Sleep functionality used
                
        if len(self.Received)==4:
                #print (self.Received)
                self.Float = bytestofloat(self.Received)

        elif len(self.Received)==1:
                print ("1 byte received")
                self.Character = chr(self.Received[0])

        elif len(self.Received) > 5:
                #print "String received"
                self.String = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])

        elif len(self.Received)==5:
                #print "5 byte received"
                self.Version = ''.join(chr(x) for x in self.Received[:(len(self.Received)-1)])

                

                        
                        
