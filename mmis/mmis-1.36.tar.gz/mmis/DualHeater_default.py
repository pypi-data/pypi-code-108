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
        Plots the histogram from the temperature data received from Dual heater module

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
        Contains all the Settings graphical elements present on the GUI of Dual Heater Module

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

        self.paused = True
        self.pubsubname = pubsub1
        self.pubsubalarm = pubsub2
        self.mc = memcache.Client([('127.0.0.1', 11211)])

        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        self.lblname1 = wx.StaticText(self, label = "Ambient Control :", pos = (40,30))
        
        
        self.lblname2 = wx.StaticText(self, label = "Kp :", pos = (220,30))
        
        #self.SET_Kp_Amb = NumCtrl(self, id = -1, value = 8.00,integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (250,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Kp_Amb = wx.SpinCtrlDouble(self, size=(170,-1), min =-400, max = 800, inc = 0.1, value='8.00', pos = (250,25))
        self.SET_Kp_Amb.SetDigits(5)
        self.SET_Kp_Amb.SetBackgroundColour('white')
        ################
        self.Kp_Data_Amb = 0
        self.Ki_Data_Amb = 0
        self.Kp_Data_N2 = 0
        self.Ki_Data_N2 = 0
        ################

        self.lblname3 = wx.StaticText(self, label = "Ki :", pos = (430,30))
        #self.SET_Ki_Amb = NumCtrl(self, id = -1, value = 0.0099,integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (460,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Ki_Amb = wx.SpinCtrlDouble(self, size=(170,-1), min = 0, max = 800, inc = 0.1, value='8.00', pos = (460,25))
        self.SET_Ki_Amb.SetDigits(5)
        self.SET_Ki_Amb.SetBackgroundColour('white')

        self.button1 = wx.Button(self, label="Set", pos=(650, 25), size = (100,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TAMB_Params, self.button1)
        self.button1.SetForegroundColour('black')
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname4 = wx.StaticText(self, label = "Nitrogen Control :", pos = (40,85))

        self.lblname5 = wx.StaticText(self, label = "Kp :", pos = (220,85))
        #self.SET_Kp_N2 = NumCtrl(self, id = -1, value = 16.00, integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (250,80), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Kp_N2 = wx.SpinCtrlDouble(self, size=(170,-1), min =-400, max = 800, inc = 0.1, value='8.00', pos = (250,80))
        self.SET_Kp_N2.SetDigits(5)
        self.SET_Kp_N2.SetBackgroundColour('white')

        self.lblname6 = wx.StaticText(self, label = "Ki :", pos = (430,85))
        #self.SET_Ki_N2 = NumCtrl(self, id = -1, value = 0.0099, integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(60,40), pos = (460,80), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Ki_N2 = wx.SpinCtrlDouble(self, size=(170,-1), min = 0, max = 800, inc = 0.1, value='8.00', pos = (460,80))
        self.SET_Ki_N2.SetDigits(5)
        self.SET_Ki_N2.SetBackgroundColour('white')

        self.button2 = wx.Button(self, label="Set", pos=(650, 80), size = (100,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TN2_Params,self.button2)
        self.button2.SetForegroundColour('black')
        self.button2.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname7 = wx.StaticText(self, label = "Module Information :", pos = (40,160))
        self.Info = wx.TextCtrl(self, size=(200,100), pos = (220,130), style = wx.TE_LEFT|wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2)
        #self.Info.SetBackgroundColour('black')
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
        self.SET_Kp_N2.SetValue(str(self.Kp_Data_N2))
        self.SET_Ki_N2.SetValue(str(self.Ki_Data_N2))

        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.button4.SetFont(self.font2)
            self.button3.SetFont(self.font2)
            self.button5.SetFont(self.font2)
            self.lblname7.SetFont(self.font2)
            self.button2.SetFont(self.font2)
            self.lblname6.SetFont(self.font2)
            self.lblname5.SetFont(self.font2)
            self.lblname4.SetFont(self.font2)
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
        Retrieves all the Kp and Ki values set for both the Dual heaters Amb and N2 control

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
        Kp_N2 = mmis.Functions.GETTransactions(0X16, self.chipselect, self.interruptpin)
        self.Kp_Data_N2 =  round(Kp_N2.Float.Float[0],8)
        Ki_N2 = mmis.Functions.GETTransactions(0X17, self.chipselect, self.interruptpin)
        self.Ki_Data_N2 =  round(Ki_N2.Float.Float[0],8)
        print (Ki_N2.Received)
        
        self.Info.SetDefaultStyle(wx.TextAttr(wx.BLUE))
        self.Info.AppendText(name.String + '- V' + Version.Version + '\n')
        self.Info.AppendText('Kp_Amb' + ' = ' + str(self.Kp_Data_Amb)[:8] + '\n')
        self.Info.AppendText('Ki_Amb' + ' = ' + str(self.Ki_Data_Amb)[:8] + '\n')
        self.Info.AppendText('Kp_N2' + ' = ' + str(self.Kp_Data_N2)[:8] + '\n')
        self.Info.AppendText('Ki_N2' + ' = ' + str(self.Ki_Data_N2)[:8])

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Get Amb Kp" + "," + str(self.Kp_Data_Amb) + "\n")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Get Amb Ki" + "," + str(self.Ki_Data_Amb) + "\n")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Get N2 Kp" + "," + str(self.Kp_Data_N2) + "\n")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Get N2 Ki" + "," + str(self.Ki_Data_N2) + "\n")
            f.close()
        except TypeError:
            pass

    def ON_SET_TAMB_Params(self, e):
        """
        Sets the Kp, Ki Constants for Dual heater ambient control

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
        set_Ki_Amb = mmis.Functions.SETTransactions(0X11, Ki_Amb , self.chipselect, self.interruptpin)
        time.sleep(0.5)
        set_Kp_Amb = mmis.Functions.SETTransactions(0X10, Kp_Amb , self.chipselect, self.interruptpin)
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Set Amb Kp" + "," + Kp_Amb + "\n")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Set Amb Ki" + "," + Ki_Amb + "\n")
            f.close()
        except TypeError:
            pass

    def ON_SET_TN2_Params(self, e):
        """
        Sets the Kp, Ki Constants for Dual heater N2 control

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
        Kp_N2 = str(self.SET_Kp_N2.GetValue())
        set_Kp_N2 = mmis.Functions.SETTransactions(0X14, Kp_N2 , self.chipselect, self.interruptpin)
        time.sleep(0.5)
        Ki_N2 = str(self.SET_Ki_N2.GetValue())
        set_Ki_N2 = mmis.Functions.SETTransactions(0X15, Ki_N2 , self.chipselect, self.interruptpin)
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Set N2 Kp" + "," + Kp_N2 + "\n")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Set N2 Ki" + "," + Ki_N2 + "\n")
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
        To request the version number of the firmware programmed in the Dual Heater module

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
        Resets the firmware of the Dual Heater module.

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
        Resets all the alarms raised from the Dual Heater module.

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
        Initializes all the control graphical user elements of the Dual heater module

        Parameters
        ----------
        parent : notebook element (wx.nb)
            notebook element from wx library GUI.
        Module : [uint8, uint8]
            list contains chip select gpio and interrupt gpio.
        pubsub1 : string
            it is subscribed get values from settings module of Dual heater but currently not used.
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
        self.data2 = []                       #data2 list stores all the data regarding N2 temperature control                          
        self.paused_Amb = True                #At start up data generation event is paused until user starts it
        self.paused_N2 = True                 #At start up data generation event is paused until user starts it 
        
        self.A_PTC = 3.9083*math.pow(10,-3)   #Constants to convert the signal to temperature for N2
        self.B_PTC = -5.775*math.pow(10,-7)   #Constants to convert the signal to temperaturefor N2 as well
        
        """ Creating a Timer for updating the Frame rate of the real time graph displayed"""
        self.redraw_graph_timer1 = wx.Timer(self)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer1, self.redraw_graph_timer1)  

        self.get_data_timer1 = wx.Timer(self)          # this timer controls the sampling rate of the data for plotting on the graph 
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer1, self.get_data_timer1)

        self.redraw_graph_timer2 = wx.Timer(self)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer2, self.redraw_graph_timer2)  

        self.get_data_timer2 = wx.Timer(self)          # this timer controls the sampling rate of the data for plotting on the graph 
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer2, self.get_data_timer2)
            
        self.get_read_timer = wx.Timer(self)          # this timer controls the sampling rate of the data immediately when machine is turned on and keeps showing data on the indicators
        self.Bind(wx.EVT_TIMER, self.on_get_read_timer, self.get_read_timer)
        self.get_read_timer.Start(100)
        
        """ Initializing the graph plot to display the temperatures"""
        self.init_plot1()
        self.init_plot2()
        self.canvas1 = FigureCanvas(self, -1, self.fig1)
        self.canvas2 = FigureCanvas(self, -1, self.fig2)
        self.Xticks1 = 400                      #default initialized to plot 400 data points on the xaxis
        self.Xticks2 = 400                      #default initialized to plot 400 data points on the xaxis
        self.Yticks1 = 1                        #default initialized to plot +or-1 of actual value
        self.Yticks2 = 1                        #default initialized to plot +or-1 of actual value

        """GRID and Font created"""
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font3 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        
        """Control Mode Selection Box"""
        self.lblname1 = wx.StaticText(self, label = "Control Mode:")
        self.Mode_Selection = ['Amb-Control', 'N2-Control']
        self.Combo1 = wx.ComboBox(self, choices = self.Mode_Selection, size = (140,-1))
        self.Combo1.Bind(wx.EVT_COMBOBOX, self.ON_SET_MODE)

        # Check box - to Show/delete the grid
        self.cb_grid1 = wx.CheckBox(self, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid1, self.cb_grid1)
        self.cb_grid1.SetValue(True)

        self.cb_grid2 = wx.CheckBox(self, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid2, self.cb_grid2)
        self.cb_grid2.SetValue(True)

        self.lblname3 = wx.StaticText(self, label = "X-Scale")
        self.grid.Add(self.lblname3, pos = (1,0))
        self.three = wx.TextCtrl(self, id = 6, size = (60,30), style = wx.TE_PROCESS_ENTER)
        self.three.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength1)
        self.three.SetBackgroundColour('white')
        self.grid.Add(self.three, pos=(1,1))

        self.lblname10 = wx.StaticText(self, label = "X-Scale")
        self.grid.Add(self.lblname10, pos = (10,0))
        self.ten = wx.TextCtrl(self, id = 69, size = (60,30), style = wx.TE_PROCESS_ENTER)
        self.ten.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength2)
        self.ten.SetBackgroundColour('white')
        self.grid.Add(self.ten, pos=(10,1))

        self.lblname11 = wx.StaticText(self, label = "Y-Scale")
        self.grid.Add(self.lblname11, pos = (21,0))
        self.eleven = wx.TextCtrl(self, id = 80, size = (60,30), style = wx.TE_PROCESS_ENTER)
        self.eleven.Bind(wx.EVT_TEXT_ENTER, self.OnSetYLabelLength1)
        self.eleven.SetBackgroundColour('white')
        self.grid.Add(self.eleven, pos=(21,1))

        self.lblname12 = wx.StaticText(self, label = "Y-Scale")
        self.grid.Add(self.lblname12, pos = (20,0))
        self.twelve = wx.TextCtrl(self, id = 79, size = (60,30), style = wx.TE_PROCESS_ENTER)
        self.twelve.Bind(wx.EVT_TEXT_ENTER, self.OnSetYLabelLength2)
        self.twelve.SetBackgroundColour('white')
        self.grid.Add(self.twelve, pos=(20,1))

        self.button1 = wx.Button(self, label = 'Plot Hist', size = (90, 25), id =121)
        self.button1.Bind(wx.EVT_BUTTON, self.OnGetHistogram1)             
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        self.button2 = wx.Button(self, label = 'Plot Hist', size = (90, 25), id =122)
        self.button2.Bind(wx.EVT_BUTTON, self.OnGetHistogram2)             
        self.button2.SetBackgroundColour(wx.Colour(211,211,211))

        """Create Buttons and other and Bind their events"""
        self.button5 = wx.Button(self, label = 'Start Amb', size = (70, 30), id =12) #Stop/Start button - Data Acquisition
        self.button5.Bind(wx.EVT_BUTTON, self.on_pause_button_Amb)             #this event changes the state of self.paused
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('light green')

        self.button6 = wx.Button(self, label = 'Set-Tamb', size = (75,40), id=5)    # Static text and num control box -  to set the value of temperature
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

        self.button10 = wx.Button(self, label = 'Start N2', size = (80, 30), id =67) #Stop/Start button - Data Acquisition
        self.button10.Bind(wx.EVT_BUTTON, self.on_pause_button_N2)             #this event changes the state of self.paused
        self.button10.SetForegroundColour('black')
        self.button10.SetBackgroundColour('light green')

        self.button9 = wx.Button(self, label = 'Set-TN2', size = (75,40), id=13)    # Static text and num control box -  to set the value of temperature
        self.button9.Bind(wx.EVT_BUTTON, self.SetNitrogenTemperature)
        self.button9.SetBackgroundColour(wx.Colour(211,211,211))
        self.four = wx.SpinCtrlDouble(self, size=(140,-1), min =-400, max = 800, inc = 0.1, value='180.001')
        self.four.SetDigits(3)  
        self.four.SetBackgroundColour('white')

        self.lblname5 = wx.StaticText(self, label = "Temperature(\u00b0C)")
        self.grid.Add(self.lblname5, pos = (2,0))
        self.lblname5.SetForegroundColour('purple')
        self.five = wx.TextCtrl(self, id = 41, size=(125,35), style = wx.TE_READONLY)
        self.five.SetBackgroundColour('grey')
        self.grid.Add(self.five, pos=(2,1))

        self.lblname7 = wx.StaticText(self, label = "Current(mA)")
        self.grid.Add(self.lblname7, pos = (3,0))
        self.lblname7.SetForegroundColour('purple')
        self.seven = wx.TextCtrl(self, id = 43, size=(130,35), style = wx.TE_READONLY)
        self.seven.SetBackgroundColour('grey')
        self.grid.Add(self.seven, pos=(3,1))

        self.lblname9 = wx.StaticText(self, label = "Power(mW)")
        self.grid.Add(self.lblname9, pos = (6,0))
        
        self.lblname9.SetForegroundColour('purple')
        self.nine = wx.TextCtrl(self, id = 45, size=(130,35), style = wx.TE_READONLY)
        self.nine.SetBackgroundColour('grey')
        self.grid.Add(self.nine, pos=(6,1))
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)     # Set all the buttons, check boxes and text controls in a BOX
        self.hbox1.Add(self.lblname1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(4)
        self.hbox1.Add(self.Combo1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.one, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

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

        self.hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox7.Add(self.four, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox7.Add(self.button9, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox7.Add(self.button10, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox8.Add(self.lblname5, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox8.Add(self.five, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox9.Add(self.lblname7, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox9.AddSpacer(25)
        self.hbox9.Add(self.seven, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox10.Add(self.lblname9, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox10.AddSpacer(32)
        self.hbox10.Add(self.nine, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox11.Add(self.lblname10, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox11.Add(self.ten, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox11.Add(self.lblname12, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox11.Add(self.twelve, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        

        self.hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox12.Add(self.cb_grid1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox12.Add(self.button1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox13 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox13.Add(self.cb_grid2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox13.Add(self.button2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)      
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox6, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox7, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox8, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox9, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox10, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox11, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox12, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox13, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas1, 3, flag=wx.LEFT | wx.TOP , border = 5)
        self.hbox.Add(self.canvas2, 3, flag=wx.LEFT | wx.TOP , border = 5)
        self.hbox.Add(self.vbox, 1.8, flag=wx.LEFT | wx.TOP )  
        
        self.SetSizer(self.hbox)
        self.hbox.Fit(self)
        self.hbox.Hide(1)
        self.vbox.Hide(1)
        self.vbox.Hide(2)
        self.vbox.Hide(3)
        self.vbox.Hide(4)
        self.vbox.Hide(5)
        self.vbox.Hide(6)
        self.vbox.Hide(7)
        self.vbox.Hide(8)
        self.vbox.Hide(9)
        self.vbox.Hide(10)
        self.vbox.Hide(11)
        self.vbox.Hide(12)
        self.GetAmbientTemperatureSetValue()
        self.GetN2TemperatureSetValue()

        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.button6.SetFont(self.font3)
            self.lblname1.SetFont(self.font2)
            self.three.SetFont(self.font2)
            self.eleven.SetFont(self.font2)
            self.ten.SetFont(self.font2)
            self.twelve.SetFont(self.font2)
            self.button1.SetFont(self.font2)
            self.button2.SetFont(self.font2)
            self.button5.SetFont(self.font2)
            self.two.SetFont(self.font1)
            self.lblname6.SetFont(self.font2)
            self.six.SetFont(self.font1)
            self.lblname8.SetFont(self.font2)
            self.eight.SetFont(self.font1)
            self.button10.SetFont(self.font2)
            self.button9.SetFont(self.font3)
            self.lblname5.SetFont(self.font2)
            self.five.SetFont(self.font1)
            self.lblname7.SetFont(self.font2)
            self.seven.SetFont(self.font1)
            self.lblname9.SetFont(self.font2)
            self.nine.SetFont(self.font1)
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

    def ON_SET_MODE(self, e):
        """
        Combo box event to show Graphical elements specific to chosen control (Ambient/N2) 

        Parameters
        ----------
        e : event
            drop down menu selection.

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file

        """
        
        data = str(self.Combo1.GetSelection())
        if int(data) == 0:
            Type = "Ambient Control"
            self.hbox.Hide(1)
            self.hbox.Show(0)
            self.vbox.Show(1)
            self.vbox.Show(2)
            self.vbox.Show(3)
            self.vbox.Show(4)
            self.vbox.Show(5)
            self.vbox.Show(11)
            self.vbox.Hide(6)
            self.vbox.Hide(7)
            self.vbox.Hide(8)
            self.vbox.Hide(9)
            self.vbox.Hide(10)
            self.vbox.Hide(12)
            self.hbox.Layout()
            
        elif int(data) == 1:
            Type = "Nitrogen Control"
            self.hbox.Hide(0)
            self.hbox.Show(1)
            self.vbox.Show(6)
            self.vbox.Show(7)
            self.vbox.Show(8)
            self.vbox.Show(9)
            self.vbox.Show(10)
            self.vbox.Show(12)
            self.vbox.Hide(1)
            self.vbox.Hide(2)
            self.vbox.Hide(3)
            self.vbox.Hide(4)
            self.vbox.Hide(5)
            self.vbox.Hide(11)
            self.hbox.Layout()

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Select Control" + "," + Type + "\n")
            f.close()
        except TypeError:
            pass
            
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
        Data Acquisition of the resistance, voltage and current of both ambient/N2 control is requested from Dual heater module.
        Further the resistance is converted to Temperature

        Returns
        -------
        Temp : list of [Temperature, resistance, Voltage, Current, Temperature, resistance, Voltage, Current] float
            list of all the  values described above.
            
        Raised:
        -------    
        AttributeError: simply passed
        ZeroDivisionError:
        ValueError:    

        """
        Temp = np.zeros(8)
        ADC_Amb = mmis.Functions.GETTransactions(0X19, self.chipselect, self.interruptpin)
        Voltage_Amb = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        Current_Amb = mmis.Functions.GETTransactions(0X08, self.chipselect, self.interruptpin)
        self.Alarm = ADC_Amb.Alarm
        try:
            ADC_Data_Amb =  ADC_Amb.Float.Float[0]
            Voltage_Data_Amb =  5.0 - 2*Voltage_Amb.Float.Float[0]*3.300/1024.0
            Current_Data_Amb =  Current_Amb.Float.Float[0]*3300.0/1024.0
        except AttributeError:
            ADC_Data_Amb = 0
            Voltage_Data_Amb = 0
            Current_Data_Amb = 0
        try:
            Resistance_Amb = ((ADC_Data_Amb-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_Amb))*10000
        except ZeroDivisionError:
            Resistance_Amb = 0
        
        ADC_N2 = mmis.Functions.GETTransactions(0X18, self.chipselect, self.interruptpin)
        Voltage_N2 = mmis.Functions.GETTransactions(0X09, self.chipselect, self.interruptpin)
        Current_N2 = mmis.Functions.GETTransactions(0X0A, self.chipselect, self.interruptpin)
        try:
            ADC_Data_N2 =  ADC_N2.Float.Float[0]
            Voltage_Data_N2 =  5.0 - 2*Voltage_N2.Float.Float[0]*3.300/1024.0
            Current_Data_N2 =  Current_N2.Float.Float[0]*3300.0/1024.0
        except AttributeError:
            ADC_Data_N2 = 0
            Voltage_Data_N2 = 0
            Current_Data_N2 = 0    
        try:
            Resistance_N2 = ((ADC_Data_N2-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_N2))*1000
        except ZeroDivisionError:
            Resistance_N2 = 0
     
        if Voltage_Data_Amb < 0:
            Voltage_Data_Amb = 0
        if Voltage_Data_N2 < 0:
            Voltage_Data_N2 = 0
        try:
            Temperature_Amb = 3435.0/(math.log(Resistance_Amb/0.09919119)) - 273.0
        except ValueError:
            Temperature_Amb = -9999.0
        try:    
            Temperature_N2 = (-self.A_PTC+math.sqrt(self.A_PTC*self.A_PTC - 4*self.B_PTC*(1-(Resistance_N2/1000.0))))/(2*self.B_PTC)
            if (Temperature_N2 > 1000) or (Temperature_N2 < -300):
                Temperature_N2 = -9999.0
        except ValueError:
            Temperature_N2 = -9999.0
            
        Temp[0] = Temperature_Amb
        Temp[1] = Resistance_Amb
        Temp[2] = Voltage_Data_Amb
        Temp[3] = Current_Data_Amb
        Temp[4] = Temperature_N2
        Temp[5] = Resistance_N2
        Temp[6] = Voltage_Data_N2
        Temp[7] = Current_Data_N2
        pub.sendMessage(self.pubsub_logdata, data = Temp, alarm = self.Alarm)
        return Temp

    def init_plot1(self):
        """
        The settings for the Ambient control plot are initialized

        Returns
        -------
        None.

        """
        self.dpi = 60
        self.fig1 = Figure((5.0, 5.1), dpi = self.dpi)

        self.axes = self.fig1.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Temperature Control', size = 15)
        self.axes.set_xlabel('Samples(past 2 mins)', size = 15)
        self.axes.set_ylabel('Sample Temperature (C)', color = 'red', size=12)

        pylab.setp(self.axes.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes.get_yticklabels(), fontsize=12, color = 'red')
        
        self.plot_data1 = self.axes.plot(
            self.data1,
            linewidth=1.5,
            color='red',
            )[0]

    def init_plot2(self):
        """
        The settings for the N2 control plot are initialized

        Returns
        -------
        None.

        """
        self.dpi2 = 60
        self.fig2 = Figure((5.0, 5.1), dpi = self.dpi2)

        self.axes2 = self.fig2.add_subplot(111)
        self.axes2.set_facecolor('black')
        self.axes2.set_title('Temperature Control', size = 15)
        self.axes2.set_xlabel('Samples(past 2 mins)', size = 15)
        self.axes2.set_ylabel('Nitrogen Temperature (C)', color = 'purple', size=12)

        pylab.setp(self.axes2.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes2.get_yticklabels(), fontsize=12, color = 'purple')

        self.plot_data2 = self.axes2.plot(
            self.data2,
            linewidth=1.5,
            color=(1,0,1),
            )[0]

    def draw_plot1(self):
        """
        Draws the Ambient control plot every one second with the updated measurements. 

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

    def draw_plot2(self):
        """
        Draws the N2 control plot every one second with the updated measurements. 

        Returns
        -------
        None.

        """
        xmax = len(self.data2) if len(self.data2) > 400 else 400           
        xmin = xmax - self.Xticks2

        ymin2 = round(min(self.data2[(-self.Xticks2):]), 4) - self.Yticks2 
        ymax2 = round(max(self.data2[(-self.Xticks2):]), 4) + self.Yticks2 

        self.axes2.set_xbound(lower=xmin, upper=xmax)
        self.axes2.set_ybound(lower=ymin2, upper=ymax2)
        self.axes2.grid(True, color='gray')

        if self.cb_grid2.IsChecked():
            self.axes2.grid(True, color='gray')
        else:
            self.axes2.grid(False)
        
        pylab.setp(self.axes2.get_xticklabels(), 
            visible=False)

        self.plot_data2.set_xdata(np.arange(len(self.data2)))
        self.plot_data2.set_ydata(np.array(self.data2))
        
        self.canvas2.draw()
        
    def OnSetXLabelLength1(self, e):
        """
        Number of Data points to be plotted (X scale) can be changed through a control box on GUI in Ambient control

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

    def OnSetXLabelLength2(self, e):
        """
        Number of Data points to be plotted (X scale) can be changed through a control box on GUI in N2 control

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
        Xtks = self.ten.GetValue()
        self.Xticks2 = int(Xtks.encode())
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "X label N2 Temp" + "," + str(Xtks) + "\n")
            f.close()
        except TypeError:
            pass

    def OnSetYLabelLength1(self, e):
        """
        Y axis scale can be changed through a control box on GUI in Ambient Control

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

    def OnSetYLabelLength2(self, e):
        """
        Y axis scale can be changed through a control box on GUI in N2 Control

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
        Ytks = self.twelve.GetValue()
        self.Yticks2 = float(Ytks.encode())
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Y label N2 Temp" + "," + str(Ytks) + "\n")
            f.close()
        except TypeError:
            pass

    def on_cb_grid1(self, event):
        """
        Grid on the plot can be enabled and disabled from a tick box on GUI for Ambient control

        Parameters
        ----------
        event : Event
            Tick box event.

        Returns
        -------
        None.

        """
        self.draw_plot1()

    def on_cb_grid2(self, event):
        """
        Grid on the plot can be enabled and disabled from a tick box on GUI for N2 control

        Parameters
        ----------
        event : Event
            Tick box event.

        Returns
        -------
        None.

        """
        self.draw_plot2()

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
        Sends ON and OFF commands to the Dual heater module to Control the Ambient temperature. 

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
            label = "Start Amb"
            color = "light green"
            self.redraw_graph_timer1.Stop()
            self.get_data_timer1.Stop()
            mmis.Functions.GETTransactions(0X03, self.chipselect, self.interruptpin)
            status = "stop"
        else:
            label = "Stop Amb"
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

    def on_pause_button_N2(self, e):
        """
        Sends ON and OFF commands to the Dual heater module to Control the N2 temperature. 

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
        self.paused_N2 = not self.paused_N2
        
        if self.paused_N2:
            label = "Start N2"
            color = "light green"
            self.redraw_graph_timer2.Stop()
            self.get_data_timer2.Stop()
            mmis.Functions.GETTransactions(0X04, self.chipselect, self.interruptpin)
            status = "stop"
        else:
            label = "Stop N2"
            color = "red"
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
            self.redraw_graph_timer2.Start(1000)
            self.get_data_timer2.Start(250)
            status = "start"

        self.button10.SetLabel(label)
        self.button10.SetBackgroundColour(color)

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "N2 Control" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def on_redraw_graph_timer1(self, e):
        """
        This interrupt is generated by the graph timer for updating the graph every 1 second on ambient Control.

        Parameters
        ----------
        e : Event
            Graph update timer interrupt.

        Returns
        -------
        None.

        """
        self.draw_plot1()

    def on_redraw_graph_timer2(self, e):
        """
        This interrupt is generated by the graph timer for updating the graph every 1 second on N2 Control.

        Parameters
        ----------
        e : Event
            Graph update timer interrupt.

        Returns
        -------
        None.

        """
        self.draw_plot2()

    def on_get_data_timer1(self, e):
        """
        The interrupt is generated every 200ms when start ambient control (data_timer) gets a start. Total data points to be stored in buffer
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

    def on_get_data_timer2(self, e):
        """
        The interrupt is generated every 200ms when start N2 control (data_timer) gets a start. Total data points to be stored in buffer
        is limited to 400 and beyond that based on FIFO the data gets cleared.

        Parameters
        ----------
        e : Event
            Data retreive timer interrupt.

        Returns
        -------
        None.
        
        """
        if not self.paused_N2: 
            if len(self.data2)<400:
                self.data2.append(self.x[4])
            else:
                del self.data2[0]
                self.data2.append(self.x[4])

    def on_get_read_timer(self, e):
        """
        The interrupt is generated every few milliseconds by read_timer interrupt to update the values of Temperature, Current and Voltage
        onto the control window of GUI for both Ambient & N2 control. 

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
        self.five.SetValue(str(self.x[4])[:7]) # Temperature Nitrogen
        self.six.SetValue(str(round(self.x[3], 0))) # Current Ambient
        self.seven.SetValue(str(round(self.x[7], 0))) # Current Nitrogen
        self.eight.SetValue(str(round(self.x[2] * self.x[3], 0)))
        self.nine.SetValue(str(round(self.x[7] * self.x[6], 0)))
        

    def SetAmbientTemperature(self, e):
        """
        Sets the Ambient temperature setpoint to the Dual heater module

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

    def SetNitrogenTemperature(self, e):
        """
        Sets the N2 temperature setpoint to the Dual heater module

        Parameters
        ----------
        e : event
            button press event.

        Returns
        -------
        None.

        """
        temp = self.four.GetValue()
        Rset = 1000*(1+self.A_PTC*temp+self.B_PTC*temp*temp)
        ADC = str(round(math.pow(2,15)*(1.5 - (Rset/(1000+Rset))),0))
        set_Tn2 = mmis.Functions.SETTransactions(0X06, ADC , self.chipselect, self.interruptpin)
        self.GetN2TemperatureSetValue()

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Set N2 Temp" + "," + str(temp) + "\n")
            f.close()
        except TypeError:
            pass
        
    def GetAmbientTemperatureSetValue(self):
        """
        Requests the set value of ambient temperature from the Dual heater module

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
        self.button6.SetLabel("Set-Tamb\n"+str(round(Temperature_Amb,2)).center(10))
        self.button6.SetFont(self.font3)
        self.one.SetValue(round(Temperature_Amb,3))

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Get Amb Temp" + "," + str(Temperature_Amb) + "\n")
            f.close()
        except TypeError:
            pass

    def GetN2TemperatureSetValue(self):
        """
        Requests the set value of N2 temperature from the Dual heater module

        Returns
        -------
        None.
        
        Raised:
        -------    
        TypeError: Error raised when not able to load event recording file
        ValueError:

        """
        ADC_N2 = mmis.Functions.GETTransactions(0X1B, self.chipselect, self.interruptpin)
        ADC_Data_N2 =  ADC_N2.Float.Float[0]
        Resistance_N2 = ((ADC_Data_N2-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_N2))*1000
        Temperature_N2 = (-self.A_PTC+math.sqrt(self.A_PTC*self.A_PTC - 4*self.B_PTC*(1-(Resistance_N2/1000.0))))/(2*self.B_PTC)
        self.button9.SetLabel("Set-TN2\n"+str(round(Temperature_N2,2)).center(10))
        self.button9.SetFont(self.font3)
        self.four.SetValue(str(round(Temperature_N2,4))[:8])

        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "DH" + "," + "Get N2 Temp" + "," + str(Temperature_N2) + "\n")
            f.close()
        except TypeError:
            pass

    def OnGetHistogram1(self,e):
        """
        Opens a histogram plot of the Ambient data in a new window

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        SubWindow(None, -1, self.data1).Show()

    def OnGetHistogram2(self,e):
        """
        Opens a histogram plot of the N2 data in a new window

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        SubWindow(None, -1, self.data2).Show()
    
    def OnClose(self):
        """
        Destroys all the events subjected to the Dual heater class

        Returns
        -------
        None.

        """
        self.Destroy()
