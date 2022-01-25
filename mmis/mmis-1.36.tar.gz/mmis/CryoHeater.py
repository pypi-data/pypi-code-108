import wx
import math
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
from wx.lib import masked
from wx.lib.masked import NumCtrl
import wx.lib.agw.floatspin as FS
import random
import sys
import pprint
import pylab
import RPi.GPIO as GPIO
import mmis.Functions
from datetime import datetime
import math
import memcache
import distro

class SubWindow(wx.Frame):
    def __init__(self, parent, id, variable):
        """
        Plots the histogram from the temperature data received from Cryo heater module

        Parameters
        ----------
        parent : Wx
            elements from wx library.
        id : uint
            Unique id given to a subwindow.
        variable : float32
            List of floats.

        Returns
        -------
        None.

        """
        wx.Frame.__init__(self,parent,wx.ID_ANY,title="Histogram",size=(400,400),style=wx.DEFAULT_FRAME_STYLE|wx.FULL_REPAINT_ON_RESIZE)
        self.data_hist= variable
        self.init_plot()
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.SetBackgroundColour(wx.Colour(100,100,100))
        self.Centre()
        self.Show()

    def init_plot(self):
        """
        Initializes the histogram plot with all the necessary settings

        Returns
        -------
        None.
        
        Raised:
        -------    
        ValueError: Error raised when the data is not available

        """
        try:
            self.dpi=60
            self.fig = Figure((5.0,5.1), dpi=self.dpi)
            self.axes = self.fig.add_subplot(111)
            self.axes.set_facecolor('black')
            self.axes.set_title('Histogram Plot', size = 15)
            self.axes.set_xlabel('bins', size = 12)
            self.axes.set_ylabel('occurance', size = 12)
            n = len(self.data_hist)
            Range = max(self.data_hist)-min(self.data_hist)
            interval = math.sqrt(n)
            width = int(Range/interval)

            self.plot_data = self.axes.hist(
                self.data_hist, bins=10,
                linewidth=1,
                color=(1,1,0),
                )[0]
            
        except ValueError:
            self.lblname1 = wx.StaticText(self, label = "No data available", pos = (20,330))
            self.lblname1.SetForegroundColour('white')

class Settings(wx.Panel):
    
    def __init__(self, parent, Module, pubsub1, pubsub2):
        """
        Contains all the Settings graphical elements present on the GUI of Cryo Heater Module

        Parameters
        ----------
        parent : Wx
            notebook element from wx library GUI.
        Module : [uint8, uint8]
            list contains chip select gpio and interrupt gpio.
        pubsub1 : String
            Not used in this module
        pubsub2 : String
            Not used in this module

        Returns
        -------
        None.

        """

        wx.Panel.__init__(self, parent = parent)

        self.chipselect = Module[0]
        self.interruptpin = Module[1]
        self.Kp_Data_Amb = 0
        self.Ki_Data_Amb = 0
        self.Kd_Data_Amb = 0

        self.paused = True
        self.pubsubname = pubsub1
        self.pubsubalarm = pubsub2
        self.mc = memcache.Client([('127.0.0.1', 11211)])
        
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        self.lblname1 = wx.StaticText(self, label = "PID Settings:", pos = (40,30))
        self.lblname2 = wx.StaticText(self, label = "Kp :", pos = (150,30))
        self.SET_Kp_Amb = wx.SpinCtrlDouble(self, size=(170,-1), min =-400, max = 800, inc = 0.1, value='8.00', pos = (180,25))
        self.SET_Kp_Amb.SetDigits(5)
        self.SET_Kp_Amb.SetBackgroundColour('white')

        self.lblname3 = wx.StaticText(self, label = "Ki :", pos = (360,30))
        self.SET_Ki_Amb = wx.SpinCtrlDouble(self, size=(170,-1), min = 0, max = 800, inc = 0.1, value='8.00', pos = (390,25))
        self.SET_Ki_Amb.SetDigits(5)
        self.SET_Ki_Amb.SetBackgroundColour('white')

        self.lblname4 = wx.StaticText(self, label = "Kd :", pos = (360,80))
        self.SET_Kd_Amb = wx.SpinCtrlDouble(self, size=(170,-1), min = 0, max = 800, inc = 0.1, value='0.00', pos = (390,75))
        self.SET_Kd_Amb.SetDigits(5)
        self.SET_Kd_Amb.SetBackgroundColour('white')

        self.button1 = wx.Button(self, label="Set", pos=(580, 50), size = (100,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TAMB_Params, self.button1)
        self.button1.SetForegroundColour('black')
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname7 = wx.StaticText(self, label = "Module Information :", pos = (40,160))
        self.Info = wx.TextCtrl(self, size=(200,100), pos = (220,130), style = wx.TE_LEFT|wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2)
        self.Info.SetFont(self.font2)

        self.button5 = wx.Button(self, label="Get Info", pos=(450, 160), size = (200,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_GET_INFO,self.button5)
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour(wx.Colour(211,211,211))

        self.button3 = wx.Button(self, label="Software Reset", pos=(40, 245), size = (200,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_SOFT_RESET,self.button3)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour(wx.Colour(211,211,211))

        self.button4 = wx.Button(self, label="Alarm Reset", pos=(290, 245), size = (200,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_ALARM_RESET,self.button4)
        self.button4.SetForegroundColour('black')
        self.button4.SetBackgroundColour(wx.Colour(211,211,211))

        self.Generate_Get_Info_Event()
        self.SET_Kp_Amb.SetValue(str(self.Kp_Data_Amb))
        self.SET_Ki_Amb.SetValue(str(self.Ki_Data_Amb))
        self.SET_Kd_Amb.SetValue(str(self.Kd_Data_Amb))
        

        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.button4.SetFont(self.font2)
            self.button3.SetFont(self.font2)
            self.button5.SetFont(self.font2)
            self.lblname7.SetFont(self.font2)
            self.button1.SetFont(self.font2)
            self.lblname3.SetFont(self.font2)
            self.lblname2.SetFont(self.font2)
            self.lblname1.SetFont(self.font2)

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

    def Generate_Get_Info_Event(self):
        """
        Programmatically generates the Get info event

        Returns
        -------
        None.

        """
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button5)
        evt.SetId(self.button5.GetId())
        self.button5.GetEventHandler().ProcessEvent(evt)

    def ON_GET_INFO(self, e):
        """
        Retrieves all the Kp, Ki, Kd values set for the cryo heater control

        Parameters
        ----------
        e : event
            Button Press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        self.Info.Clear()
        name = mmis.Functions.GETTransactions(0X0C, self.chipselect, self.interruptpin)
        Version = mmis.Functions.GETTransactions(0X0D, self.chipselect, self.interruptpin)
        Kp_Amb = mmis.Functions.GETTransactions(0X12, self.chipselect, self.interruptpin)
        self.Kp_Data_Amb =  round(Kp_Amb.Float.Float[0],8)
        Ki_Amb = mmis.Functions.GETTransactions(0X13, self.chipselect, self.interruptpin)
        self.Ki_Data_Amb =  round(Ki_Amb.Float.Float[0],8)
        Kd_Amb = mmis.Functions.GETTransactions(0X1D, self.chipselect, self.interruptpin)
        self.Kd_Data_Amb =  round(Kd_Amb.Float.Float[0],8)
        #self.Kd_Data_Amb = 0
        
        self.Info.SetDefaultStyle(wx.TextAttr(wx.BLUE))
        self.Info.AppendText(name.String + '- V' + Version.Version + '\n')
        self.Info.AppendText('Kp' + ' = ' + str(self.Kp_Data_Amb)[:8] + '\n')
        self.Info.AppendText('Ki' + ' = ' + str(self.Ki_Data_Amb)[:8] + '\n')
        self.Info.AppendText('Kd' + ' = ' + str(self.Kd_Data_Amb)[:8])

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "CH" + "," + "Get Kp" + "," + str(self.Kp_Data_Amb) + "\n")
            f.write(str(datetime.now()) + "," + "CH" + "," + "Get Ki" + "," + str(self.Ki_Data_Amb) + "\n")
            f.write(str(datetime.now()) + "," + "CH" + "," + "Get Kd" + "," + str(self.Kd_Data_Amb) + "\n")
            f.close()
        except TypeError:
            pass

    def ON_SET_TAMB_Params(self, e):
        """
        Sets the Kp, Ki and Kd Constants for cryo heater control module

        Parameters
        ----------
        e : event
            Button Press event.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        Ki_Amb = str(self.SET_Ki_Amb.GetValue())
        Kp_Amb = str(self.SET_Kp_Amb.GetValue())
        Kd_Amb = str(self.SET_Kd_Amb.GetValue())
        set_Ki_Amb = mmis.Functions.SETTransactions(0X11, Ki_Amb , self.chipselect, self.interruptpin)
        time.sleep(0.5)
        set_Kp_Amb = mmis.Functions.SETTransactions(0X10, Kp_Amb , self.chipselect, self.interruptpin)
        time.sleep(0.5)
        set_Kd_Amb = mmis.Functions.SETTransactions(0X1C, Kd_Amb , self.chipselect, self.interruptpin)
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "CH" + "," + "Set Kp" + "," + Kp_Amb + "\n")
            f.write(str(datetime.now()) + "," + "CH" + "," + "Set Ki" + "," + Ki_Amb + "\n")
            f.write(str(datetime.now()) + "," + "CH" + "," + "Set Kd" + "," + Kd_Amb + "\n")
            f.close()
        except TypeError:
            pass

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
        To request the version number of the firmware programmed in the Cryo Heater module

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
        Resets the firmware of the Cryo Heater module.

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
            f.write(str(datetime.now()) + "," + "DH" + "," + "Software Reset" + "," + "1" + "\n")
            f.close()
        except TypeError:
            pass
            
    def ON_ALARM_RESET(self, e):
        """
        Resets all the alarms raised from the Cryo Heater module.

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
            f.write(str(datetime.now()) + "," + "DH" + "," + "Alarm Reset" + "," + "1" + "\n")
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
        Initializes all the control graphical user elements of the cryo heater module

        Parameters
        ----------
        parent : notebook element (wx.nb)
            notebook element from wx library GUI.
        Module : [uint8, uint8]
            list contains chip select gpio and interrupt gpio.
        pubsub1 : string
            it is subscribed get values from settings module of Cryo heater but currently not used.
        pubsub2 : string
            All the logging data and alarm details from this controls module are communicated to the main GUI over this publicataion/subscription.

        Returns
        -------
        None.

        """
        
        wx.Panel.__init__(self, parent = parent)

        """ SPI Communication port open"""
        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        """ Initialize publishers and subscribers"""
        pub.subscribe(self.OnBvalue, pubsub1) #pubsub1 is used to get the data from settings window/other windows within Dualheater
        self.pubsub_logdata = pubsub2         #pubsub2 is used to send the data from current dualheater window to main GUI window for logging  
        self.mc = memcache.Client([('127.0.0.1', 11211)])
        
        """ Initilize the lists to store the temperature data """
        self.data1 = []                       #data1 list stores all the data regarding ambient temperature control
        self.paused_Amb = True                #At start up data generation event is paused until user starts it
        
        self.A_PTC = 3.9083*math.pow(10,-3)   #Constants to convert the signal to temperature for N2
        self.B_PTC = -5.775*math.pow(10,-7)   #Constants to convert the signal to temperaturefor N2 as well
        
        """ Creating a Timer for updating the Frame rate of the real time graph displayed"""
        self.redraw_graph_timer1 = wx.Timer(self)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer1, self.redraw_graph_timer1)  

        self.get_data_timer1 = wx.Timer(self)          # this timer controls the sampling rate of the data for plotting on the graph 
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer1, self.get_data_timer1)
            
        self.get_read_timer = wx.Timer(self)          # this timer controls the sampling rate of the data immediately when machine is turned on and keeps showing data on the indicators
        self.Bind(wx.EVT_TIMER, self.on_get_read_timer, self.get_read_timer)
        self.get_read_timer.Start(100)
        
        """ Initializing the graph plot to display the temperatures"""
        self.init_plot1()
        self.canvas1 = FigureCanvas(self, -1, self.fig1)
        self.Xticks1 = 400                      #default initialized to plot 400 data points on the xaxis
        self.Yticks1 = 1                        #default initialized to plot +or-1 of actual value

        """GRID and Font created"""
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font3 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
    
        # Check box - to Show/delete the grid
        self.cb_grid1 = wx.CheckBox(self, -1, "Show Grid", style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid1, self.cb_grid1)
        self.cb_grid1.SetValue(True)

        self.lblname3 = wx.StaticText(self, label = "X-Scale")
        self.grid.Add(self.lblname3, pos = (1,0))
        self.three = wx.TextCtrl(self, id = 6, size = (60,30), style = wx.TE_PROCESS_ENTER)
        self.three.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength1)
        self.three.SetBackgroundColour('white')
        self.grid.Add(self.three, pos=(1,1))

        self.lblname11 = wx.StaticText(self, label = "Y-Scale")
        self.grid.Add(self.lblname11, pos = (21,0))
        self.eleven = wx.TextCtrl(self, id = 80, size = (60,30), style = wx.TE_PROCESS_ENTER)
        self.eleven.Bind(wx.EVT_TEXT_ENTER, self.OnSetYLabelLength1)
        self.eleven.SetBackgroundColour('white')
        self.grid.Add(self.eleven, pos=(21,1))

        self.button1 = wx.Button(self, label = 'Plot Hist', size = (90, 25), id =121)
        self.button1.Bind(wx.EVT_BUTTON, self.OnGetHistogram1)             
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        """Create Buttons and other and Bind their events"""
        self.button5 = wx.Button(self, label = 'Start', size = (70, 30), id =12) #Stop/Start button - Data Acquisition
        self.button5.Bind(wx.EVT_BUTTON, self.on_pause_button_Amb)             #this event changes the state of self.paused
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('light green')

        self.button6 = wx.Button(self, label = 'Set', size = (75,40), id=5)    # Static text and num control box -  to set the value of temperature
        self.button6.Bind(wx.EVT_BUTTON, self.SetAmbientTemperature)
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))
        self.one = wx.SpinCtrlDouble(self, size=(140,-1), min =-400, max = 800, inc = 0.1, value='25')
        self.one.SetBackgroundColour('white')
        self.one.SetDigits(3)
        
        self.lblname2 = wx.StaticText(self, label = "Temperature(\u00b0C)")                   # Static text and text control box - to display the current value of temperature
        self.grid.Add(self.lblname2, pos = (0,0))
        self.two = wx.TextCtrl(self, id = 40, size=(125,35), style = wx.TE_READONLY)
        self.two.SetBackgroundColour('grey')
        self.grid.Add(self.two, pos=(0,1))

        self.lblname6 = wx.StaticText(self, label = "Current(mA)")
        self.grid.Add(self.lblname6, pos = (4,0))
        self.six = wx.TextCtrl(self, id = 42, size=(130,35), style = wx.TE_READONLY)
        self.six.SetBackgroundColour('grey')
        self.grid.Add(self.six, pos=(4,1))

        self.lblname8 = wx.StaticText(self, label = "Power(mW)")
        self.grid.Add(self.lblname8, pos = (5,0))
        self.eight = wx.TextCtrl(self, id = 44, size=(130,35), style = wx.TE_READONLY)
        self.eight.SetBackgroundColour('grey')
        self.grid.Add(self.eight, pos=(5,1))

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.one, border=2, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button6, border=2, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button5, border=2, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.lblname2, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.Add(self.two, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.lblname6, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(25)
        self.hbox4.Add(self.six, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.lblname8, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.AddSpacer(32)
        self.hbox5.Add(self.eight, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.lblname3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.three, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.lblname11, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.eleven, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox12.Add(self.cb_grid1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox12.Add(self.button1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.vbox = wx.BoxSizer(wx.VERTICAL)      
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox6, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox12, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas1, 3, flag=wx.LEFT | wx.TOP , border = 5)
        self.hbox.Add(self.vbox, 1.8, flag=wx.LEFT | wx.TOP )  
        
        self.SetSizer(self.hbox)
        self.hbox.Fit(self)
        
        self.GetAmbientTemperatureSetValue()

        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.button6.SetFont(self.font3)
            self.lblname1.SetFont(self.font2)
            self.three.SetFont(self.font2)
            self.eleven.SetFont(self.font2)
            self.button1.SetFont(self.font2)
            self.button5.SetFont(self.font2)
            self.two.SetFont(self.font1)
            self.lblname6.SetFont(self.font2)
            self.six.SetFont(self.font1)
            self.lblname8.SetFont(self.font2)
            self.eight.SetFont(self.font1)
            self.seven.SetFont(self.font1)
            self.lblname2.SetFont(self.font2)

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
            
    
    def OnBvalue(self, value1, value2): 
        """
        This function is currently not used. This funtion can retrieve data from other windows.

        Parameters
        ----------
        value1 : Anything
            DESCRIPTION.
        value2 : Anything
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.A = value1
        self.B = value2
        self.Refresh()
    
    def Temperature_Acquisition(self):
        """
        Data Acquisition of the resistance, voltage and current is requested from cryo heater module.
        Further the resistance is converted to Temperature

        Returns
        -------
        Temp : list of [Temperature, Voltage, Current] float
            list of all the  values described above.
            
        Raised:
        -------    
        AttributeError: simply passed
        ZeroDivisionError:
        ValueError:    

        """
        Temp = np.zeros(3)
        ADC_Amb = mmis.Functions.GETTransactions(0X19, self.chipselect, self.interruptpin)
        Voltage_Amb = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        Current_Amb = mmis.Functions.GETTransactions(0X08, self.chipselect, self.interruptpin)
        self.Alarm = ADC_Amb.Alarm
        try:
            ADC_Data_Amb =  ADC_Amb.Float.Float[0]
            Voltage_Data_Amb =  12.0 - 3.637*Voltage_Amb.Float.Float[0]*3.300/1024.0
            Current_Data_Amb =  Current_Amb.Float.Float[0]*1000/1024.0
        except AttributeError:
            ADC_Data_Amb = 0
            Voltage_Data_Amb = 0
            Current_Data_Amb = 0
        try:
            Resistance_Amb = ((ADC_Data_Amb-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_Amb))*10000
        except ZeroDivisionError:
            Resistance_Amb = 0
     
        if Voltage_Data_Amb < 0:
            Voltage_Data_Amb = 0
            
        try:
            Temperature_Amb = 3435.0/(math.log(Resistance_Amb/0.09919119)) - 273.0
        except ValueError:
            Temperature_Amb = -9999.0
            
        Temp[0] = Temperature_Amb
        Temp[1] = Voltage_Data_Amb
        Temp[2] = Current_Data_Amb
        pub.sendMessage(self.pubsub_logdata, data = Temp, alarm = self.Alarm)
        return Temp

    def init_plot1(self):
        """
        The settings for the plot are initialized

        Returns
        -------
        None.

        """

        self.dpi = 60
        self.fig1 = Figure((5.0, 5.1), dpi = self.dpi)

        self.axes = self.fig1.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Cryo Heater Temperature Control', size = 15)
        self.axes.set_xlabel('Samples(past 2 mins)', size = 15)
        self.axes.set_ylabel('Sample Temperature (C)', color = 'red', size=12)

        pylab.setp(self.axes.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes.get_yticklabels(), fontsize=12, color = 'red')
        
        self.plot_data1 = self.axes.plot(
            self.data1,
            linewidth=1.5,
            color='red',
            )[0]

    def draw_plot1(self):
        """
        Draws the plot every one second with the updated measurements. 

        Returns
        -------
        None.

        """
        xmax = len(self.data1) if len(self.data1) > 400 else 400           
        xmin = xmax - self.Xticks1

        ymin1 = round(min(self.data1[(-self.Xticks1):]), 4) - self.Yticks1
        ymax1 = round(max(self.data1[(-self.Xticks1):]), 4) + self.Yticks1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin1, upper=ymax1)
        self.axes.grid(True, color='gray')

        if self.cb_grid1.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)
        
        pylab.setp(self.axes.get_xticklabels(), 
            visible=False)
        
        self.plot_data1.set_xdata(np.arange(len(self.data1)))
        self.plot_data1.set_ydata(np.array(self.data1))
        
        self.canvas1.draw()

    def OnSetXLabelLength1(self, e):
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
        self.Xticks1 = int(Xtks.encode())
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "X label Amb Temp" + "," + str(Xtks) + "\n")
            f.close()
        except TypeError:
            pass

    def OnSetYLabelLength1(self, e):
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
        self.Yticks1 = float(Ytks.encode())
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Y label Amb Temp" + "," + str(Ytks) + "\n")
            f.close()
        except TypeError:
            pass

    def on_cb_grid1(self, event):
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
        self.draw_plot1()

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
        self.draw_plot1()

    def on_pause_button_Amb(self, e):
        """
        Sends ON and OFF commands to the Cryo heater module to Control the temperature. 

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
        self.paused_Amb = not self.paused_Amb
        
        if self.paused_Amb:
            label = "Start"
            color = "light green"
            self.redraw_graph_timer1.Stop()
            self.get_data_timer1.Stop()
            mmis.Functions.GETTransactions(0X03, self.chipselect, self.interruptpin)
            status = "stop"
        else:
            label = "Stop"
            color = "red"
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer1.Start(1000)
            self.get_data_timer1.Start(250)
            status = "start"

        self.button5.SetLabel(label)
        self.button5.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Ambient Control" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def on_redraw_graph_timer1(self, e):
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
        self.draw_plot1()

    def on_get_data_timer1(self, e):
        """
        The interrupt is generated every 200ms when start control (data_timer) gets a start. Total data points to be stored in buffer
        is limited to 400 and beyond that based on FIFO the data gets cleared.

        Parameters
        ----------
        e : Event
            Data retreive timer interrupt.

        Returns
        -------
        None.
        
        """
        if not self.paused_Amb: 
            if len(self.data1)<400:
                self.data1.append(self.x[0])
            else:
                del self.data1[0]
                self.data1.append(self.x[0])

    def on_get_read_timer(self, e):
        """
        The interrupt is generated every few milliseconds by read_timer interrupt to update the values of Temperature, Current and Voltage
        onto the control window of GUI. 

        Parameters
        ----------
        e : event
            Timer event to update the values to the indicators of GUI.

        Returns
        -------
        None.

        """
        self.x = self.Temperature_Acquisition()
        self.two.SetValue(str(self.x[0])[:7])  # Temperature Ambient
        self.six.SetValue(str(round(self.x[2], 0))) # Current Ambient
        self.eight.SetValue(str(round(self.x[2] * self.x[1], 0)))

    def SetAmbientTemperature(self, e):
        """
        Sets the Ambient temperature setpoint to the cryo heater module

        Parameters
        ----------
        e : event
            button press event.

        Returns
        -------
        None.

        """
        temp = self.one.GetValue()+273.0
        Rset = 10000*math.exp(-3435*((1/298.15)-(1/temp)))
        ADC = str(round(math.pow(2,15)*(1.5 - (Rset/(10000+Rset))),0))
        set_Tamb = mmis.Functions.SETTransactions(0X05, ADC , self.chipselect, self.interruptpin)
        self.GetAmbientTemperatureSetValue()
        
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Set Amb Temp" + "," + str(temp-273) + "\n")
            f.close()
        except TypeError:
            pass
        
    def GetAmbientTemperatureSetValue(self):
        """
        Requests the set value of ambient temperature from the cryo heater module

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file
        ValueError:

        """
        ADC_Amb = mmis.Functions.GETTransactions(0X1A, self.chipselect, self.interruptpin)
        ADC_Data_Amb =  ADC_Amb.Float.Float[0]
        Resistance_Amb = ((ADC_Data_Amb-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_Amb))*10000

        try:
            Temperature_Amb = 3435.0/(math.log(Resistance_Amb/0.09919119)) - 273.0
        except ValueError:
            Temperature_Amb = -999.0
        self.button6.SetLabel("Set Temp\n"+str(round(Temperature_Amb,2)).center(5))
        self.button6.SetFont(self.font3)
        self.one.SetValue(round(Temperature_Amb,3))

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Get Amb Temp" + "," + str(Temperature_Amb) + "\n")
            f.close()
        except TypeError:
            pass

    def OnGetHistogram1(self,e):
        """
        Opens a histogram plot of the data in a new window

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        SubWindow(None, -1, self.data1).Show()
    
    def OnClose(self):
        """
        Destroys all the events subjected to the Cryo heater class

        Returns
        -------
        None.

        """
        self.Destroy()
