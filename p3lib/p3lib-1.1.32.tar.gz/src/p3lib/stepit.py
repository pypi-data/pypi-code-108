#!/usr/bin/env python3

import sys
import argparse

from   time import sleep

from   p3lib.uio import UIO
from   p3lib.helper import logTraceBack

from smotor import SMotor

# TODO
# Add run permanently option.
#

class StepItError(Exception):
    pass

class StepIt(object):

    def __init__(self, uio, options):
        """@brief Constructor
           @param uio A UIO instance handling user input and output (E.G stdin/stdout or a GUI)
           @param options An instance of the OptionParser command line options."""
        self._uio = uio
        self._options = options
        self._sMotor = SMotor()
        self._sMotor.setUIO(uio)

    def move(self, angle, revSec, relative):
        """@brief Move the motor by the require angle from the current position.
           @param angle The angle to move the motor in degrees.
           @param revSec The speed to move the motor in revolutions per second.
           @param relative If True move the motor to it's absolute angle. If False
                  move the motor relative to it's current position."""
        self._uio.info("Moving {:.1f}° at {:.1f} revs/sec.".format(angle, revSec))
        self._sMotor.setRevSec(revSec)
        self._sMotor.enableHold(False)
        self._sMotor.move(angle, absolute = not relative)
        absPos = self._sMotor.getAbsolutePosition()
        self._uio.info("The absolute position of the motor is now {}°".format(absPos))
        
    def setMode(self, mode):
        """@brief Set the step mode.
           @param mode The mode (1,2,4,8,16 or 32)."""
        if mode == 1:
            modeStr = SMotor.MODE_1
        elif mode == 2:
            modeStr = SMotor.MODE_1_2
        elif mode == 4:
            modeStr = SMotor.MODE_1_4
        elif mode == 8:
            modeStr = SMotor.MODE_1_8
        elif mode == 16:
            modeStr = SMotor.MODE_1_16
        elif mode == 32:
            modeStr = SMotor.MODE_1_32
        else:
            raise Exception("{} is an invalid mode.".format(mode))

        self._uio.info("Set Mode to {}.".format(modeStr))
        self._sMotor.setStepMode(modeStr)

    def on(self, enabled):
        """@param disable the motor hold current.
           @param enabled IF True the motor current is on. If False the motor current is off and the motor can be moved manually."""
        if enabled:
            enabledS="ON"
        else:
            enabledS="OFF"
            
        self._uio.info("Motor current: {}".format(enabledS))
        self._sMotor.enableHold(not enabled)
            
    def zero(self):
        """@brief Reset the reference/zero position to the current position."""
        self._sMotor.resetRef()
        self._uio.info("Set the current motor position to the zero/reference position.")

    def stop(self):
        """@brief Stop the motor if running."""
        self._sMotor.stop()
        self._uio.info("The motor is now stopped.")
        
    def runUntilStopped(self):
        """@brief Run the stepper motor until stopped."""
        self._sMotor.setRevSec(self._options.speed)
        self._sMotor.runUntilStopped()
        self._uio.info("Running the stepper motor at {:.1f} revs/sec until the  motor is stopped.".format(self._options.speed))
                
def main():
    """@brief Program entry point"""
    uio = UIO()

    try:
        parser = argparse.ArgumentParser(description="Example interface to drive a stepper motor.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug",    action='store_true', help="Enable debugging.")
        parser.add_argument("-a", "--angle",    type=float, help="Set the angle to move the motor spindle. Set a -ve angle to reverse the motor direction (anti clockwise). If the -r option is not used then the angle set is an absolute angle with reference to the zero/reference position.", default=None)
        parser.add_argument("-m", "--mode",     type=int,   help="The mode of the stepper motor. 1 = Full Step, 2 = 1/2 step, 4 = 1/4 step, 8 = 1/8 step, 16 = 1/16 step, 32 = 1/32 step (default=2).", default=2)
        parser.add_argument("-s", "--speed",    type=float, help="Set the speed of the motor in revolutions per second (default=1.0).", default=1.0)
        parser.add_argument("-o", "--on",       action='store_true', help="Turn the motor current on. The motor will hold it's position and can be moved.")
        parser.add_argument("-f", "--off",      action='store_true', help="Turn the motor current off. The motor will not draw power and can be manually moved.")
        parser.add_argument("-r", "--relative", action='store_true', help="Turn relative to the current position. By default the absolute position of the motor spindle is set.")
        parser.add_argument("-z", "--zero",     action='store_true', help="Set the rzero/reference position of the motor to it's current position.")
        parser.add_argument("-p", "--stop",     action='store_true', help="Stop the motor if it is running. If this option is used then the absolute position of the motor is lost.")
        parser.add_argument("-n", "--non_stop", action='store_true', help="Run the motor non stop. If this option is used then the absolute position of the motor is lost.")
        
        options = parser.parse_args()

        uio.enableDebug(options.debug)
        stepIt = StepIt(uio, options)
        
        stepIt.setMode(options.mode)
            
        if options.stop:
            stepIt.stop()
            return
            
        if options.on:
            stepIt.on(True)
            
        elif options.off:
            stepIt.on(False)
            
        if options.zero:
            stepIt.zero()
                            
        if options.angle is not None:
            stepIt.move(options.angle, options.speed, options.relative)

        elif options.non_stop:
            stepIt.runUntilStopped()

    #If the program throws a system exit exception
    except SystemExit:
        pass
    #Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logTraceBack(uio)
        raise
        if options.debug:
            raise
        else:
            uio.error(str(ex))

if __name__== '__main__':
    main()
