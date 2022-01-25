'''
mmis is a package to control the Modular Microscope Instrument
'''

import mmis.Functions           # SPI communication protocol low level functions to talk to the PIC controller
#import mmis.DebugFunctions      # Similar to the Functions library except it is tweaked a bit to use it while debugging
import mmis.RealTimeClock       # SPI Communication bitbang protocol low level functions to talk to the RTC sensor 
import mmis.Clock               # GUI for updating the system clock settings 
import mmis.Softwareupdate      # GUI for software updates to do it through a pendrive or online

import mmis.SampleHeater        # Graphical elements and controls of the sample heater module
import mmis.DualHeater          # Graphical elements and controls of the dual heater module
import mmis.LiqN2Control        # Graphical elements and controls of the LiqN2Control module
import mmis.CryoHeater          # Graphical elements and controls of the Cryo heater module
import mmis.GUI                 # Graphical elements to host all the modules - Top Level
