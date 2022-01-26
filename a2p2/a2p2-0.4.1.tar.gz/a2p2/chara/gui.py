#!/usr/bin/env python

__all__ = []

import sys
import traceback
import logging

from a2p2.gui import FacilityUI

if sys.version_info[0] == 2:
    from Tkinter import *
    from tkMessageBox import *
else:
    from tkinter import *
    from tkinter.messagebox import *

# Constants
_HR = "\n----------------------------------------------\n"

logger = logging.getLogger(__name__)

class CharaUI(FacilityUI):

    def __init__(self, a2p2client):
        FacilityUI.__init__(self, a2p2client)
        # first version store all in a single widget
        self.text = Text(self, width=120)
        scroll = Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        # more control could be added in the futur in this area for CHARA
        # specific

        # avoid repeat of baseline on successive schedules
        self.lastBaselines = "-"

    def get(self, obj, fieldname):
        if fieldname in obj._fields:
            return getattr(obj, fieldname)
        else:
            return None

    def displayOB(self, ob):
        try:
            buffer = self.extractReport(ob)
        except:
            buffer = "Error during report generation\n" + \
                     traceback.format_exc() + _HR + str(ob)

        self.text.insert(END, buffer)

    def extractReport(self, ob):
        """ We coud try to mimic the output below
----------------------------------------------
Baselines: S2(2)-E2(4)
           Ref Cart: BL 2
Times in [brackets] are when target is above 30 deg and has delay
----------------------------------------------
S2(2)E2(4)
----------------------------------------------
Start-5:00 UT [Start-7:58 UT]
Object:
HD 78209 (A3V, 30pc): V=4.45, R=4.21, tht=0.54
Fringe Finder:
HD 79158: V=5.29, R=5.29, tht=0.19 (good for fringe finding)
AO Flat Star:
HD 82328: V=3.18
Cals:
1) HD 77309: V=5.73, R=5.65, tht=0.22
2) HD 79158: V=5.29, R=5.29, tht=0.19 (good for fringe finding)
----------------------------------------------
5:00-6:30 UT [Start-9:44 UT]
Object:
HD 91312 (A7IV, IRx, 35pc): V=4.72, R=3.76, tht=0.58
AO Flat Star:
"""
        buffer = ""

        # Display baselines on change
        stations = ob.interferometerConfiguration.stations
        if self.lastBaselines != stations:
            buffer += _HR
            buffer += "Baselines: " + stations + "\n"
            self.lastBaselines = stations
        buffer += _HR

        # Retrieve all stars (as obsConf) and build sciences list
        sciences = []
        targets = {}  # store  ids for futur retrieval in schedule
        for oc in ob.observationConfiguration:
            targets[oc.id] = oc
            if "SCI" in oc.type:
                sciences.append(oc)

        # Retrieve cals from schedule
        cals = {}
        for schedule in ob.observationSchedule.OB:
            try:  # hack for single element observationSchedule
                ref = schedule.ref
            except:
                ref = schedule
            target = targets[ref]
            if "CAL" in target.type:
                cals[ref] = target

        # TODO check for calibrator only ?

        for oc in sciences:
            sct = oc.SCTarget
            ftt = self.get(oc, "FTTarget")
            aot = self.get(oc, "AOTarget")
            buffer += oc.observationConstraints.LSTinterval + "\n"
            buffer += "Object:\n"
            fluxes = ", ".join([e[0] + "=" + e[1]
                                for e in ob.getFluxes(sct).items()])
            info = sct.SPECTYP + ", " + sct.PARALLAX
            buffer += sct.name + " (" + info + ") : " + fluxes + "\n"
            if ftt:
                buffer += "Fringe Finder:\n"
                fluxes = ", ".join([e[0] + "=" + e[1]
                                    for e in ob.getFluxes(ftt).items()])
                buffer += ftt.name + " : " + fluxes + "\n"
            if aot:
                buffer += "AO Flat Star:\n"
                fluxes = ", ".join([e[0] + "=" + e[1]
                                    for e in ob.getFluxes(aot).items()])
                buffer += aot.name + " : " + fluxes + "\n"

            if len(cals) >= 1:
                buffer += "Cals:\n"
                for cal in cals:
                    buffer += "- " + cal + "\n"

            buffer += _HR

        return buffer
