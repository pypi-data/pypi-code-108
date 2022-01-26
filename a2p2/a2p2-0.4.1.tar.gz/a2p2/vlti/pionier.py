#!/usr/bin/env python

__all__ = []

import re

from a2p2.vlti.instrument import OBConstraints
from a2p2.vlti.instrument import OBTarget
from a2p2.vlti.instrument import TSF
from a2p2.vlti.instrument import VltiInstrument

HELPTEXT = """
Please define PIONIER instrument help in a2p2/vlti/pionier.py
"""


class Pionier(VltiInstrument):

    def __init__(self, facility):
        VltiInstrument.__init__(self, facility, "PIONIER")

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

        # Retrieve SPEC and POL info from instrumentMode
        for disp in self.getRange("PIONIER_acq.tsf", "INS.DISP.NAME"):
            if disp in instrumentMode[0:len(disp)]:
                ins_disp = disp

        for observationConfiguration in self.getSequence(ob):

            # create keywords storage objects
            acqTSF = TSF(self, "PIONIER_acq.tsf")
            obsTSF = TSF(self, "PIONIER_obs_calibrator.tsf")
            # alias for PIONIER_obs_calibrator.tsf and
            # PIONIER_obs_science.tsf")
            kappaTSF = TSF(self, "PIONIER_gen_cal_kappa.tsf")
            darkTSF = TSF(self, "PIONIER_gen_cal_dark.tsf")

            obTarget = OBTarget()
            obConstraints = OBConstraints(self)

            # set common properties
            acqTSF.INS_DISP_NAME = ins_disp

            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            scienceTarget = observationConfiguration.SCTarget

            # define target
            # acqTSF.SEQ_INS_SOBJ_NAME = scienceTarget.name.strip()


            obTarget.name = scienceTarget.name.strip().replace(
                ' ', '_')  # allowed characters: letters, digits, + - _ . and no spaces
            obTarget.ra, obTarget.dec = self.getCoords(scienceTarget)
            obTarget.properMotionRa, obTarget.properMotionDec = self.getPMCoords(
                scienceTarget)

            # Set baseline  interferometric array code (should be a keywordlist)
            acqTSF.ISS_BASELINE = [self.getBaselineCode(BASELINE)]

            self.checkIssVltiType(acqTSF)

            # define some default values
            DIAMETER = float(self.get(scienceTarget, "DIAMETER", 0.0))
            VIS = 1.0  # FIXME

            # Retrieve Fluxes
            TEL_COU_MAG = self.getFlux(scienceTarget, "V")
            acqTSF.ISS_IAS_HMAG = self.getFlux(scienceTarget, "H")

            # setup some default values, to be changed below
            TEL_COU_GSSOURCE = 'SCIENCE'  # by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'

            # initialize FT variables (must exist)

            # AO target
            aoTarget = ob.get(observationConfiguration, "AOTarget")
            if aoTarget != None:
                AONAME = aoTarget.name
                TEL_COU_GSSOURCE = 'SETUPFILE'  # since we have an AO
                # TODO check if AO coords should be required by template
                # AORA, AODEC  = self.getCoords(aoTarget,
                # requirePrecision=False)
                acqTSF.TEL_COU_PMA, acqTSF.TEL_COU_PMD = self.getPMCoords(
                    aoTarget)

            # Guide Star
            gsTarget = ob.get(observationConfiguration, 'GSTarget')
            if gsTarget != None:
                TEL_COU_GSSOURCE = 'SETUPFILE'  # since we have an GS
                GSRA, GSDEC = self.getCoords(gsTarget, requirePrecision=False)
                # no PMRA, PMDE for GS !!
                TEL_COU_MAG = float(gsTarget.FLUX_V)

            # LST interval
            try:
                obsConstraint = observationConfiguration.observationConstraints
                LSTINTERVAL = obsConstraint.LSTinterval
            except:
                LSTINTERVAL = None

            # Constraints
            obConstraints.name = 'Aspro-created constraints'
            skyTransparencyMagLimits = {"AT": 3, "UT": 5}
            if acqTSF.ISS_IAS_HMAG < skyTransparencyMagLimits[tel]:
                obConstraints.skyTransparency = 'Variable, thin cirrus'
            else:
                obConstraints.skyTransparency = 'Clear'

            if acqTSF.ISS_IAS_HMAG > 7.5:
                acqTSF.INS_DISP_NAME = "FREE"

            # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
            # The seeing value allowed for this OB is >= java0x0 arcsec."
            # FIXME REPLACE SEEING THAT IS NO MORE SUPPORTED
            # obConstraints.seeing = 1.0
            # FIXME: default values NOT IN ASPRO!
            # constaints.airmass = 5.0
            # constaints.fli = 1

            # compute dit, ndit, nexp

            # and store computed values in obsTSF
            obsTSF.SEQ_NEXPO = 5
            # obsTSF.NSCANS = 100
            # kappaTSF.SEQ_DOIT=False
            # darkTSF.SEQ_DOIT=True

            # then call the ob-creation using the API if p2container exists.
            if p2container == None:
                ui.addToLog(obTarget.name +
                            " ready for p2 upload (details logged)")
                ui.addToLog(obTarget, False)
                ui.addToLog(obConstraints, False)
                ui.addToLog(acqTSF, False)
                ui.addToLog(obsTSF, False)
                ui.addToLog(kappaTSF, False)
                ui.addToLog(darkTSF, False)
            else:
                self.createPionierOB(p2container, obTarget, obConstraints, acqTSF,
                                     obsTSF, kappaTSF, darkTSF, OBJTYPE, instrumentMode, TEL_COU_GSSOURCE, GSRA, GSDEC,
                                     TEL_COU_MAG, LSTINTERVAL)
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

    def formatDitTable(self):
        ditTable = self.getDitTable()
        buffer = '   Tel | Spec |  Pol  |     H   | DIT(s)\n'
        buffer += '--------------------------------------------------------\n'
        for tel in ['AT']:
            for spec in ['GRISM', 'FREE']:
                for pol in ['IN', 'OUT']:
                    for i in range(len(ditTable[tel][spec][pol]['DIT'])):
                        buffer += ' %3s | %4s | %3s | %2s |' % (tel,
                                                                spec, pol, tel)
                        buffer += ' %4.1f <K<= %3.1f | %4.1f' % (ditTable[tel][spec][pol]['MAG'][i],
                                                                 ditTable[tel][spec][
                                                                     pol]['MAG'][i + 1],
                                                                 ditTable[tel][spec][pol]['DIT'][i])
                        buffer += "\n"
            Hut = ditTable[tel]['Hut']
        return buffer

    def getPionierTemplateName(self, templateType, OBJTYPE):
        objType = "calibrator"
        if OBJTYPE and "SCI" in OBJTYPE:
            objType = "science"
        if OBJTYPE:
            return "_".join((self.getName(), templateType, objType))
        return "_".join((self.getName(), templateType))

    def getPionierObsTemplateName(self, OBJTYPE):
        return self.getPionierTemplateName("obs", OBJTYPE)

    def createPionierOB(
            self, p2container, obTarget, obConstraints, acqTSF, obsTSF, kappaTSF, darkTSF, OBJTYPE, instrumentMode,
            TEL_COU_GSSOURCE, GSRA, GSDEC, TEL_COU_MAG, LSTINTERVAL):

        api = self.facility.getAPI()
        ui = self.ui
        ui.setProgress(0.1)

        # TODO compute value
        VISIBILITY = 1.0

        # everything seems OK
        # create new OB in container:
        # TODO use a common function for next lines
        goodName = re.sub('[^A-Za-z0-9]+', '_', obTarget.name)
        OBS_DESCR = OBJTYPE[0:3] + '_' + goodName + '_PIONIER_' + \
            acqTSF.ISS_BASELINE[0] + '_' + instrumentMode

        ob, obVersion = api.createOB(p2container.containerId, OBS_DESCR)
        ui.addToLog("Getting new ob from p2: ")
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
        tpl, tplVersion = api.createTemplate(obId, 'PIONIER_acq')
        # and put values
        # start with acqTSF ones and complete manually missing ones
        values = acqTSF.getDict()
        # TODO move next updates earlier so it can be tested during checkOb phase
        values.update({'TEL.COU.GSSOURCE': TEL_COU_GSSOURCE,
                       'TEL.COU.ALPHA': GSRA,
                       'TEL.COU.DELTA': GSDEC,
                       'TEL.COU.MAG': round(TEL_COU_MAG, 3)
                       })

        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.3)

        # Put Obs template
        tpl, tplVersion = api.createTemplate(
            obId, self.getPionierObsTemplateName(OBJTYPE))
        ui.setProgress(0.4)
        values = obsTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.5)

        # put Kappa Matrix Template
        tpl, tplVersion = api.createTemplate(obId, 'PIONIER_gen_cal_kappa')
        ui.setProgress(0.6)
        values = kappaTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.7)

        # put Dark Template
        tpl, tplVersion = api.createTemplate(obId, 'PIONIER_gen_cal_dark')
        ui.setProgress(0.8)
        values = darkTSF.getDict()
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.9)

        # verify OB online
        response, _ = api.verifyOB(obId, True)
        ui.setProgress(1.0)
        self.showP2Response(response, ob, obId)
