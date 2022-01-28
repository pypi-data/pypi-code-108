# from threading import Thread
# import wx
# from wx.lib.pubsub import pub
# import time
# class WorkThread(Thread):
#
#     def __init__(self):
#         """Init Worker Thread Class."""
#         Thread.__init__(self)
#         self.stop_work_thread = 0
#         self.start()  # start the thread
#
#     def run(self):
#         for i in range(10):
#             if self.stop_work_thread == 1:
#                 break
#             time.sleep(1)
#             val = 100 / 10
#             wx.CallAfter(pub.sendMessage, "update", step=val)
#         wx.CallAfter(pub.sendMessage, "finish")
#         return
#
#     def stop(self):
#         self.stop_work_thread = 1
#
# class ProgressDialog(wx.Dialog):
#     def __init__(self,parent):
#         wx.Dialog.__init__(self, parent)
#         self.parent = parent
#         self.abort = False
#         self.progress = 0
#
#         bSizer2 = wx.BoxSizer(wx.VERTICAL)
#         self.gauge = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
#         self.gauge.SetValue(0)
#
#         self.m_button1 = wx.Button(self, wx.ID_ANY, u"Stop Training", wx.DefaultPosition, wx.DefaultSize, 0)
#         bSizer2.Add(self.gauge, 0, 0, 5)
#         bSizer2.Add(self.m_button1, 0, 0, 5)
#
#         self.SetSizer(bSizer2)
#         self.Layout()
#         self.Centre(wx.BOTH)
#
#         ## Connect Events
#
#         self.m_button1.Bind(wx.EVT_BUTTON, self.on_cancel)
#         pub.subscribe(self.updateProgress, "update")
#         pub.subscribe(self.on_finish, "finish")
#
#     def updateProgress(self, step):
#         self.progress += step
#         self.gauge.SetValue(self.progress)
#
#     def on_cancel(self, event):
#         """Cancels the conversion process"""
#         self.parent.work.stop()
#         self.parent.work.join()
#         pub.unsubscribe(self.updateProgress, "update")
#         pub.unsubscribe(self.on_finish, "finish")
#         self.Destroy()
#         # pub.unsubscribe(self.if_abort, 'cancel')
#
#     def on_finish(self):
#         """conversion process finished"""
#         pub.unsubscribe(self.updateProgress, "update")
#         pub.unsubscribe(self.on_finish, "finish")
#         self.Close()
#
#     def __del__(self):
#         pass
#
#
# ########################################################################################
#
# class MainFrame(wx.Frame):
#     # ----------------------------------------------------------------------
#     def __init__(self,parent):
#         wx.Frame.__init__(self,parent)
#         # Add a panel so it looks the correct on all platforms
#         self.panel = wx.Panel(self, wx.ID_ANY)
#         self.btn = btn = wx.Button(self.panel, label="Start Thread")
#         btn.Bind(wx.EVT_BUTTON, self.onButton)
#
#         sizer = wx.BoxSizer(wx.VERTICAL)
#         sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)
#         self.panel.SetSizer(sizer)
#
#     # ----------------------------------------------------------------------
#     def onButton(self, event):
#         btn = event.GetEventObject()
#         btn.Disable()
#         self.panel.work = WorkThread()
#         self.dlg = ProgressDialog(self.panel)
#         self.dlg.ShowModal()
#         btn.Enable()
#
# app = wx.App()
# frame = MainFrame(None)
# frame.Show(True)
# # start the applications
# app.MainLoop()

import wx
from openlabcluster.gui.train_network import ImagePanel
class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)

        self.panel = wx.Panel(self)

        # create controls
        self.cntrlPanel = wx.Panel(self.panel)
        stc1 = wx.StaticText(self.cntrlPanel, label="wow it works")
        stc2 = wx.StaticText(self.cntrlPanel, label="yes it works")
        btn = wx.Button(self.cntrlPanel, label="help?")
        btn.Bind(wx.EVT_BUTTON, self._onShowHelp)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(stc1)
        sizer.Add(stc2)
        sizer.Add(btn)
        self.cntrlPanel.SetSizer(sizer)

        # create help panel
        self.helpPanel = wx.Panel(self.panel)
        self.stcHelp = wx.StaticText(self.helpPanel, label="help help help\n"*8)
        btn = wx.Button(self.helpPanel, label="close[x]")
        btn.Bind(wx.EVT_BUTTON, self._onShowCntrls)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.stcHelp)
        sizer.Add(btn)
        self.helpPanel.SetSizer(sizer)

        self.helpPanel.Hide()
        self.helpPanel.Raise()
        self.helpPanel.SetBackgroundColour((240,250,240))

        self.Bind(wx.EVT_SIZE, self._onSize)

        self._onShowCntrls(None)

    def _onShowHelp(self, event):
        self.helpPanel.SetPosition((0,0))
        self.helpPanel.Show()
        self.cntrlPanel.Hide()

    def _onShowCntrls(self, event):
        self.cntrlPanel.SetPosition((0,0))
        self.helpPanel.Hide()
        self.cntrlPanel.Show()

    def _onSize(self, event):
        event.Skip()
        self.helpPanel.SetSize(self.GetClientSize())
        self.cntrlPanel.SetSize(self.GetClientSize())

app = wx.App(False)
frame = MyFrame()
frame.Show()
app.SetTopWindow(frame)
app.MainLoop()

