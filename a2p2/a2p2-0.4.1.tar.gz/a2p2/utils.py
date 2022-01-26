#!/usr/bin/env python

__all__ = []

import cgi
import re
import traceback
import xml.etree.ElementTree

import numpy as np
from astropy.coordinates import SkyCoord


#
# This code is dead code but still leave the time we validate the new vlti directory code.
#


def parseXmlMessage(client, url, p2container):
    ui = client.ui
    api = client.facilityManager.getAPI()

    ui.setProgress(0)

    currentInstrument = p2container.instrument
    containerId = p2container.containerId

    e = xml.etree.ElementTree.parse(url)

    try:
        interferometerConfiguration = e.find('interferometerConfiguration')
        interferometer = interferometerConfiguration.find('name').text

        if interferometer != "VLTI":
            ui.ShowErrorMessage(
                "ASPRO did not sent obs for VLTI, no action taken.")
            return

        BASELINE = interferometerConfiguration.find('stations').text

        instrumentConfiguration = e.find('instrumentConfiguration')
        instrument = instrumentConfiguration.find('name').text
        if instrument != currentInstrument:
            ui.ShowErrorMessage("ASPRO not set for currently selected instrument: %s , expected %s" %
                                (currentInstrument, instrument))
            return
        # FIXME: TBD CHANGE TO HAVE OTHER INSTRUMENTS THAN GRAVITY!
        supportedInstruments = client.facilityManager.getSupportedInstruments()
        if not instrument in supportedInstruments:
            ui.ShowErrorMessage(
                "ASPRO not set for supported instruments [%s], no action taken." % (', '.join(supportedInstruments)))
            return

        instrumentMode = instrumentConfiguration.find('instrumentMode').text

        # if we have more than 1 obs, then better put it in a subfolder waiting
        # for the existence of a block sequence not yet implemented in P2
        obsconflist = e.findall('observationConfiguration')
        doFolder = (len(obsconflist) > 1)
        parentContainerId = containerId
        if doFolder:
            folderName = (obsconflist[0].find('SCTarget')).find('name').text
            folderName = re.sub('[^A-Za-z0-9]+', '_', folderName.strip())
            folder, _ = api.createFolder(containerId, folderName)
            containerId = folder['containerId']

        for observationConfiguration in e.findall('observationConfiguration'):
            # science. If calibrator, get also DIAMETER (and compute VIS?)

            TYPE = observationConfiguration.find('type').text
            if TYPE == 'SCIENCE':
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            scienceTarget = observationConfiguration.find('SCTarget')
            NAME = scienceTarget.find('name').text
            SCRA = scienceTarget.find('RA').text
            # RA MUST have 3 digits precision and DEC at least 2!!!
            w = SCRA.rfind('.')
            l = len(SCRA)
            if l - w < 4:
                ui.ShowErrorMessage(
                    "Object " + NAME + " has a too low precision in RA to be useable by VLTI, please correct.")
                return

            if l - w > 4:
                SCRA = SCRA[0:w + 4]
            SCDEC = scienceTarget.find('DEC').text
            w = SCDEC.rfind('.')
            l = len(SCDEC)
            if l - w < 3:
                ui.ShowErrorMessage(
                    "Object " + NAME + " has a too low precision in DEC to be useable by VLTI, please correct.")
                return
            if l - w > 4:
                SCDEC = SCDEC[0:w + 4]

            PMRA = 0.0
            PMDEC = 0.0
            # PMRA and DEC may be null without problem.
            pmratxt = scienceTarget.find('PMRA')
            if pmratxt != None:
                PMRA = float(pmratxt.text)
            pmdetxt = scienceTarget.find('PMDEC')
            if pmdetxt != None:
                PMDEC = float(pmdetxt.text)

            # but these should be defined.
            COU_GS_MAG = float(scienceTarget.find('FLUX_V').text)
            SEQ_INS_SOBJ_MAG = float(scienceTarget.find('FLUX_K').text)
            SEQ_FI_HMAG = float(scienceTarget.find('FLUX_H').text)
            # setup some default values, to be changed below
            COU_AG_GSSOURCE = 'SCIENCE'  # by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'
            COU_AG_PMA = 0.0
            COU_AG_PMD = 0.0
            dualField = False
            DIAMETER = 0.0
            VIS = 1.0

            if OBJTYPE == 'CALIBRATOR' and scienceTarget.find('DIAMETER') != None:
                DIAMETER = float(scienceTarget.find('DIAMETER').text)
                VIS = 1.0  # FIXME

            # initialize FT variables (must exist)
            FTRA = ""
            FTDEC = ""
            SEQ_FT_ROBJ_NAME = ""
            SEQ_FT_ROBJ_MAG = -99.99
            SEQ_FT_ROBJ_DIAMETER = -1.0
            SEQ_FT_ROBJ_VIS = -1.0

            # if FT Target is not ScTarget, we are in dual-field (TBD)
            ftTarget = observationConfiguration.find('FTTarget')
            if ftTarget != None:
                try:
                    SEQ_FT_ROBJ_NAME = ftTarget.find('name').text
                    FTRA = ftTarget.find('RA').text
                    w = FTRA.rfind('.')
                    l = len(FTRA)
                    if l - w < 4:
                        ui.ShowErrorMessage(
                            "Object " + SEQ_FT_ROBJ_NAME + " has a too low precision in RA to be useable by VLTI, please correct.")
                        return
                    if l - w > 4:
                        FTRA = FTRA[0:w + 4]
                    FTDEC = ftTarget.find('DEC').text
                    w = FTDEC.rfind('.')
                    l = len(FTDEC)
                    if l - w < 3:
                        ui.ShowErrorMessage(
                            "Object " + SEQ_FT_ROBJ_NAME + " has a too low precision in DEC to be useable by VLTI, please correct.")
                    return
                    if l - w > 4:
                        FTDEC = FTDEC[0:w + 4]
                    # no PMRA, PMDE for FT !!
                    SEQ_FI_HMAG = float(ftTarget.find('FLUX_H').text)
                    # just to say we must treat the case
                    # there is no FT Target
                    SEQ_FT_ROBJ_MAG = SEQ_FI_HMAG
                    SEQ_FT_ROBJ_DIAMETER = 0.0  # FIXME
                    SEQ_FT_ROBJ_VIS = 1.0  # FIXME
                    dualField = True
                except:
                    # print ("incomplete Fringe Tracker Target definition!")
                    ui.ShowErrorMessage(
                        "incomplete Fringe Tracker Target definition, OB not set!")

            # AO target
            aoTarget = observationConfiguration.find('AOTarget')
            if aoTarget != None:
                try:
                    AONAME = aoTarget.find('name').text
                    COU_AG_GSSOURCE = 'SETUPFILE'  # since we have an AO
                    AORA = aoTarget.find('RA').text
                    w = AORA.rfind('.')
                    l = len(AORA)
                    if l - w > 4:
                        AORA = AORA[0:w + 4]
                    AODEC = aoTarget.find('DEC').text
                    w = AODEC.rfind('.')
                    l = len(AODEC)
                    if l - w > 4:
                        AODEC = AODEC[0:w + 4]

                    COU_AG_PMA = 0.0
                    COU_AG_PMD = 0.0
                    # PMRA and DEC may be null without problem.
                    pmratxt = aoTarget.find('PMRA')
                    if pmratxt != None:
                        COU_AG_PMA = float(pmratxt.text)
                    pmdetxt = aoTarget.find('PMDEC')
                    if pmdetxt != None:
                        COU_AG_PMD = float(pmdetxt.text)

                except:
                    # print ("incomplete Adaptive Optics Target definition!")
                    ui.ShowErrorMessage(
                        "incomplete Adaptive Optics Target definition, OB not set!")

            # Guide Star
            gsTarget = observationConfiguration.find('GSTarget')
            if gsTarget != None:
                try:
                    GSNAME = gsTarget.find('name').text
                    COU_AG_SOURCE = 'SETUPFILE'  # since we have an GS
                    GSRA = gsTarget.find('RA').text
                    w = GSRA.rfind('.')
                    l = len(GSRA)
                    if l - w > 4:
                        GSRA = GSRA[0:w + 4]
                    GSDEC = gsTarget.find('DEC').text
                    w = GSDEC.rfind('.')
                    l = len(GSDEC)
                    if l - w > 4:
                        GSDEC = GSDEC[0:w + 4]
                    COU_GS_MAG = float(gsTarget.find('FLUX_V').text)
                    # no PMRA, PMDE for GS !!

                except:
                    # print ("incomplete GuideStar Target definition!")
                    ui.ShowErrorMessage(
                        "incomplete GuideStar Target definition, OB not set!")

            # LST interval
            try:
                obsConstraint = observationConfiguration.find(
                    'observationConstraints')
                LSTINTERVAL = obsConstraint.find('LSTinterval').text
            except:
                LSTINTERVAL = None

            # then call the ob-creation using the API.
            createGravityOB(
                ui, client.getUsername(
                ), api, containerId, OBJTYPE, NAME, BASELINE, instrumentMode, SCRA, SCDEC, PMRA, PMDEC,
                SEQ_INS_SOBJ_MAG, SEQ_FI_HMAG, DIAMETER,
                COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, COU_AG_PMA, COU_AG_PMD, dualField, FTRA, FTDEC,
                SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG, SEQ_FT_ROBJ_DIAMETER, SEQ_FT_ROBJ_VIS, LSTINTERVAL)
            ui.addToLog("Processed: " + NAME)
        # endfor
        if doFolder:
            containerId = parentContainerId
            doFolder = False
    except Exception as e:
        trace = traceback.format_exc(limit=1)
        ui.ShowErrorMessage(
            "General error or Absent Parameter in template!\n Missing magnitude or OB not set ?\n\nError :\n %s " % (
                trace))
        ui.setProgress(0)


# here dit must be a string since this is what p2 expects. NOT an integer
# or real/double.


def getDit(mag, spec, pol, tel, mode):
    string_dit = "1"

    if mode == 1:  # Dual
        if tel == 1:
            mag -= 3.7  # UT, DUAL
        else:
            mag -= 0.7  # AT, DUAL
    elif tel == 1:
        mag -= 3.0  # UT, SINGLE

    if spec == 2:  # HR
        if pol == 1:  # SPLIT
            if mag > 1:
                string_dit = "30"
            elif mag > 0:
                string_dit = "10"
            elif mag > -0.5:
                string_dit = "5"
            else:
                string_dit = "3"
        else:  # COMB
            if mag > 2:
                string_dit = "30"
            elif mag > 0.5:
                string_dit = "10"
            elif mag > -0.5:
                string_dit = "5"
            else:
                string_dit = "1"
    elif spec == 1:  # MR
        if pol == 1:  # SPLIT
            if mag > 4:
                string_dit = "30"
            elif mag > 3:
                string_dit = "10"
            elif mag > 2.5:
                string_dit = "5"
            elif mag > 1.5:
                string_dit = "3"
            elif mag > 0.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
        else:  # COMB
            if mag > 5:
                string_dit = "30"
            elif mag > 3.5:
                string_dit = "10"
            elif mag > 3.0:
                string_dit = "5"
            elif mag > 2.5:
                string_dit = "3"
            elif mag > 1.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
    elif spec == 0:  # LR FIXME VALUES ARE NOT GIVEN!!!!!!!!
        if pol == 1:  # SPLIT
            if mag > 9:
                string_dit = "30"
            elif mag > 7:
                string_dit = "10"
            elif mag > 6.5:
                string_dit = "5"
            elif mag > 5.5:
                string_dit = "3"
            elif mag > 4.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
        else:  # COMB
            if mag > 10:
                string_dit = "30"
            elif mag > 9:
                string_dit = "10"
            elif mag > 7.5:
                string_dit = "5"
            elif mag > 6.5:
                string_dit = "3"
            elif mag > 5.0:
                string_dit = "1"
            else:
                string_dit = "0.3"
    return string_dit


# define function creating the OB:


def createGravityOB(ui, username, api, containerId, OBJTYPE, NAME, BASELINE, instrumentMode, SCRA, SCDEC, PMRA, PMDEC,
                    SEQ_INS_SOBJ_MAG, SEQ_FI_HMAG, DIAMETER, COU_AG_GSSOURCE, GSRA, GSDEC, COU_GS_MAG, COU_AG_PMA,
                    COU_AG_PMD, dualField, FTRA, FTDEC, SEQ_FT_ROBJ_NAME, SEQ_FT_ROBJ_MAG, SEQ_FT_ROBJ_DIAMETER,
                    SEQ_FT_ROBJ_VIS, LSTINTERVAL):
    ui.setProgress(0.1)
    # UT or AT?
    isUT = (BASELINE[0] == "U")
    if isUT:
        SCtoREFmaxDist = 2000
        SCtoREFminDist = 400
        tel = 1
        if SEQ_INS_SOBJ_MAG < 5:
            skyTransparencyConstrainText = 'Variable, thin cirrus'
        else:
            skyTransparencyConstrainText = 'Clear'
    else:
        SCtoREFminDist = 1500
        SCtoREFmaxDist = 4000
        tel = 0
        if SEQ_INS_SOBJ_MAG < 3:
            skyTransparencyConstrainText = 'Variable, thin cirrus'
        else:
            skyTransparencyConstrainText = 'Clear'

    VISIBILITY = 1.0
    dualmode = 0
    # if Dualfield and offset between fields is bad, complain and do Nothing
    diff = [0, 0]
    if dualField:
        dualmode = 1
        # compute x,y between science and ref beams:
        diff = getSkyDiff(SCRA, SCDEC, FTRA, FTDEC)
        if np.abs(diff[0]) < SCtoREFminDist:
            ui.ShowErrorMessage("Dual-Field distance of two stars is  < " + str(
                SCtoREFminDist) + " mas, Please Correct.")
            return
        elif np.abs(diff[0]) > SCtoREFmaxDist:
            ui.ShowErrorMessage("Dual-Field distance of two stars is  > " + str(
                SCtoREFmaxDist) + " mas, Please Correct.")
            return

    if instrumentMode == 'LOW-COMBINED':
        INS_SPEC_RES = 'LOW'
        INS_FT_POL = 'OUT'
        INS_SPEC_POL = 'OUT'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 0, 0, tel, dualmode)
    elif instrumentMode == 'LOW-SPLIT':
        INS_SPEC_RES = 'LOW'
        INS_FT_POL = 'IN'
        INS_SPEC_POL = 'IN'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 0, 1, tel, dualmode)
    elif instrumentMode == 'MEDIUM-COMBINED':
        INS_SPEC_RES = 'MED'
        INS_FT_POL = 'OUT'
        INS_SPEC_POL = 'OUT'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 1, 0, tel, dualmode)
    elif instrumentMode == 'MEDIUM-SPLIT':
        INS_SPEC_RES = 'MED'
        INS_FT_POL = 'IN'
        INS_SPEC_POL = 'IN'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 1, 1, tel, dualmode)
    elif instrumentMode == 'HIGH-COMBINED':
        INS_SPEC_RES = 'HIGH'
        INS_FT_POL = 'OUT'
        INS_SPEC_POL = 'OUT'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 2, 0, tel, dualmode)
    elif instrumentMode == 'HIGH-SPLIT':
        INS_SPEC_RES = 'HIGH'
        INS_FT_POL = 'IN'
        INS_SPEC_POL = 'IN'
        string_dit = getDit(SEQ_INS_SOBJ_MAG, 2, 1, tel, dualmode)
    else:
        ui.ShowErrorMessage("Invalid Instrument Mode, Please Correct.")
        return

    # compute ndit, nexp
    dit = float(string_dit)
    ndit = 300 / dit
    if ndit < 10:
        ndit = 10
    if ndit > 300:
        ndit = 300
    ndit = int(ndit)  # must be integer
    exptime = int(ndit * dit + 40)  # 40 sec overhead by exp
    nexp = (1800 - 900) / exptime
    nexp = int(nexp)
    ui.addToLog('number of exposures to reach 1800 s per OB is ' + str(nexp))
    if nexp < 3:
        nexp = 3  # min is O S O
        # recompute ndit
        exptime = (1800 - 900) / nexp
        ndit = (exptime - 40) / dit
        ndit = int(ndit)
        if ndit < 10:
            ndit = 10
            ui.addToLog(
                "**Warning**, OB NDIT has been set to min value=10, but OB will take longer than 1800 s")
    nexp %= 40
    sequence = 'O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O'
    my_sequence = sequence[0:2 * nexp]

    # everything seems OK
    # create new OB in container:
    goodName = re.sub('[^A-Za-z0-9]+', '_', NAME.strip())
    if OBJTYPE == 'SCIENCE':
        isCalib = False
        OBS_DESCR = 'SCI_' + goodName + '_GRAVITY_' + \
                    BASELINE.replace(' ', '') + '_' + instrumentMode
    else:
        isCalib = True
        OBS_DESCR = 'CAL_' + goodName + '_GRAVITY_' + \
                    BASELINE.replace(' ', '') + '_' + instrumentMode
    ob, obVersion = api.createOB(containerId, OBS_DESCR)
    obId = ob['obId']

    # we use obId to populate OB
    ob['obsDescription']['name'] = OBS_DESCR[0:min(len(OBS_DESCR), 31)]
    ob['obsDescription']['userComments'] = 'Generated by ' + \
                                           username + ' using ASPRO 2 (c) JMMC'
    # ob['obsDescription']['InstrumentComments'] = 'AO-B1-C2-E3' #should be a
    # list of alternative quadruplets!

    ob['target']['name'] = NAME.replace(' ', '_')
    ob['target']['ra'] = SCRA
    ob['target']['dec'] = SCDEC
    ob['target']['properMotionRa'] = round(PMRA / 1000.0, 4)
    ob['target']['properMotionDec'] = round(PMDEC / 1000.0, 4)

    ob['constraints']['name'] = 'Aspro-created constraint'
    # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
    # The seeing value allowed for this OB is >= java0x0 arcsec."
    ob['constraints']['seeing'] = 1.0
    ob['constraints']['skyTransparency'] = skyTransparencyConstrainText
    ob['constraints']['baseline'] = BASELINE.replace(' ', '-')
    # FIXME: default values NOT IN ASPRO!
    # ob['constraints']['airmass'] = 5.0
    # ob['constraints']['fli'] = 1

    ob, obVersion = api.saveOB(ob, obVersion)

    # LST constraints if present
    # by default, above 40 degree. Will generate a WAIVERABLE ERROR if not.
    if LSTINTERVAL:
        sidTCs, stcVersion = api.getSiderealTimeConstraints(obId)
        lsts = LSTINTERVAL.split('/')
        lstStartSex = lsts[0]
        lstEndSex = lsts[1]
        # p2 seems happy with endlst < startlst
        # a = SkyCoord(lstStartSex+' +0:0:0',unit=(u.hourangle,u.deg))
        # b = SkyCoord(lstEndSex+' +0:0:0',unit=(u.hourangle,u.deg))
        # if b.ra.deg < a.ra.deg:
        # api.saveSiderealTimeConstraints(obId,[ {'from': lstStartSex, 'to': '00:00'},{'from': '00:00','to': lstEndSex}], stcVersion)
        # else:
        api.saveSiderealTimeConstraints(
            obId, [{'from': lstStartSex, 'to': lstEndSex}], stcVersion)

    ui.setProgress(0.2)

    # then, attach acquisition template(s)
    if dualField:
        tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_dual_acq')
        # put values
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
            'SEQ.FT.ROBJ.NAME': SEQ_FT_ROBJ_NAME,
            'SEQ.FT.ROBJ.MAG': round(SEQ_FT_ROBJ_MAG, 3),
            'SEQ.FT.ROBJ.DIAMETER': SEQ_FT_ROBJ_DIAMETER,
            'SEQ.FT.ROBJ.VIS': SEQ_FT_ROBJ_VIS,
            'SEQ.FT.MODE': "AUTO",
            'SEQ.INS.SOBJ.NAME': NAME,
            'SEQ.INS.SOBJ.MAG': round(SEQ_INS_SOBJ_MAG, 3),
            'SEQ.INS.SOBJ.DIAMETER': DIAMETER,
            'SEQ.INS.SOBJ.VIS': VISIBILITY,
            'SEQ.INS.SOBJ.X': diff[0],
            'SEQ.INS.SOBJ.Y': diff[1],
            'SEQ.FI.HMAG': round(SEQ_FI_HMAG, 3),
            'TEL.TARG.PARALLAX': 0.0,
            'INS.SPEC.RES': INS_SPEC_RES,
            'INS.FT.POL': INS_FT_POL,
            'INS.SPEC.POL': INS_SPEC_POL,
            'COU.AG.GSSOURCE': COU_AG_GSSOURCE,
            'COU.AG.ALPHA': GSRA,
            'COU.AG.DELTA': GSDEC,
            'COU.GS.MAG': round(COU_GS_MAG, 3),
            'COU.AG.PMA': round(COU_AG_PMA / 1000, 4),
            'COU.AG.PMD': round(COU_AG_PMD / 1000, 4)
        }, tplVersion)

    else:
        tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_single_acq')
        # put values
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
            'SEQ.INS.SOBJ.NAME': NAME,
            'SEQ.INS.SOBJ.MAG': round(SEQ_INS_SOBJ_MAG, 3),
            'SEQ.INS.SOBJ.DIAMETER': DIAMETER,
            'SEQ.INS.SOBJ.VIS': VISIBILITY,
            'COU.AG.GSSOURCE': COU_AG_GSSOURCE,
            'COU.AG.ALPHA': GSRA,
            'COU.AG.DELTA': GSDEC,
            'COU.GS.MAG': round(COU_GS_MAG, 3),
            'COU.AG.PMA': round(COU_AG_PMA / 1000, 4),
            'COU.AG.PMD': round(COU_AG_PMD / 1000, 4),
            'SEQ.FI.HMAG': round(SEQ_FI_HMAG, 3),
            'TEL.TARG.PARALLAX': 0.0,
            'INS.SPEC.RES': INS_SPEC_RES,
            'INS.FT.POL': INS_FT_POL,
            'INS.SPEC.POL': INS_SPEC_POL
        }, tplVersion)

    templateId = tpl['templateId']

    ui.setProgress(0.3)

    if isCalib:
        if dualField:
            tpl, tplVersion = api.createTemplate(
                obId, 'GRAVITY_dual_obs_calibrator')
        else:
            tpl, tplVersion = api.createTemplate(
                obId, 'GRAVITY_single_obs_calibrator')
    else:
        if dualField:
            tpl, tplVersion = api.createTemplate(obId, 'GRAVITY_dual_obs_exp')
        else:
            tpl, tplVersion = api.createTemplate(
                obId, 'GRAVITY_single_obs_exp')
    templateId = tpl['templateId']

    ui.setProgress(0.4)

    # put values. they are the same except for dual obs science (?)
    if dualField and not isCalib:
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
            'DET2.DIT': string_dit,
            'DET2.NDIT.OBJECT': ndit,
            'DET2.NDIT.SKY': ndit,
            'SEQ.OBSSEQ': my_sequence,
            'SEQ.SKY.X': 2000,
            'SEQ.SKY.Y': 2000
        }, tplVersion)
    else:
        tpl, tplVersion = api.setTemplateParams(obId, tpl, {
            'DET2.DIT': string_dit,
            'DET2.NDIT.OBJECT': ndit,
            'DET2.NDIT.SKY': ndit,
            'SEQ.OBSSEQ': my_sequence,
            'SEQ.RELOFF.X': "0.0",
            'SEQ.RELOFF.Y': "0.0",
            'SEQ.SKY.X': 2000,
            'SEQ.SKY.Y': 2000
        }, tplVersion)

    ui.setProgress(0.5)

    # verify OB online
    response, _ = api.verifyOB(obId, True)

    ui.setProgress(1.0)

    if response['observable']:
        ui.ShowInfoMessage('OB ' + str(obId) + ' ' + ob['name'] + ' is OK.')
        ui.addToLog('OB: ' + str(obId) + ' is ok')
    else:
        s = ""
        for ss in response['messages']:
            s += cgi.escape(ss) + '\n'
        ui.ShowWarningMessage(
            'OB ' + str(obId) + ' <b>HAS Warnings</b>. ESO says:\n\n' + s)
        ui.addToLog('OB: ' + str(obId) + ' created with warnings')
        # (NOTE: we need to escape things like <= in returned text)

        # fetch OB again to confirm its status change
        #   ob, obVersion = api.getOB(obId)
        # python3: print('Status of verified OB', obId, 'is now',
        # ob['obStatus'])

    def getSkyDiff(ra, dec, ftra, ftdec):
        science = SkyCoord(ra, dec, frame='icrs', unit='deg')
        ft = SkyCoord(ftra, ftdec, frame='icrs', unit='deg')
        ra_offset = (science.ra - ft.ra) * np.cos(ft.dec.to('radian'))
        dec_offset = (science.dec - ft.dec)
        return [ra_offset.deg * 3600 * 1000, dec_offset.deg * 3600 * 1000]  # in mas
