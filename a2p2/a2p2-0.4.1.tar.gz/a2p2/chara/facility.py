#!/usr/bin/env python

__all__ = []

from a2p2.chara.gui import CharaUI
from a2p2.facility import Facility
import logging

HELPTEXT = "TODO update this HELP message in a2p2/chara/facility.py"

logger = logging.getLogger(__name__)

class CharaFacility(Facility):

    def __init__(self, a2p2client):
        Facility.__init__(self, a2p2client, "CHARA", HELPTEXT)
        self.charaUI = CharaUI(self)

    def processOB(self, ob):
        self.a2p2client.ui.addToLog(
            "OB received for '" + self.facilityName + "' interferometer")
        # show ob dict for debug
        self.a2p2client.ui.addToLog(str(ob), False)

        # performs operation
        self.consumeOB(ob)

        # give focus on last updated UI
        self.a2p2client.ui.showFacilityUI(self.charaUI)

    def consumeOB(self, ob):
        # for the prototype: just delegate handling to the GUI
        # we could imagine to store obs in a list and recompute a sorted
        # summary report e.g.
        self.charaUI.displayOB(ob)
