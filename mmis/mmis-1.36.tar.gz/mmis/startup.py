#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import wx
import distro
#ImgFolder = '/usr/local/lib/python3.5/dist-packages/mmis/Images/' 
#ImgFolder = '/home/pi/Desktop/package/mmis/Images/'

class TabOne(wx.Frame):
    def __init__(self, parent):
        """
        This is start up image that pops up when the mmi software is started and destroys within 10 seconds

        Parameters
        ----------
        parent : Wx
            DESCRIPTION.

        Returns
        -------
        None.

        """
        wx.Frame.__init__(self,parent,wx.ID_ANY,"Loading",size=(400,400), style=wx.DEFAULT_FRAME_STYLE^(~wx.CLOSE_BOX))
        self.ImgFolder = '/home/pi/.local/lib/python3.7/site-packages/mmis/Images/'
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Onclosewindow, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 
        self.redraw_timer.Start(10000)
        
        myserial, model = self.getserial()
        dist = float(distro.linux_distribution()[1])
        if dist < 10:
            self.ImgFolder = '/home/pi/.local/lib/python3.5/site-packages/mmis/Images/'
            
        self.Logo = wx.StaticBitmap(self, -1, pos = (50,50))
        self.image_file = self.ImgFolder+'MMIstart.png'
        self.Logo.SetFocus()
        self.Logo.SetBitmap(wx.Bitmap(self.image_file))

    def getserial(self):
        """
        Extract serial from cpuinfo file

        Returns
        -------
        cpuserial : string
            uniques serial id of the raspebrry pi.
        model : string
            raspberry pis model number.

        """
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
              if line[0:6]=='Serial':
                cpuserial = line[10:26]
              if line[0:5]=='Model':
                model = line[9:23]
            f.close()
        except:
            cpuserial = "ERROR000000000"

        return cpuserial, model        

    def Onclosewindow(self, e):
        self.Destroy()

def StartTest():
    """
    Starts the GUI

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
