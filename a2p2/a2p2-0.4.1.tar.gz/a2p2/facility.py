#!/usr/bin/env python

__all__ = []

import logging

logger = logging.getLogger(__name__)

class FacilityManager():
    """
    Manage real and fake apis.
    """

    def __init__(self, a2p2client):
        self.apiName = a2p2client.apiName
        self.a2p2client = a2p2client

        # define facilities
        self.facilities = {}
        from a2p2.chara.facility import CharaFacility
        self.registerFacility(CharaFacility(self.a2p2client))
        from a2p2.vlti.facility import VltiFacility
        self.registerFacility(VltiFacility(self.a2p2client))
        # with default one
        self.defaultFacility = Facility(self.a2p2client, "Dumm-facilit-y", "")

    def registerFacility(self, facilityObject):
        self.facilities[facilityObject.facilityName] = facilityObject
        self.a2p2client.ui.addHelp(
            facilityObject.facilityName, facilityObject.facilityHelp)

    def get_status(self):
        status = []
        for facility in self.facilities.values():
            if facility.getStatus():
                status.append(
                    facility.facilityName + " [" + facility.getStatus() + " ]")

        return " | ".join(status)

    def processOB(self, ob):
        """ Test instrument on facility that registerInstrument() before OB forward for specialized handling."""
        interferometer = ob.interferometerConfiguration.name
        insname = ob.instrumentConfiguration.name

        if interferometer in self.facilities:
            facility = self.facilities[interferometer]
        else:
            facility = self.defaultFacility

        supportedIns = facility.getSupportedInsnames()
        if len(supportedIns) == 0 or insname in supportedIns:
            self.a2p2client.ui.addToLog(
                "Received OB for '" + insname + "@" + interferometer + "' ")
            facility.processOB(ob)
        else:
            self.a2p2client.ui.ShowErrorMessage("Received OB for unsupported instrument \n" +
                                                insname + " @ " + interferometer + "\n" + "Supported instrument(s): " + ", ".join(
                                                    supportedIns))


# TODO move to a dedicated source file
class Facility():

    def __init__(self, a2p2client, facilityName, facilityHelp):
        self.a2p2client = a2p2client
        self.facilityName = facilityName
        self.facilityHelp = facilityHelp
        self.facilityInstruments = {}

    def processOB(self, ob):
        """ Please override this method in your facility class to handle incoming OB. """
        interferometer = ob.interferometerConfiguration.name
        self.a2p2client.ui.addToLog(
            "'" + interferometer + "' interferometer not supported by A2P2")

    def registerInstrument(self, instrument):
        self.facilityInstruments[instrument.getName()] = instrument

    def getSupportedInsnames(self):
        return self.facilityInstruments.keys()

    def hasSupportedInsname(self, insname):
        # ... we may log failures
        if insname in self.getSupportedInsnames():
            return True
        for i in self.getSupportedInstruments():
            if i.getShortName() == insname:
                return True

    def getSupportedInstruments(self):
        return self.facilityInstruments.values()

    def getInstrument(self, insname):
        return self.facilityInstruments[insname]

    def getName(self):
        return self.facilityName

    def getStatus(self):
        """ Please override this method in your facility class to include status in the API entry of the main status bar. """
        return None
