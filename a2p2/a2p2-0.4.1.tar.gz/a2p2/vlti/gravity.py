
#!/usr/bin/env python

__all__ = []

import re

import numpy as np

from a2p2.vlti.instrument import OBConstraints
from a2p2.vlti.instrument import OBTarget
from a2p2.vlti.instrument import TSF
from a2p2.vlti.instrument import VltiInstrument

HELPTEXT = """
Please define Gravity instrument help in a2p2/vlti/gravity.py
"""


class Gravity(VltiInstrument):

    def __init__(self, facility):
        VltiInstrument.__init__(self, facility, "GRAVITY")

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

        # Retrieve SPEC_RES and POL info from instrumentMode

        # We could force ins_spec_res to be default but prefer a bad keyword value
        # that throws a Value Error if instrumentMode does not start with an accepted one
        # ins_spec_res = self.getDefault("GRAVITY_gen_acq.tsf", "INS.SPEC.RES")
        ins_spec_res = "BAD_SPEC_RES"
        for res in self.getRange("GRAVITY_gen_acq.tsf", "INS.SPEC.RES"):
            if res in instrumentMode[0:len(res)]:
                ins_spec_res = res

        if "COMBINED" in instrumentMode:
            ins_pol = "OUT"
        else:
            ins_pol = 'IN'

        for observationConfiguration in self.getSequence(ob):

            # create keywords storage objects
            acqTSF = TSF(self, "GRAVITY_gen_acq.tsf")
            obsTSF = TSF(self, "GRAVITY_single_obs_exp.tsf")
            # alias for
            # ,GRAVITY_single_obs_calibrator.tsf,GRAVITY_dual_obs_exp.tsf,GRAVITY_dual_obs_calibrator.tsf")
            obTarget = OBTarget()
            obConstraints = OBConstraints(self)

            # set common properties if any
            if ins_spec_res:
                acqTSF.INS_SPEC_RES = ins_spec_res
            acqTSF.INS_FT_POL = ins_pol
            acqTSF.INS_SPEC_POL = ins_pol

            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            scienceTarget = observationConfiguration.SCTarget

            # define target
            acqTSF.SEQ_INS_SOBJ_NAME = scienceTarget.name.strip()
            obTarget.name = acqTSF.SEQ_INS_SOBJ_NAME.replace(
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
            COU_GS_MAG = self.getFlux(scienceTarget, "V")
            acqTSF.SEQ_INS_SOBJ_MAG = self.getFlux(scienceTarget, "K")
            acqTSF.SEQ_FI_HMAG = self.getFlux(scienceTarget, "H")

            # setup some default values, to be changed below
            COU_AG_GSSOURCE = 'SCIENCE'  # by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'
            dualField = False
            dualFieldDistance = 0.0  # needed as must exist for the argument list of createGravityOB

            # initialize FT variables (must exist)
            # TODO remove next lines using a dual_acq TSF that would handle
            # them
            SEQ_FT_ROBJ_NAME = ""
            SEQ_FT_ROBJ_MAG = -99.99
            SEQ_FT_ROBJ_DIAMETER = -1.0
            SEQ_FT_ROBJ_VIS = -1.0

            # if FT Target is not ScTarget, we are in dual-field (TBD)
            ftTarget = ob.get(observationConfiguration, "FTTarget")
            if ftTarget != None:
                SEQ_FT_ROBJ_NAME = ftTarget.name
                FTRA, FTDEC = self.getCoords(ftTarget)
                # no PMRA, PMDE for FT !!
                SEQ_FI_HMAG = float(ftTarget.FLUX_H)
                # just to say we must treat the case there
                # is no FT Target
                SEQ_FT_ROBJ_MAG = self.getFlux(ftTarget, "K")
                SEQ_FT_ROBJ_DIAMETER = 0.0  # FIXME
                SEQ_FT_ROBJ_VIS = 1.0  # FIXME
                dualField = True

                # test distance in dual field mode
                if tel == "UT":
                    SCtoREFmaxDist = 2000
                    SCtoREFminDist = 0  # before P103: 400
                else:
                    SCtoREFminDist = 0  # before P103: 1500
                    SCtoREFmaxDist = 4000
                # compute x,y between science and ref beams:
                dualFieldDistance = self.getSkyDiff(
                    obTarget.ra, obTarget.dec, FTRA, FTDEC)
                if np.abs(dualFieldDistance[0]) < SCtoREFminDist:
                    raise ValueError("Dual-Field distance of two stars is  < " + str(
                        SCtoREFminDist) + " mas, Please Correct.")
                elif np.abs(dualFieldDistance[0]) > SCtoREFmaxDist:
                    raise ValueError("Dual-Field distance of two stars is  > " + str(
                        SCtoREFmaxDist) + " mas, Please Correct.")

            # AO target
            aoTarget = ob.get(observationConfiguration, "AOTarget")
            if aoTarget != None:
                AONAME = aoTarget.name
                COU_AG_GSSOURCE = 'SETUPFILE'  # since we have an AO
                GSRA, GSDEC = self.getCoords(aoTarget, requirePrecision=False)
                acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(
                    aoTarget)
                # Case of CIAO to be implemented...based on v and k magnitudes?
                COU_GS_MAG = float(aoTarget.FLUX_V)

            # Guide Star
            gsTarget = ob.get(observationConfiguration, 'GSTarget')
            if gsTarget != None and aoTarget == None:
                COU_AG_SOURCE = 'SETUPFILE'  # since we have an GS
                GSRA, GSDEC = self.getCoords(gsTarget, requirePrecision=False)
                acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(
                    gsTarget)
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
            if acqTSF.SEQ_INS_SOBJ_MAG < skyTransparencyMagLimits[tel]:
                obConstraints.skyTransparency = 'Variable, thin cirrus'
            else:
                obConstraints.skyTransparency = 'Clear'
            # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.

            # The seeing value allowed for this OB is >= java0x0 arcsec."
            # FIXME REPLACE SEEING THAT IS NO MORE SUPPORTED
            # obConstraints.seeing = 1.0

            # FIXME: default values NOT IN ASPRO!
            # constaints.airmass = 5.0
            # constaints.fli = 1

            # compute dit, ndit, nexp
            dit = self.getDit(tel, acqTSF.INS_SPEC_RES, acqTSF.INS_SPEC_POL,
                              acqTSF.SEQ_INS_SOBJ_MAG, dualField, showWarning=(p2container == None))
            ndit = 300 / dit
            if ndit < 10:
                ndit = 10
            if ndit > 300:
                ndit = 300
            ndit = int(ndit)  # must be integer
            exptime = int(ndit * dit + 40)  # 40 sec overhead by exp
            nexp = (1800 - 900) / exptime
            nexp = int(nexp)
            ui.addToLog(
                'number of exposures to reach 1800 s per OB is ' + str(nexp))
            if nexp < 3:
                nexp = 3  # min is O S O
                # recompute ndit
                exptime = (1800 - 900) / nexp
                ndit = (exptime - 40) / dit
                ndit = int(ndit)
                if ndit < 10:
                    ndit = 10
                    ui.addToLog(
                        "**Warning**, OB NDIT has been set to min value=%d, but OB will take longer than 1800 s" % (
                            ndit))
            nexp %= 40
            sequence = 'O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O'
            my_sequence = sequence[0:2 * nexp]
            # and store computed values in obsTSF
            obsTSF.DET2_DIT = str(dit)
            obsTSF.DET2_NDIT_OBJECT = ndit
            obsTSF.DET2_NDIT_SKY = ndit
            obsTSF.SEQ_OBSSEQ = my_sequence
            obsTSF.SEQ_SKY_X = 2000
            obsTSF.SEQ_SKY_Y = 2000

            # then call the ob-creation using the API if p2container exists.
            if p2container == None:
                ui.addToLog(obTarget.name +
                            " ready for p2 upload (details logged)")
                ui.addToLog(obTarget, False)
                ui.addToLog(obConstraints, False)
                ui.addToLog(acqTSF, False)
                ui.addToLog(obsTSF, False)
            else:
                self.createGravityOB(p2container, obTarget, obConstraints, acqTSF, obsTSF, OBJTYPE, instrumentMode,
                                     DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, dualField, dualFieldDistance,
                                     SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG, SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS,
                                     LSTINTERVAL)
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
        buffer = '    Mode     |Spec |  Pol  |Tel |       K       | DIT(s)\n'
        buffer += '--------------------------------------------------------\n'
        for tel in ['AT']:
            for spec in ['LOW', 'MED', 'HIGH']:
                for pol in ['OUT', 'IN']:
                    for i in range(len(ditTable[tel][spec][pol]['DIT'])):
                        buffer += 'Single Field | %4s | %3s | %2s |' % (
                            spec, pol, tel)
                        buffer += ' %4.1f <K<= %3.1f | %4.1f' % (ditTable[tel][spec][pol]['MAG'][i],
                                                                 ditTable[tel][spec][
                                                                     pol]['MAG'][i + 1],
                                                                 ditTable[tel][spec][pol]['DIT'][i])
                        buffer += "\n"
            Kdf = ditTable[tel]['Kdf']
            Kut = ditTable[tel]['Kut']
            buffer += ' Dual Field  |  all | all | %2s | Kdf = K - %.1f |  -\n' % (
                tel, Kdf)
            tel = "UT"
            buffer += 'Single Field |  all | all | %2s | Kdf = K - %.1f |  -\n' % (
                tel, Kut)
            buffer += ' Dual Field  |  all | all | %2s | Kdf = K - %.1f |  -\n' % (
                tel, Kut + Kdf)
        return buffer

    def getGravityTemplateName(self, templateType, dualField, OBJTYPE):
        objType = "calibrator"
        if OBJTYPE and "SCI" in OBJTYPE:
            objType = "exp"
        field = "single"

        if dualField:
            field = "dual"
        if OBJTYPE:
            return "_".join((self.getName(), field, templateType, objType))
        return "_".join((self.getName(), field, templateType))

    def getGravityObsTemplateName(self, OBJTYPE, dualField=False):
        return self.getGravityTemplateName("obs", dualField, OBJTYPE)

    def getGravityAcqTemplateName(self, dualField=False, OBJTYPE=None):
        return self.getGravityTemplateName("acq", dualField, OBJTYPE)

    def createGravityOB(
            self, p2container, obTarget, obConstraints, acqTSF, obsTSF, OBJTYPE, instrumentMode,
            DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, dualField, dualFieldDistance, SEQ_FT_ROBJ_NAME,
            SEQ_FT_ROBJ_MAG,
            SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL):

        api = self.facility.getAPI()
        ui = self.ui
        ui.setProgress(0.1)

        # TODO compute value
        VISIBILITY = 1.0

        # everything seems OK
        # create new OB in container:
        # TODO use a common function for next lines
        goodName = re.sub('[^A-Za-z0-9]+', '_', acqTSF.SEQ_INS_SOBJ_NAME)
        OBS_DESCR = OBJTYPE[0:3] + '_' + goodName + '_GRAVITY_' + \
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
        tpl, tplVersion = api.createTemplate(
            obId, self.getGravityAcqTemplateName(dualField=dualField))
        # and put values
        # start with acqTSF ones and complete manually missing ones
        values = acqTSF.getDict()
        # TODO move next updates earlier so it can be tested during checkOb phase
        values.update({
            'SEQ.INS.SOBJ.DIAMETER': DIAMETER,
            'SEQ.INS.SOBJ.VIS': VISIBILITY,
            'COU.AG.GSSOURCE': COU_AG_GSSOURCE,
            'COU.AG.ALPHA': GSRA,
            'COU.AG.DELTA': GSDEC,
            'COU.GS.MAG': round(COU_GS_MAG, 3),
            'TEL.TARG.PARALLAX': 0.0
        })
        if dualField:
            values.update({'SEQ.INS.SOBJ.X': dualFieldDistance[0],
                           'SEQ.INS.SOBJ.Y': dualFieldDistance[1],
                           'SEQ.FT.ROBJ.NAME': SEQ_FT_ROBJ_NAME,
                           'SEQ.FT.ROBJ.MAG': round(SEQ_FT_ROBJ_MAG, 3),
                           'SEQ.FT.ROBJ.DIAMETER': SEQ_FT_ROBJ_DIAMETER,
                           'SEQ.FT.ROBJ.VIS': SEQ_FT_ROBJ_VIS,
                           'SEQ.FT.MODE': "AUTO"})
        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.3)

        tpl, tplVersion = api.createTemplate(
            obId, self.getGravityObsTemplateName(OBJTYPE, dualField))
        ui.setProgress(0.4)

        # put values. they are the same except for dual obs science (?)
        values = obsTSF.getDict()
        # TODO move next updates earlier so it can be tested during checkOb phase
        if dualField and OBJTYPE == 'SCIENCE':
            values.update({'SEQ.RELOFF.X': [0.0], 'SEQ.RELOFF.Y': [0.0]})

        tpl, tplVersion = api.setTemplateParams(obId, tpl, values, tplVersion)
        ui.setProgress(0.5)

        # verify OB online
        response, _ = api.verifyOB(obId, True)
        ui.setProgress(1.0)
        self.showP2Response(response, ob, obId)
