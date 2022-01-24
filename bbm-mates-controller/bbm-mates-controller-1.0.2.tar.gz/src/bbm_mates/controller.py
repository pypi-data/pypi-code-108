"""
A module used for communicating with BBM Devices, over serial port.

Module contains various methods for sending and retrieving data
relating to display widgets, their states and parameters and
the health of the controller
"""
import io
import time
from mates.controller import MatesController
from mates.data import *
from mates.constants import *
from mates.commands import MatesCommand

class BreadboardMatesController(MatesController):
    """
    A class representing the BBM Python Mates Serial controller.
    """    

    def __init__(self, portName: str, debugStream: io.TextIOWrapper=None, debugFileLength: int=50):
        """
        Constructs all the necessary attributes associated with an instance
        of a Mates Controller Object.

        Args:

            portName: str
                - the name of the port to be opened. Example: /dev/ttyUSB0 for linux.

            debugStream: io.TextIOWrapper
                - Text file object to write debugging code to, supply of none
                will result in no debugging. Examples include sys.stdout, open('log.txt', 'r+')

            debugFileLength: int
                - Determines the extent of debug history kept with respect to lines in a file,
                given a circular log. O indicates full history kept with no circular logging.
                Users must be careful here to manage storage space effectively.
        """
        super().__init__(portName, self.resetFunc, debugStream, debugFileLength)

    def resetFunc(self):
        self.serial_port.dtr = True
        time.sleep(0.1)
        self.serial_port.dtr = False

if __name__ == '__main__':
    print("bbm mates controller module")