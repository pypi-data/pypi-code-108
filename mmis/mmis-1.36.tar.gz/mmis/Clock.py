#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import wx
import mmis.RealTimeClock as RTC
import time


class TabOne(wx.Frame):
    def __init__(self, parent):
        """
        Initializes the GUI for the clock syncing and checks if there is internet connectivity and syncs the time accordingly

        Parameters
        ----------
        parent : WX

        Returns
        -------
        None.

        """
        wx.Frame.__init__(self,parent,wx.ID_ANY,"Synchronize System Clock",size=(400,280), style=wx.DEFAULT_FRAME_STYLE)

        self.redraw_timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Ontimer1, self.redraw_timer1) #Timer event occurs every few milliseconds that it was set 
        self.redraw_timer1.Start(1000)
            
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Ontimer, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 
        self.font1 = wx.Font(18, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        self.lblname = wx.StaticText(self, label = "Checking in Progress and takes upto 20 seconds.......", pos = (40,45))
        #self.lblname.SetFont(self.font1)
        

    def Ontimer1(self, e):
        """
        Checks for internet connection and if:
            Connected: Syncs time from teh NTP server
            Not connected: Requests to sync manually by entering the time/date

        Parameters
        ----------
        e : Event
            Timer event.

        Returns
        -------
        None.

        """
        self.redraw_timer1.Stop()
        response = RTC.NTPservertoRTC()
        #print (response)
        #response = 'fhdjf'
        if (response == 'Connected'):
            self.lblname.Destroy()
            self.lblname = wx.StaticText(self, label = "Time Successfully Synced", pos = (20,45))
            #self.lblname.SetFont(self.font1)
            #self.Onclosewindow()
            
        else:
            self.lblname.Destroy()

            self.lblname0 = wx.StaticText(self, label = "Synchronize Time Manually", pos = (20,15))
            #self.lblname0.SetFont(self.font1)

            self.lblname = wx.StaticText(self, label = "Current system time:", pos = (20,55))
            #self.lblname.SetFont(self.font2)

            self.Currenttime = wx.TextCtrl(self, size=(150,30), pos = (200,50), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
            self.Currenttime.SetBackgroundColour('grey')

            self.lblname1 = wx.StaticText(self, label = "Current RTC time:", pos = (20,105))
            #self.lblname1.SetFont(self.font2)

            self.CurrentRTCtime = wx.TextCtrl(self, size=(150,30), pos = (200,100), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
            self.CurrentRTCtime.SetBackgroundColour('grey')

            self.redraw_timer.Start(1000)
            self.lblname1 = wx.StaticText(self, label = "Set system time:", pos = (20,155))
            #self.lblname1.SetFont(self.font2)
            self.Month = wx.TextCtrl(self, value = 'mm', size=(30,30), pos = (155,150), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)
            wx.StaticText(self, label = "/", pos = (187,155))
            self.Date = wx.TextCtrl(self, value = 'dd', size=(30,30), pos = (195,150), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)
            wx.StaticText(self, label = "/", pos = (227,155))
            self.Year = wx.TextCtrl(self, value = 'yy', size=(30,30), pos = (235,150), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)

            self.Hour = wx.TextCtrl(self, value = 'hh', size=(30,30), pos = (275,150), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)
            wx.StaticText(self, label = ":", pos = (308,155))
            self.Minute = wx.TextCtrl(self, value = 'mm', size=(30,30), pos = (315,150), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)
            wx.StaticText(self, label = ":", pos = (348,155))
            self.Second = wx.TextCtrl(self, value = 'ss', size=(30,30), pos = (355,150), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)

            self.button = wx.Button(self, label="Program Clock Time", pos=(170, 200), size = (200,40), id = -1)
            #self.button.SetFont(self.font2)
            self.button.Bind(wx.EVT_BUTTON, self.ON_Set)
            self.button.SetForegroundColour('black')
            self.button.SetBackgroundColour(wx.Colour(211,211,211))

    def ON_Set(self, e):
        """
        Programs the RTC with the date/time

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        
        RTC.writeyear(int(self.Year.GetValue()))
        RTC.writemonth(int(self.Month.GetValue()))
        RTC.writedate(int(self.Date.GetValue()))
        RTC.writehours(int(self.Hour.GetValue()))
        RTC.writeminutes(int(self.Minute.GetValue()))
        RTC.writeseconds(int(self.Second.GetValue()))
        time.sleep(3)
        RTC.RTCtoSystemClock()
        
    
    def Ontimer(self, e):
        """
        Timer event to read the current time/date from Real time clock and display it every second

        Parameters
        ----------
        e : event
            Timer event.

        Returns
        -------
        None.

        """
        current = time.localtime(time.time())
        ts = time.strftime("%D %H:%M:%S", current)
        currentRTC = RTC.RTCTime()
        #print (ts)
        self.CurrentRTCtime.SetValue(currentRTC)
        self.Currenttime.SetValue(ts)
        
    def Onclosewindow(self):
        """
        Closes the GUI safely without hanging in the background

        Returns
        -------
        None.

        """
        self.Destroy()

def StartTest():
    """
    Starts the GUI Application for setting the system clock

    Returns
    -------
    None.

    """
    app1 = wx.App(None)
    frame1 = TabOne(None)
    frame1.Show()
    frame1.Centre()
    app1.MainLoop()
        
if __name__ == '__main__':
    StartTest()
