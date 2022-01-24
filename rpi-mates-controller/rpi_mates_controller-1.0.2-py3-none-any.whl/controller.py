"""
A module used for communicating with BBM Devices, over serial port.

Module contains various methods for sending and retrieving data
relating to display widgets, their states and parameters and
the health of the controller
"""
import io
import time
import typing
import gpiozero
from mates.controller import MatesController
from mates.data import *
from mates.constants import *
from mates.commands import MatesCommand

class RPiMatesController(MatesController):
    """
    A class representing the Raspberry Pi Python Mates Serial controller.

    Attributes
    ----------
    reset_output_device: gpiozero.DigitalOutputDevice
        - driver of reset pin for Mates device

    mates_reset_pin_index: int
        - pin number used to drive a hard reset.
    """    

    def __init__(self, portName: str, resetPinIndex: typing.Union[int, str]=4, resetActiveHigh: bool=False, debugStream: io.TextIOWrapper=None, debugFileLength: int=50):
        """
        Constructs all the necessary attributes associated with an instance
        of a Mates Controller Object.

        Args:

            portName: str
                - the name of the port to be opened. Example: /dev/ttyUSB0 for linux.

            resetPinIndex: int, string
                - index of pin connected to reset pin of Mates device.

            resetActiveHigh: bool
                - whether the reset pin is driven from logic low, to logic high to
                reset the device.

            debugStream: io.TextIOWrapper
                - Text file object to write debugging code to, supply of none
                will result in no debugging. Examples include sys.stdout, open('log.txt', 'r+')

            debugFileLength: int
                - Determines the extent of debug history kept with respect to lines in a file,
                given a circular log. O indicates full history kept with no circular logging.
                Users must be careful here to manage storage space effectively.
        """
        self.mates_reset_pin_index = resetPinIndex
        self.reset_output_device = gpiozero.DigitalOutputDevice(
            resetPinIndex, active_high=resetActiveHigh, initial_value=False)

        super().__init__(portName, self.resetFunc, debugStream, debugFileLength)

    def resetFunc(self):
        self.reset_output_device.on()
        time.sleep(0.1)
        self.reset_output_device.off()

if __name__ == '__main__':
    print("rpi mates controller module")