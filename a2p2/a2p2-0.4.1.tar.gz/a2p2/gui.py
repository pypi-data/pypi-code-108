#!/usr/bin/env python

__all__ = []

import sys
import logging

from a2p2 import __release_notes__
from a2p2 import __version__

if sys.version_info[0] == 2:
    from Tkinter import *
    from tkMessageBox import *
    import ttk
else:
    from tkinter import *
    from tkinter.messagebox import *
    import tkinter.ttk as ttk

from distutils.version import LooseVersion

HELPTEXT = """This application provides the link between ASPRO (that you should have started) and interferometers facilities.

"""

logger = logging.getLogger(__name__)

class MainWindow():

    def __init__(self, a2p2client):

        self.a2p2client = a2p2client

        self.requestAbort = False

        self.window = Tk()

        try:
            dpi_value = self.window.winfo_fpixels('1i')
            # print("dpi: " + str(dpi_value));
            self.window.tk.call(
                'tk', 'scaling', '-displayof', '.', dpi_value / 72.0)
        except:
            print("Can not set tk scaling !")

        self.window.protocol("WM_DELETE_WINDOW", self._requestAbort)

        self.notebook = ttk.Notebook(self.window)

        self.logFrame = Frame(self.notebook)

        self.logtext = Text(self.logFrame)
        scroll = Scrollbar(self.logFrame, command=self.logtext.yview)
        self.logtext.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.logtext.pack(side=LEFT, fill=BOTH, expand=True)
        self.logFrame.pack(side=TOP, fill=BOTH, expand=True)

        self.helpFrame = Frame(self.notebook)
        self.helptabs = ttk.Notebook(self.helpFrame)
        self.helptabs.pack(side=TOP, fill=BOTH, expand=True)
        self.helpFrame.pack(fill=BOTH, expand=True)
        self.addHelp("A2P2", HELPTEXT)

        self.releaseNotesFrame = Frame(self.notebook)
        self.releaseNotesFrame.pack(fill=BOTH, expand=True)
        self.addReleaseNotes(self.releaseNotesFrame)

        # add tab and store index for later use in showFacilityUI
        self.tabIdx = {}
        self.registerTab("LOG", self.logFrame)
        self.registerTab("HELP", self.helpFrame)
        self.registerTab("RELEASE NOTES", self.releaseNotesFrame)
        self.notebook.select(self.tabIdx["LOG"])

        self.notebook.pack(side=TOP, fill=BOTH, expand=True)

        self.log_string = StringVar()
        self.log_string.set("log...")
        self.log = Label(self.window, textvariable=self.log_string, fg="blue")
        self.log.pack()

        self.status_bar = StatusBar(self.window)
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.progress_value = self.status_bar.progress_value

    def __del__(self):
        self.window.destroy()

    def setSampId(self, id):
        if id:
            self.window.title("A2P2 v%s [%s]" % (__version__, id))
        else:
            self.window.title("A2P2 v" + __version__)

    def _requestAbort(self):
        self.requestAbort = True

    def addHelp(self, tabname, txt):
        frame = Frame(self.helptabs)
        widget = Text(frame, width=120)
        helpscroll = Scrollbar(frame, command=widget.yview)
        widget.configure(yscrollcommand=helpscroll.set)
        helpscroll.pack(side=RIGHT, fill=Y)
        widget.pack(side=LEFT, fill=BOTH, expand=True)
        frame.pack(side=TOP, fill=BOTH, expand=True)
        self.helptabs.add(frame, text=tabname)
        widget.insert(END, txt)

    def addReleaseNotes(self, frame):
        """
        Present in a ordered way the dictionnary version items.
        """
        txt = ""
        lvs = [LooseVersion(v) for v in __release_notes__]
        for lv in sorted(lvs, reverse=True):
            v=lv.vstring
            txt += "\nV " + v + " :"
            txt += "\n---------------"
            keys = []
            for k in sorted(__release_notes__[v]):
                if not ("TODO" in k):
                    keys.append(k)
            for k in sorted(__release_notes__[v]):
                if "TODO" in k:
                    keys.append(k)

            for e in keys:
                infos = __release_notes__[v][e]
                if infos:
                    txt += "\n  " + e + " : "
                    for i in infos:
                        txt += "\n    - " + i
            txt += "\n\n"

        widget = Text(frame, width=120)
        helpscroll = Scrollbar(frame, command=widget.yview)
        widget.configure(yscrollcommand=helpscroll.set)
        helpscroll.pack(side=RIGHT, fill=Y)
        widget.pack(side=LEFT, fill=BOTH, expand=True)
        widget.insert(END, txt)

    def registerTab(self, text, widget):
        self.notebook.add(widget, text=text)
        self.tabIdx[text] = len(self.tabIdx)

    def showFacilityUI(self, facilityUI):
        if not facilityUI.facility.facilityName in self.tabIdx.keys():
            self.registerTab(facilityUI.facility.facilityName, facilityUI)
        self.notebook.select(self.tabIdx[facilityUI.facility.facilityName])

    def quitAfterRunOnce(self):
        self.window.quit()

    def loop(self):
        self.window.after(50, self.quitAfterRunOnce)
        self.window.mainloop()
        self.update_status_bar()

    def innerloop(self):
        self.window.after(50, self.quitAfterRunOnce)
        self.window.mainloop()

    def update_status_bar(self):
        self.status_bar.set_label("SAMP", "SAMP: %s" %
                                  self.a2p2client.a2p2SampClient.get_status())
        self.status_bar.set_label(
            "API", "%s" % self.a2p2client.facilityManager.get_status())

    def get_api(self):
        return self.api

    def addToLog(self, text, displayString=True, level=logging.INFO):
        if displayString:
            self.log_string.set(str(text))
        self.logtext.insert(END, "\n" + str(text))
        self.logtext.see(END)
        self.showFrameToFront()
        self.refresh()
        logger.log(level,text)

    def refresh(self):
        self.window.update()

    def ShowErrorMessage(self, text):
        if self.a2p2client.fakeAPI:
            pass
        else:
            showerror("Error", text)
        self.addToLog("Error message")
        self.addToLog(text, False, logging.ERROR)

        # do also append to simple error stack (for testing purpose first)
        self.a2p2client.addError(text)

    def ShowWarningMessage(self, text):
        if self.a2p2client.fakeAPI:
            pass
        else:
            showwarning("Warning", text)
        self.addToLog("Warning message")
        self.addToLog(text, False, loggin.WARNING)

    def ShowInfoMessage(self, text):
        if self.a2p2client.fakeAPI:
            pass
        else:
            showinfo("Info", text)
        self.addToLog("Info message")
        self.addToLog(text, False, logging.INFO)

    def setProgress(self, perc):
        if perc > 1:
            perc = perc / 100.0
        self.progress_value.set(perc)
        if (perc <= 0) or (perc > 0.99):
            self.window.config(cursor="left_ptr")
        else:
            self.window.config(cursor="watch")
        self.innerloop()
        self.showFrameToFront()

    def showFrameToFront(self):
        self.window.attributes('-topmost', 1)
        self.window.attributes('-topmost', 0)


class StatusBar(Frame):

    def __init__(self, root, **kw):
        Frame.__init__(self, root, **kw)
        self.labels = {}

        self.progress_value = DoubleVar()
        self.progress_value.set(0.0)
        self.progressbar = ttk.Progressbar(
            self, orient='horizontal', length=200, maximum=1,
            variable=self.progress_value,
            mode='determinate')  # , from_=0, to=1, resolution=0.01,showvalue=0,takefocus=0)
        self.progressbar.pack(side=LEFT)

    def set_label(self, name, text='', side=RIGHT, width=0):
        if name not in self.labels:
            label = Label(self)
            label.pack(side=side, pady=0, padx=4, anchor=E)
            self.labels[name] = label
        else:
            label = self.labels[name]
        if width != 0:
            label.config(width=width)
        label.config(text=text)


class FacilityUI(Frame):

    def __init__(self, facility):
        Frame.__init__(self, facility.a2p2client.ui.notebook)
        # self.pack(fill=BOTH)
        self.facility = facility
        self.a2p2client = facility.a2p2client

    def addToLog(self, *args, **kwargs):
        """ Wrapper to log message in the common textfield """
        self.a2p2client.ui.addToLog(*args, **kwargs)

    def ShowErrorMessage(self, *args, **kwargs):
        self.a2p2client.ui.ShowErrorMessage(*args, **kwargs)

    def ShowWarningMessage(self, *args, **kwargs):
        self.a2p2client.ui.ShowWarningMessage(*args, **kwargs)

    def ShowInfoMessage(self, *args, **kwargs):
        self.a2p2client.ui.ShowInfoMessage(*args, **kwargs)

    def setProgress(self, perc):
        """ Wrapper to update progress bar """
        if perc > 1:
            perc = perc / 100.0
        if (perc <= 0) or (perc > 0.99):
            self.isIdle()
        else:
            self.isBusy()
        self.a2p2client.ui.setProgress(perc)

    def isBusy(self):
        """ Override me to lock specific widgets. """
        pass

    def isIdle(self):
        """ Override me to unlock specific widgets. """
        pass
