#!/usr/bin/env python

__all__ = []

import os
from tkinter.constants import TRUE
import traceback
import logging

import p2api

from a2p2.facility import Facility
from a2p2.vlti.gui import VltiUI

MODE_SM = 'SM'

ITEMTYPE_CONCATENATION = 'Concatenation'

JMMC_LOGIN = 'jmmc'

TUTORIAL_LOGIN = '52052'
PRODUCTION_APITYPE = 'production'
DEMO_APITYPE = 'demo'

# TODO handle a period subdirectory
CONFDIR = "conf"

# Look for configuration files in the same level directory as this module/conf/
try:
    _confdir = os.path.join(os.path.dirname(__file__), CONFDIR)
except NameError:
    _confdir = CONFDIR
if os.path.isdir(_confdir):
    CONFDIR = _confdir
elif not os.path.isdir(CONFDIR):
    raise RuntimeError("can't find conf directory (%r)" % (CONFDIR,))

HELPTEXT = """
ESO's P2 repository for Observing Blocks (OBs):


Send configuration from Aspro:
- In ASPRO, have an object, or an object selected, and check that all important informations (magnitudes, but also Instrument and Fringe Tracker Modes, eventually hour angles), are correctly set.
- In menu "Interop" select "Send Obs. blocks to A2p2"
- Block(s) are created and put in the P2 repository.
- If the source had one or more calibrators, blocks are created for them too.
- For each block submitted, a report is produced. Warnings are usually not significant.
- For more than 1 object sent, a <b>folder</b> containing the two or more blocks is created. In the absence of availability of grouping OBs (like for CAL-SCI-CAL) provided by ESO, this is the closets we can do.
- All the new OBs and folders will be available on p2web at https://www.eso.org/p2

On your first valid VLTI's OB, A2p2 will ask for your ESO User Portal credentials to interact with P2 using it's API. You can follow actions and organize more in details your OB on https://www.eso.org/p2 . Please use prefilled values of the login panel for testing purpose and follow ESO database from https://www.eso.org/p2demo/
"""
HELPTEXT += "Config files loaded from " + CONFDIR

logger = logging.getLogger(__name__)

class VltiFacility(Facility):

    def __init__(self, a2p2client):
        Facility.__init__(self, a2p2client, VltiFacility.getName(), HELPTEXT)
        self.ui = VltiUI(self)

        # Instanciate instruments
        # TODO complete list and make it more object oriented
        from a2p2.vlti.gravity import Gravity
        gravity = Gravity(self)
        from a2p2.vlti.pionier import Pionier
        pionier = Pionier(self)
        from a2p2.vlti.matisse import Matisse
        matisse = Matisse(self)

        # complete help
        for i in self.getSupportedInstruments():
            self.facilityHelp += "\n" + i.getHelp()

        self.connected = False
        # set to demo by default (may change in connectAPI)
        self.apitype = 'demo'
        self.containerInfo = P2Container(self)

        # will store later : name for status info, api
        self.username = None
        self.api = None

    def getName():
        return "VLTI"

    def autologin(self):
        self.ui.addToLog("\nAutologin into P2 API please wait...\n")
        self.ui.loginFrame.on_loginbutton_clicked()
        self.a2p2client.ui.showFacilityUI(self.ui)
        self.ui.showTreeFrame()

    def processOB(self, ob):
        # give focus on last updated UI
        self.a2p2client.ui.showFacilityUI(self.ui)
        # show ob dict for debug
        self.ui.addToLog(str(ob), False)

        # OB is checked and submitted by instrument
        instrument = self.getInstrument(ob.instrumentConfiguration.name)
        try:
            # run checkOB which may raise some error before connection request
            # TODO we should test much more because lot of stuff still are beeing processed on live ob creations

            instrument.checkOB(ob)

            insname = instrument.getShortName()

            # performs operation
            if not self.isConnected():
                self.ui.showLoginFrame(ob)
            elif not self.isReadyToSubmit(ob):
                # self.a2p2client.ui.addToLog("Receive OB for
                # '"+ob.instrumentConfiguration.name+"'")
                self.ui.addToLog(
                    f"Please select a {insname}'s folder (not a concatenation) in the above list to submit your science object (OBs are not shown).")
            elif  insname.lower() != self.containerInfo.getInstrument().lower():
                self.ui.ShowErrorMessage("Aborting: container's instrument '%s' in not applicable for received OB's one '%s'." %(self.containerInfo.getInstrument(),insname))
            else:
                self.ui.addToLog(
                    "Everything ready! Request OB creation inside selected container ")
                instrument.submitOB(ob, self.containerInfo)
                self.ui.addToLog(
                    "Run filled! Please check logs and fix last details on P2 web.")
                self.refreshTree()

        # TODO add P2Error handling P2Error(r.status_code, method, url,
        # r.json()['error'])
        except ValueError as e:
            traceback.print_exc()
            trace = traceback.format_exc(limit=1)
            # ui.ShowErrorMessage("Value error :\n %s \n%s\n\n%s" % (e, trace,
            # "Aborting submission to P2. Look at the whole traceback in the log."))
            self.ui.ShowErrorMessage("Value error :\n %s \n\n%s" %
                                     (e, "Aborting submission to P2. Please check LOG and fix before new submission."))
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False)
            self.ui.setProgress(0)
        except Exception as e:
            traceback.print_exc()
            # limit = 2 should raise errors in our codes
            trace = traceback.format_exc(limit=1)
            self.ui.ShowErrorMessage(
                "General error or Absent Parameter in template!\n Missing magnitude or OB not set ?\n\nError :\n %s \n Please check LOG and fix before new submission." % (
                    trace))
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False)
            self.ui.setProgress(0)

    def isReadyToSubmit(self, ob):
        return self.api and self.containerInfo.isOk(ob)

    def isConnected(self):
        return self.connected

    def setConnected(self, flag):
        self.connected = flag

    def getStatus(self):
        if self.isConnected():
            return " P2API(%s) connected with %s" % ( self.apitype, self.username )

    def connectAPI(self, username, password, ob):
        if username == TUTORIAL_LOGIN: # or username == JMMC_LOGIN:
            self.apitype = DEMO_APITYPE
        else:
            self.apitype = PRODUCTION_APITYPE
        try:
            logger.info("Connecting to p2 api...")
            self.api = p2api.ApiConnection(self.apitype, username, password)

            self.ui.addToLog("Connected to p2 api (%s)"%self.apitype)
            # TODO test that api is ok and handle error if any...

            self.refreshTree()

            self.setConnected(True)
            self.username = username
            self.ui.showTreeFrame(ob)
        except:
            self.ui.ShowErrorMessage("Can't connect to P2 (see LOG).")
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False, level=logging.ERROR)

    def refreshTree(self):
        runs, _ = self.api.getRuns()
        self.ui.fillTree(runs)

    def isDemoAPI(self):
        return self.apitype == DEMO_APITYPE

    def isTutorialAccount(self):
        return self.username == TUTORIAL_LOGIN

    def getAPI(self):
        return self.api

    def getConfDir(self):
        """
        returns the configuration directory with instrument's json files
        """
        return CONFDIR


# TODO Move code out of this class

class P2Container:
    # run object stores:
    # {'pi': {'lastName': 'Accont', 'emailAddress': '52052@nodomain.net', 'firstName': 'Phase 1/2 Ttorial'},
    # 'telescope': 'VLTI', 'title': 'p2 tutorial', 'schedledPeriod': 60, 'isToO': False, 'period': 60, 'owned': Tre,
    # 'ipVersion': 104.05, 'instrument': 'PIONIER', 'containerId': 1601182, 'observingConstraints': {'fli' : 'd', 'seeing': 0.8},
    # 'mode': 'SM', 'progId': '60.A-9253(T)', 'itemCont': 2, 'delegated': False, 'runId': 60925319}
    # and item (when not run) :
    # {u'containerStatus': u'P', u'itemType': u'Group', u'name': u'New Group', u'groupScore': 0.0,
    # u'containerId': 2609528, u'runId': 60925213, u'userPriority': 1, u'itemCount': 0, u'parentContainerId': 2609516}

    def __init__(self, facility):
        self.facility = facility
        self.run = None  # dict returned by p2api
        self.containerId = None
        self.item = None

    def store(self, run, item):
        self.run = run
        self.item = item
        self.containerId = item['containerId']
        self.log()

    def log(self):
        if self.run != self.item and self.item['itemType'] == ITEMTYPE_CONCATENATION:
            self.facility.ui.addToLog(
                "*** Please do not select a Concatenation and select another container. Or just append a calibrator. ***")
        else:
            self.facility.ui.addToLog("*** Working with %s ***" % self)

    def isOk(self, ob):
        """ Tell if given container is ready to receive content of given OB."""
        if self.run == None:
            return False
        if self.run == self.item:
            return True

        has_calib = False
        has_science = False
        for obsConf in ob.observationConfiguration:
            if 'SCIENCE' in obsConf.type:
                has_science = True
            else:
                has_calib = True

        if has_science:
            return self.item['itemType'] != ITEMTYPE_CONCATENATION
        return has_calib

    def getInstrument(self):
        return self.run['instrument']

    def isRoot(self):
        return self.item.keys() != None and 'pi' in self.item.keys()

    def isServiceModeRun(self):
        return self.run['mode'] == MODE_SM

    def __str__(self):
        return """instrument:'%s', containerId:'%s'""" % (self.run['instrument'], self.containerId)
