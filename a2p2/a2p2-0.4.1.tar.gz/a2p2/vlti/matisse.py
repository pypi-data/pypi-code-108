#!/usr/bin/env python

__all__ = []

import re

from a2p2.vlti.instrument import OBConstraints
from a2p2.vlti.instrument import OBTarget
from a2p2.vlti.instrument import TSF
from a2p2.vlti.instrument import VltiInstrument

HELPTEXT = """
    Please define MATISSE instrument help in a2p2/vlti/matisse.py
"""


class Matisse(VltiInstrument):

    def __init__(self, facility):
        # MATISSE_LM" MATISSE_N
        VltiInstrument.__init__(self, facility, "MATISSE_LM")

    def checkOB(self, ob, p2container=None):
        ui = self.ui

        instrumentConfiguration = ob.instrumentConfiguration
        BASELINE = ob.interferometerConfiguration.stations
        # Compute tel = UT or AT
        # TODO move code into common part
        if "U" in BASELINE:
            tel = "UT"
        else:
            tel = "AT"

        instrumentMode = instrumentConfiguration.instrumentMode

        for observationConfiguration in self.getSequence(ob):

            # create keywords storage objects
            acqTSF = TSF(self, "MATISSE_img_acq.tsf")  # or .tsfx?
            obsTSF = TSF(self, "MATISSE_hyb_obs.tsf")

            obTarget = OBTarget()
            obConstraints = OBConstraints(self)

            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            scienceTarget = observationConfiguration.SCTarget

            # define target

            obTarget.name = scienceTarget.name.replace(' ',
                                                       '_')  # allowed characters: letters, digits, + - _ . and no spaces
            # allowed characters: letters, digits, + - _ . and no spaces
            obTarget.ra, obTarget.dec = self.getCoords(scienceTarget)
            obTarget.properMotionRa, obTarget.properMotionDec = self.getPMCoords(
                scienceTarget)

            # Set baseline  interferometric array code (should be a keywordlist)
            acqTSF.ISS_BASELINE = [self.getBaselineCode(BASELINE)]

            self.checkIssVltiType(acqTSF)

            # define some default values
            VIS = 1.0  # FIXME

            # Retrieve Fluxes
            COU_GS_MAG = self.getFlux(scienceTarget, "V")

            # setup some default values, to be changed below
            COU_AG_GSSOURCE = 'SCIENCE'  # by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'
            dualField = False

            # initialize FT variables (must exist)
            # TODO remove next lines using a dual_acq TSF that would handle
            # them

            # AO target
            aoTarget = ob.get(observationConfiguration, "AOTarget")
            if aoTarget != None:
                AONAME = aoTarget.name
                COU_AG_GSSOURCE = 'SETUPFILE'  # since we have an AO
                # TODO check if AO coords should be required by template
                # AORA, AODEC  = self.getCoords(aoTarget,
                # requirePrecision=False)
                acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(aoTarget)

            # Guide Star
            gsTarget = ob.get(observationConfiguration, 'GSTarget')
            if gsTarget != None:
                COU_GS_SOURCE = 'SETUPFILE'  # since we have an GS
                GSRA, GSDEC = self.getCoords(gsTarget, requirePrecision=False)
                # no PMRA, PMDE for GS !!
                COU_GS_MAG = float(gsTarget.FLUX_V)

            # LST interval
            try:
                obsConstraint = observationConfiguration.observationConstraints
                LSTINTERVAL = obsConstraint.LSTinterval
            except:
                LSTINTERVAL = None

            # Constraints
            obConstraints.name = 'Aspro-created constraints'
            skyTransparencyMagLimits = {"AT": 3, "UT": 5}
            #            if acqTSF.IAS.HMAG < skyTransparencyMagLimits[tel]:
            #                obConstraints.skyTransparency = 'Variable, thin cirrus'
            #            else:
            #                obConstraints.skyTransparency = 'Clear'

            obConstraints.skyTransparency = 'Clear'
            # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
            # The seeing value allowed for this OB is >= java0x0 arcsec."
            # FIXME REPLACE SEEING THAT IS NO MORE SUPPORTED
            # obConstraints.seeing = 1.0
            # baseline not in instrumecnstraints obConstraints.baseline = BASELINE.replace(' ', '-')
            # FIXME: default values NOT IN ASPRO!
            # constaints.airmass = 5.0
            # constaints.fli = 1
            # and store computed values in obsTSF

            # then call the ob-creation using the API if p2container exists.
            if p2container == None:
                ui.addToLog(obTarget.name +
                            " ready for p2 upload (details logged)")
                ui.addToLog(obTarget, False)
                ui.addToLog(obConstraints, False)
                ui.addToLog(acqTSF, False)
                ui.addToLog(obsTSF, False)
            else:
                self.createMatisseOB(p2container, obTarget, obConstraints, acqTSF, obsTSF, OBJTYPE, instrumentMode,
                                     COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, LSTINTERVAL)
                ui.addToLog(obTarget.name + " submitted on p2")

    def formatRangeTable(self):
        rangeTable = self.getRangeTable()
        buffer = ""
        for l in rangeTable.keys():
            buffer += l + "\n"
            for k in rangeTable[l].keys():
                constraint = rangeTable[l][k]
                keys = constraint.keys()
                buffer += ' %30s :' % (k)
                if 'min' in keys and 'max' in keys:
                    buffer += ' %f ... %f ' % (
                        constraint['min'], constraint['max'])
                elif 'list' in keys:
                    buffer += str(constraint['list'])
                elif "spaceseparatedlist" in keys:
                    buffer += ' ' + " ".join(constraint['spaceseparatedlist'])
                if 'default' in keys:
                    buffer += ' (' + str(constraint['default']) + ')'
                else:
                    buffer += ' -no default-'
                buffer += "\n"
        return buffer

    def getMatisseTemplateName(self, templateType, OBJTYPE):
        objType = "calibrator"
        if OBJTYPE and "SCI" in OBJTYPE:
            objType = "science"
        if OBJTYPE:
            return "_".join((self.getShortName(), templateType, objType))
        return "_".join((self.getShortName(), templateType))

    def getMatisseObsTemplateName(self, OBJTYPE):
        return self.getMatisseTemplateName("obs", OBJTYPE)

    def formatDitTable(self):
        #    fluxTable = self.getDitTable()
        buffer = '   Tel | Spec |  spec band  | Flux (Jy)    | tau(ms)\n'
        #    buffer += '--------------------------------------------------------\n'
        #    for tel in ['AT']:
        #        for spec in ['Low','Med']:
        #            for band in  ['L','M','N']:
        #                for i in range(len(fluxTable[tel][spec][band]['Flux'])):
        #                    buffer += ' %3s | %4s | %3s | %2s |' % ( tel,
        #                        spec, band, tel)
        #                    buffer += ' %4.1f <K<= %3.1f | %4.1f' % (fluxTable[tel][spec][pol]['MAG'][i],
        #                                                             fluxTable[tel][spec][
        #                        pol]['MAG'][i + 1],
        #                        fluxTable[tel][spec][pol]['DIT'][i])
        #                    buffer += "\n"

        return buffer

    def createMatisseOB(
            self, p2container, obTarget, obConstraints, acqTSF, obsTSF, OBJTYPE, instrumentMode,
            COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, LSTINTERVAL):

        api = self.facility.getAPI()
        ui = self.ui
        ui.setProgress(0.1)

        # TODO compute value
        VISIBILITY = 1.0

        # everything seems OK
        # create new OB in container:
        # TODO use a common function for next lines
        goodName = re.sub('[^A-Za-z0-9]+', '_', obTarget.name)
        OBS_DESCR = OBJTYPE[0:3] + '_' + goodName + '_MATISSE_' + \
            acqTSF.ISS_BASELINE[0] + '_' + instrumentMode

        ob, obVersion = api.createOB(p2container.containerId, OBS_DESCR)
        obId = ob['obId']

        # we use obId to populate OB
        ob['obsDescription']['name'] = OBS_DESCR[0:min(len(OBS_DESCR), 31)]
        ob['obsDescription']['userComments'] = self.getA2p2Comments()
        # ob['obsDescription']['InstrumentComments'] = 'AO-B1-C2-E3' #should be
        # a list of alternative quadruplets!

        # copy target info
        targetInfo = obTarget.getDict()
        for key in targetInfo:
            ob['target'][key] = targetInfo[key]

        # copy constraints info
        constraints = obConstraints.getDict()
        for k in constraints:
            ob['constraints'][k] = constraints[k]

        ui.addToLog("Save ob to p2:\n%s" % ob, False)
        ob, obVersion = api.saveOB(ob, obVersion)

        # time constraints if present
        self.saveSiderealTimeConstraints(api, obId, LSTINTERVAL)
        ui.setProgress(0.2)

        # then, attach acquisition template(s)
        tpl, tplVersion = api.createTemplate(obId, 'MATISSE_img_acq')
        # and put values
        # start with acqTSF ones and complete manually missing ones
        values = acqTSF.getDict()
        values.update({'COU.AG.GSSOURCE': COU_AG_GSSOURCE,
                       'COU.AG.ALPHA': GSRA,
                       'COU.AG.DELTA': GSDEC,
                       'COU.GS.MAG': round(COU_GS_MAG, 3),
                       'TEL.TARG.PARALLAX': 0.0
                       })

        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.3)

        # was :
        # tpl, tplVersion = api.createTemplate(obId, self.getMatisseObsTemplateName(OBJTYPE))
        tpl, tplVersion = api.createTemplate(obId, obsTSF.getP2Name())
        ui.setProgress(0.4)

        # put values. they are the same except for dual obs science (?)
        values = obsTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.5)

        # verify OB online
        response, _ = api.verifyOB(obId, True)
        ui.setProgress(1.0)
        self.showP2Response(response, ob, obId)
