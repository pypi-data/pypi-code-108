#!/usr/bin/env python

__all__ = []

import sys
import logging

from a2p2.gui import FacilityUI

if sys.version_info[0] == 2:
    from Tkinter import *
    from tkMessageBox import *
    import ttk
else:
    from tkinter import *
    from tkinter.messagebox import *
    import tkinter.ttk as ttk

logger = logging.getLogger(__name__)

class VltiUI(FacilityUI):

    def __init__(self, a2p2client):
        logger.info("init VltiUI")
        FacilityUI.__init__(self, a2p2client)

        self.container = Frame(self, bd=3, relief=SUNKEN)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.loginFrame = LoginFrame(self)
        self.loginFrame.grid(row=0, column=0, sticky="nsew")

        self.treeFrame = TreeFrame(self)
        self.treeFrame.grid(row=0, column=0, sticky="nsew")
        self.tree = self.treeFrame.tree

        self.container.pack(fill=BOTH, expand=True)
        self.treeItemToRuns = {}
        self.treeItemToP2Items = {}

        self.ob=None

    def showLoginFrame(self, ob):
        self.ob = ob
        self.addToLog(
            "Sorry, your %s OB can't be submitted, please log in first, select container and send OB again from Aspro2." %
            (ob.instrumentConfiguration.name))
        self.loginFrame.tkraise()

    def showTreeFrame(self, ob=None):
        if ob:
            instrum = ob.instrumentConfiguration.name
        else:
            instrum = "incoming"
        self.addToLog("Please select a runId in ESO P2 database to process %s OB" % instrum )
        self.treeFrame.tkraise()

    def fillTree(self, runs):
        logger.debug("Start filling tree")
        if len(runs) == 0:
            self.ShowErrorMessage(
                "No Runs defined, impossible to program ESO's P2 interface.")
            return
        # cleanup old entries if any
        for item in self.treeItemToRuns:
            try:
                self.tree.delete(item)
            except:
                pass
        self.treeItemToRuns = {}

        for run in runs:
            if self.facility.hasSupportedInsname(run['instrument']):
                cid = run['containerId']
                self._insertInTree('', run['progId'], cid, run, run)
                # if folders, add them recursively
                folders = getFolders(self.facility.api, cid)
                if len(folders) > 0:
                    try:
                        self.folder_explore(folders, cid, run)
                    except:
                        pass

    def folder_explore(self, folders, contid, run):
        for folder in folders:
            self._insertInTree(
                contid, folder['name'], folder['containerId'], run, folder)
            folders2 = getFolders(self.facility.api, folder['containerId'])
            if len(folders2) > 0:
                try:
                    self.folder_explore(folders2, folder['containerId'], run)
                except:
                    pass

    def _insertInTree(self, parentContainerID, name, containerID, run, item):
        instrument = run['instrument']
        if run != item:
            label = item['itemType']
        else:
            # {"runId":60900301,"progId":"60.A-9003(B)","title":"Tutorial account","period":60,
            # "scheduledPeriod":60,"mode":"VM","instrument":"FORS2","telescope":"UT1","ipVersion":104.26,
            # "isToO":false,"owned":true,"delegated":false,"itemCount":0,"containerId":2587672,
            # "pi":{"emailAddress":"52052@nodomain.net","firstName":"Phase 1/2 Tutorial","lastName":"Account"},
            # "observingConstraints":{"seeing":2.0}}
            label = "%s Run (IP %s)" % (run['mode'], run['ipVersion'])

        e = self.tree.insert(parentContainerID, 'end', containerID,
                             text=name, values=(run['instrument'], label))
        self.treeItemToRuns[e] = run
        self.treeItemToP2Items[e] = item

    def on_tree_selection_changed(self, selection):
        curItem = self.tree.focus()
        ret = self.tree.item(curItem)
        if len(ret['values']) > 0:
            self.facility.containerInfo.store(
                self.treeItemToRuns[curItem], self.treeItemToP2Items[curItem])

    def isBusy(self):
        self.tree.configure(selectmode='none')

    def isIdle(self):
        self.tree.configure(selectmode='browse')


class TreeFrame(Frame):

    def __init__(self, vltiUI):
        Frame.__init__(self, vltiUI.container)
        self.vltiUI = vltiUI

        subframe = Frame(self)

        self.tree = ttk.Treeview(
            subframe, columns=('Project ID'))  # , 'instrument'))#, 'folder ID'))
        ysb = ttk.Scrollbar(
            subframe, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(
            subframe, orient='horizontal', command=self.tree.xview)

        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Project ID', anchor='w')
        self.tree.heading('#1', text='Instrument', anchor='w')
        self.tree.heading('#2', text='Container type', anchor='w')
        self.tree.bind(
            '<ButtonRelease-1>', self.vltiUI.on_tree_selection_changed)

        # grid layout does not expand and fill all area then move to pack
        #       self.tree.grid(row=0, column=0, sticky='nsew')
        #       ysb.grid(row=0, column=1, sticky='ns')
        #       xsb.grid(row=1, column=0, sticky='ew')
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        ysb.pack(side=RIGHT, fill="y")
        # xsb.pack(side=BOTTOM, fill="y") # will probably require to add
        # another 2 frames

        subframe.pack(side=TOP, fill=BOTH, expand=True)


class LoginFrame(Frame):

    def __init__(self, vltiUI):
        Frame.__init__(self, vltiUI.container)
        self.vltiUI = vltiUI

        prefs = vltiUI.a2p2client.preferences

        self.loginframe = LabelFrame(
            self, text="login (ESO USER PORTAL or demo account)")

        self.username_label = Label(self.loginframe, text="USERNAME")
        self.username_label.pack()
        self.username = StringVar()
        self.username.set(prefs.getP2Username())
        self.username_entry = Entry(
            self.loginframe, textvariable=self.username)
        self.username_entry.pack()

        self.password_label = Label(self.loginframe, text="PASSWORD")
        self.password_label.pack()
        self.password = StringVar()
        self.password.set(prefs.getP2Password())
        self.password_entry = Entry(
            self.loginframe, textvariable=self.password, show="*")
        self.password_entry.pack()

        self.loginbutton = Button(
            self.loginframe, text="LOG IN", command=self.on_loginbutton_clicked)
        self.loginbutton.pack()

        self.loginframe.pack()
        self.pack(side=TOP, fill=BOTH, expand=True)

    def on_loginbutton_clicked(self):
        self.vltiUI.facility.connectAPI(
            self.username.get(), self.password.get(), self.vltiUI.ob)


# TODO move into a common part
def getFolders(p2api, containerId):
    folders = []
    items, _ = p2api.getItems(containerId)
    for item in items:
        if item['itemType'] in ['Folder', 'Concatenation']:
            folders.append(item)
    return folders
