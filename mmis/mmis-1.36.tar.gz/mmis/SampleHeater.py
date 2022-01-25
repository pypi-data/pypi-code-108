import wx
from pubsub import pub
import os
import time
import spidev
import matplotlib
matplotlib.use('wxAgg')
import matplotlib.dates as md
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import pandas as pd
import numpy as np
from wx.lib.masked import NumCtrl
import pylab
import math
import RPi.GPIO as GPIO
import mmis.Functions
import mmis.DebugFunctions
from datetime import datetime
import memcache
import matplotlib.pyplot as plt
import distro

class Settings(wx.Panel):
    
    def __init__(self, parent, Module, pubsub1, pubsub2):
        """
        Initializes all the settings graphical elements and parameters of Sample heater module 

        Parameters
        ----------
        parent : notebook element (wx.nb)
            notebook element from wx library GUI.
        Module : [uint8, uint8]
            list contains chip select gpio and interrupt gpio.
        pubsub1 : string
            A, B and R0 values of sample heater are communicated to the Control module over this publicataion/subscription.
        pubsub2 : string
            Alarm details from this settings modules are communicated to the main GUI over this publicataion/subscription.

        Returns
        -------
        None.

        """

        wx.Panel.__init__(self, parent = parent)
        self.chipselect = Module[0]
        self.interruptpin = Module[1]
        self.mc = memcache.Client([('127.0.0.1', 11211)])        
        
        self.R0 = []
        self.paused = True
        self.pubsubname = pubsub1
        self.pubsubalarm = pubsub2

        """ Creating a Timer """
         
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 

        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font3 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
                
        self.lblname1 = wx.StaticText(self, label = "A:", pos = (40,30))
        units1 = wx.StaticText(self, label = "(*10\u207b\u00b3))", pos = (150,10))
        units1.SetFont(self.font3)
        self.SET_A = wx.SpinCtrlDouble(self, size=(145,-1), min =0, max = 800, inc = 0.01, value='2.2', pos = (70,25), style=wx.SP_ARROW_KEYS)
        self.SET_A.SetDigits(3)
        self.SET_A.SetBackgroundColour('white')

        self.lblname7 = wx.StaticText(self, label = "B :", pos = (225,30))
        units2 = wx.StaticText(self, label = "(*10\u207b\u2077))", pos = (335,10))
        units2.SetFont(self.font3)
        self.SET_B = wx.SpinCtrlDouble(self, size=(155,-1), min =-300, max = 800, inc = 0.01, value='0.0', pos = (255,25), style=wx.SP_ARROW_KEYS)
        self.SET_B.SetDigits(3)
        self.SET_B.SetBackgroundColour('white')
        
        self.lblname8 = wx.StaticText(self, label = "R\u2080 :", pos = (40,85))
        #self.SET_R0 = wx.TextCtrl(self, size=(140,-1), pos = (70,80), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
        self.SET_R0 = wx.SpinCtrlDouble(self, size=(150,-1), min = 0, max = 500, inc = 0.01, value='0.0', pos = (70,80), style=wx.SP_ARROW_KEYS)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.On_R0_Changed, self.SET_R0)
        self.SET_R0.SetBackgroundColour('light grey')

        self.lblname10 = wx.StaticText(self, label = "R\u209c = R\u2080(1+AT+BT\u00b2)", pos = (640,185))

        self.lblname2 = wx.StaticText(self, label = "T\u2080(C):", pos = (425,30))
        self.SET_Tamb = wx.SpinCtrlDouble(self, size=(155,-1), min =-300, max = 800, inc = 0.1, value='20.00', pos = (465,25))
        self.SET_Tamb.SetDigits(3)
        self.SET_Tamb.SetBackgroundColour('white')
        
        self.button1 = wx.Button(self, label="Start Calibration", pos=(640, 20), size = (140,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_CALIBRATE_R0, self.button1)
        self.button1.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button)
        self.button1.SetForegroundColour('black')
        
        self.lblname3 = wx.StaticText(self, label = "T-Max(C):", pos = (40,140))
        self.SET_Tmax = wx.SpinCtrlDouble(self, size=(160,40), min = 0, max = 800, inc = 0.1, value='800.0', pos = (200,130))
        self.SET_Tmax.SetDigits(3)
        self.SET_Tmax.SetBackgroundColour('white')

        self.button3 = wx.Button(self, label="Set", pos=(380, 130), size = (100,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TMAX,self.button3)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname5 = wx.StaticText(self, label = "Resistance (Ohm):", pos = (40,195))
        self.resistance = wx.TextCtrl(self, size=(150,40), pos = (200,185), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
        self.resistance.SetBackgroundColour('grey')

        self.lblname6 = wx.StaticText(self, label = "Power (mW):", pos = (360,195))
        self.power = wx.TextCtrl(self, size=(150,40), pos = (450,185), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
        self.power.SetBackgroundColour('grey')

        myserial, model = self.getserial()
        print (myserial)
        if myserial=='10000000647b5ee6': 
            self.lblname4 = wx.StaticText(self, label = "Calibration :", pos = (240,85))
            self.Mode_Selection = ['Open Circuit', 'Short Circuit', '200 Ohm', 'CAL_MDAC']
            self.Combo1 = wx.ComboBox(self, choices = self.Mode_Selection, pos = (340,80), size = (160,-1))
            
            self.button2 = wx.Button(self, label="Set", pos=(540, 75), size = (100,40), id = -1)
            self.Bind(wx.EVT_BUTTON, self.ON_SET_MODE,self.button2)
            self.button2.SetForegroundColour('black')
            self.button2.SetBackgroundColour(wx.Colour(211,211,211))

        self.button5 = wx.Button(self, label="Software Reset", pos=(40, 245), size = (200,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_SOFT_RESET,self.button5)
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour(wx.Colour(211,211,211))

        self.button6 = wx.Button(self, label="Alarm Reset", pos=(290, 245), size = (200,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_ALARM_RESET,self.button6)
        self.button6.SetForegroundColour('black')
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))

        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.lblname1.SetFont(self.font2)
            self.lblname7.SetFont(self.font2)
            self.lblname8.SetFont(self.font2)
            self.lblname2.SetFont(self.font2)
            self.button1.SetFont(self.font2)
            self.lblname3.SetFont(self.font2)
            self.button3.SetFont(self.font2)
            self.lblname5.SetFont(self.font2)
            self.lblname6.SetFont(self.font2)
            self.button6.SetFont(self.font2)
            self.button5.SetFont(self.font2)

    def getserial(self):
        """
        Extract serial and model number from cpuinfo file

        Returns
        -------
        cpuserial : String
            Unique serial number of the Raspberry pi.
        model : String
            Model name of raspberry pi.
        
        Raised:
        -------    
        Error: Incase unable to read the CPUserial an error is raised.

        """
      
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                  cpuserial = line[10:26]
                if line[0:5]=='Model':
                  model = line[9:23]
                else:
                  model = 'Raspberry Pi 3'
            f.close()
        except:
          cpuserial = "ERROR000000000"
     
        return cpuserial, model

    def ON_CALIBRATE_R0(self, e):
        """
        Function executed when the button to Calibrate is clicked. Timer is started and an event is executed every 1 second. 

        Parameters
        ----------
        e : event
            Button event when calibrate button is pressed.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        
        self.R0.clear()
        self.paused = not self.paused
        self.A = self.SET_A.GetValue()*0.001
        self.B = self.SET_B.GetValue()*0.0000001
        self.Tamb = self.SET_Tamb.GetValue()
        print (self.A, self.B, self.Tamb)
        self.redraw_timer.Start(1000)
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Calibration" + "," + "Started" + "\n")
            f.write(str(datetime.now()) + "," + "SH" + "," + "A value" + "," + self.A + "\n")
            f.write(str(datetime.now()) + "," + "SH" + "," + "B value" + "," + self.B + "\n")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Tamb value" + "," + self.Tamb + "\n")
            f.close()
        except TypeError:
            pass

    def On_R0_Changed(self, e):
        """
        Function executed when R0 value is changed. Further calculates the power consumed by the heater and is displayed.

        Parameters
        ----------
        e : event
            Value change event from the indicator box.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        R = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        self.Alarm = R.Alarm
        pub.sendMessage(self.pubsubalarm, alarm = int(self.Alarm))
        Get_R = R.Float.Float[0]
        
        Voltage = mmis.Functions.GETTransactions(0X05, self.chipselect, self.interruptpin)
        Voltage_Data =  (Voltage.Float.Float[0]*10*3)/(math.pow(2,24)) #in Volts
        Current = mmis.Functions.GETTransactions(0X06, self.chipselect, self.interruptpin)
        Current_Data =  (Current.Float.Float[0]*10*3)/(1000*math.pow(2,24)) #in A
        power = Voltage_Data*Current_Data*1000 # converts to mW from Watts
        
        self.resistance.SetValue(str(Get_R))
        self.power.SetValue(str(power))
        self.A = self.SET_A.GetValue()*0.001
        self.B = self.SET_B.GetValue()*0.0000001
        self.Tamb = self.SET_Tamb.GetValue()
        self.R0.append(self.SET_R0.GetValue())
        pub.sendMessage(self.pubsubname, value1 = self.A, value2 = self.B, value3 = self.R0[len(self.R0)-1])
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "R0 value" + "," + self.R0 + "\n")
            f.write(str(datetime.now()) + "," + "SH" + "," + "A value" + "," + self.A + "\n")
            f.write(str(datetime.now()) + "," + "SH" + "," + "B value" + "," + self.B + "\n")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Tamb value" + "," + self.Tamb + "\n")
            f.close()
        except TypeError:
            pass

    def on_update_pause_button(self, e):
        """
        Function executed when start calibration pressed. Toggles the button color between Red (Stop) and Green (Start) 

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        if self.paused:
            label = "Start Calibration"
            color = "light green"
            self.redraw_timer.Stop()
        else:
            label = "Stop Calibration"
            color = "red"
    
        self.button1.SetLabel(label)
        self.button1.SetBackgroundColour(color)

    def on_redraw_timer(self, e):
        """
        The timer event is generated every second while the calibration is on.

        Parameters
        ----------
        e : event
            Executed when the redraw_Timer is on.

        Returns
        -------
        None.

        """
        R = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        self.Alarm = R.Alarm
        pub.sendMessage(self.pubsubalarm, alarm = int(self.Alarm))
        Get_R = R.Float.Float[0]
        R0 = Get_R/(1+self.A*self.Tamb+self.B*self.Tamb*self.Tamb)
        self.R0.append(Get_R/(1+self.A*self.Tamb+self.B*self.Tamb*self.Tamb))
        pub.sendMessage(self.pubsubname, value1 = self.A, value2 = self.B, value3 = self.R0[len(self.R0)-1]) # used Pubsub functionality to set data across different frames
        self.SET_R0.SetValue(str(self.R0[len(self.R0)-1]))
        
        Voltage = mmis.Functions.GETTransactions(0X05, self.chipselect, self.interruptpin)
        Voltage_Data =  (Voltage.Float.Float[0]*10*3)/(math.pow(2,24)) #in Volts
        Current = mmis.Functions.GETTransactions(0X06, self.chipselect, self.interruptpin)
        Current_Data =  (Current.Float.Float[0]*10*3)/(1000*math.pow(2,24)) #in A
        power = Voltage_Data*Current_Data*1000 # converts to mW from Watts
        
        self.resistance.SetValue(str(Get_R))
        self.power.SetValue(str(power))
        self.Stop_Calibration()
        

    def Stop_Calibration(self):
        """
        Checks whether sufficient number of samples has been collected to calculate R0. 
        Also checks whether the value of R0 is stable enough to stop the calibration process. 

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        if len(self.R0)>4:
            delta_R0 = self.R0[len(self.R0)-1] - self.R0[len(self.R0)-5]
            if abs(delta_R0)<0.1:
                print ("Calibration finished")
                self.paused = not self.paused
                self.button1.SetLabel("Start Calibration")
                self.button1.SetBackgroundColour("light green")
                self.redraw_timer.Stop()
                try:
                    self.UEfile = self.mc.get("UE")
                    f = open(self.UEfile, "a")
                    f.write(str(datetime.now()) + "," + "SH" + "," + "Calibration" + "," + "Completed" + "\n")
                    f.write(str(datetime.now()) + "," + "SH" + "," + "R0 Value" + "," + self.R0 + "\n")
                    f.close()
                except TypeError:
                    pass
            else:
                print ("Calibration still Going on ....")
                
            Get_Rmax = mmis.Functions.GETTransactions(0X09, self.chipselect, self.interruptpin)
            Rmax =  Get_Rmax.Float.Float[0]
            R0 = float(self.SET_R0.GetValue())
            print (R0, Rmax)
            Temperature_Data = self.R_to_Temp(R0, Rmax)
            print (Temperature_Data)
            self.SET_Tmax.SetValue(str(Temperature_Data)[:5])
            self.Generate_set_Tmax_Event()

    def R_to_Temp(self, R0, Rmax):
        """
        Calculates the temperature from resistance values. Second order math calculation

        Parameters
        ----------
        R0 : Float
            Heater resistance at room temperature.
        Rmax : Float
            Maximum allowed heater resistance.

        Returns
        -------
        Temperature_Data : Float
            Floating point value of calculated temperature.
        
        Raised:
        -------    
        ValueError: When there is value error, the temperature data is given a 0 value

        """
        if self.B == 0:
                Temperature_Data = ((Rmax/R0)-1)/self.A # according to standard formula
        else:
            try:
                quad = math.sqrt((math.pow(self.A,2)-4*self.B*(1-(Rmax/R0)))) 
                if quad >= 0:
                    Temperature_Data = (-self.A+quad)/(2*self.B)
                else:
                    if -quad > 0:
                        Temperature_Data = (-self.A-quad)/(2*self.B)
                    else:
                        Temperature_Data = 0
            except ValueError:
                Temperature_Data = 0
        return Temperature_Data
        
    def ON_SET_TMAX(self, e):
        """
        Function executed when Set Tmax button is pressed. From Tmax value, maximum resistance is calculated and
        further sent to the Sample heater module

        Parameters
        ----------
        e : Event
            event generated while the button is pressed.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        
        Tmax = self.SET_Tmax.GetValue()
        #Rmax = str(self.A*Tmax*Tmax + self.B*Tmax+ self.R0[len(self.R0)-1])
        Rmax = str(self.R0[len(self.R0)-1]*(1+self.A*Tmax+self.B*Tmax*Tmax)) # new standard formula
        set_tmax = mmis.Functions.SETTransactions(0X08, Rmax , self.chipselect, self.interruptpin)

        Get_Rmax = mmis.Functions.GETTransactions(0X09, self.chipselect, self.interruptpin)
        Get_Rmax =  Get_Rmax.Float.Float[0]
        R0 = float(self.SET_R0.GetValue())
        Tmax = self.R_to_Temp(R0, Get_Rmax)
        self.button3.SetLabel("   Set\n"+str(round(Tmax,2)).center(10))
        self.button3.SetFont(self.font3)
        print(Tmax)
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Set Tmax" + "," + str(Tmax) + "\n")
            f.close()
        except TypeError:
            pass
        
    def Generate_set_Tmax_Event(self):
        """
        Function programmatically generates a user event to set the Tmax

        Returns
        -------
        None.

        """

        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button3)
        evt.SetId(self.button3.GetId())
        self.button3.GetEventHandler().ProcessEvent(evt)
        
    def ON_SET_MODE(self, e):
        """
        Function executed when an option from the drop down menu of sample heater module calibration is pressed.
        This menu is available to the developer alone and not to the user. The module needs to be calibrated in certain order
        starting with open circuit calibration --> short circuit calibration --> 200 ohm calibration --> MDAC calibration

        Parameters
        ----------
        e : Event
            Dropdown menu selection event.

        Returns
        -------
        None.

        """
        data = str(self.Combo1.GetSelection())
        if int(data) == 0:
            print ("Open Circuit Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X4E, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 1:
            print ("Short Circuit Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X4D, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 2:
            print ("200 Ohm Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X4C, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 3:
            print ("Calibration MDAC Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X46, self.chipselect, self.interruptpin, 30)
            print (mode.Received)

    def ON_MODULE_NAME(self, e):
        """
        To request the name of the module

        Parameters
        ----------
        e : Event
            Button press event. Currently not available to the user

        Returns
        -------
        None.

        """
        name = mmis.Functions.GETTransactions(0X0C, self.chipselect, self.interruptpin)
        print (name.Received)
        self.Module_Name.SetValue(name.String) 

    def ON_VERSION_REQUEST(self, e):
        """
        To request the version number of the firmware programmed in the sample heater module

        Parameters
        ----------
        e : Event
            Button press event. Currently not availabel to the user

        Returns
        -------
        None.

        """
        Version = mmis.Functions.GETTransactions(0X0D, self.chipselect, self.interruptpin)
        print (Version.Version)
        self.Soft_Version.SetValue(Version.Version)

    def ON_SOFT_RESET(self, e):
        """
        Resets the firmware of the sample heater module.

        Parameters
        ----------
        e : Event
            Button press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        Reset = mmis.Functions.GETTransactions(0X0E, self.chipselect, self.interruptpin)
        print (Reset.Received)
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Software Reset" + "," + "1" + "\n")
            f.close()
        except TypeError:
            pass
    
    def ON_ALARM_RESET(self, e):
        """
        Resets all the alarms raised from the sample heater module.

        Parameters
        ----------
        e : Event
            Button press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        Reset = mmis.Functions.GETTransactions(0X0F, self.chipselect, self.interruptpin)
        print (Reset.Character)
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Alarm Reset" + "," + "1" + "\n")
            f.close()
        except TypeError:
            pass
    
    def OnCloseWindow(self, e):
        """
        function executed while the close window button is pressed 

        Parameters
        ----------
        e : Event
            Close Button pressed event.

        Returns
        -------
        None.

        """
        self.Destroy()

class Main(wx.Panel):

    def __init__(self, parent, Module, pubsub1, pubsub2):
        """
        Initializes all the control graphical user elements of the sample heater module

        Parameters
        ----------
        parent : notebook element (wx.nb)
            notebook element from wx library GUI.
        Module : [uint8, uint8]
            list contains chip select gpio and interrupt gpio.
        pubsub1 : string
            it is subscribed to the R0 value from settings module of sample heater.
        pubsub2 : string
            All the logging data and alarm details from this controls module are communicated to the main GUI over this publicataion/subscription.

        Returns
        -------
        None.

        """
        
        wx.Panel.__init__(self, parent = parent)

        
        self.chipselect = Module[0]
        self.interruptpin = Module[1]
        self.mc = memcache.Client([('127.0.0.1', 11211)])
        
        pub.subscribe(self.OnRvalue, pubsub1)
        self.pubsub_logdata = pubsub2
        
        """ Initilize the lists to store the temperature data """
        self.data = []
        self.paused = True   # At start up data generation event is paused until user starts it
        self.paused_P = True   # At start up data generation event is paused until user starts it
        self.paused_S = True   # At start up data generation event is paused until user starts it
        self.paused_R = True   # At start up data generation event is paused until user starts it
        self.paused_PP = True  # used for power profile
        self.ctrl = True
        self.RvalueSet = False
        self.set_power = 1.0  # initialize
        self.Integrator = 0 # initialize
        
        """ Creating a Timer for updating the Frame rate of the real time graph displayed"""
        self.redraw_graph_timer = wx.Timer(self, id = 2000)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer, self.redraw_graph_timer)  

        self.get_data_timer = wx.Timer(self, id = 2001)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer, self.get_data_timer)

        self.get_read_timer = wx.Timer(self, id = 2002)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_read_timer, self.get_read_timer)
        self.get_read_timer.Start(220)

        self.get_PID_timer = wx.Timer(self, id = 2003)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.PID, self.get_PID_timer)

        self.get_slope_timer = wx.Timer(self, id = 2004)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.slope_control, self.get_slope_timer)

        self.get_ramp_timer = wx.Timer(self, id = 2005)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.ramp_control, self.get_ramp_timer)
        
        self.get_powerprofile_timer = wx.Timer(self, id = 2006)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.Power_Profile_control, self.get_powerprofile_timer)

        self.get_slowcooling_timer = wx.Timer(self, id = 2007)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.Slow_Cooling_control, self.get_slowcooling_timer)
        
        """ Initializing the graph plot to display the temperatures"""
        self.init_plot()
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.Xticks = 50
        self.Yticks = 1

        """GRID and Font created"""
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font3 = wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        """Control Mode Selection Box"""
        self.lblname1 = wx.StaticText(self, label = "Control:")
        self.Mode_Selection = ['Temperature', 'Power', 'T-Profile', 'Ramp', 'P-Profile']
        self.Combo1 = wx.ComboBox(self, choices = self.Mode_Selection, size = (120,-1))
        self.Combo1.Bind(wx.EVT_COMBOBOX, self.ON_SET_MODE)

        """Turn on heater main"""
        self.button13 = wx.Button(self, label = 'ON Heater', size = (90,35), id=-1)
        self.button13.Bind(wx.EVT_BUTTON, self.OnHeater)
        self.button13.SetForegroundColour('black')
        self.button13.SetBackgroundColour('white')

        """Loads the profile for the Profile control"""
        self.button3 = wx.Button(self, label = 'Load Profile', size = (90,35), id=3)
        self.button3.Bind(wx.EVT_BUTTON, self.OnFileOpen)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour('white')

        """Starts the Profile Control"""
        self.button4 = wx.Button(self, label = 'ON Ctrl', size = (55, 35), id =24)
        self.button4.Bind(wx.EVT_BUTTON, self.on_pause_button_S)    
        self.button4.SetForegroundColour('black')
        self.button4.SetBackgroundColour('light green')

        """Status of the profile for the Profile control"""
        self.button12 = wx.Button(self, label = 'Show Status', size = (100,35), id=-1)
        self.button12.Bind(wx.EVT_BUTTON, self.OnShowProfileStatus)
        self.button12.SetForegroundColour('black')
        self.button12.SetBackgroundColour('white')

        """Loads the profile for the Power Profile control"""
        self.button14 = wx.Button(self, label = 'Load Profile', size = (90,35), id=-1)
        self.button14.Bind(wx.EVT_BUTTON, self.OnFileOpen_PP)
        self.button14.SetForegroundColour('black')
        self.button14.SetBackgroundColour('white')

        """Starts the Power Profile Control"""
        self.button15 = wx.Button(self, label = 'ON Ctrl', size = (55, 35), id =-1)
        self.button15.Bind(wx.EVT_BUTTON, self.on_pause_button_PP)    
        self.button15.SetForegroundColour('black')
        self.button15.SetBackgroundColour('light green')

        """Status of the Power profile for the Profile control"""
        self.button16 = wx.Button(self, label = 'Show Status', size = (100,35), id=-1)
        self.button16.Bind(wx.EVT_BUTTON, self.OnShowProfileStatus_PP)
        self.button16.SetForegroundColour('black')
        self.button16.SetBackgroundColour('white')

        """Starts the Temperature Control"""
        self.button5 = wx.Button(self, label = 'ON Ctrl', size = (70, 35), id =12)
        self.button5.Bind(wx.EVT_BUTTON, self.on_pause_button)  
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('light green')

        """Starts the Power Control"""
        self.button8 = wx.Button(self, label = 'ON Ctrl', size = (70, 35), id =14)
        self.button8.Bind(wx.EVT_BUTTON, self.on_pause_button_P)    
        self.button8.SetForegroundColour('black')
        self.button8.SetBackgroundColour('light green')

        """Starts the Ramp Control"""
        self.button9 = wx.Button(self, label = 'ON Ctrl', size = (70, 30), id =34)
        self.button9.Bind(wx.EVT_BUTTON, self.on_pause_button_R)    
        self.button9.SetForegroundColour('black')
        self.button9.SetBackgroundColour('light green')

        # Static text and text control box - to display the current value of temperature
        self.lblname2 = wx.StaticText(self, label = "Temperature(\u00b0C)")
        self.grid.Add(self.lblname2, pos = (0,0))
        self.two = wx.TextCtrl(self, id = 5, size=(135,35), style = wx.TE_READONLY)
        self.two.SetBackgroundColour('grey')
        self.two.SetFont(self.font1)
        self.grid.Add(self.two, pos=(0,1))

        # Static text and text control box - to display the current value of resistance
        self.lblname4 = wx.StaticText(self, label = "Resistance(\u2126)")
        self.grid.Add(self.lblname4, pos = (2,0))
        self.four = wx.TextCtrl(self, id = 7, size=(135,35), style = wx.TE_READONLY)
        self.four.SetBackgroundColour('grey')
        self.four.SetFont(self.font1)
        self.grid.Add(self.four, pos=(2,1))

        # Static text and text control box - to display the current value of resistance
        self.lblname5 = wx.StaticText(self, label = "Power(mW)")
        self.grid.Add(self.lblname5, pos = (4,0))
        self.five = wx.TextCtrl(self, id = 7, size=(135,35), style = wx.TE_READONLY)
        self.five.SetBackgroundColour('grey')
        self.five.SetFont(self.font1)
        self.grid.Add(self.five, pos=(3,1))

        # Static text and num control box -  to set the value of temperature
        self.button6 = wx.Button(self, label = 'Set(\u00b0C)', size = (57,35), id=5)
        self.button6.Bind(wx.EVT_BUTTON, self.SetResistance)
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))
        self.one = wx.SpinCtrlDouble(self, size=(140,-1), min =-300, max = 800, inc = 0.1, value='80.00')
        self.one.SetDigits(3)
        self.one.SetBackgroundColour('white')

        self.button7 = wx.Button(self, label = 'Set(mW)', size = (65,35), id=7)
        self.button7.Bind(wx.EVT_BUTTON, self.SetPower)
        self.button7.SetBackgroundColour(wx.Colour(211,211,211))
        self.six = wx.SpinCtrlDouble(self, size=(140,-1), min =0, max = 50, inc = 0.1, value='1.0')
        self.six.SetDigits(3)
        self.six.SetBackgroundColour('white')

        self.button10 = wx.Button(self, label = 'set\u00b0C/s', size = (60,30), id=8) # Set slope
        self.button10.Bind(wx.EVT_BUTTON, self.SetRampRate)
        self.button10.SetBackgroundColour(wx.Colour(211,211,211))
        self.seven = wx.SpinCtrlDouble(self, size=(140,-1), min =-100, max = 100, inc = 0.1, value='10.0')
        self.seven.SetDigits(3)
        self.seven.SetBackgroundColour('white')

        self.button11 = wx.Button(self, label = 'set end(\u00b0C)', size = (90,30), id=15) # Set set point temperature
        self.button11.Bind(wx.EVT_BUTTON, self.SetFinalTemperature)
        self.button11.SetBackgroundColour(wx.Colour(211,211,211))
        self.eight = wx.SpinCtrlDouble(self, size=(140,-1), min =-300, max = 800, inc = 0.1, value='80.00')
        self.eight.SetDigits(3)
        self.eight.SetBackgroundColour('white')

        # Static text and text control box - set the value to display the number of values on X -axis
        self.lblname3 = wx.StaticText(self, label = "X-Scale")
        self.grid.Add(self.lblname3, pos = (1,0))
        self.three = wx.TextCtrl(self, id = 6, size = (70,30), style = wx.TE_PROCESS_ENTER)
        self.three.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength)
        self.three.SetBackgroundColour('white')
        self.grid.Add(self.three, pos=(1,1))

        self.lblname11 = wx.StaticText(self, label = "Y-Scale")
        self.grid.Add(self.lblname11, pos = (21,0))
        self.eleven = wx.TextCtrl(self, id = 80, size = (60,30), style = wx.TE_PROCESS_ENTER)
        self.eleven.Bind(wx.EVT_TEXT_ENTER, self.OnSetYLabelLength)
        self.eleven.SetBackgroundColour('white')
        self.grid.Add(self.eleven, pos=(21,1))

        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.three.SetFont(self.font2)
            self.eleven.SetFont(self.font2)
            self.button11.SetFont(self.font3)
            self.button10.SetFont(self.font3)
            self.button7.SetFont(self.font3)
            self.button6.SetFont(self.font3)
            self.lblname5.SetFont(self.font2)
            self.lblname4.SetFont(self.font2)
            self.lblname2.SetFont(self.font2)
            self.button9.SetFont(self.font2)
            self.button8.SetFont(self.font2)
            self.button5.SetFont(self.font2)
            self.button4.SetFont(self.font2)
            self.button3.SetFont(self.font2)
            self.button12.SetFont(self.font2)
            self.button13.SetFont(self.font2)
            self.lblname1.SetFont(self.font2)
            self.button14.SetFont(self.font2)
            self.button15.SetFont(self.font2)
            self.button16.SetFont(self.font2)

        # Set all the buttons, check boxes and text controls in a BOX
        self.hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox0.Add(self.lblname1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox0.Add(self.Combo1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox0.Add(self.button13, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.button8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.one, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.six, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button7, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.eight, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button11, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button12, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button14, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button15, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button16, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2_1.Add(self.seven, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.button10, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.button9, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.lblname2, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.AddSpacer(5)
        self.hbox3.Add(self.two, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.lblname4, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(25)
        self.hbox4.Add(self.four, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.lblname5, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.AddSpacer(40)
        self.hbox5.Add(self.five, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        #self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox5.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox5.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.lblname3, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.three, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.lblname11, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.eleven, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox6.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox0, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        #self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2_1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox6, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas, 3.0, flag=wx.LEFT | wx.TOP)  
        self.hbox.Add(self.vbox, 1.99, flag=wx.LEFT | wx.TOP)  
        
        self.SetSizer(self.hbox)
        self.hbox.Fit(self)
        self.hbox2.Hide(0)
        self.hbox2.Hide(1)
        self.hbox2.Hide(2)
        self.hbox2.Hide(3)
        self.hbox2.Hide(4)
        self.hbox2.Hide(5)
        self.hbox2.Hide(6)
        self.hbox2.Hide(7)
        self.hbox2.Hide(8)
        self.hbox2.Hide(9)
        self.hbox2.Hide(10)
        self.hbox2.Hide(11)
        self.hbox2.Hide(12)
        self.hbox2.Hide(13)
        self.hbox2_1.Hide(0)
        self.hbox2_1.Hide(1)
        self.hbox2_1.Hide(2)


    def OnShowProfileStatus(self, e):
        """
        Shows a status of the Temperature profile control on a xy plot with respective to the reference setpoints of the profile

        Parameters
        ----------
        e : event
            Button click event.

        Returns
        -------
        None.

        """
        x = list(np.array(self.Times)/240)
        y = self.SetPoints
        plt.figure(figsize=(6,4))
        plt.plot(x, y, '-+', label='Profile Reference')
        plt.plot((self.Count_Seconds/240), y[self.count_setpoint], 'or', label='Current status')
        plt.title('Profile Status')
        plt.xlabel('Time (mins)')
        plt.ylabel('Temperature')
        plt.legend()
        plt.show()

    def OnShowProfileStatus_PP(self, e):
        """
        Shows a status of the Power profile control on a xy plot with respective to the reference setpoints of the profile

        Parameters
        ----------
        e : Event
            Button click event.

        Returns
        -------
        None.

        """
        x = list(np.array(self.Times_PP)/240)
        y = self.SetPoints_PP
        plt.figure(figsize=(6,4))
        plt.plot(x, y, '-+', label='Profile Reference')
        plt.plot((self.Count_Seconds_PP/240), y[self.count_setpoint_PP], 'or', label='Current status')
        plt.title('Profile Status')
        plt.xlabel('Time (mins)')
        plt.ylabel('Temperature')
        plt.legend()
        plt.show()

    def getserial(self):
        """
        Extract serial and model number from cpuinfo file

        Returns
        -------
        cpuserial : String
            Unique serial number of the Raspberry pi.
        model : String
            Model name of raspberry pi.
        
        Raised:
        -------    
        Error: Incase unable to read the CPUserial an error is raised.

        """
      
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                  cpuserial = line[10:26]
                if line[0:5]=='Model':
                  model = line[9:23]
                else:
                  model = 'Raspberry Pi 3'
            f.close()
        except:
          cpuserial = "ERROR000000000"
     
        return cpuserial, model

    def OnFileOpen(self,e):
        """
        The text file with the temperature profile setpoints are loaded and parsed for the information about time, setpoint, slope and comments

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        self.dirname = ''
        self.Times = []
        self.SetPoints = []
        self.Slopes = []
        self.Comments = []
        mylines = []
        words = []
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.file = open(os.path.join(self.dirname, self.filename), 'rt')
            for myline in self.file:
                mylines.append(myline.partition('#')[0])
            #print (mylines)    
            #x = self.file.readlines()
            self.file.close()
            
            for line in mylines:
                for element in line.split():
                    words.append(element)
                    
        for i in range(int(len(words)/2 - 1)):
    
            self.Times.append(words[(i+1)*2])
            self.SetPoints.append(words[(i+1)*2+1])
            #self.Comments.append(words[(i+1)*3+2])
            
        self.Times = [float(i) for i in self.Times]
        self.Times = [round(i * 60 * 4) for i in self.Times] # Conversion to seconds from minutes
        self.SetPoints = [float(i) for i in self.SetPoints]
        
        #self.Slopes = [(a*1.0)/b for a, b in zip(self.SetPoints, self.Times)]
        current_temp = self.x[0]
        init_time = 0
        for i in range(len(self.Times)):
            self.Slopes.append((self.SetPoints[i]-current_temp)/(self.Times[i]-init_time))
            current_temp = self.SetPoints[i]
            init_time = self.Times[i]
        
        #print (self.Times)
        #print (self.SetPoints)
        #print (self.Slopes)
        #print (self.Comments)
        self.Count_Seconds = 0
        dlg.Destroy()

    def OnFileOpen_PP(self,e):
        """
        The text file with the power profile setpoints are loaded and parsed for the information about time, setpoint, slope and comments

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        self.dirname = ''
        self.Times_PP = []
        self.SetPoints_PP = []
        self.Slopes_PP = []
        self.Comments_PP = []
        mylines = []
        words = []
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.file = open(os.path.join(self.dirname, self.filename), 'rt')
            for myline in self.file:
                mylines.append(myline.partition('#')[0])
            #print (mylines)    
            #x = self.file.readlines()
            self.file.close()
            
            for line in mylines:
                for element in line.split():
                    words.append(element)
                    
        for i in range(int(len(words)/2 - 1)):
    
            self.Times_PP.append(words[(i+1)*2])
            self.SetPoints_PP.append(words[(i+1)*2+1])
            #self.Comments_PP.append(words[(i+1)*3+2])
            
        self.Times_PP = [float(i) for i in self.Times_PP]
        self.Times_PP = [round(i * 60 * 4) for i in self.Times_PP] # Conversion to seconds from minutes
        self.SetPoints_PP = [float(i) for i in self.SetPoints_PP]
        
        current_power = self.measured_power
        init_time = 0
        for i in range(len(self.Times_PP)):
            self.Slopes_PP.append((self.SetPoints_PP[i]-current_power)/(self.Times_PP[i]-init_time))
            current_power = self.SetPoints_PP[i]
            init_time = self.Times_PP[i]
        
        #print (self.Times_PP)
        #print (self.SetPoints_PP)
        #print (self.Slopes_PP)
        #print (self.Comments_PP)
        self.Count_Seconds_PP = 0
        dlg.Destroy()

    def ON_SET_MODE(self, e):
        """
        Dropdown menu function to select the type of experiment to perform with the sample heater module
        1. Temperature control
        2. Power Control
        3. Temperature Profile Control
        4. Ramp Control
        5. Power Profile Control
        upon the selection from menu, the respective graphical user interface elements are displayed
        
        Parameters
        ----------
        e : event
            Drop down menu selection event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        data = str(self.Combo1.GetSelection())
        if int(data) == 0:
            Type = "Temperature Control"
            self.hbox2.Show(0)
            self.hbox2.Show(1)
            self.hbox2.Show(2)
            self.hbox2.Hide(3)
            self.hbox2.Hide(4)
            self.hbox2.Hide(5)
            self.hbox2.Hide(6)
            self.hbox2.Hide(7)
            self.hbox2.Hide(8)
            self.hbox2.Hide(9)
            self.hbox2.Hide(10)
            self.hbox2.Hide(11)
            self.hbox2.Hide(12)
            self.hbox2.Hide(13)
            self.hbox2_1.Hide(0)
            self.hbox2_1.Hide(1)
            self.hbox2_1.Hide(2)
            self.hbox.Layout()
            #self.GetSetResistanceSetValue()
            
        elif int(data) == 1:
            Type = "Power Control"
            self.hbox2.Hide(0)
            self.hbox2.Hide(1)
            self.hbox2.Hide(2)
            self.hbox2.Show(3)
            self.hbox2.Show(4)
            self.hbox2.Show(5)
            self.hbox2.Hide(6)
            self.hbox2.Hide(7)
            self.hbox2.Hide(8)
            self.hbox2.Hide(9)
            self.hbox2.Hide(10)
            self.hbox2.Hide(11)
            self.hbox2.Hide(12)
            self.hbox2.Hide(13)
            self.hbox2_1.Hide(0)
            self.hbox2_1.Hide(1)
            self.hbox2_1.Hide(2)
            self.hbox.Layout()
            
        elif int(data) == 2:
            Type = "Profile Control"
            self.hbox2.Hide(0)
            self.hbox2.Hide(1)
            self.hbox2.Hide(2)
            self.hbox2.Hide(3)
            self.hbox2.Hide(4)
            self.hbox2.Hide(5)
            self.hbox2.Show(6)
            self.hbox2.Show(7)
            self.hbox2.Hide(8)
            self.hbox2.Hide(9)
            self.hbox2.Show(10)
            self.hbox2.Hide(11)
            self.hbox2.Hide(12)
            self.hbox2.Hide(13)
            self.hbox2_1.Hide(0)
            self.hbox2_1.Hide(1)
            self.hbox2_1.Hide(2)
            self.hbox.Layout()
            
        elif int(data) == 3:
            Type = "Ramp Control"
            self.hbox2.Hide(0)
            self.hbox2.Hide(1)
            self.hbox2.Hide(2)
            self.hbox2.Hide(3)
            self.hbox2.Hide(4)
            self.hbox2.Hide(5)
            self.hbox2.Hide(6)
            self.hbox2.Hide(7)
            self.hbox2.Show(8)
            self.hbox2.Show(9)
            self.hbox2.Hide(10)
            self.hbox2.Hide(11)
            self.hbox2.Hide(12)
            self.hbox2.Hide(13)
            self.hbox2_1.Show(0)
            self.hbox2_1.Show(1)
            self.hbox2_1.Show(2)
            self.hbox.Layout()

        elif int(data) == 4:
            Type = "P-Profile Control"
            self.hbox2.Hide(0)
            self.hbox2.Hide(1)
            self.hbox2.Hide(2)
            self.hbox2.Hide(3)
            self.hbox2.Hide(4)
            self.hbox2.Hide(5)
            self.hbox2.Hide(6)
            self.hbox2.Hide(7)
            self.hbox2.Hide(8)
            self.hbox2.Hide(9)
            self.hbox2.Hide(10)
            self.hbox2.Show(11)
            self.hbox2.Show(12)
            self.hbox2.Show(13)
            self.hbox2_1.Hide(0)
            self.hbox2_1.Hide(1)
            self.hbox2_1.Hide(2)
            self.hbox.Layout()

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Select Control" + "," + Type + "\n")
            f.close()
        except TypeError:
            pass
        
    def OnRvalue(self, value1, value2, value3):
        """
        Executed when R0 value from the settings panel is updated. Event appended to the publication/subscription from settings window

        Parameters
        ----------
        value1 : Float
            A value.
        value2 : Float
            B value.
        value3 : Float
            R0 value.

        Returns
        -------
        None.

        """
        self.RvalueSet = True
        self.A = value1
        self.B = value2
        self.R0 = value3
        self.Refresh()
    
    def Temperature_Acquisition(self):
        """
        Data Acquisition of the resistance, voltage and current is executed from sample heater module.
        Further the resistance is converted to Temperature

        Returns
        -------
        Temp : list of [Temperature, Voltage, Current, Resistance] float
            list of all the  values described above.
            
        Raised:
        -------    
        AttributeError: simply passed

        """
        try:
            Temp = np.zeros(4)
            Resistance = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
            Resistance_Data =  Resistance.Float.Float[0]
            self.Alarm = Resistance.Alarm
            if self.B == 0:
                #Temperature_Data = ((Resistance_Data-self.R0)/self.B)
                Temperature_Data = ((Resistance_Data/self.R0)-1)/self.A # according to standard formula
            else:
                try:
                    #quad = math.sqrt((math.pow(self.B,2)-4*(self.R0-Resistance_Data)*self.A))
                    quad = math.sqrt((math.pow(self.A,2)-4*self.B*(1-(Resistance_Data/self.R0)))) 
                    if quad >= 0:
                        Temperature_Data = (-self.A+quad)/(2*self.B)
                    else:
                        if -quad > 0:
                            Temperature_Data = (-self.A-quad)/(2*self.B)
                        else:
                            Temperature_Data = 0
                except ValueError:
                    Temperature_Data = 0
            
            Voltage = mmis.Functions.GETTransactions(0X05, self.chipselect, self.interruptpin)
            Voltage_Data =  (Voltage.Float.Float[0]*10*3)/(math.pow(2,24)) #in Volts
            
            Current = mmis.Functions.GETTransactions(0X06, self.chipselect, self.interruptpin)
            Current_Data =  (Current.Float.Float[0]*10*3)/(1000*math.pow(2,24)) #in A

            #print (Voltage.Float.Float[0], Voltage_Data, Current.Float.Float[0], Current_Data)
            Temp[0] = Temperature_Data
            Temp[1] = Voltage_Data
            Temp[2] = Current_Data
            Temp[3] = Resistance_Data
            self.measured_power = Voltage_Data*Current_Data*1000 # converts to mW from Watts
            pub.sendMessage(self.pubsub_logdata, data = Temp, alarm = self.Alarm)
            #print (Temp[0]/self.measured_power)
            return Temp
        except AttributeError:
            #print ("hello")
            pass

    def init_plot(self):
        """
        The settings for the plot are initialized

        Returns
        -------
        None.

        """

        self.dpi = 60
        self.fig = Figure((5.0, 5.1), dpi = self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Temperature acquisition', size = 15)
        self.axes.set_xlabel('Samples', size = 12)
        self.axes.set_ylabel('Ambient Temperature (C)', size = 15)

        pylab.setp(self.axes.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes.get_yticklabels(), fontsize=12)
        
        self.plot_data = self.axes.plot(
            self.data,
            linewidth=1,
            color=(1,1,0),
            )[0]

    def draw_plot(self):
        """
        Draws the plot every one second with the updated measurements. 

        Returns
        -------
        None.

        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.

        xmax = len(self.data) if len(self.data) > 50 else 50           
        xmin = xmax - self.Xticks

        """ for ymin and ymax, find the minimal and maximal values
        in the data set and add a mininal margin.
        
        note that it's easy to change this scheme to the 
        minimal/maximal value in the current display, and not
        the whole data set. """
        
        ymin = round(min(self.data[(-self.Xticks):]), 0) - self.Yticks
        ymax = round(max(self.data[(-self.Xticks):]), 0) + self.Yticks

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #
        #if self.cb_grid.IsChecked():
        self.axes.grid(True, color='gray')
        #else:
            #self.axes.grid(False)
        
        pylab.setp(self.axes.get_xticklabels(), 
            visible=True)
        
        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))
        self.canvas.draw()
        
    def OnSetXLabelLength(self, e):
        """
        Number of Data points to be plotted (X scale) can be changed through a control box on GUI

        Parameters
        ----------
        e : Event
            Change of Value event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        Xtks = self.three.GetValue()
        self.Xticks = int(Xtks.encode())
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "X label" + "," + str(Xtks) + "\n")
            f.close()
        except TypeError:
            pass
        
    def OnSetYLabelLength(self, e):
        """
        Y axis scale can be changed through a control box on GUI

        Parameters
        ----------
        e : Event
            Change of Value event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        Ytks = self.eleven.GetValue()
        self.Yticks = float(Ytks.encode())
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Y label" + "," + str(Ytks) + "\n")
            f.close()
        except TypeError:
            pass
    
    def on_cb_grid(self, event):
        """
        Grid on the plot can be enabled and disabled from a tick box on GUI 

        Parameters
        ----------
        event : Event
            Tick box event.

        Returns
        -------
        None.

        """
        self.draw_plot()

    def on_cb_xlab(self, event):
        """
        X axis lables on the plot can be enabled and disabled from a tick box on GUI 

        Parameters
        ----------
        event : Event
            Tick box event.

        Returns
        -------
        None.

        """
        self.draw_plot()

    def OnHeater(self, e):
        """
        Sends ON and OFF commands to the sample heater module. Also asks the user whether
        to start the slow cooldown control upon a heater control turn off. 

        Parameters
        ----------
        e : Event
            Button press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        

        if not self.paused:
            self.paused = not self.paused
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.button5.SetLabel(label)
            self.button5.SetBackgroundColour(color)
        if not self.paused_P:
            self.paused_P = not self.paused_P
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.button8.SetLabel(label)
            self.button8.SetBackgroundColour(color)
        if not self.paused_PP:
            self.paused_PP = not self.paused_PP
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.get_powerprofile_timer.Stop()
            self.button15.SetLabel(label)
            self.button15.SetBackgroundColour(color)
        if not self.paused_R:
            self.paused_R = not self.paused_R
            label = "ON Ctrl"
            color = "light green"
            self.get_ramp_timer.Stop()
            status = "stop"
            self.button9.SetLabel(label)
            self.button9.SetBackgroundColour(color)
        if not self.paused_S:
            self.Generate_stop_Sctrl_Event()

        self.ctrl = not self.ctrl
        
        if self.ctrl:
            status = "stop"
            box = wx.MessageDialog(self, 'Would you like to Slow Cool down the heater to room temperature', 'Slow Cool Down', wx.YES_NO)
            answer = box.ShowModal()
            box.Destroy()
            if (answer == 5104): # The number 5104 is the ID for WX.NO
                label = "ON heater"
                color = "light green"
                print("Heater Turned OFF")
                self.redraw_graph_timer.Stop()
                self.get_data_timer.Stop()
                mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
            if (answer == 5103):
                label = "Slow Cooling"
                color = "red"
                self.ctrl = not self.ctrl
                self.get_slowcooling_timer.Start(230)
                self.redraw_graph_timer.Start(1000)
                self.get_data_timer.Start(200)
                self.slow_cooling_slope = (self.x[0]-30)/2400
                self.slow_cooling_counter = 0
                self.slow_cooling_start_temp = self.x[0]
                print(self.slow_cooling_slope)
        else:
            label = "OFF heater"
            color = "red"
            print("Heater Turned ON")
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(200)
            status = "start"

        self.button13.SetLabel(label)
        self.button13.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Heater" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def on_pause_button(self, e):
        """
        Sends ON and OFF commands to the sample heater modules Temperature Control. 

        Parameters
        ----------
        e : Event
            Button Press Event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
                
        if not self.paused_P:
            self.paused_P = not self.paused_P
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.button8.SetLabel(label)
            self.button8.SetBackgroundColour(color)
        if not self.paused_PP:
            self.paused_PP = not self.paused_PP
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.get_powerprofile_timer.Stop()
            self.button15.SetLabel(label)
            self.button15.SetBackgroundColour(color)
        if not self.paused_S:
            self.paused_S = not self.paused_S
            label = "ON Ctrl"
            color = "light green"
            self.get_slope_timer.Stop()
            status = "stop"
            self.button4.SetLabel(label)
            self.button4.SetBackgroundColour(color)
        if not self.paused_R:
            self.paused_R = not self.paused_R
            label = "ON Ctrl"
            color = "light green"
            self.get_ramp_timer.Stop()
            status = "stop"
            self.button9.SetLabel(label)
            self.button9.SetBackgroundColour(color)

        self.paused = not self.paused
        print ("T Control")
        print (self.paused, self.paused_P, self.paused_S, self.paused_R, self.paused_PP)
        
        if self.paused:
            label = "ON Ctrl"
            color = "light green"
            print("Temperature control stopped")
            status = "stop"
        else:
            label = "OFF Ctrl"
            color = "red"
            print("Temperature control started")
            status = "start"
        self.button5.SetLabel(label)
        self.button5.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Temperature Control" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def on_pause_button_P(self, e):
        """
        Sends ON and OFF commands to the sample heater modules Power Control. 

        Parameters
        ----------
        e : Event
            Button Press Event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        
        if not self.paused:
            self.paused = not self.paused
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.button5.SetLabel(label)
            self.button5.SetBackgroundColour(color)
        if not self.paused_PP:
            self.paused_PP = not self.paused_PP
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.get_powerprofile_timer.Stop()
            self.button15.SetLabel(label)
            self.button15.SetBackgroundColour(color)
        if not self.paused_S:
            self.paused_S = not self.paused_S
            label = "ON Ctrl"
            color = "light green"
            self.get_slope_timer.Stop()
            status = "stop"
            self.button4.SetLabel(label)
            self.button4.SetBackgroundColour(color)
        if not self.paused_R:
            self.paused_R = not self.paused_R
            label = "ON Ctrl"
            color = "light green"
            self.get_ramp_timer.Stop()
            status = "stop"
            self.button9.SetLabel(label)
            self.button9.SetBackgroundColour(color)

        self.paused_P = not self.paused_P
        print ("P Control")
        print (self.paused, self.paused_P, self.paused_S, self.paused_R, self.paused_PP)
        self.Kp = 0.5
        self.Ki = 1.7
        
        if self.paused_P:
            label = "ON Ctrl"
            color = "light green"
            self.get_PID_timer.Stop()
            print("power control stopped")
            status = "stop"
            
        else:
            label = "OFF Ctrl"
            color = "red"
            print("Power control started")
            self.Integrator = self.x[0]/self.Ki
            self.set_power = self.measured_power
            self.get_PID_timer.Start(250)
            status = "start"

        self.button8.SetLabel(label)
        self.button8.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Power Control" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def on_pause_button_S(self, e):
        """
        Sends ON and OFF commands to the sample heater modules Temperature Profile Control. 

        Parameters
        ----------
        e : Event
            Button Press Event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        
        if not self.paused:
            self.paused = not self.paused
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.button5.SetLabel(label)
            self.button5.SetBackgroundColour(color)
        if not self.paused_P:
            self.paused_P = not self.paused_P
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.button8.SetLabel(label)
            self.button8.SetBackgroundColour(color)
        if not self.paused_PP:
            self.paused_PP = not self.paused_PP
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.get_powerprofile_timer.Stop()
            self.button15.SetLabel(label)
            self.button15.SetBackgroundColour(color)
        if not self.paused_R:
            self.paused_R = not self.paused_R
            label = "ON Ctrl"
            color = "light green"
            self.get_ramp_timer.Stop()
            status = "stop"
            self.button9.SetLabel(label)
            self.button9.SetBackgroundColour(color)

        self.paused_S = not self.paused_S
        print ("S Control")
        print (self.paused, self.paused_P, self.paused_S, self.paused_R, self.paused_PP)

        if self.paused_S:
            label = "ON Ctrl"
            color = "light green"
            self.get_slope_timer.Stop()
            status = "stop"
        else:
            label = "OFF Ctrl"
            color = "red"
            self.get_slope_timer.Start(230)
            status = "start"

        self.button4.SetLabel(label)
        self.button4.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Profile Control" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def on_pause_button_PP(self, e):
        """
        Sends ON and OFF commands to the sample heater modules Power Profile Control. 

        Parameters
        ----------
        e : Event
            Button Press Event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        
        if not self.paused:
            self.paused = not self.paused
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.button5.SetLabel(label)
            self.button5.SetBackgroundColour(color)
        if not self.paused_P:
            self.paused_P = not self.paused_P
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.button8.SetLabel(label)
            self.button8.SetBackgroundColour(color)
        if not self.paused_R:
            self.paused_R = not self.paused_R
            label = "ON Ctrl"
            color = "light green"
            self.get_ramp_timer.Stop()
            status = "stop"
            self.button9.SetLabel(label)
            self.button9.SetBackgroundColour(color)
        if not self.paused_S:
            self.paused_S = not self.paused_S
            label = "ON Ctrl"
            color = "light green"
            self.get_slope_timer.Stop()
            status = "stop"
            self.button4.SetLabel(label)
            self.button4.SetBackgroundColour(color)

        self.paused_PP = not self.paused_PP
        print ("Power Profile Control")
        print (self.paused, self.paused_P, self.paused_S, self.paused_R, self.paused_PP)
        self.Kp = 0.5
        self.Ki = 1.7

        if self.paused_PP:
            label = "ON Ctrl"
            color = "light green"
            self.get_powerprofile_timer.Stop()
            self.get_PID_timer.Stop()
            status = "stop"
        else:
            label = "OFF Ctrl"
            color = "red"
            self.get_powerprofile_timer.Start(230)
            self.Integrator = self.x[0]/self.Ki
            self.set_power = self.measured_power
            self.get_PID_timer.Start(250)
            status = "start"

        self.button15.SetLabel(label)
        self.button15.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Power Profile Control" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def on_pause_button_R(self, e):  
        """
        Sends ON and OFF commands to the sample heater modules Ramp Control. 

        Parameters
        ----------
        e : Event
            Button Press Event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        
        if not self.paused:
            self.paused = not self.paused
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.button5.SetLabel(label)
            self.button5.SetBackgroundColour(color)
        if not self.paused_P:
            self.paused_P = not self.paused_P
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.button8.SetLabel(label)
            self.button8.SetBackgroundColour(color)
        if not self.paused_PP:
            self.paused_PP = not self.paused_PP
            label = "ON Ctrl"
            color = "light green"
            status = "stop"
            self.get_PID_timer.Stop()
            self.get_powerprofile_timer.Stop()
            self.button15.SetLabel(label)
            self.button15.SetBackgroundColour(color)
        if not self.paused_S:
            self.paused_S = not self.paused_S
            label = "ON Ctrl"
            color = "light green"
            self.get_slope_timer.Stop()
            status = "stop"
            self.button4.SetLabel(label)
            self.button4.SetBackgroundColour(color)

        self.paused_R = not self.paused_R
        print ("R Control")
        print (self.paused, self.paused_P, self.paused_S, self.paused_R, self.paused_PP)

        if self.paused_R:
            label = "ON Ctrl"
            color = "light green"
            self.get_ramp_timer.Stop()
            status = "stop"
        else:
            label = "OFF Ctrl"
            color = "red"
            self.get_ramp_timer.Start(230)
            self.init_ramp_temp = self.x[0]
            status = "start"

        self.button9.SetLabel(label)
        self.button9.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Ramp Control" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def Generate_stop_Tctrl_Event(self):
        """
        Programatically generates the event to stop the Temperature Control

        Returns
        -------
        None.

        """
        #print("T Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button5)
        evt.SetId(self.button5.GetId())
        self.button5.GetEventHandler().ProcessEvent(evt)

    def Generate_stop_Pctrl_Event(self):
        """
        Programatically generates the event to stop the Power Control

        Returns
        -------
        None.

        """
        #print("P Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button8)
        evt.SetId(self.button8.GetId())
        self.button8.GetEventHandler().ProcessEvent(evt)

    def Generate_stop_PPctrl_Event(self):
        """
        Programatically generates the event to stop the Power Profile Control

        Returns
        -------
        None.

        """
        #print("PP Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button15)
        evt.SetId(self.button15.GetId())
        self.button15.GetEventHandler().ProcessEvent(evt)

    def Generate_stop_Sctrl_Event(self):
        """
        Programatically generates the event to stop the Temperature Profile Control

        Returns
        -------
        None.

        """
        #print("S Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button4)
        evt.SetId(self.button4.GetId())
        self.button4.GetEventHandler().ProcessEvent(evt)

    def Generate_stop_Rctrl_Event(self):
        """
        Programatically generates the event to stop the Ramp Control

        Returns
        -------
        None.

        """
        #print("R Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button9)
        evt.SetId(self.button9.GetId())
        self.button9.GetEventHandler().ProcessEvent(evt)

    def Slow_Cooling_control(self, e):
        """
        Executes the slow cooling control of the heater when user requests for slow control 

        Parameters
        ----------
        e : event
            Button press event on the dialog box.

        Returns
        -------
        None.

        """
        if (self.x[0] < 25):
            self.slow_cooling_counter = 0
            self.get_slowcooling_timer.Stop()
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
            self.ctrl = not self.ctrl
            self.get_slowcooling_timer.Stop()
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()
            label = "ON heater"
            color = "light green"
            self.button13.SetLabel(label)
            self.button13.SetBackgroundColour(color)
            box = wx.MessageDialog(self, 'Holder Cooled down to room temperature', 'Finished', wx.OK)
            answer = box.ShowModal()
            box.Destroy()
        else:
            self.slow_cooling_counter = self.slow_cooling_counter+1
            temp = self.slow_cooling_start_temp-(self.slow_cooling_slope*self.slow_cooling_counter)
            #print(temp)
            self.New_SetResistance(temp)
            

    def on_redraw_graph_timer(self, e):
        """
        This interrupt is generated by the graph timer for updating the graph every 1 second.

        Parameters
        ----------
        e : Event
            Graph update timer interrupt.

        Returns
        -------
        None.

        """
        self.draw_plot()

    def on_get_data_timer(self, e):
        """
        The interrupt is generated every 200ms when start control (data_timer) gets a start. Total data points to be stored in buffer
        is limited to 2100 and beyond that based on FIFO the data gets cleared.

        Parameters
        ----------
        e : Event
            Data retreive timer interrupt.

        Returns
        -------
        None.
        
        """

        try:
            if not (self.ctrl):
                if len(self.data)<2100:
                    self.data.append(self.x[0])
                else:
                    del self.data[0]
                    self.data.append(self.x[0])
        except TypeError:
            pass

    def on_get_read_timer(self, e):
        """
        The interrupt is generated every few milliseconds by read_timer interrupt to update the values of Temperature and Resistance
        onto the control window of GUI. These values get updated only if the Rvalue is set atleast once

        Parameters
        ----------
        e : event
            Timer event to update the values to the indicators of GUI.

        Returns
        -------
        None.

        """
        
        try:
            if self.RvalueSet == True:
                self.x = self.Temperature_Acquisition()          # Data acquisition of all variables
                self.two.SetValue(str(self.x[0])[:6])            # Updates the measured temperature
                self.four.SetValue(str(self.x[3])[:6])           # Updates the measured resistance
                self.five.SetValue(str(self.measured_power)[:6]) # Updates the measured power
        except TypeError:
            pass

    def SetResistance(self, e):
        """
        Temperature set point is retreived from the GUI and is converterd to Resistance with the function R=R0*(1+A*T+B*T*T)
        and the new resistance set point is written to the sample heater module

        Parameters
        ----------
        e : Event
            Button press event to set the setpoint of temperature.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """

        if not self.paused:
            try:
                temp = self.one.GetValue()
                Rset = str(self.R0*(1+self.A*temp+self.B*temp*temp))
                set_rset = mmis.Functions.SETTransactions(0X03, Rset , self.chipselect, self.interruptpin)
                time.sleep(0.1)
                self.GetSetResistanceSetValue()

            except AttributeError as e:
                print (e)
                message = "Please first calibrate for R0 in Settings Tab"
                dialog = wx.MessageDialog(self, message, caption="Error", style=wx.OK|wx.CENTRE)
                if dialog.ShowModal() == wx.ID_OK:
                    dialog.Destroy()
                    return
                dialog.Destroy()
                
            try:
                self.UEfile = self.mc.get("UE")
                f = open(self.UEfile, "a")
                f.write(str(datetime.now()) + "," + "SH" + "," + "Temp-Control Set Temperature" + "," + str(temp) + "\n")
                f.close()
            except TypeError:
                pass
            
    def GetSetResistanceSetValue(self):
        """
        To request the set value of temperature back from the sample heater module

        Returns
        -------
        None.
        
        Raised:
        -------    
        ValueError: Error raised when a proper value is not received back

        """
        Rset = mmis.Functions.GETTransactions(0X04, self.chipselect, self.interruptpin)
        Rset = Rset.Float.Float[0]
        if self.B == 0:
                #Temperature_Data = ((Resistance_Data-self.R0)/self.B)
                Temperature_Data = ((Rset/self.R0)-1)/self.A # according to standard formula
        else:
            try:
                #quad = math.sqrt((math.pow(self.B,2)-4*(self.R0-Resistance_Data)*self.A))
                quad = math.sqrt((math.pow(self.A,2)-4*self.B*(1-(Rset/self.R0)))) 
                if quad >= 0:
                    Temperature_Data = (-self.A+quad)/(2*self.B)
                else:
                    if -quad > 0:
                        Temperature_Data = (-self.A-quad)/(2*self.B)
                    else:
                        Temperature_Data = 0
            except ValueError:
                Temperature_Data = 0
        #print (Temperature_Data)
        self.button6.SetLabel("Set(\u00b0C)\n"+str(round(Temperature_Data,3)).center(5))
        self.button6.SetFont(self.font3)
        

    def SetPower(self, e):
        """
        Sets the power setpoint to the sample heater module control

        Parameters
        ----------
        e : Event
            Button Press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        if not self.paused_P:
            self.set_power = self.six.GetValue()
            self.current_power = self.measured_power
            try:
                self.UEfile = self.mc.get("UE")
                f = open(self.UEfile, "a")
                f.write(str(datetime.now()) + "," + "SH" + "," + "Power-Control Set Power" + "," + str(self.set_power) + "\n")
                f.close()
            except TypeError:
                pass

    def SetRampRate(self, e):
        """
        Sets the ramp rate to the sample heater module control

        Parameters
        ----------
        e : Event
            Button Press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        self.set_ramp = self.seven.GetValue()/4.0
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Ramp-Control Set RampRate" + "," + str(self.seven.GetValue()) + "\n")
            f.close()
        except TypeError:
            pass

    def SetFinalTemperature(self, e):
        """
        Sets the Final temperature setpoint to the sample heater module in ramp control

        Parameters
        ----------
        e : Event
            Button Press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        self.final_temperature = self.eight.GetValue()
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "SH" + "," + "Ramp-Control Set Temperature" + "," + str(self.final_temperature) + "\n")
            f.close()
        except TypeError:
            pass
        
    def ramp_control(self, e):
        """
        Logic for the ramp control of the sample heater

        Parameters
        ----------
        e : event
            Timer event for ramp control.

        Returns
        -------
        None.

        """
        if (self.set_ramp > 0 and self.final_temperature > self.init_ramp_temp):
            self.init_ramp_temp = self.init_ramp_temp + self.set_ramp
            if (self.init_ramp_temp <= self.final_temperature):
                self.New_SetResistance(self.init_ramp_temp)
            else:
                self.New_SetResistance(self.final_temperature)
                self.init_ramp_temp = self.init_ramp_temp - self.set_ramp
        elif (self.set_ramp < 0 and self.final_temperature < self.init_ramp_temp):
            self.init_ramp_temp = self.init_ramp_temp + self.set_ramp
            if (self.init_ramp_temp >= self.final_temperature):
                self.New_SetResistance(self.init_ramp_temp)
            else:
                self.New_SetResistance(self.final_temperature)
                self.init_ramp_temp = self.init_ramp_temp + self.set_ramp
        
    def New_SetResistance(self, temp):
        """
        Temperature set point is retreived from the GUI and is converterd to Resistance with the function R=R0*(1+A*T+B*T*T)
        and the new resistance set point is written to the sample heater module in the temperature profile/power profile/ramp control

        Parameters
        ----------
        temp : Float
            New temperature setpoint.

        Returns
        -------
        None.
        
        Raised:
        -------    
        AttributeError: Error raised when R0 value is not calibrated

        """
        
        try:
            Rset = str(self.R0*(1+self.A*temp+self.B*temp*temp))
            set_rset = mmis.Functions.SETTransactions(0X03, Rset , self.chipselect, self.interruptpin)
        except AttributeError:
            message = "Please first calibrate for R0 in Settings Tab"
            dialog = wx.MessageDialog(self, message, caption="Error", style=wx.OK|wx.CENTRE)
            if dialog.ShowModal() == wx.ID_OK:
                dialog.Destroy()
                return
            dialog.Destroy()


    def PID(self, e):
        """
        PID control for the power setpoint control and power profile control 

        Parameters
        ----------
        e : event
            Timer event.

        Returns
        -------
        None.

        """
        error = self.set_power - self.measured_power
        self.P_value = self.Kp*error
        self.Integrator = self.Integrator+error
        #print (self.Integrator)
        if self.Integrator > 1000: self.Integrator = 1000
        elif self.Integrator < -1000: self.Integrator = -1000
        self.I_value = self.Integrator*self.Ki
        PID = self.P_value+self.I_value
        if PID<20: PID=20.0
        #if not self.paused_P:
        self.New_SetResistance(PID)

    def slope_control(self, e):
        """
        Temperature profile control logic. Dialogue box is popped upon the completion of the temperature profile. 

        Parameters
        ----------
        e : event
            Timer event.

        Returns
        -------
        None.

        """
        self.Count_Seconds = self.Count_Seconds+1
        if (self.Count_Seconds > 1):    # This loop executes from the second time
            self.New_SetResistance(self.init_temp)
            if ((self.Count_Seconds-2) == self.Times[self.count_setpoint]):
                self.New_SetResistance(self.SetPoints[self.count_setpoint])
                self.init_temp = self.SetPoints[self.count_setpoint]
                self.count_setpoint = self.count_setpoint+1
                if (self.count_setpoint == len(self.SetPoints)):
                    self.slope = 0
                    self.Generate_stop_Sctrl_Event()
                    box = wx.MessageDialog(self, 'Temperature Profile Completed', 'Finished', wx.OK)
                    answer = box.ShowModal()
                    box.Destroy()
                    self.count_setpoint = self.count_setpoint - 1
                else:
                    self.slope = self.Slopes[self.count_setpoint]
                
            self.init_temp = self.init_temp+self.slope
            
        else:                           # This loop only executes one time when the profile control is started
            self.init_temp = self.x[0]  # initial temperature
            self.count_setpoint = 0     # keeps track of the setpoints index
            self.slope = self.Slopes[0] # initializes with the first Slope value

    def Power_Profile_control(self, e):
        """
        Power profile control logic. Dialogue box is popped upon the completion of the Power profile. 

        Parameters
        ----------
        e : event
            Timer event.

        Returns
        -------
        None.

        """
        self.Count_Seconds_PP = self.Count_Seconds_PP+1
        if (self.Count_Seconds_PP > 1):
            #self.Integrator = self.measured_power/self.Ki
            self.set_power = self.init_power_PP
            self.current_power = self.measured_power
            if ((self.Count_Seconds_PP-2) == self.Times_PP[self.count_setpoint_PP]):
                self.set_power = self.SetPoints_PP[self.count_setpoint_PP]
                self.current_power = self.measured_power
                self.init_power_PP = self.SetPoints_PP[self.count_setpoint_PP]
                self.count_setpoint_PP = self.count_setpoint_PP+1
                if (self.count_setpoint_PP == len(self.SetPoints_PP)):
                    self.slope_PP = 0
                    self.Generate_stop_PPctrl_Event()
                    box = wx.MessageDialog(self, 'Power Profile Completed', 'Finished', wx.OK)
                    answer = box.ShowModal()
                    box.Destroy()
                    self.count_setpoint_PP = self.count_setpoint_PP - 1
                else:
                    self.slope_PP = self.Slopes_PP[self.count_setpoint_PP]
                
            self.init_power_PP = self.init_power_PP+self.slope_PP
        else:
            self.init_power_PP = self.measured_power
            self.count_setpoint_PP = 0
            self.slope_PP = self.Slopes_PP[0]

    def OnSave(self,e):
        """
        This function allows to get the screenshot of the live graph runnning on GUI. Currently this function is
        disabled on the GUI due to space constraints

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """

        file_choices = "PNG (*.png)|*.png"
        dlg = wx.FileDialog(
            self,
            message = "Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.FD_SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi = 200)
        
    def OnClose(self):
        """
        Destroys all the events subjected to the Sample heater class

        Returns
        -------
        None.

        """
        self.Destroy()
