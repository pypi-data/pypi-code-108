#!/usr/bin/env python3

#@brief This module provides an interface to control stepper motors.

from time import sleep

from p3lib.pconfig import ConfigManager

import pigpio # Useful URL https://abyz.me.uk/rpi/pigpio/index.html

class SMotorError(Exception):
    pass

class SMotorPinout(object):
    """@brief The raspberry PI pins connected to a stepper motor."""
    UNCONNECTED_PIN = -1            # Denotes an unconnected pin
    
    def __init__(self):
        #DRV8825 input pins
        
        #Required pins
        self.mode   = (16, 17, 18)  # The GPIO pins connected to the DRV8825 microstep mode GPIO Pins (MODE0, MODE1 & MODE2 respectively).
        self.dir    = 20            # The GPIO pin connected to the DRV8825 DIR pin.
        self.step   = 21            # The GPIO pin connected to the DRV8825 STEP pin.
        #Optional pins
        self.nSleep  = 27           # The GPIO pin connected to the DRV8825 nSLEEP pin. This needs to be connected if you wish 
                                    # to turn off the stepper motor current. This removes the hold current so that the motor
                                    # spindle can be moved manually. If not connected to a Raspberry Pi GPIO pin it should 
                                    # be connected to the 3V3 rail through a pullup resistor as the DRV8825 has an internal 
                                    # pulldown on this pin. If set to -1 then this pin is not used.
        self.nReset  = 25           # The GPIO pin connected to the DRV8825 nRESET pin. If not connected to a Raspberry Pi GPIO 
                                    # pin it should be connected to the 3V3 rail through a pullup resistor as the DRV8825 has 
                                    # an internal pulldown on this pin. If set to -1 then this pin is not used.
        self.nEnable = 25           # The GPIO pin connected to the DRV8825 nRESET pin. This can be left unconnected as the 
                                    # DRV8825 has an internal pulldown on this pin. If set to -1 then this pin 
                                    # is not used.
        
        # DRV8825 output pins
        self.nFault  = 19           # The GPIO pin connected to the DRV8825 nFAULT pin. This does low when a fault condition 
                                    # (over temp, over current) occurs. If set to -1 then this pin is not used.                                
        
        
class SMotor(object):
    """@brief Control a Bi polar stepper motor connected to a RPi with the 
              'RPi Bi Polar Stepper Hat' connected."""
    # The keys to the MODES dict
    MODE_1              = "1"                   # Full step
    MODE_1_2            = "1/2"                 # 1/2 step
    MODE_1_4            = "1/4"                 # 1/4 step
    MODE_1_8            = "1/8"                 # 1/8 step
    MODE_1_16           = "1/16"                # 1/16 step
    MODE_1_32           = "1/32"                # 1/32 step
    VALID_STEP_MODES    = (MODE_1, MODE_1_2, MODE_1_4, MODE_1_8, MODE_1_16, MODE_1_32)
    CW                  = 0                     # Clockwise Rotation state for the DRV8825 DIR pin
    CCW                 = 1                     # Counterclockwise Rotation for the DRV8825 DIR pin
    VALID_DIRS          = (CW, CCW)
    TRUE_FALSE_STATES   = (True, False)
    
    #The states of the mode pins for each step mode
    MODES = {MODE_1:    (0, 0, 0),
             MODE_1_2:  (1, 0, 0),
             MODE_1_4:  (0, 1, 0),
             MODE_1_8:  (1, 1, 0),
             MODE_1_16: (0, 0, 1),
             MODE_1_32: (1, 0, 1)}

    CURRENT_ANGLE_KEY = "CURRENT_ANGLE_KEY"
    
    DefaultPosConfig = {
        CURRENT_ANGLE_KEY:   0.0,
    }

    MAX_WAVE_STEP_COUNT = 65535
    MAX_CHAIN_COUNT = 600
    ELEMENTS_IN_CHAIN = 7       # The number of elements in a single chain
    
    def __init__(self, pinout = SMotorPinout() ):
        """@brief Constructor."""
        self._pinout = pinout
        self._dir                   = SMotor.CW       # Default to clockwise rotation
        self._fullStepsPerRev       = 200             # Default to 1.8° step size
        self._mode                  = SMotor.MODE_1_2 # Default to 1/2 step mode
        self._revSec                = 1               # Default to 1 revolution per second
        self._accelerationFactor    = 1.0             # Default = 1.0 = Move straight to the required revolutions per second.
        self._accelerationBinCount  = 10              # The number of acceleration speed changes during the acceleration phase.
        self._decelerationFactor    = 1.0             # Default = 1.0 = Stop immediately with no deceleration.
        self._decelerationBinCount  = 10              # The number of acceleration speed changes during the acceleration phase.
        self._holdEnabled           = True
        self._uio                   = None            # If set then debug messages are displayed using this UIO instance.
        self._pi                    = pigpio.pi()     # Connect to the pigpio daemon which must be running.
        self._waitPollSecs          = 0.1             # The poll period when waiting for a move to complete.
        self._initPins()     
        self._persistentPosCfg = ConfigManager(None, "SMotor_step_pin_{}.cfg".format(pinout.step), SMotor.DefaultPosConfig)
        self._debug("CFG FILE = {}".format( self._persistentPosCfg._getConfigFile() ) )
        self._persistentPosCfg.load()

    def setUIO(self, uio):
        """@brief Associate a UIO instance with this object so that debug messages can be displayed.
           @param uio A UIO instance."""
        self._uio = uio

    def _debug(self, msg):
        if self._uio:
            self._uio.debug(msg)
            
    def _initPins(self):
        """@brief Configure the pins that connect between the RPi interface and the DRV8825."""
        # Set pin directions etc
        self._pi.set_mode(self._pinout.nEnable, pigpio.OUTPUT)
        self._pi.set_mode(self._pinout.nReset, pigpio.OUTPUT)
        self._pi.set_mode(self._pinout.nSleep, pigpio.OUTPUT)
        self._pi.set_mode(self._pinout.dir, pigpio.OUTPUT)
        self._pi.set_mode(self._pinout.step, pigpio.OUTPUT)
        self._pi.set_mode(self._pinout.nFault, pigpio.INPUT)
        self._pi.set_pull_up_down(self._pinout.nFault, pigpio.PUD_UP)
        #Set the state of the mode pins
        self.setStepMode(self._mode)
    
    def setStepsPerRev(self, fullStepsPerRev):
        """@brief Set the steps per revolution of the connected stepper motor (default=200).
                  The spec for the connected stepper motor will define this usually in degrees per step.
           @param fullStepsPerRev The number of steps per revolution of the stepper motor."""
        self._fullStepsPerRev = fullStepsPerRev
        
    def setStepMode(self, mode):
        """@brief Set the step mode.
           @param mode The step mode. Must be MODE_1, MODE_1_2, MODE_1_4, MODe_1_8, MODE_1_16 or
                          MODE_1_32."""
        if mode not in SMotor.VALID_STEP_MODES:
            raise Exception("{} is an invalid step mode(valid = {}).".format(mode, ",".join(SMotor.VALID_STEP_MODES)))
        self._mode = mode
        # Set the mode pins to the correct state
        for i in range( len(self._pinout.mode) ):
            self._pi.write(self._pinout.mode[i], SMotor.MODES[mode][i])
        
    def setDir(self, dir):
        """@brief Set the direction of rotation
           @param dir Either SMotor.CW or SMotor.CCW for clockwise and counter clockwise."""
        if dir in SMotor.VALID_DIRS:
            self._pi.write(self._pinout.dir, dir)
            self._dir = dir
        else:
            raise SMotorError("dir invalid. Valid = {}".format( ",".join(SMotor.VALID_DIRS) ))
            
    def setRevSec(self, revSec):
        """@brief Set the speed of the motor in revolutions per second 
           @revSec The number of revolutions per second."""
        if revSec <= 0:
            raise Exception("{} revolutions per second is invalid. Must be greater than 0".format(revSec))
        self._revSec = revSec
        
    def enableHold(self, enable):
        """@brief Enable/Disable the motor hold current.
           @param enable If True the motor hold current is enabled."""
        if enable in SMotor.TRUE_FALSE_STATES:
            self._pi.write(self._pinout.nSleep, not enable)

        else:
            raise SMotorError("{} is an invalid hold state. Valid = {}".format(enable, ",".join(map(str, SMotor.TRUE_FALSE_STATES)) ))
        self._showDebugState()
        self._holdEnabled = enable
        
    def setAccelDecelFactors(self, accelerationFactor, decelerationFactor, accelerationBinCount=10, decelerationBinCount=10):
        """@brief Set the factors that determine rate at which the motor accelerates when the motor
                  starts and decelerates as the motor comes to a stop. If both factors are set to 
                  1.0 (the maximum) then the motor jumps straight to the required revolutions per 
                  second (maximum acceleration) and when the required angle is reached the 
                  motor stops immediately. This risks missing/jumping steps particularly if 
                  the motor is under load.
                  If the acceleration and deceleration factors are set to 0.5 the motor will 
                  accelerate to the required revolutions per second in half the travel time
                  or 0.5 of the required angular movement at which point it will start 
                  decelerating at the same rate before finally coming to a stop at the 
                  required number of steps.
                  If the acceleration factor + the deceleration factors is greater than 1
                  then the acceleration factor will be followed and then the deceleration 
                  factor will be used to slow the motor down. When the required angular
                  movement is reached the motor will stop.
            @param accelerationFactor The acceleration factor as detailed above.
            @param decelerationFactor The deceleration factor as detailed above.
            @param accelerationBinCount The number of bins for each speed change through the acceleration phase (assuming accelerationFactor is not set to 1.0).
            @param decelerationBinCount The number of bins for each speed change through the deceleration phase (assuming decelerationFactor is not set to 1.0).
            """
        self._accelerationFactor    = accelerationFactor
        self._decelerationFactor    = decelerationFactor
        self._accelerationBinCount  = accelerationBinCount
        self._decelerationBinCount  = decelerationBinCount

    def stop(self):
        """@brief  Stop motor moving."""
        self._pi.wave_clear()     # clear existing waves

    def stepMotor(self, stepCount, freqHz, repeat=False):
        """@brief Pulse the step pin at the required rate to move the motor the required amount.
           @param stepCount The number of steps to move.
           @param freqHz The frequency in Hz.
           @param repeat If True repeat the motor movement until stopped."""
        self.stop()

        if repeat:
            self._stopMotorUntilStopped()
            
    def runUntilStopped(self, cw=True):
        """@brief Run the motor at the required rate until stopped.
           @param cw If True rotate the motor clockwise."""
        if cw >= 0:
            self.setDir(SMotor.CW)
        else:
            self.setDir(SMotor.CCW)
        self.enableHold(False)
        
        freqHz = self._getFreqHz()
        micros = int(500000 / freqHz)
        wf = []
        wf.append(pigpio.pulse(1 << self._pinout.step, 0, micros))  # pulse on
        wf.append(pigpio.pulse(0, 1 << self._pinout.step, micros))  # pulse off
        self._pi.wave_add_generic(wf)
        wave = self._pi.wave_create()
        self._pi.wave_send_repeat(wave)
        
    def _move(self, stepCount):
        """@brief Move the motor through the required number of steps.
           @param stepCount The number of steps to move the motor."""
        if stepCount > 0:
            freqHz = self._getFreqHz()
            micros = int(500000 / freqHz)
            pulseWave = []
            pulseWave.append(pigpio.pulse(1 << self._pinout.step, 0, micros))  # pulse on
            pulseWave.append(pigpio.pulse(0, 1 << self._pinout.step, micros))  # pulse off
            self._pi.wave_add_generic(pulseWave)
            waveID = self._pi.wave_create()
            
            chainCount = stepCount/SMotor.MAX_WAVE_STEP_COUNT
            chain = []
            if chainCount <= 1.0:
                x = stepCount & 255
                y = stepCount >> 8
                chain += [255, 0, waveID, 255, 1, x, y]
            else:
                # If more than one chain is required to send all the steps then
                # send chains with the max number of steps followed by a chain to send the remaining steps (if not 0)
                stepsSent = 0
                while stepsSent < stepCount:
                    stepsLeft = stepCount - stepsSent 
                    if stepsLeft >= SMotor.MAX_WAVE_STEP_COUNT:
                        #Create a chain with the max number of steps
                        lsb = SMotor.MAX_WAVE_STEP_COUNT&0xff
                        msb = SMotor.MAX_WAVE_STEP_COUNT >> 8
                        chain += [255, 0, waveID, 255, 1, lsb, msb]
                        stepsSent = stepsSent + SMotor.MAX_WAVE_STEP_COUNT
                    else:
                        lsb = stepsLeft&0xff
                        msb = stepsLeft >> 8
                        chain += [255, 0, waveID, 255, 1, lsb, msb]
                        stepsSent = stepsSent + stepsLeft
                    
                #7 is the number of elements in each chain    
                if (len(chain)/SMotor.ELEMENTS_IN_CHAIN) > SMotor.MAX_CHAIN_COUNT:
                    raise Exception("Unable to move {} steps max = {} steps.".format(stepCount, SMotor.MAX_WAVE_STEP_COUNT*SMotor.MAX_CHAIN_COUNT))
     
            self._pi.wave_chain(chain)  # Transmit chain.
            
    def _showDebugState(self):
        """@brief Show messages to indicate the state of the interface."""
        #Don't bother to read the pin states unless we have a UIO instance to display debug info
        if self._uio:
            self._debug("self._fullStepsPerRev   = {}".format(self._fullStepsPerRev))
            self._debug("self._revSec            = {}".format(self._revSec))
            self._debug("self._mode              = {}".format(self._mode))
            if self._uio:
                for pinIndex in range(0, len(self._pinout.mode)):
                    self._debug("  PIN {}                = {}".format(self._pinout.mode[pinIndex], self._pi.read(self._pinout.mode[pinIndex])))
            self._debug("DIR PIN {}              = {}".format(self._pinout.dir, self._pi.read(self._pinout.dir)))
            self._debug("_SLEEP PIN {}           = {}".format(self._pinout.nSleep, self._pi.read(self._pinout.nSleep)))
                
    def _updatePersistentPosition(self, angleMoved):
        """@brief Update the persistent absolute position of the motor spindle.
           @param angleMoved The angle that was moved."""
        self._persistentPosCfg.load()
        configDict = self._persistentPosCfg._getDict()
        previousAngle = configDict[SMotor.CURRENT_ANGLE_KEY]
        self._persistentPosCfg.addAttr(SMotor.CURRENT_ANGLE_KEY, previousAngle + angleMoved)
        self._persistentPosCfg.store()
                
    def getAbsolutePosition(self):
        """@brief Get the absolute position of the motor spindle.
           @return The angle in degrees."""
        self._persistentPosCfg.load()
        configDict = self._persistentPosCfg._getDict()
        return configDict[SMotor.CURRENT_ANGLE_KEY]
                
    def resetRef(self):
        """@brief Update the persistent absolute position of the motor spindle.
           @param angleMoved The angle that was moved."""
        self._persistentPosCfg.load()
        self._persistentPosCfg.addAttr(SMotor.CURRENT_ANGLE_KEY, 0)
        self._persistentPosCfg.store()
        
    def _getFreqHz(self):
        """@brief Get the step freq of the motor on Hz
           @return The step frequency in Hz"""
        stepFreqHz = int( self._revSec * self._fullStepsPerRev )   
        if self._mode == SMotor.MODE_1_2:
            stepFreqHz = stepFreqHz * 2
        elif self._mode == SMotor.MODE_1_4:
            stepFreqHz = stepFreqHz * 4
        elif self._mode == SMotor.MODE_1_8:
            stepFreqHz = stepFreqHz * 8
        elif self._mode == SMotor.MODE_1_16:
            stepFreqHz = stepFreqHz * 16
        elif self._mode == SMotor.MODE_1_32:
            stepFreqHz = stepFreqHz * 32
        return stepFreqHz
         
    def move(self, angle, absolute=True, block=True):
        """@brief Move the motor through an angle.
                  The angular movement (360 = one revolution clockwise, 720 = two, etc, -360 one revolution in anti clockwise direction.
           @param angle The angle to set the motor to.
           @param absolute If True then the absolute angle is set. If False then the angle is set 
                  relative to the current position.
           @param block If True block until the motor movement is complete."""
           
        if absolute:
            self._persistentPosCfg.load()
            configDict = self._persistentPosCfg._getDict()
            previousAngle = configDict[SMotor.CURRENT_ANGLE_KEY]
            angle = angle - previousAngle

        if angle >= 0:
            self.setDir(SMotor.CW)
        else:
            self.setDir(SMotor.CCW)
        self.enableHold(False)
        
        stepCount = int( (abs(angle)/360.0) * self._fullStepsPerRev )
        stepFreqHz = self._getFreqHz()

        self._debug("angle                   = {}".format(angle))
        self._showDebugState()
        #Adjust for the micro step setting.
        if self._mode == SMotor.MODE_1_2:
            stepCount = stepCount * 2
        elif self._mode == SMotor.MODE_1_4:
            stepCount = stepCount * 4
        elif self._mode == SMotor.MODE_1_8:
            stepCount = stepCount * 8
        elif self._mode == SMotor.MODE_1_16:
            stepCount = stepCount * 16
        elif self._mode == SMotor.MODE_1_32:
            stepCount = stepCount * 32
        self._debug("stepCount               = {}".format(stepCount))
        self._debug("stepFreqHz              = {}".format(stepFreqHz))
            
        if self._accelerationFactor >= 1.0 and self._decelerationFactor >= 1.0:
            self._move(stepCount)
        else:
            raise Exception("TODO Implement acceleration and deceleration.")
        
        if block:
            self.wait()
            
        self._updatePersistentPosition(angle)            

    def isMoving(self):
        """@brief Determine if the motor is moving."""
        return self._pi.wave_tx_busy()
    
    def wait(self):
        """@brief Wait for the motor movement to complete."""
        while True:
            if not self.isMoving():
                break
            sleep(self._waitPollSecs)

        
        
        
        
        