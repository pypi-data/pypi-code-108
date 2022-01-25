#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 16:17:01 2017

@author: rrbheemireddy
"""
''' Import All the Necessary libraries'''
import datetime
from datetime import datetime
import wx
import wx.adv
from pubsub import pub
from wx.lib.dialogs import ScrolledMessageDialog
import os
import time
import spidev
import matplotlib
import mmis.Functions
matplotlib.use('wxAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
   FigureCanvasWxAgg as FigureCanvas, \
   NavigationToolbar2WxAgg as NavigationToolbar
import pandas as pd
import numpy as np
import RPi.GPIO as GPIO
import mmis.SampleHeater
import mmis.DualHeater
import mmis.CryoHeater
import mmis.LiqN2Control
import mmis.RealTimeClock as RTC
import memcache
import distro
import matplotlib.pyplot as plt
from pandas import DataFrame
import csv
import warnings

Version = 'v1.36' # Keep changing the version number here everytime with the new release
warnings.filterwarnings("ignore") # Ignores all the warnings

class DataAnalysis(wx.Panel):
    '''Data Analysis Class is used to import the log file and plot the graphs.
       Also used to downsample the logfile
       inputs: Logfile with extension .CSV
       outputs: Plots of selected Parameters
              : recreates a downsampled log file'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        ''' Initialization function sets up all the necessary Graphical User Interface Elements'''
        self.lblname0 = wx.StaticText(self, label = "Choose the file to Analyze:")
        self.button0 = wx.Button(self, label = 'Load File', size = (90,35), id=-1)
        self.button0.Bind(wx.EVT_BUTTON, self.OnFileOpen)
        self.button0.SetForegroundColour('black')
        self.button0.SetBackgroundColour('grey')

        self.button1 = wx.Button(self, label = 'Plot', size = (90,35), id=-1)
        self.button1.Bind(wx.EVT_BUTTON, self.OnPlotSH)
        self.button1.SetForegroundColour('black')
        self.button1.SetBackgroundColour('grey')

        self.button2_1 = wx.Button(self, label = 'Plot', size = (90,35), id=-1)
        self.button2_1.Bind(wx.EVT_BUTTON, self.OnPlotDH_A)
        self.button2_1.SetForegroundColour('black')
        self.button2_1.SetBackgroundColour('grey')

        self.button2_2 = wx.Button(self, label = 'Plot', size = (90,35), id=-1)
        self.button2_2.Bind(wx.EVT_BUTTON, self.OnPlotDH_N)
        self.button2_2.SetForegroundColour('black')
        self.button2_2.SetBackgroundColour('grey')

        self.button3 = wx.Button(self, label = 'Plot', size = (90,35), id=-1)
        self.button3.Bind(wx.EVT_BUTTON, self.OnPlotLN)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour('grey')

        self.button4 = wx.Button(self, label = 'Plot', size = (90,35), id=-1)
        self.button4.Bind(wx.EVT_BUTTON, self.OnPlotCH)
        self.button4.SetForegroundColour('black')
        self.button4.SetBackgroundColour('grey')

        self.lblname5 = wx.StaticText(self, label = "Choose 1 point every?", id=-1)
        self.Samples = wx.SpinCtrlDouble(self, size=(155,-1), min = 1, max = 1000, inc = 1, value='100.00')
        self.Samples.SetBackgroundColour('white')
        self.lblname6 = wx.StaticText(self, label = "Samples and ", id=-1)

        self.button5 = wx.Button(self, label = 'Generate New File', size = (150,35), id=-1)
        self.button5.Bind(wx.EVT_BUTTON, self.filereduction)
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('grey')

        self.lblname1 = wx.StaticText(self, label = "Sample Heater:")
        self.SH_T = wx.CheckBox(self, -1, "Temperature", style=wx.ALIGN_RIGHT)
        self.SH_V = wx.CheckBox(self, -1, "Voltage", style=wx.ALIGN_RIGHT)
        self.SH_I = wx.CheckBox(self, -1, "Current", style=wx.ALIGN_RIGHT)
        self.SH_R = wx.CheckBox(self, -1, "Resistance", style=wx.ALIGN_RIGHT)
        
        self.lblname2_1 = wx.StaticText(self, label = "Dual Heater Amb:")
        self.DH_AT = wx.CheckBox(self, -1, "Temperature", style=wx.ALIGN_RIGHT)
        self.DH_AV = wx.CheckBox(self, -1, "Voltage", style=wx.ALIGN_RIGHT)
        self.DH_AI = wx.CheckBox(self, -1, "Current", style=wx.ALIGN_RIGHT)
        self.DH_AR = wx.CheckBox(self, -1, "Resistance", style=wx.ALIGN_RIGHT)
        
        self.lblname2_2 = wx.StaticText(self, label = "Dual Heater N2:")
        self.DH_NT = wx.CheckBox(self, -1, "Temperature", style=wx.ALIGN_RIGHT)
        self.DH_NV = wx.CheckBox(self, -1, "Voltage", style=wx.ALIGN_RIGHT)
        self.DH_NI = wx.CheckBox(self, -1, "Current", style=wx.ALIGN_RIGHT)
        self.DH_NR = wx.CheckBox(self, -1, "Resistance", style=wx.ALIGN_RIGHT)
        
        self.lblname3 = wx.StaticText(self, label = "LiqN2 Control:")
        self.LN_C = wx.CheckBox(self, -1, "Capacitance", style=wx.ALIGN_RIGHT)
        self.LN_MC = wx.CheckBox(self, -1, "Motor Current", style=wx.ALIGN_RIGHT)
        self.LN_R = wx.CheckBox(self, -1, "Resistance", style=wx.ALIGN_RIGHT)

        self.lblname4 = wx.StaticText(self, label = "Cryo Heater:")
        self.CH_T = wx.CheckBox(self, -1, "Temperature", style=wx.ALIGN_RIGHT)
        self.CH_V = wx.CheckBox(self, -1, "Voltage", style=wx.ALIGN_RIGHT)
        self.CH_I = wx.CheckBox(self, -1, "Current", style=wx.ALIGN_RIGHT)

        self.hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox0.Add(self.lblname0, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox0.AddSpacer(20)
        self.hbox0.Add(self.button0, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.lblname1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.SH_T, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.SH_V, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.SH_I, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.SH_R, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.button1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2_1.Add(self.lblname2_1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.DH_AT, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.DH_AV, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.DH_AI, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.DH_AR, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.button2_1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2_2.Add(self.lblname2_2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_2.Add(self.DH_NT, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_2.Add(self.DH_NV, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_2.Add(self.DH_NI, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_2.Add(self.DH_NR, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_2.Add(self.button2_2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.lblname3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.Add(self.LN_C, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.Add(self.LN_MC, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.Add(self.LN_R, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.Add(self.button3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.lblname4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.Add(self.CH_T, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.Add(self.CH_V, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.Add(self.CH_I, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.Add(self.button4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.lblname5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.Samples, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.lblname6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
    
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox0, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox2_1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox2_2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.vbox.Hide(3)
        self.vbox.Hide(5)
        self.vbox.Hide(7)
        self.vbox.Hide(9)
        self.vbox.Hide(11)
        self.vbox.Layout()

    def OnPlotSH(self,e):
            """This function is a reference to the event generated when plot button is clicked for the sample heater modules data logs"""
            x = [] # local variable initialized to hold the list of data from the sample heater log
            if self.SH_T.IsChecked():
                x.append('Temperature')
            if self.SH_V.IsChecked():
                x.append('Voltage')
            if self.SH_I.IsChecked():
                x.append('Current')
            if self.SH_R.IsChecked():
                x.append('Resistance')
            if len(x) == 1:
                self.df[x].plot()
                plt.show()
            if len(x) == 2:
                self.plots_2(x)
            if len(x) == 3:
                self.plots_3(x)
            if len(x) == 4:
                self.plots_4(x)

    def OnPlotDH_A(self,e):
            """This function is a reference to the event generated when plot button
            is clicked for the Dual heater modules ambient data log"""
            x = [] # local variable initialized to hold the list of data from the dual heater ambient log
            if self.DH_AT.IsChecked():
                x.append('Temperature Ambient')
            if self.DH_AV.IsChecked():
                x.append('Voltage - Amb - Ctrl')
            if self.DH_AI.IsChecked():
                x.append('Current - Amb - Ctrl')
            if self.DH_AR.IsChecked():
                x.append('Resistance Ambient')
            if len(x) == 1:
                self.df[x].plot()
                plt.show()
            if len(x) == 2:
                self.plots_2(x)
            if len(x) == 3:
                self.plots_3(x)
            if len(x) == 4:
                self.plots_4(x)

    def OnPlotDH_N(self,e):
        """This function is a reference to the event generated when plot button is clicked for the Dual heater modules nitrogen data log"""
        x = [] # local variable initialized to hold the list of data from the dual heater nitrogen log
        if self.DH_NT.IsChecked():
            x.append('Temperature N2')
        if self.DH_NV.IsChecked():
            x.append('Voltage - N2 - Ctrl')
        if self.DH_NI.IsChecked():
            x.append('Current - N2 - Ctrl')
        if self.DH_NR.IsChecked():
            x.append('Resistance N2')
        if len(x) == 1:
            self.df[x].plot()
            plt.show()
        if len(x) == 2:
            self.plots_2(x)
        if len(x) == 3:
            self.plots_3(x)
        if len(x) == 4:
            self.plots_4(x)

    def OnPlotLN(self,e):
        '''This function is a reference to the event generated when plot button is clicked for the Liquid nitrogen height control modules data log'''
        x = [] # local variable initialized to hold the list of data from the liquid nitrogen log
        if self.LN_C.IsChecked():
            x.append('Capacitance(pF)')
        if self.LN_MC.IsChecked():
            x.append('Motor Current(mA)')
        if self.LN_R.IsChecked():
            x.append('Resistance (kOhms)')
        if len(x) == 1:
            self.df[x].plot()
            plt.show()
        if len(x) == 2:
            self.plots_2(x)
        if len(x) == 3:
            self.plots_3(x)

    def OnPlotCH(self,e):
        '''This function is a reference to the event generated when plot button is clicked for the Cryo heater modules data log'''
        x = [] # local variable initialized to hold the list of data from the cryo heater log
        if self.CH_T.IsChecked():
            x.append('Temperature')
        if self.CH_V.IsChecked():
            x.append('Voltage')
        if self.CH_I.IsChecked():
            x.append('Current')
        if len(x) == 1:
            self.df[x].plot()
            plt.show()
        if len(x) == 2:
            self.plots_2(x)
        if len(x) == 3:
            self.plots_3(x)

    def plots_3(self, x):
        ''' This function plots the data with 3 y-axes. At a time 3 parameters data is visualized with respect to number of samples on a same plot.'''
        fig, ax = plt.subplots()
        ax3 = ax.twinx()
        rspine = ax3.spines['right']
        rspine.set_position(('axes', 1.15))
        ax3.set_frame_on(True)
        ax3.patch.set_visible(False)
        fig.subplots_adjust(right=0.7)

        self.df[x[0]].plot(ax=ax, style='b-')
        # same ax as above since it's automatically added on the right
        self.df[x[1]].plot(ax=ax, style='r-', secondary_y=True)
        self.df[x[2]].plot(ax=ax3, style='g-')
        ax.set_xlabel('Time')
        ax.set_ylabel(x[0])
        ax.right_ax.set_ylabel(x[1])
        ax3.set_ylabel(x[2])
        ax3.set_title(str(self.filename))
        ax3.legend([ax.get_lines()[0], ax.right_ax.get_lines()[0], ax3.get_lines()[0]], x , bbox_to_anchor=(1.5, 0.5))
        plt.show()

    def plots_4(self,x):
        '''This function plots the data with 4 y-axes. At a time 4 parameters data is visualized with respect to number of samples on a same plot'''
        fig, ax = plt.subplots()
        ax3 = ax.twinx()
        ax4 = ax.twinx()
        rspine = ax3.spines['right']
        rspine.set_position(('axes', 1.15))
        lspine = ax4.spines['right']
        lspine.set_position(('axes', 1.35))

        ax4.set_frame_on(True)
        ax4.patch.set_visible(False)
        fig.subplots_adjust(right=0.7)

        self.df[x[0]].plot(ax=ax, style='b-')
        self.df[x[1]].plot(ax=ax, style='r-', secondary_y=True)
        self.df[x[2]].plot(ax=ax3, style='g-')
        self.df[x[3]].plot(ax=ax4, style='y-')
        ax.set_xlabel('Time')
        ax.set_ylabel(x[0])
        ax3.set_ylabel(x[2])
        ax.right_ax.set_ylabel(x[1])
        ax4.set_ylabel(x[3])
        ax4.set_title(str(self.filename))
        ax4.legend([ax.get_lines()[0], ax.right_ax.get_lines()[0], ax3.get_lines()[0], ax4.get_lines()[0]],x)
        plt.show()

    def plots_2(self, x):
        '''This function plots the data with 2 y-axes. At a time 2 parameters data is visualized with respect to number of samples on a same plot'''
        fig, ax = plt.subplots()
        self.df[x[0]].plot(ax=ax, style='b-')
        self.df[x[1]].plot(ax=ax, style='r-', secondary_y=True)
        ax.set_xlabel('Time')
        ax.set_ylabel(x[0])
        ax.right_ax.set_ylabel(x[1])
        ax.set_title(str(self.filename))
        ax.legend([ax.get_lines()[0], ax.right_ax.get_lines()[0]], x)
        plt.show()
        
    def OnFileOpen(self,e):
        ''' This function is a reference to a event generated when a "Chose a file to analyze" button is pressed. This function automatically looks out for the
            avaialble data from various modules and displays the list of parameters for the user to be selected.
                Input: The file to be analyzed 
                Ouptut: A list of paramaters available in the data file along with a check box displayed'''
        self.vbox.Hide(3)
        self.vbox.Hide(5)
        self.vbox.Hide(7)
        self.vbox.Hide(9)
        self.vbox.Hide(11)
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.file = str(self.dirname+'/'+self.filename)
            df_module = pd.read_csv(self.file, delimiter = ',', nrows = 1)
            self.df = pd.read_csv(self.file, delimiter = ',', header = 1)
            self.Modules_Found = []
            for i in np.arange(len(df_module.columns)):
                if df_module.columns[i] == 'Sample Heater':
                        self.Modules_Found.append('Sample Heater')
                        self.vbox.Show(3)
                elif df_module.columns[i] == 'Dual Heater':
                        self.Modules_Found.append('Dual Heater')
                        self.vbox.Show(5)
                        self.vbox.Show(7)
                elif df_module.columns[i] == 'LiqN2 Control':
                        self.Modules_Found.append('LiqN2 Control')
                        self.vbox.Show(9)
                elif df_module.columns[i] == 'Cryo Heater':
                        self.Modules_Found.append('Cryo Heater')
                        self.vbox.Show(11)
            self.vbox.Layout()
        dlg.Destroy()

    def filereduction(self,e):
        ''' This function is a reference to a event generated when a "Generate new file" button is pressed.
			Input: Choose 1 point every .. for e.g. 10, 100 or 1000 or any number of samples.
			Output: A new downsampled file is generated'''
        try:
            with open(self.file, 'r') as inp, open(self.dirname+'/'+self.filename[:-4]+str(int(self.Samples.GetValue()))+'_compressed.csv', 'w') as out:
                i = 0
                writer = csv.writer(out)
                for row in csv.reader(inp):
                    i = i+1
                    if (i%self.Samples.GetValue()==0):
                        writer.writerow(row)
                    elif (i<3):
                        writer.writerow(row)
                        
        except AttributeError:
            box = wx.MessageDialog(self, 'Please load the file that needs to be reduced first', 'File Size Reduction', wx.OK)
            answer = box.ShowModal()
            box.Destroy()

class TabSettings(wx.Panel):
    def __init__(self, parent):
        '''The settings Tab is the first tab that pops when the application is opened. Here, user gets to choose to create a log file. Also, the error indicators are
            displayed per module slot of MMI'''
        wx.Panel.__init__(self, parent)
        self.paused = True
        self.file_creation = False
        self.Alarm1 = 0 
        self.Alarm2 = 0
        self.Alarm3 = 0
        self.Alarm4 = 0
        self.data1 = [0, 0, 0, 0, 0, 0, 0] 
        self.data2 = [0, 0, 0, 0, 0, 0, 0]
        self.data3 = [0, 0, 0, 0, 0, 0, 0]
        self.data4 = [0, 0, 0, 0, 0, 0, 0]
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        Datalog_Pubsub = ['Logmod1','Logmod2', 'Logmod3', 'Logmod4']
        Alarm_Pubsub = ['Alarm1', 'Alarm2', 'Alarm3', 'Alarm4']
        self.mc = memcache.Client([('127.0.0.1', 11211)])
        
        pub.subscribe(self.OnModule1_Data, Datalog_Pubsub[0]) # The data from the first slot is subscribed
        pub.subscribe(self.OnModule2_Data, Datalog_Pubsub[1]) # The data from the second slot is subscribed
        pub.subscribe(self.OnModule3_Data, Datalog_Pubsub[2]) # The data from the third slot is subscribed
        pub.subscribe(self.OnModule4_Data, Datalog_Pubsub[3]) # The data from the fourth slot is subscribed
        
        pub.subscribe(self.OnModule1_Alarm, Alarm_Pubsub[0]) # The alarms from the first slot is subscribed
        pub.subscribe(self.OnModule2_Alarm, Alarm_Pubsub[1]) # The alarms from the second slot is subscribed
        pub.subscribe(self.OnModule3_Alarm, Alarm_Pubsub[2]) # The alarms from the third slot is subscribed
        pub.subscribe(self.OnModule4_Alarm, Alarm_Pubsub[3]) # The alarms from the fourth slot is subscribed
        pub.subscribe(self.On_List_of_Modules, "Modules List")
        
        self.Logging_Timer = wx.Timer(self) # Timer defined for logging the data
        self.Bind(wx.EVT_TIMER, self.on_logging_timer, self.Logging_Timer) 

        self.lblname = wx.StaticText(self, label = "Create Log File :", pos = (40,45))
        self.File_name = wx.TextCtrl(self, size=(160,40), value = '', pos = (200,35), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)
        self.lblname2 = wx.StaticText(self, label = "type file name ....", pos = (200, 75))
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD, True )
        self.lblname2.SetFont(font.MakeBold())
        
        self.button1 = wx.Button(self, label="Create", pos=(380, 35), size = (100,40), id = -1)
        self.Bind(wx.EVT_BUTTON, self.ON_CREATE,self.button1)
        self.button1.SetForegroundColour('black')
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        self.button2 = wx.Button(self, label="Start Logging", pos=(520, 35), size = (150,40), id = -1)
        self.Bind(wx.EVT_UPDATE_UI, self.ON_Update_Logging,self.button2)
        self.Bind(wx.EVT_BUTTON, self.ON_Logging, self.button2)
        self.button2.SetForegroundColour('black')

        self.lblname3 = wx.StaticText(self, label = "Module - 1 Alarm :", pos = (40,115))
        self.lblname4 = wx.StaticText(self, label = "Module - 2 Alarm :", pos = (40,165))
        self.lblname5 = wx.StaticText(self, label = "Module - 3 Alarm :", pos = (40,215))
        self.lblname6 = wx.StaticText(self, label = "Module - 4 Alarm :", pos = (40,265))
        self.ImgFolder = '/home/pi/.local/lib/python3.7/site-packages/mmis/Images/'
        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.ImgFolder = '/home/pi/.local/lib/python3.5/site-packages/mmis/Images/'

        self.Logo = wx.StaticBitmap(self, -1, pos = (500,100))
        self.image_file = self.ImgFolder+'HZlogo.png'
        self.Logo.SetFocus()
        self.Logo.SetBitmap(wx.Bitmap(self.image_file))

    def getserial(self):
        ''' This function finds out the unique identification number and the model of the Raspberry pi
                Output: Model Number, Unique identification number'''
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

    def OnPaint(self, evt):
            ''' This function paints the error indicators red/white depending on whether the error has obtained. '''
            dc = wx.PaintDC(self)
            dc.Clear()
            
            if self.Alarm1 == 0:
                dc.SetBrush(wx.Brush('White'))
                dc.DrawCircle(220, 123, 20)
                #GPIO.output(40,0)
            else:
                dc.SetBrush(wx.Brush('Red'))
                dc.DrawCircle(220, 123, 20)
                #GPIO.output(40,1)

            if self.Alarm2 == 0:
                dc.SetBrush(wx.Brush('White'))
                dc.DrawCircle(220, 173, 20)
                #GPIO.output(40,0)
            else:
                dc.SetBrush(wx.Brush('Red'))
                dc.DrawCircle(220, 173, 20)
                #GPIO.output(40,1)
            
            if self.Alarm3 == 0:
                dc.SetBrush(wx.Brush('White'))
                dc.DrawCircle(220, 223, 20)
                #GPIO.output(40,0)
            else:
                dc.SetBrush(wx.Brush('Red'))
                dc.DrawCircle(220, 223, 20)
                #GPIO.output(40,1)
                
            if self.Alarm4 == 0:
                dc.SetBrush(wx.Brush('White'))
                dc.DrawCircle(220, 273, 20)
                #GPIO.output(40,0)
            else:
                dc.SetBrush(wx.Brush('Red'))
                dc.DrawCircle(220, 273, 20)
                #GPIO.output(40,1)
                
    def OnModule1_Data(self, data, alarm):
        ''' This function retreives the data and alarm variable for the module in slot 1 '''
        self.data1 = data
        self.Alarm1 = alarm
        self.Refresh()

        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)

    def OnModule2_Data(self, data, alarm):
        ''' This function retreives the data and alarm variable for the module in slot 2 '''
        self.data2 = data
        self.Alarm2 = alarm
        self.Refresh()

        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)

    def OnModule3_Data(self, data, alarm):
        ''' This function retreives the data and alarm variable for the module in slot 3 '''
        self.data3 = data
        self.Alarm3 = alarm
        self.Refresh()

        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)
            
    def OnModule4_Data(self, data, alarm):
        ''' This function retreives the data and alarm variable for the module in slot 4 '''
        self.data4 = data
        self.Alarm4 = alarm
        self.Refresh()
        
        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)

    def OnModule1_Alarm(self, alarm):
        ''' This function retreives the alarm variable for the module in slot 1 '''
        self.Alarm1 = alarm
        self.Refresh()

        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)
    
    def OnModule2_Alarm(self, alarm):
        ''' This function retreives the alarm variable for the module in slot 2 '''
        self.Alarm2 = alarm
        self.Refresh()

        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)

    def OnModule3_Alarm(self, alarm):
        ''' This function retreives the alarm variable for the module in slot 3 '''
        self.Alarm3 = alarm
        self.Refresh()
        
        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)

    def OnModule4_Alarm(self, alarm):
        ''' This function retreives the alarm variable for the module in slot 4 '''
        self.Alarm4 = alarm
        self.Refresh()

        if ((self.Alarm1 or self.Alarm2 or self.Alarm3 or self.Alarm4) == 1):
            GPIO.output(40, 1)
        else:
            GPIO.output(40, 0)
    
    def ON_Logging(self, e):
        ''' This function is a reference to an event generated when "start logging" button is pressed.
                First checks whether the file has been created before it starts logging '''
        if not self.file_creation:
                #print ("file not created")
                self.lblname2.SetBackgroundColour("Red")
                status = "closed"
        else:
            self.paused = not self.paused
            if not self.paused:
                self.Logging_Timer.Start(200)
                status = "start"
            else:
                left = len(self.Buffer)
                for i in range(left):
                    try:
                        self.file.write(self.Buffer[i])   
                    except ValueError:
                        pass  
                self.Buffer.clear() 
                self.file.flush()
                self.file.close()
                self.file_creation = not self.file_creation
                status = "stop"
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write(str(datetime.now()) + "," + "Main" + "," + "Data logging" + "," + status + "\n")
            f.close()
        except TypeError:
            pass

    def Close_LogSheet(self):
        ''' Closes the log sheet before the application is closed.'''
        if self.file_creation == True:
            left = len(self.Buffer)
            for i in range(left):
                try:
                    self.file.write(self.Buffer[i])   
                except ValueError:
                    pass  
            self.Buffer.clear() 
            self.file.flush()
            self.file.close()
            
    def ON_Update_Logging(self, e):
        ''' Stops the logging '''
        if self.paused:
            label = "Start Logging"
            color = "light green"
            self.Logging_Timer.Stop()
        else:
            label = "Stop Logging"
            color = "Red"
        self.button2.SetLabel(label)
        self.button2.SetBackgroundColour(color)

    def on_logging_timer(self, e):
        ''' When the logging starts the timer is initialized to generate a event every 250ms. This function is called every 250ms and logs the 
            data to the excel sheet. '''
        Module_names = ['Not Found','Sample Heater', 'Dual Heater', 'LiqN2 Control', 'Cryo Heater']
        Module_data = {'0': self.data1, '1': self.data2, '2': self.data3, '3': self.data4}
        #self.i += 1
        temp = str(datetime.now())+","

        for i in range(4):
            if self.Modules_List[i] == Module_names[0]:
                temp = temp + str(Module_data[str(i)][0]) + ","
            elif self.Modules_List[i] == Module_names[1]:
                temp = temp + str(Module_data[str(i)][0]) + ","
                temp = temp + str(Module_data[str(i)][1]) + ","
                temp = temp + str(Module_data[str(i)][2]) + ","
                temp = temp + str(Module_data[str(i)][3]) + ","
                
            elif self.Modules_List[i] == Module_names[2]:
                temp = temp + str(Module_data[str(i)][0]) + ","
                temp = temp + str(Module_data[str(i)][1]) + ","
                temp = temp + str(Module_data[str(i)][2]) + ","
                temp = temp + str(Module_data[str(i)][3]) + ","
                temp = temp + str(Module_data[str(i)][4]) + ","
                temp = temp + str(Module_data[str(i)][5]) + ","
                temp = temp + str(Module_data[str(i)][6]) + ","
                temp = temp + str(Module_data[str(i)][7]) + ","

            elif self.Modules_List[i] == Module_names[3]:
                temp = temp + str(Module_data[str(i)][0]) + ","
                temp = temp + str(Module_data[str(i)][1]) + ","
                temp = temp + str(Module_data[str(i)][2]) + ","

            elif self.Modules_List[i] == Module_names[4]:
                temp = temp + str(Module_data[str(i)][0]) + ","
                temp = temp + str(Module_data[str(i)][1]) + ","
                temp = temp + str(Module_data[str(i)][2]) + ","
        
        
        temp = temp + "\n"
        self.Buffer.append(temp)
        
        if len(self.Buffer) == 240:
            for i in range(240):
                try:
                    self.file.write(self.Buffer[i])   
                except ValueError:
                    pass
                
            self.Buffer.clear()
                
        self.file.flush()

    def On_List_of_Modules(self, name):
        ''' Retreives the list of modules attached to the MMI device '''
        self.Modules_List = name
        #print (self.Modules_List)
        self.Refresh()

    def Excel_File_Header_Generation(self):
        ''' The following function creates the header for the datalogging file '''
        Module_names = ['Not Found','Sample Heater', 'Dual Heater', 'LiqN2 Control', 'Cryo Heater']
        SH_Header = "Sample Heater,"+"Sample Heater,"+"Sample Heater,"+"Sample Heater,"
        SH_Header_Params = "Temperature,"+"Voltage,"+"Current,"+"Resistance,"
        DH_Header = "Dual Heater,"+"Dual Heater,"+"Dual Heater,"+"Dual Heater,"+"Dual Heater,"+"Dual Heater,"+"Dual Heater,"+"Dual Heater,"
        DH_Header_Params = "Temperature Ambient,"+"Resistance Ambient,"+"Voltage - Amb - Ctrl,"+"Current - Amb - Ctrl,"+"Temperature N2,"+"Resistance N2,"+"Voltage - N2 - Ctrl,"+"Current - N2 - Ctrl,"
        LNC_Header = "LN2 Control,"+"LN2 Control,"+"LN2 Control,"
        LNC_Header_Params = "Capacitance(pF)," + "Motor Current(mA)," + "Resistance (kOhms),"
        CH_Header = "Cryo Heater,"+"Cryo Heater,"+"Cryo Heater,"
        CH_Header_Params = "Temperature,"+"Voltage,"+"Current,"
        NM_Header = "No Module,"
        NM_Header_Params = " ,"
        self.Header = "Time,"
        self.Header_Params = " ,"
        for i in range(4):
            if self.Modules_List[i] == Module_names[0]:
                self.Header = self.Header + NM_Header
                self.Header_Params = self.Header_Params + NM_Header_Params
            elif self.Modules_List[i] == Module_names[1]:
                self.Header = self.Header + SH_Header
                self.Header_Params = self.Header_Params + SH_Header_Params
            elif self.Modules_List[i] == Module_names[2]:
                self.Header = self.Header + DH_Header
                self.Header_Params = self.Header_Params + DH_Header_Params
            elif self.Modules_List[i] == Module_names[3]:
                self.Header = self.Header + LNC_Header
                self.Header_Params = self.Header_Params + LNC_Header_Params
            elif self.Modules_List[i] == Module_names[4]:
                self.Header = self.Header + CH_Header
                self.Header_Params = self.Header_Params + CH_Header_Params
        self.Header = self.Header+"\n"
        self.Header_Params = self.Header_Params+"\n"

    def Generate_filecreation_Event(self):
        ''' File creation event is programmatically generated here instead of user generating from GUI '''
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button1)
        evt.SetId(self.button1.GetId())
        self.button1.GetEventHandler().ProcessEvent(evt)

    def Generate_startlogging_Event(self):
        ''' Starting the log file event is programmatically generated here instead of user generating from GUI '''
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button2)
        evt.SetId(self.button2.GetId())
        self.button2.GetEventHandler().ProcessEvent(evt)
        
    def ON_CREATE(self,e):
        ''' This function is a result of event generated when a "Create" button is clicked. A new file is created for the data to be logged'''
        Params = {}
        Parameters = pd.DataFrame(Params)
        self.dirName = ""
        self.fileName = self.File_name.GetValue() + '-' + str(datetime.now())[:16]
        pub.sendMessage("File", name = self.fileName)
        dlg = wx.FileDialog(self, "Save As", self.dirName, self.fileName, "Excel Files (*.csv)|*.csv|All Files|*.*", wx.FD_SAVE)
        if (dlg.ShowModal() == wx.ID_OK):
            self.lblname2.SetBackgroundColour("White")
            if self.file_creation:
                self.file.close()
                self.file_creation = not self.file_creation
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            outputfile = os.path.join(self.dirName,self.fileName)
            self.file = open(self.fileName, "a")
            self.file_creation = not self.file_creation
            self.Excel_File_Header_Generation()
            self.Buffer = []
            if os.stat(self.fileName).st_size == 0:
                self.file.write(self.Header)
                self.file.write(self.Header_Params)
            try:
                self.UEfile = self.mc.get("UE")
                f = open(self.UEfile, "a")
                f.write(str(datetime.now()) + "," + "Main" + "," + "Data logging File" + "," + str(outputfile) + "\n")
                f.close()
            except TypeError:
                pass
        
class TabOne(wx.Panel):
    ''' Empty Tab to display when the module is not present in the slot 1'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
 
class TabTwo(wx.Panel):
    ''' Empty Tab to display when the module is not present in the slot 2'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

class TabThree(wx.Panel):
    ''' Empty Tab to display when the module is not present in the slot 3'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
 
class TabFour(wx.Panel):
    ''' Empty Tab to display when the module is not present in the slot 4'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        

class MainWindow(wx.Frame):
    ''' The Main Window sets all the entire frame work for the GUI and loads each slot's panel when the module is detected'''
    def __init__(self, parent, id, title, w, h, adj):
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(w,h),style = wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)
        self.Set_GPIOS()
        #RTC.Check_Connection()
        spi = spidev.SpiDev()
        spi.open(0,0)
        spi.max_speed_hz = 100000
        self.mc = memcache.Client([('127.0.0.1', 11211)])
        self.mc.delete("UE")
        location = "/home/pi/Documents/"
        self.UEfile = location+(str(datetime.now()))[:16]+"-UE.txt"
        self.mc.set("UE", self.UEfile)
        f=open(self.UEfile,"w+")
        f.write("File created at %s \n" %str(datetime.now()))
        f.write("Time, Module, Event, Value \n")
        f.close()
        self.Test_Modules()
        self.ImgFolder = '/home/pi/.local/lib/python3.7/site-packages/mmis/Images/'
        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.ImgFolder = '/home/pi/.local/lib/python3.5/site-packages/mmis/Images/'
            
        self.Create_Notebook()  # Creates the Notebook along with the empty tabs  
        self.Create_Menubar()   # Creates Menubar with functionalities such open, close, help etc
        self.Create_Statusbar()
        self.Find_Modules_test()
        self.Create_Data_Panel()
        self.Bind(wx.EVT_CLOSE, self.Onclosewindow)
        pub.sendMessage("Modules List", name = self.List_of_Modules)
        #self.Maximize(True)  #Use this function to maximize to Fit screen
        self.nb.SetSelection(0)
        self.tab0.Generate_filecreation_Event()
        self.tab0.Generate_startlogging_Event()
        #self.tab0.ON_CREATE()
        #self.ShowFullScreen(True) #Use this function to maximize to Full Screen - Not preferred

    def getserial(self):
        ''' this function is used to find out the unique serial number of the
        raspberry pi and its model number'''
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

    def Create_Notebook(self):
        ''' This function initializes the notebook and the panel 1
                        Panel1: Settings Panel
                        panel2: GUI for Slot 1
                        panel3: GUI for Slot 2
                        panel4: GUI for Slot 3
                        panel5: GUI for Slot 4
                        panel6: Data Analysis Panel'''
                        
        self.p = wx.Panel(self)
        self.nb = wx.Notebook(self.p)
        self.font1 = wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        #self.nb.SetFont(wx.Font(wx.FontInfo(18).Bold()))

        # Create the tab windows
        self.tab0 = TabSettings(self.nb)
        
        bmp1 = wx.Bitmap(self.ImgFolder+"Connected.png", wx.BITMAP_TYPE_ANY)
        bmp2 = wx.Bitmap(self.ImgFolder+"Disconnected.png", wx.BITMAP_TYPE_ANY)
        bmp3 = wx.Bitmap(self.ImgFolder+"warning.png", wx.BITMAP_TYPE_ANY)
        bmp4 = wx.Bitmap(self.ImgFolder+"graph.png", wx.BITMAP_TYPE_PNG)
        Image = wx.ImageList(16,16)
        self.Image1 = Image.Add(bmp1) # Connected
        self.Image2 = Image.Add(bmp2) # DisConnected
        self.Image3 = Image.Add(bmp3) # Warning
        self.Image4 = Image.Add(bmp4) # graph
        self.nb.AssignImageList(Image)
        
        # Add the windows to tabs and name them.

        self.nb.AddPage(self.tab0, "START")
        
        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.p.SetSizer(sizer)
        self.p.Show()

    def Create_Data_Panel(self):
        ''' This function creates the Data analysis panel at the end after all the slots panels are created '''
        self.tab13 = DataAnalysis(self.nb)
        self.nb.AddPage(self.tab13, "Data Analysis")
        self.nb.SetPageImage(self.TabID, self.Image4)

    #menu bar
    def Create_Menubar(self):
        ''' This function creates the menubar and the elements present within it '''
        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.FD_OPEN, "&Open", "Open a file to edit")
        filemenu.AppendSeparator()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "Information about the developers")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", "Terminate the program")
        helpmenu = wx.Menu()
        generalhelp = helpmenu.Append(5, "&StartUp", "General help on StartUp, Recovery mode and System update")
        helpmenu.AppendSeparator()
        sampleheaterhelp = helpmenu.Append(2, "&Sample Heater", "Help on using the sample heater")
        helpmenu.AppendSeparator()
        dualheaterhelp = helpmenu.Append(3, "&Dual Heater", "Help on using the dual heater")
        helpmenu.AppendSeparator()
        LN2Controlhelp = helpmenu.Append(4, "&LN2 Control", "Help on using the Liquid N2 Control")

        #Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        
        #set events
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)  
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)  
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnStartup, generalhelp)
        self.Bind(wx.EVT_MENU, self.Onsampleheater, sampleheaterhelp)
        self.Bind(wx.EVT_MENU, self.Ondualheater, dualheaterhelp)
        self.Bind(wx.EVT_MENU, self.OnLN2Control, LN2Controlhelp)
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        

    def Create_Statusbar(self):    
        ''' This function creates a status bar in the bottom of the Graphical User Interface'''
        # STATUS BAR
        sb = self.CreateStatusBar(3)
        sb.SetStatusWidths([-1, 65, 150])
        sb.PushStatusText("Ready", 0)
    
    def Set_GPIOS(self):
        ''' This function initializes all the used GPIO's of the raspberry pi'''
        GPIO.setmode(GPIO.BOARD) #
        GPIO.setwarnings(False)
        GPIO.setup(33, GPIO.OUT) # Chip Select Module 1
        GPIO.setup(16, GPIO.OUT) # Chip Select Module 2
        GPIO.setup(12, GPIO.OUT) # Chip Select Module 3
        GPIO.setup(7, GPIO.OUT)  # Chip Select Module 4

        GPIO.setup(35, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Module 1 Present
        GPIO.setup(15, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Module 2 Present
        GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Module 3 Present
        GPIO.setup(5, GPIO.IN)  # Module 4 Present

        GPIO.setup(37, GPIO.IN)  # Module 1 Interrupt Master
        GPIO.setup(18, GPIO.IN)  # Module 2 Interrupt Master
        GPIO.setup(13, GPIO.IN)  # Module 3 Interrupt Master
        GPIO.setup(3, GPIO.IN)   # Module 4 Interrupt Master

        GPIO.setup(40, GPIO.OUT)  # Error LED

        #GPIO.add_event_detect(5, GPIO.BOTH, callback = self.OnModule4)
        #GPIO.add_event_detect(11, GPIO.BOTH, callback = self.OnModule3)
        #GPIO.add_event_detect(15, GPIO.BOTH, callback = self.OnModule2)
        #GPIO.add_event_detect(35, GPIO.BOTH, callback = self.OnModule1)

    def Test_Modules(self):
        #print ("1")
        if GPIO.input(5) == 0:
            mod_name4 = mmis.Functions.GETTransactions(0X0C, 7, 3)
            #mod_name4 = GETTransactions(0X0C, 7, 3)
        #name4 = mod_name4.String
        #print ("2")
        if GPIO.input(11) == 0:
            mod_name3 = mmis.Functions.GETTransactions(0X0C, 12, 13)
            #mod_name3 = GETTransactions(0X0C, 12, 13)
        #name3 = mod_name3.String
        #print ("3")
        if GPIO.input(15) == 0:
            mod_name2 = mmis.Functions.GETTransactions(0X0C, 16, 18)
            #mod_name2 = GETTransactions(0X0C, 16, 18)
        #name2 = mod_name2.String
        #print ("4")
        if GPIO.input(35) == 0:
            mod_name1 = mmis.Functions.GETTransactions(0X0C, 33, 37)
            #mod_name1 = GETTransactions(0X0C, 33, 37)
        #name1 = mod_name1.String
        #print (name1, name2, name3, name4)

    def Find_Modules_test(self):
        ''' This function checks whether the module is present in particular slot and displays its graphical elements in their respective slot of the user interface'''
        Modulepins = [35, 15, 11, 5] # Module present pins on raspberry pi GPIOs
        self.Module1 = [33, 37]      # element 1 = Chipselect pin, element 2 = Interrupt Pin
        self.Module2 = [16, 18]
        self.Module3 = [12, 13]
        self.Module4 = [7, 3]
        self.Com_Pins = {0:self.Module1, 1:self.Module2, 2:self.Module3, 3:self.Module4}

        self.TabID = 1
        Module_Names = ['Sample Heater', 'Dual Heater', 'LiqN2 Control', 'Cryo Heater']
        Module_Classes = {'0': mmis.SampleHeater, '1': mmis.DualHeater, '2': mmis.LiqN2Control, '3': mmis.CryoHeater}
        Module_Pubsub = ['Datamod1','Datamod2', 'Datamod3', 'Datamod4']
        Datalog_Pubsub = ['Logmod1','Logmod2', 'Logmod3', 'Logmod4']
        Alarm_Pubsub = ['Alarm1', 'Alarm2', 'Alarm3', 'Alarm4']
        self.List_of_Modules = []
            
        if GPIO.input(Modulepins[0]) == 0:
            #time.sleep(5)
            #print ('module 1 found')
            module1 = False
            
            while module1 is False:
                try:
                    mod_name = mmis.Functions.GETTransactions(0X0C, 33, 37)
                    name = mod_name.String
                    print (name)
                    if name in Module_Names:
                        module1 = True
                        self.List_of_Modules.append(name)
                except AttributeError as err:
                    #print (err, '---> Module Not Responding - Attribute Error')
                    pass
            

            for i in range(len(Module_Names)):
                if name == Module_Names[i]:
                    self.tab2 = Module_Classes[str(i)].Main(self.nb, self.Module1, Module_Pubsub[0], Datalog_Pubsub[0])
                    self.tab3 = Module_Classes[str(i)].Settings(self.nb, self.Module1, Module_Pubsub[0], Alarm_Pubsub[0])

                    self.button1 = wx.Button(self.tab2, label = 'Settings', pos = (w-330+adj, 295), size = (240, 30), id = 13)
                    self.button1.Bind(wx.EVT_BUTTON, self.OnSettings1)
                    self.button1.SetForegroundColour('black')
                    self.button1.SetBackgroundColour('light blue')

                    self.button2 = wx.Button(self.tab3, label = 'Control', pos = (535, 295), size = (240, 30), id = 12)
                    self.button2.Bind(wx.EVT_BUTTON, self.GotoTestModule1)
                    self.button2.SetForegroundColour('black')
                    self.button2.SetBackgroundColour('light blue')

                    self.Mod1_AcquisitionID = self.TabID
                    self.TabID = self.TabID+1
                    self.Mod1_settingsID = self.TabID
                    self.TabID = self.TabID+1
                    
                    self.nb.InsertPage(self.Mod1_AcquisitionID, self.tab2, name)
                    self.nb.InsertPage(self.Mod1_settingsID, self.tab3, name)
                    self.nb.SetSelection(self.Mod1_settingsID)
                    self.tab2.Hide()
                    
                    self.nb.SetPageImage(self.Mod1_settingsID, self.Image1) # Connected
                    self.nb.SetPageImage(self.Mod1_AcquisitionID, self.Image1) # Connected
                    #print ('Module name is %s'%Module_Names[i])

        else:
            self.tab1 = TabOne(self.nb)
            self.nb.AddPage(self.tab1, "Module 1")
            self.nb.SetPageImage(self.TabID, self.Image2)
            self.TabID = self.TabID+1
            self.List_of_Modules.append("Not Found")
            
             
                    
        if GPIO.input(Modulepins[1]) == 0:
            #time.sleep(5)  
            #print ('module 2 found')
            module2 = False
            
            while module2 is False:
                try:
                    mod_name = mmis.Functions.GETTransactions(0X0C, 16, 18)
                    name = mod_name.String
                    if name in Module_Names:
                        module2 = True
                        self.List_of_Modules.append(name)
                except AttributeError:
                    #print (err, '---> Module 2 Not Responding - Attribute Error')
                    pass
                
            for i in range(len(Module_Names)):
                if name == Module_Names[i]:
                    self.tab6 = Module_Classes[str(i)].Settings(self.nb, self.Module2, Module_Pubsub[1], Alarm_Pubsub[1])
                    self.tab5 = Module_Classes[str(i)].Main(self.nb, self.Module2, Module_Pubsub[1], Datalog_Pubsub[1])
                    
                    self.button3 = wx.Button(self.tab5, label = 'Settings', pos = (w-330+adj, 295), size = (240, 30), id = 13)
                    self.button3.Bind(wx.EVT_BUTTON, self.OnSettings2)
                    self.button3.SetForegroundColour('black')
                    self.button3.SetBackgroundColour('light blue')

                    self.button4 = wx.Button(self.tab6, label = 'Control', pos = (535, 295), size = (240, 30), id = 12)
                    self.button4.Bind(wx.EVT_BUTTON, self.GotoTestModule2)
                    self.button4.SetForegroundColour('black')
                    self.button4.SetBackgroundColour('light blue')

                    self.Mod2_AcquisitionID = self.TabID
                    self.TabID = self.TabID+1
                    self.Mod2_settingsID = self.TabID
                    self.TabID = self.TabID+1
                    
                    self.nb.InsertPage(self.Mod2_AcquisitionID, self.tab5, name)
                    self.nb.InsertPage(self.Mod2_settingsID, self.tab6, name)
                    self.nb.SetSelection(self.Mod2_settingsID)
                    self.tab5.Hide()
                    
                    self.nb.SetPageImage(self.Mod2_settingsID, self.Image1) # Connected
                    self.nb.SetPageImage(self.Mod2_AcquisitionID, self.Image1) # Connected
                    #print ('Module name is %s'%Module_Names[i])
        else:
            self.tab4 = TabTwo(self.nb)
            self.nb.AddPage(self.tab4, "Module 2")
            self.nb.SetPageImage(self.TabID, self.Image2)
            self.TabID = self.TabID+1
            self.List_of_Modules.append("Not Found")

        
        if GPIO.input(Modulepins[2]) == 0:
            #time.sleep(5)
            #print ('module 3 found')
            module3 = False
            
            while module3 is False:
                try:
                    mod_name = mmis.Functions.GETTransactions(0X0C, 12, 13)
                    name = mod_name.String
                    print (name)
                    if name in Module_Names:
                        module3 = True
                        self.List_of_Modules.append(name)
                except AttributeError as err:
                    #print (err, '---> Module 3 Not Responding - Attribute Error')
                    pass
            
            for i in range(len(Module_Names)):
                if name == Module_Names[i]:
                    self.tab8 = Module_Classes[str(i)].Main(self.nb, self.Module3, Module_Pubsub[2], Datalog_Pubsub[2])
                    self.tab9 = Module_Classes[str(i)].Settings(self.nb, self.Module3, Module_Pubsub[2], Alarm_Pubsub[2])

                    self.button5 = wx.Button(self.tab8, label = 'Settings', pos = (w-330+adj, 295), size = (240, 30), id = 13)
                    self.button5.Bind(wx.EVT_BUTTON, self.OnSettings3)
                    self.button5.SetForegroundColour('black')
                    self.button5.SetBackgroundColour('light blue')

                    self.button6 = wx.Button(self.tab9, label = 'Control', pos = (535, 295), size = (240, 30), id = 12)
                    self.button6.Bind(wx.EVT_BUTTON, self.GotoTestModule3)
                    self.button6.SetForegroundColour('black')
                    self.button6.SetBackgroundColour('light blue')  

                    self.Mod3_AcquisitionID = self.TabID
                    self.TabID = self.TabID+1
                    self.Mod3_settingsID = self.TabID
                    self.TabID = self.TabID+1
                    
                    self.nb.InsertPage(self.Mod3_AcquisitionID, self.tab8, name)
                    self.nb.InsertPage(self.Mod3_settingsID, self.tab9, name)
                    self.nb.SetSelection(self.Mod3_settingsID)
                    self.tab8.Hide()
                    
                    self.nb.SetPageImage(self.Mod3_settingsID, self.Image1) # Connected
                    self.nb.SetPageImage(self.Mod3_AcquisitionID, self.Image1) # Connected
                    #print ('Module name is %s'%name)    
        else:
            self.tab7 = TabThree(self.nb)
            self.nb.AddPage(self.tab7, "Module 3")
            self.nb.SetPageImage(self.TabID, self.Image2)
            self.TabID = self.TabID+1
            self.List_of_Modules.append("Not Found")
        
        
        if GPIO.input(Modulepins[3]) == 0:
            #time.sleep(5)
            #print ('module 4 found')
            module4 = False
            
            while module4 is False:
                try:
                    mod_name = mmis.Functions.GETTransactions(0X0C, 7, 3)
                    name = mod_name.String
                    if name in Module_Names:
                        module4 = True
                        self.List_of_Modules.append(name)
                except AttributeError as err:
                    #print (err, '---> Module 4 Not Responding - Attribute Error')
                    pass
            
            for i in range(len(Module_Names)):
                if name == Module_Names[i]:
                    self.tab11 = Module_Classes[str(i)].Main(self.nb, self.Module4, Module_Pubsub[3], Datalog_Pubsub[3])
                    self.tab12 = Module_Classes[str(i)].Settings(self.nb, self.Module4, Module_Pubsub[3], Alarm_Pubsub[3])

                    self.button7 = wx.Button(self.tab11, label = 'Settings', pos = (w-330+adj, 295), size = (240, 30), id = 13)
                    self.button7.Bind(wx.EVT_BUTTON, self.OnSettings4)
                    self.button7.SetForegroundColour('black')
                    self.button7.SetBackgroundColour('light blue')

                    self.button8 = wx.Button(self.tab12, label = 'Control', pos = (535, 295), size = (240, 30), id = 12)
                    self.button8.Bind(wx.EVT_BUTTON, self.GotoTestModule4)
                    self.button8.SetForegroundColour('black')
                    self.button8.SetBackgroundColour('light blue')

                    self.Mod4_AcquisitionID = self.TabID
                    self.TabID = self.TabID+1
                    self.Mod4_settingsID = self.TabID
                    self.TabID = self.TabID+1

                    self.nb.InsertPage(self.Mod4_AcquisitionID, self.tab11, name)
                    self.nb.InsertPage(self.Mod4_settingsID, self.tab12, name)
                    self.nb.SetSelection(self.Mod4_settingsID)
                    self.tab11.Hide()
                    
                    self.nb.SetPageImage(self.Mod4_AcquisitionID, self.Image1) # Connected
                    self.nb.SetPageImage(self.Mod4_settingsID, self.Image1) # Connected
                    #print ('Module name is %s'%name)    

        else:
            self.tab10 = TabFour(self.nb)
            self.nb.AddPage(self.tab10, "Module 4")
            self.nb.SetPageImage(self.TabID, self.Image2)
            self.TabID = self.TabID+1
            self.List_of_Modules.append("Not Found")
            
        
    def OnSettings4(self, e):
        ''' This function simply hides the Controls page of the module from slot 4 '''
        if self.tab11.IsShown():
            self.tab11.Hide()
            self.tab12.Show()
            self.nb.SetSelection(self.Mod4_settingsID)
            self.nb.Layout()
        else:
            self.tab12.Hide()
            self.tab11.Show()
        

    def GotoTestModule4(self, e):
        ''' This function simply hides the Settings page of the module from slot 4 '''
        if self.tab12.IsShown():
            self.tab12.Hide()
            self.tab11.Show()
            self.nb.SetSelection(self.Mod4_AcquisitionID)
            self.nb.Layout()
        else:
            self.tab11.Hide()
            self.tab12.Show()

    def OnSettings3(self, e):
        ''' This function simply hides the Controls page of the module from slot 3 '''
        if self.tab8.IsShown():
            self.tab9.Show()
            self.tab8.Hide()
            self.nb.SetSelection(self.Mod3_settingsID)
            self.nb.Layout()
        else:
            self.tab9.Hide()
            self.tab8.Show()
    
    def GotoTestModule3(self, e):
        ''' This function simply hides the Settings page of the module from slot 3 '''
        if self.tab9.IsShown():
            self.tab8.Show()
            self.tab9.Hide()
            self.nb.SetSelection(self.Mod3_AcquisitionID)
            self.nb.Layout()
        else:
            self.tab8.Hide()
            self.tab9.Show()

    def OnSettings2(self, e):
        ''' This function simply hides the Controls page of the module from slot 2 '''
        if self.tab5.IsShown():
            self.tab6.Show()
            self.tab5.Hide()
            self.nb.SetSelection(self.Mod2_settingsID)
            self.nb.Layout()
        else:
            self.tab6.Hide()
            self.tab5.Show()
    
    def GotoTestModule2(self, e):
        ''' This function simply hides the Settings page of the module from slot 2 '''
        if self.tab6.IsShown():
            self.tab5.Show()
            self.tab6.Hide()
            self.nb.SetSelection(self.Mod2_AcquisitionID)
            self.nb.Layout()
        else:
            self.tab5.Hide()
            self.tab6.Show()

    def OnSettings1(self, e):
        ''' This function simply hides the Controls page of the module from slot 1 '''
        if self.tab2.IsShown():
            self.tab3.Show()
            self.tab2.Hide()
            self.nb.SetSelection(self.Mod1_settingsID)
            self.nb.Layout()
        else:
            self.tab3.Hide()
            self.tab2.Show()
    
    def GotoTestModule1(self, e):
        ''' This function simply hides the Settings page of the module from slot 1 '''
        if self.tab3.IsShown():
            self.tab2.Show()
            self.tab3.Hide()
            self.nb.SetSelection(self.Mod1_AcquisitionID)
            self.nb.Layout()
        else:
            self.tab2.Hide()
            self.tab3.Show()
        
    def OnModule4(self,e):
        ''' This function sets the tick mark or cross mark on the GUI pages to indicate whether the module has been detected in the slot 4 '''
        if(GPIO.input(5)):
            self.nb.SetPageImage(0, self.Image2)
            print ("Module4 Triggered (High)")
        else:
            self.nb.SetPageImage(0, self.Image1)
            print ("Module4 Triggered (Low)")
        
    def OnModule3(self,e):
        ''' This function sets the tick mark or cross mark on the GUI pages to indicate whether the module has been detected in the slot 3 '''
        if(GPIO.input(11)):
            self.nb.SetPageImage(1, self.Image2)
            print ("Module3 Triggered (High)")
        else:
            self.nb.SetPageImage(1, self.Image1)
            print ("Module3 Triggered (Low)")
        
    def OnModule2(self,e):
        ''' This function sets the tick mark or cross mark on the GUI pages to indicate whether the module has been detected in the slot 2 '''
        if(GPIO.input(15)):
            self.nb.SetPageImage(2, self.Image2)
            print ("Module2 Triggered (High)")
        else:
            self.nb.SetPageImage(2, self.Image1)
            print ("Module2 Triggered (Low)")
        
    def OnModule1(self,e):
        ''' This function sets the tick mark or cross mark on the GUI pages to indicate whether the module has been detected in the slot 1 '''
        if(GPIO.input(35)):
            self.nb.SetPageImage(3, self.Image2)
            print ("Module1 Triggered (High)")
        else:
            self.nb.SetPageImage(3, self.Image1)
            print ("Module1 Triggered (Low)")
         
    def OnAbout(self,e):
        ''' This function describes the information about the developers of the project '''
        self.about=wx.adv.AboutDialogInfo()
        self.about.SetName("Modular Microscope Instrument "+Version)
        self.about.SetCopyright("(c) 2017 DEMO")
        #self.about.SetWebSite("http://www.demo.tudelft.nl/")
        self.about.AddDeveloper("Rajeev Bheemireddy")
        self.about.AddDeveloper("Danny de Gans")
        self.about.AddDeveloper("Lars Leenheer")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.ImgFolder+"DEMOico.ico", wx.BITMAP_TYPE_ANY))
        self.about.SetIcon(icon)
        wx.adv.AboutBox(self.about)
        
    def OnExit(self,e):
        ''' This function is present from the menu bar and is used to exit from the application '''
        for i in range(4):
            if (self.List_of_Modules[i] == 'Sample Heater'):
                mmis.Functions.GETTransactions(0X02, self.Com_Pins[i][0], self.Com_Pins[i][1])
            elif (self.List_of_Modules[i] == 'Dual Heater'):
                mmis.Functions.GETTransactions(0X03, self.Com_Pins[i][0], self.Com_Pins[i][1])
                mmis.Functions.GETTransactions(0X04, self.Com_Pins[i][0], self.Com_Pins[i][1])
            elif (self.List_of_Modules[i] == 'LiqN2 Control'):
                mmis.Functions.GETTransactions(0X03, self.Com_Pins[i][0], self.Com_Pins[i][1])
                mmis.Functions.GETTransactions(0X04, self.Com_Pins[i][0], self.Com_Pins[i][1])
            elif (self.List_of_Modules[i] == 'Cryo Heater'):
                mmis.Functions.GETTransactions(0X03, self.Com_Pins[i][0], self.Com_Pins[i][1])
        print ("Safe Shutdown Process Executed")
        x = self.nb.GetPageCount()
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write("Program closed at " + str(datetime.now()) + "\n")
            f.close()
        except TypeError:
            pass
        self.mc.delete("UE")
        self.tab0.Close_LogSheet()
        GPIO.cleanup()
        for i in range(x):
            self.nb.DeletePage(i)
        self.Destroy()

    def Onclosewindow(self, e):
        ''' This function is executed when the close button mark is pressed on the Applications GUI'''
        for i in range(4):
            if (self.List_of_Modules[i] == 'Sample Heater'):
                mmis.Functions.GETTransactions(0X02, self.Com_Pins[i][0], self.Com_Pins[i][1])
            elif (self.List_of_Modules[i] == 'Dual Heater'):
                mmis.Functions.GETTransactions(0X03, self.Com_Pins[i][0], self.Com_Pins[i][1])
                mmis.Functions.GETTransactions(0X04, self.Com_Pins[i][0], self.Com_Pins[i][1])
            elif (self.List_of_Modules[i] == 'LiqN2 Control'):
                mmis.Functions.GETTransactions(0X03, self.Com_Pins[i][0], self.Com_Pins[i][1])
                mmis.Functions.GETTransactions(0X04, self.Com_Pins[i][0], self.Com_Pins[i][1])
            elif (self.List_of_Modules[i] == 'Cryo Heater'):
                mmis.Functions.GETTransactions(0X03, self.Com_Pins[i][0], self.Com_Pins[i][1])
        print ("Safe Shutdown Process Executed")
        x = self.nb.GetPageCount()
        try:
            self.UEfile = self.mc.get("UE")
            f = open(self.UEfile, "a")
            f.write("Program closed at " + str(datetime.now()) + "\n")
            f.close()
        except TypeError:
            pass
        self.mc.delete("UE")
        self.tab0.Close_LogSheet()
        GPIO.cleanup()
        for i in range(x):
            self.nb.DeletePage(i)
        self.Destroy()
    
    def OnOpen(self,e):
        ''' Open a file function - currently not used '''
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()

    def OnStartup(self,e):
        ''' menu help function for the general usage of the device '''
        T1 = "1) Turn on the Machine and wait until the login page is loaded \n"
        T2 = "2) Login Details:\t name: pi\tpassword: heater007 \n"
        T3 = "3) Start the program by double clicking the MMI icon on Desktop or menu-->others-->MMI \n"
        T5 = "4) Once the application is loaded, you will see the SAVE AS window which is used to save the log file \n"
        T6 = "5) click on Save if you need a log file otherwise cancel \n"
        T7 = "6) Then it is redirected to START tab \n"
        T8 = "7) You can also Create a log file here if you miss out on the startup \n"
        T9 = "8) Type a desired file name in create log file window and click on CREATE \n"
        T10 = "9) You will be redirected to SAVE AS window and click on save on desired location \n"
        T11 = "10) Then click on START LOGGING button to start logging the data \n"
        T12 = "\n Software Update:\n"
        T13 = "1) To update the software go to raspberry menu --> other --> system update\n"
        T14 = "2) Click on systemupdate and wait for the update to happen\n"

        T15 = "\n How to recover the Image when the SD card is corrupt?\n"
        T16 = "1) Once the machine is turned on, wait for the page that indicates click Shift to go into recovery mode\n"
        T17 = "2) Click SHIFT to get into recovery mode\n"
        T18 = "3) You will see the Image name DEMO 0.1 (Debian Stretch lite)\n"
        T19 = "4) Mark on the check box and click on Install, it will take 8-9 minutes for the recovery to happen\n"

        
        Text = T1 + T2 +T3+T5+T6+T7+T8+T9+T10+T11+T12+T13+T14+T15+T16+T17+T18+T19
        dlg = ScrolledMessageDialog(self,Text, "General Help", size=(600,430))
        dlg.ShowModal()
        dlg.Destroy()

    def Onsampleheater(self,e):
        ''' menu help function for the Sample Heater module '''
        T0 = "PROCEDURE: \n"
        T1 = "1) Set the Parameter A (default value - 0.250)\n"
        T2 = "2) Set Ambient Temperature Parameter T-Amb (default value - 20 Centigrade)\n"
        T3 = "3) Click on green icon START CALIBRATION and the icon turns red\n"
        T4 = "4) Wait until the icon turns green color again (usually takes around 5 seconds)\n"
        T5 = "5) Now the calibration is finished\n"
        T6 = "6) Set the value T-Max (default value - 800 Centigrade)\n" 
        T7 = "7) Then click on Control icon to start controlling heater\n"
        T8 = "8) Click on the START to start controlling \n"
        T9 = "9) set the desired set point and click on SET VALUE\n"
        T10 = "10) X-AXIS length can be adjusted to desired value and click enter(indicates the amount of samples that can be seen on the graph)\n"
        T11 = "11) Save graph icon saves the current image of the graph in .PNG format\n"
        T12 = "12) Click on Settings to go back to the settings window\n"
        T15 = "\n"
        T16 = "ERROR DEBUG:\n"
        T17 = "1) When there is an error, the red led on the front panel goes bright\n"
        T18 = "2) Go to START tab to find out from which module the error is coming from\n" 
        T19 = "3) Go to Settings tab of respective module and click on Alarm reset if you figured out the error\n"
        T20 = "\n When does Sample Heater give an Error Alarm?\n"
        T21 = "if the cable connections are wrong" 

        Text = T0+T1 + T2 +T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+T15+T16+T17+T18+T19+T20+T21
        dlg = ScrolledMessageDialog(self,Text, "Sample Heater Help", size=(600,430))
        dlg.ShowModal()
        dlg.Destroy()

    def Ondualheater(self,e):
        ''' menu help function for the Dual Heater module '''
        T0 = "PROCEDURE: \n"
        T1 = "1) Ambient and Nitrogen Control default proportional constant and Integral constants are already programmed\n"
        T2 = "2) If you wish to use the default parameters, you dont need to modify anything\n"
        T3 = "3) You can request the default parameters by clicking on GET INFO\n"
        T4 = "4) If you wish to modify, change each value and click on SET icon\n"
        T5 = "5) Go to Control tab if you have the desired settings for the experiment\n"
        T6 = "6) The values that you see on the icons SET-TAMB and SET-TN2 are the default values\n" 
        T7 = "7) If you wish to change those, change the values and click on SET-TAMB and SET-TN2 icons\n"
        T8 = "8) Now you should see the updated values on those SET-TAMB and SET-TN2 icons\n"
        T9 = "9) Now start the control by clicking on START AMB and START N2 icons. \n"
        T10 = "10) Click on Save graph to save the current graph image\n"
        T11 = "11) The indicators TA and TN2 indicate the ambient and Nitrogen temperature\n"
        T12 = "12) The indicators IA and IN2 indicate the amount of current consumed respectively\n"
        T13 = "13) The indicators PA and PN2 indicate the amount of power consumed respectively\n"
        T14 = "14) Click on Settings to modify the parameters \n"
        T15 = "\n"
        T16 = "ERROR DEBUG:\n"
        T17 = "1) When there is an error, the red led on the front panel goes bright\n"
        T18 = "2) Go to START tab to find out from which module the error is coming from\n" 
        T19 = "3) Go to Settings tab of respective module and click on Alarm reset if you figured out the error\n"
        T20 = "\n When does DualHeater give an Error Alarm?\n"
        T21 = "if the cable connections are wrong" 

        
        Text = T0+T1 + T2 +T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+T13+T14+T15+T16+T17+T18+T19+T20+T21
        dlg = ScrolledMessageDialog(self,Text, "Dual Heater Help", size=(600,430))
        dlg.ShowModal()
        dlg.Destroy()

    def OnLN2Control(self,e):
        ''' menu help function for the Liquid nitrogen module '''
        T0 = "PROCEDURE: \n"
        T1 = "1) Nitrogen Level control Proportional constant is default set to 50 \n"
        T2 = "2) If you wish to use the default parameters, you dont need to modify anything else change and click on set button\n"
        T3 = "3) Click on Start Measuring icon to see what the capacitance value is. Note down the capacitance value when the sensor is fully immersed in Liquid N2 and when it is completely outside.\n"
        T4 = "4) Set the Anti Rewound Limit (ARL) value to the capacitance value when the sensor is completely outside + 0.2 (ARL is to make sure that the N2 control stops when the dewar runs out of LiqN2).\n"
        T5 = "5) Click on Forward and Reverse button to set the height of the weights dropped by the motor manually during the start of experiment\n"
        T6 = "6) Set the Upper Limit to the value of capacitive sensor when it is fully immersed - 0.1 and Lower Limit to the value when it is completely outside + 0.1\n" 
        T7 = "7) Set the Slope at which rate you would like to change the set point of LiqN2 in time only if you wish to do the slope control \n"
        T8 = "8) Now click on control to leave the settings tab and go to Control tab. \n"
        T9 = "9) Set the desired value of the Capacitance which should be between the value when it is fully immersed and when it is completely outside. \n"
        T10 = "10) Click on the start button under LiqN2 control\n"
        T11 = "11) Click on Save graph to save the current graph image\n"
        T12 = "12) The indicators capacitance and current indicate the current capacitance of the sensor and current consumption of the Motor respectively\n"
        T13 = "13) X-AXIS length can be adjusted to desired value and click enter(indicates the amount of samples that can be seen on the graph)\n"
        T14 = "14) Click on Settings to modify the initialized parameters. Before changing the settings first stop the control \n"
        T15 = "\n"
        T16 = "ERROR DEBUG:\n"
        T17 = "1) When there is an error, the red led on the front panel goes bright\n"
        T18 = "2) Go to START tab to find out from which module the error is coming from\n" 
        T19 = "3) Go to Settings tab of respective module and click on Alarm reset if you figured out the error\n"
        T20 = "\n When does LiqN2 control give an Error Alarm?\n"
        T21 = "if the cable connections are wrong" 

        
        Text = T0+T1 + T2 +T3+T4+T5+T6+T7+T8+T9+T10+T11+T12+T13+T14+T15+T16+T17+T18+T19+T20+T21
        dlg = ScrolledMessageDialog(self,Text, "LN2 height Control Help", size=(600,430))
        dlg.ShowModal()
        dlg.Destroy()
    
    def __del__(self):
        """ Class delete event: don't leave timer hanging around! """
        self.timer.stop()
        del self.timer
    
    def Notify(self):
        """ Timer event """
        self.t = time.localtime(time.time())
        self.st = time.strftime("%b-%d-%Y  %I:%M:%S", self.t)
        # --- could also use self.sb.SetStatusText
        self.SetStatusText(self.st, 2)


def StartGUI():
    ''' This functions starts the GUI and adjusts the size based on where it is opened either remotely or on MMI directly'''
    global w, adj
    app = wx.App(0)
    w,h = wx.GetDisplaySize() #global app,w,h,adj,frame
    if w>800:
        adj = 0
        w = w-300
        frame = MainWindow(None, -1, "Modular Microscope Instrument "+Version, w, h-600, adj)
    else:
        adj = 50
        frame = MainWindow(None, -1, "Modular Microscope Instrument "+Version, w, h, adj)
    frame.Show()
    app.MainLoop()
        
if __name__ == '__main__':
    StartGUI()
    
    
