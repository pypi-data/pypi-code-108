#!/usr/bin/env python3
import subprocess
import sys
import os, fnmatch
import wx
import urllib.request
from bs4 import BeautifulSoup

#results = find(pattern, path)

class UPDATE(wx.Frame):
    def __init__(self, parent):
        """
        
        Checks for the latest updates from USB and Internet 

        Parameters
        ----------
        parent : Wx frames from WX library for GUI

        Returns
        -------
        None.

        """
        wx.Frame.__init__(self,parent,wx.ID_ANY,"Check Updates",size=(400,230), style=wx.DEFAULT_FRAME_STYLE)

        self.path = '/media'
        self.pattern = '*.tar.gz'
        self.cmd = 'pip3 install '

        self.redraw_timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.find, self.redraw_timer1) #Timer event occurs every few milliseconds that it was set 

        self.redraw_timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.checkonlineupdate, self.redraw_timer2)
        #self.redraw_timer2.Start(1000)

        self.font1 = wx.Font(18, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        self.Function_back()

    def Function_back(self):
        """
        Holds two buttons for the online and USB update

        Returns
        -------
        None.

        """
            
        self.button1 = wx.Button(self, label="Check Online Update", pos=(50, 50), size = (300,40), id = -1)
        #self.button1.SetFont(self.font2)
        self.button1.Bind(wx.EVT_BUTTON, self.checkonlineupdate)
        self.button1.SetForegroundColour('black')
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        self.button2 = wx.Button(self, label="Check USB update", pos=(50, 120), size = (300,40), id = -1)
        #self.button2.SetFont(self.font2)
        self.button2.Bind(wx.EVT_BUTTON, self.find)
        self.button2.SetForegroundColour('black')
        self.button2.SetBackgroundColour(wx.Colour(211,211,211))

        #self.lblname1 = wx.StaticText(self, label = "Checking online update", pos = (80,105))
        #self.lblname1.SetFont(self.font1)

    def checkonlineupdate(self, e):
        """
        Checks for the online update by checking the internet connection first and then parsing the webpage 
        https://pypi.org/project/mmis to find out for the available version.

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.
        
        Raised:
            URL error: Internet connectivity not found

        """
        try:
            #self.lblname1.Destroy()
            self.button1.Destroy()
            self.button2.Destroy()
            urllib.request.urlopen("http://www.google.com")
            #onlineversion = os.popen('pip3 search mmis').read()
            #onlineversion = float(onlineversion[6:10])
            contents = os.popen('wget -O - https://pypi.org/project/mmis | grep -i [mmis]').read()
            soup = BeautifulSoup(contents, 'lxml')
            print (soup.h1.contents[0])
            onlineversion = float((' '.join(soup.h1.contents[0].split())).split(" ")[1])
            
            self.local = os.popen('pip3 show mmis | grep Version').read()
            if len(self.local) == 0:
                self.local = 'not found'
                self.currentversion = 0.0
            else:
                #self.currentversion = float(self.local[9:13])
                self.currentversion = float(self.local.split(" ")[1])

            if (onlineversion <= self.currentversion):
                self.lblname1 = wx.StaticText(self, label = "already upto date", pos = (80,105))
                #self.lblname1.SetFont(self.font1)
            else:
                self.lblname1 = wx.StaticText(self, label = "online update found", pos = (80,105))
                #self.lblname1.SetFont(self.font1)

            currentversioninstalled = "existing installer "+ self.local
            self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
            #self.lblname0.SetFont(self.font1)
            self.lblname = wx.StaticText(self, label = "Version available:", pos = (20,65))
            #self.lblname.SetFont(self.font2)
            self.version = wx.TextCtrl(self, size=(150,30), pos = (200,60), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
            self.version.SetValue(str(onlineversion))

            self.button1 = wx.Button(self, label="Update", pos=(170, 150), size = (200,40), id = -1)
            #self.button1.SetFont(self.font2)
            self.button1.Bind(wx.EVT_BUTTON, self.ON_onlineupdate)
            self.button1.SetForegroundColour('black')
            self.button1.SetBackgroundColour(wx.Colour(211,211,211))

            self.button2 = wx.Button(self, label="Back", pos=(10, 150), size = (160,40), id = -1)
            #self.button2.SetFont(self.font2)
            self.button2.Bind(wx.EVT_BUTTON, self.ON_Back)
            self.button2.SetForegroundColour('black')
            self.button2.SetBackgroundColour(wx.Colour(211,211,211))
                
        except:
            #self.lblname1.Destroy()
            self.lblname0 = wx.StaticText(self, label = "Internet connection not found \n looking for updates in external drive", pos = (30,65))
            #self.lblname0.SetFont(self.font2)

            self.button3 = wx.Button(self, label="Back", pos=(10, 150), size = (160,40), id = -1)
            #self.button3.SetFont(self.font2)
            self.button3.Bind(wx.EVT_BUTTON, self.ON_Back_except)
            self.button3.SetForegroundColour('black')
            self.button3.SetBackgroundColour(wx.Colour(211,211,211))
            #self.redraw_timer1.Start(1000)

    def find(self, e):
        """
        Checks for the updates from USB. Looks for the file with the name mmis and parses its name
        to find out the version number

        Parameters
        ----------
        e : event
            Button press event.

        Returns
        -------
        None.

        """
        self.button1.Destroy()
        self.button2.Destroy()
        self.lblname1 = wx.StaticText(self, label = "Checking USB update", pos = (80,105))
        #self.lblname1.SetFont(self.font1)
        #self.redraw_timer1.Stop()

        self.local = os.popen('pip3 show mmis | grep Version').read()
        print (self.local)
        if len(self.local) == 0:
            self.local = 'not found'
            self.currentversion = 0.0
        else:
            self.currentversion = float(self.local[9:13])
            
        self.result = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                if fnmatch.fnmatch(name, self.pattern):
                    self.result.append(os.path.join(root, name))

        self.mmis = [s for s in self.result if 'mmis-' in s]
        print (self.mmis)
        self.lblname1.Destroy()
        
        if (len(self.mmis)>0):
            #self.lblname.Destroy()
            self.mmis.sort()
            print (self.mmis)
            self.latestversion = self.mmis[len(self.mmis)-1]
            print (self.latestversion)
            version = self.latestversion[(len(self.latestversion)-11):]
            version = float(version[:4])
            print (version)
            if (version <= self.currentversion):
                self.lblname1 = wx.StaticText(self, label = "already upto date", pos = (80,105))
                #self.lblname1.SetFont(self.font1)
            else:
                self.lblname1 = wx.StaticText(self, label = "Click to update", pos = (80,105))
                #self.lblname1.SetFont(self.font1)
            
            currentversioninstalled = "existing installer "+ self.local
            self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
            #self.lblname0.SetFont(self.font1)
            self.lblname = wx.StaticText(self, label = "Version available:", pos = (20,65))
            #self.lblname.SetFont(self.font2)
            self.version = wx.TextCtrl(self, size=(150,30), pos = (200,60), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
            self.version.SetValue(str(version))
            
            self.button1 = wx.Button(self, label="Update", pos=(190, 150), size = (160,40), id = -1)
            #self.button1.SetFont(self.font2)
            self.button1.Bind(wx.EVT_BUTTON, self.ON_update)
            self.button1.SetForegroundColour('black')
            self.button1.SetBackgroundColour(wx.Colour(211,211,211))

            self.button2 = wx.Button(self, label="Back", pos=(10, 150), size = (160,40), id = -1)
            #self.button2.SetFont(self.font2)
            self.button2.Bind(wx.EVT_BUTTON, self.ON_Back)
            self.button2.SetForegroundColour('black')
            self.button2.SetBackgroundColour(wx.Colour(211,211,211))
            
        else:
            #self.lblname.Destroy()
            self.lblname0 = wx.StaticText(self, label = "pendrive not found", pos = (20,15))
            #self.lblname0.SetFont(self.font1)

            self.button3 = wx.Button(self, label="Back", pos=(10, 150), size = (160,40), id = -1)
            #self.button3.SetFont(self.font2)
            self.button3.Bind(wx.EVT_BUTTON, self.ON_Back_except)
            self.button3.SetForegroundColour('black')
            self.button3.SetBackgroundColour(wx.Colour(211,211,211))

    def ON_Back_except(self, e):
        """
        Back button to go to the homepage of the software update GUI from check updates through Internet

        Parameters
        ----------
        e : Event
            Button Press Event.

        Returns
        -------
        None.

        """
        self.button3.Destroy()
        self.lblname0.Destroy()
        self.Function_back()

    def ON_Back(self, e):
        """
        Back button to go to the homepage of the software update GUI from check updates through USB

        Parameters
        ----------
        e : Event
            Button Press Event.

        Returns
        -------
        None.

        """
        self.button1.Destroy()
        self.button2.Destroy()
        self.lblname.Destroy()
        self.lblname0.Destroy()
        self.lblname1.Destroy()
        self.version.Destroy()
        self.Function_back()
        
    def ON_update(self, e):
        """
        Executes to update the software from USB

        Parameters
        ----------
        e : event
            button press event.

        Returns
        -------
        None.

        """
        self.lblname1.Destroy()
        self.cmd = self.cmd + self.latestversion.replace(' ', '\ ')
        print (self.cmd)
        os.system(self.cmd)
        self.lblname0.Destroy()
        self.local = os.popen('pip3 show mmis | grep Version').read()
        print (self.local)
        if len(self.local) == 0:
            self.local = 'not found'
            self.newversion = 0.0
            self.lblname1 = wx.StaticText(self, label = "Update Failed", pos = (80,105))
            #self.lblname1.SetFont(self.font1)
            currentversioninstalled = "No existing installer found"
            self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
            #self.lblname0.SetFont(self.font1)
        else:
            self.newversion = float(self.local[9:13])
            if (self.newversion>self.currentversion):
                self.lblname1 = wx.StaticText(self, label = "Updated successfully", pos = (80,105))
                #self.lblname1.SetFont(self.font1)
                currentversioninstalled = "existing installer "+ self.local
                self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
                #self.lblname0.SetFont(self.font1)
            else:
                self.lblname1 = wx.StaticText(self, label = "Updated Failed", pos = (80,105))
                #self.lblname1.SetFont(self.font1)
                currentversioninstalled = "existing installer "+ self.local
                self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
                #self.lblname0.SetFont(self.font1)

    def ON_onlineupdate(self, e):
        """
        Executes the online update

        Parameters
        ----------
        e : event
            button press event.

        Returns
        -------
        None.

        """
        self.lblname1.Destroy()
        os.system('pip3 install mmis')
        self.lblname1 = wx.StaticText(self, label = "Updated successfully", pos = (80,105))
        #self.lblname1.SetFont(self.font1)

        self.lblname0.Destroy()
        self.local = os.popen('pip3 show mmis | grep Version').read()
        currentversioninstalled = "existing installer "+ self.local
        self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
        #self.lblname0.SetFont(self.font1)


def StartTest():
    """
    Starts the GUI

    Returns
    -------
    None.

    """
    app1 = wx.App(None)
    frame1 = UPDATE(None)
    frame1.Show()
    frame1.Centre()
    app1.MainLoop()
        
if __name__ == '__main__':
    StartTest()
