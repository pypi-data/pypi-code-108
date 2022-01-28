"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import os

import wx
import wx.adv

import openlabcluster

media_path = os.path.join(openlabcluster.__path__[0], "gui", "media")
dlc = os.path.join(media_path, "GUIplot.png")

def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result

class Welcome(wx.Panel):
    def __init__(self, parent, gui_size):
        h = gui_size[0]
        w = gui_size[1]
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, size=(h, w))
        ##         design the panel
        # sizer = wx.GridBagSizer(4, 2)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Add image of DLC

        icon = wx.StaticBitmap(self, -1, bitmap=wx.Bitmap(dlc))
        #icon.SetScaleMode(wx.StaticBitmap.ScaleMode.Scale_AspectFit)
        sizer.Add(icon, flag=wx.ALIGN_CENTRE | wx.ALL, border=10)
        # sizer.Add(icon, pos=(0, 0), span=(0, 8), flag=wx.EXPAND | wx.BOTTOM, border=10)
        line = wx.StaticLine(self)
        # sizer.Add(line, pos=(1, 0), span=(1, 8), flag=wx.EXPAND | wx.BOTTOM, border=10)
        sizer.Add(line,  flag=wx.EXPAND | wx.BOTTOM, border=10)

        # if editing this text make sure you add the '\n' to get the new line. The sizer is unable to format lines correctly.
        description = "DeepLabCluster™ is an open source tool for Unsupervised Action annotation and semi-supervised classification.\nTo get started, please click on the 'Manage Project'\n tab to create or load an existing project. \n "

        self.proj_name = wx.StaticText(self, label=description, style=wx.ALIGN_CENTRE)
        # sizer.Add(self.proj_name, pos=(2, 3), border=10)
        sizer.Add(self.proj_name, flag=wx.ALIGN_CENTRE, border=10)
        # sizer.AddGrowableCol(2)
        self.SetSizer(sizer)
        sizer.Fit(self)
