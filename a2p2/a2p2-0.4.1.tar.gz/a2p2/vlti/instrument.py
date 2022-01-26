#!/usr/bin/env python

__all__ = []

import collections
import datetime
import json
import os
# import ast
import re
import logging

import numpy as np
from astropy.coordinates import SkyCoord

from a2p2.instrument import Instrument

logger = logging.getLogger(__name__)

class VltiInstrument(Instrument):

    def __init__(self, facility, insname):
        Instrument.__init__(self, facility, insname)
        self.facility = facility
        self.ui = facility.ui

        # use in latter lazy initialisation
        self.rangeTable = None
        self.ditTable = None

    def get(self, obj, fieldname, defaultvalue):
        if fieldname in obj._fields:
            return getattr(obj, fieldname)
        else:
            return defaultvalue


    def getSequence(self, ob):
    # We may look at ob.observationSchedule but at present tuime schedule still is computed on a2p2 side
        sci=[]
        cal=[]
        for observationConfiguration in ob.observationConfiguration:
            if 'SCIENCE' in observationConfiguration.type:
                sci.append(observationConfiguration)
            else:
                cal.append(observationConfiguration)
        if len(sci)+len(cal) <= 2: # return [CAL] [SCI]
            return cal+sci
        # else return CAL1 SCI CAL2 [SCI CAL3] [SCI CAL4]
        seq=[]
        for c in cal :
            seq.append(c)
            seq+=sci
        return seq[0:-1]


    # checkOB() must be defined by each instruments
    # def checkOB(self, ob, p2container=None):
    # consider dryMode if p2container is None else check again and submit on p2 side

    def submitOB(self, ob, p2container):
        api = self.facility.getAPI()
        ui = self.ui

        # create new container
        obsconflist = ob.observationConfiguration

        # Aspro2 always send SCI at first position (or CAL if no SCI)
        folderName = obsconflist[0].SCTarget.name
        folderName = re.sub('[^A-Za-z0-9]+', '_', folderName.strip())
        # prefix with username to make test folder clearer
        if p2container.isRoot() and self.facility.isTutorialAccount():
            folderName += "_" + self.facility.a2p2client.preferences.getP2UserCommentName()

        # do create a folder or concatenation only for SM or tutorial account
        # should we create a concatenation only if we have multiple objects
        if p2container.isRoot():
            # create a concatenation if service mode (even if we do not have any cal at this stage)
            if p2container.isServiceModeRun():
                # TODO fix bug when we keep the last selection that is a Concatenation. Concatenation can't be nested.
                # use parent container  or ask user to choose another container location ?
                folder, _ = api.createConcatenation(
                    p2container.containerId, folderName)
                ui.addToLog(f"concatenation '{folderName}' created")
            else:
                folder, _ = api.createFolder(p2container.containerId, folderName)
                ui.addToLog(f"folder '{folderName}' created")
            p2container.containerId = folder['containerId']
        else:
            ui.addToLog("concatenation or folder not created")

        ui.addToLog("OB checked / preparing  submission...")
        self.checkOB(ob, p2container)

    def getCoords(self, target, requirePrecision=True):
        """
        Format coordinates from given target to be VLTI compliant.
        Throws an exception if requirePrecision is true and given inputs have less than 3 (RA) or 2 (DEC) digits.
        """

        NAME = target.name

        RA = target.RA
        w = RA.rfind('.')
        l = len(RA)
        if l - w < 4 and requirePrecision:
            raise ValueError(
                "Object " + NAME + " has a too low precision in RA to be useable by VLTI, please correct with 3 or more digits.")
        if l - w > 4:
            RA = RA[0:w + 4]

        DEC = target.DEC
        w = DEC.rfind('.')
        l = len(DEC)
        if l - w < 3 and requirePrecision:
            raise ValueError(
                "Object " + NAME + " has a too low precision in DEC to be useable by VLTI,please correct with 2 or more digits.")
        if l - w > 4:
            DEC = DEC[0:w + 4]

        return RA, DEC

    def getPMCoords(self, target, defaultPMRA=0.0, defaultPMDEC=0.0):
        """
        Returns PMRA, PMDEC as float values rounded to 4 decimal digits. 0.0 is used as default if not present.
        """
        PMRA = self.get(target, "PMRA", defaultPMRA)
        PMDEC = self.get(target, "PMDEC", defaultPMDEC)
        return round(float(PMRA) / 1000.0, 4), round(float(PMDEC) / 1000.0, 4)

    def getFlux(self, target, flux):
        """
        Returns Flux as float values rounded to 3 decimal digits.

        flux in 'V', 'J', 'H'...
        """
        return round(float(getattr(target, "FLUX_" + flux)), 3)

    def getBaselineCode(self, baseline):
        # as of P104
        # take care if you change next branch order
        if "B2" in baseline:
            return "small"
        elif "G2" in baseline:
            return "medium"
        elif "J3" in baseline:
            return "large"
        elif "K0" in baseline:
            return "astrometric"
        elif "U" in baseline:
            return "UTs"
        else:
            raise ValueError(
                "Can't detect Interferometric Array type from given baseline : %s)" % (baseline))

    def checkIssVltiType(self, acqTSF):
        # TODO improve handling of this keyword using input from Aspro2's OB
        psection="p2.iss.vltitype"
        if self.facility.a2p2client.preferences.getConfigKeys(psection):
            vltitypePref=[v for v in self.facility.a2p2client.preferences.getConfigKeys(psection) if self.isInRange(acqTSF.tpl, "ISS.VLTITYPE", v) ]
            if vltitypePref:
                self.ui.addToLog(f"Using {psection} preference value : '{vltitypePref}'")
                acqTSF.ISS_VLTITYPE = vltitypePref


    def getA2p2Comments(self):
        return 'Generated by ' + self.facility.a2p2client.preferences.getP2UserCommentName() + \
               ' using ASPRO 2 (c) JMMC on ' + \
            datetime.datetime.now().isoformat()

    # ditTable and rangeTable are extracted from online doc:
    # -- https://www.eso.org/sci/facilities/paranal/instruments/gravity/doc/Gravity_TemplateManual.pdf
    # they are saved in json and displayed in the Help on application startup

    # k = 'GRAVITY_gen_acq.tsf'
    # using collections.OrderedDict to keep the order of keys:
    # rangeTable[k] = collections.OrderedDict({})
    # rangeTable[k]['SEQ.FI.HMAG']={'min':-10., 'max':20., 'default':0.0}
    # ...

    def getDitTable(self):
        if self.ditTable:
            return self.ditTable
        f = os.path.join(
            self.facility.getConfDir(), self.getName() + "_ditTable.json")
        self.ditTable = json.load(open(f))
        return self.ditTable

    def getDit(self, tel, spec, pol, K, dualFeed=False, showWarning=False):
        """
        finds DIT according to ditTable and K magnitude K

        'tel' in "AT" or "UT"
        'spec' in ditTable[tel].keys()
        'pol' in ditTable[tel][spec].keys()

        * a ValueError is thrown for out of range values *
        """
        # TODO add LOW mode  as new 'spec' entry for Gravity
        #        if showWarning and spec == "LOW":
        #            self.ui.ShowWarningMessage("DIT table does not provide LOW values. Using MED as workarround.")
        # if spec == "LOW":
        #    spec="HIGH"
        ditTable = self.getDitTable()
        mags = ditTable["AT"][spec][pol]['MAG']
        dits = ditTable["AT"][spec][pol]['DIT']
        if dualFeed:
            dK = ditTable["AT"]['Kdf']
        else:
            dK = 0.0
        if tel == "UT":
            dK += ditTable["AT"]['Kut']
        for i, d in enumerate(dits):
            if mags[i] < (K - dK) and (K - dK) <= mags[i + 1]:
                return d

        # handle out of bounds
        kmin = 1000
        kmax = -1000
        for i, d in enumerate(dits):
            kmin = min(kmin, mags[i] + dK)
            kmax = max(kmax, mags[i + 1] + dK)
        if kmin == K:
            return minDIT
        raise ValueError(
            "K mag (%f) is out of ranges [%f,%f]\n for this mode (tel=%s, spec=%s, pol=%s, dualFeed=%s)" % (
                K, kmin, kmax, tel, spec, pol, dualFeed))

    def getRangeTable(self):
        if self.rangeTable:
            return self.rangeTable
        f = os.path.join(
            self.facility.getConfDir(), self.getShortName() + "_rangeTable.json")
        # TODO use .tmp.json keys
        # using collections.OrderedDict to keep the order of keys:
        self.rangeTable = json.load(
            open(f), object_pairs_hook=collections.OrderedDict)
        return self.rangeTable

    def isInRange(self, tpl, key, value):
        """
        check if "value" is in range of keyword "key" for template "tpl"

        ValueError raised if key or tpl is not found.
        """
        rangeTable = self.getRangeTable()
        _tpl = ''
        # -- find relevant range dictionnary
        for k in rangeTable.keys():
            if tpl in [l.strip() for l in k.split(',')]:
                _tpl = k
        if _tpl == '':
            raise ValueError("unknown template '%s'" % tpl)
        if not key in rangeTable[_tpl].keys():
            raise ValueError(
                "unknown keyword '%s' in template '%s'" % (key, tpl))
        if 'min' in rangeTable[_tpl][key].keys() and \
                'max' in rangeTable[_tpl][key].keys():
            return value >= rangeTable[_tpl][key]['min'] and \
                value <= rangeTable[_tpl][key]['max']
        if 'list' in rangeTable[_tpl][key].keys():
            #            return value in rangeTable[_tpl][key]['list']
            if type(value) is list:
                for v in value:
                    if not v in rangeTable[_tpl][key]['list']:
                        return False
                    return True
            else:
                return value in rangeTable[_tpl][key]['list']
        if 'spaceseparatedlist' in rangeTable[_tpl][key].keys():
            ssl = rangeTable[_tpl][key]['spaceseparatedlist']
            for e in value.strip().split(" "):
                if not e in ssl:
                    return False
            return True
        # no range provided in tsf file
        return True

    def getRange(self, tpl, key):
        """
        returns range of keyword "key" for template "tpl"

        ValueError raised if key or tpl is not found.
        """
        rangeTable = self.getRangeTable()
        _tpl = ''
        # -- find relevant range dictionnary
        for k in rangeTable.keys():
            if tpl in [l.strip() for l in k.split(',')]:
                _tpl = k
        if _tpl == '':
            raise ValueError("unknown template '%s'" % tpl)
        if not key in rangeTable[_tpl].keys():
            raise ValueError(
                "unknown keyword '%s' in template '%s'" % (key, tpl))
        if 'min' in rangeTable[_tpl][key].keys() and \
                'max' in rangeTable[_tpl][key].keys():
            return (rangeTable[_tpl][key]['min'], rangeTable[_tpl][key]['max'])
        if 'list' in rangeTable[_tpl][key].keys():
            return rangeTable[_tpl][key]['list']
        if 'spaceseparatedlist' in rangeTable[_tpl][key].keys():
            for e in value.split(" "):
                return rangeTable[_tpl][key]['spaceseparatedlist']

    def getDefault(self, tpl, key):
        """
        returns the default value if any exists for given "key" in template "tpl", else None

        ValueError raised if key or tpl is not found .
        """
        rangeTable = self.getRangeTable()
        _tpl = ''
        # -- find relevant range dictionnary
        for k in rangeTable.keys():
            if tpl in [l.strip() for l in k.split(',')]:
                _tpl = k
        if _tpl == '':
            raise ValueError("unknown template '%s'" % tpl)
        if not key in rangeTable[_tpl].keys():
            raise ValueError(
                "unknown keyword '%s' in template '%s'" % (key, tpl))
        if 'default' in rangeTable[_tpl][key].keys() :
            return rangeTable[_tpl][key]['default']
        return None

    def getRangeDefaults(self, tpl, ):
        """
        returns a dict of keywords/default values for template "tpl"

        ValueError raised if tpl is not found.
        """
        rangeTable = self.getRangeTable()
        _tpl = ''
        # -- find relevant range dictionnary
        for k in rangeTable.keys():
            if tpl in [l.strip() for l in k.split(',')]:
                _tpl = k
        if _tpl == '':
            raise ValueError("unknown template '%s'" % tpl)
        res = {}
        for key in rangeTable[_tpl].keys():
            if 'default' in rangeTable[_tpl][key].keys():
                res[key] = rangeTable[_tpl][key]["default"]
        return res


    def getSkyDiff(self, ra, dec, ftra, ftdec):
        science = SkyCoord(ra, dec, frame='icrs', unit='deg')
        ft = SkyCoord(ftra, ftdec, frame='icrs', unit='deg')
        ra_offset = (science.ra - ft.ra) * np.cos(ft.dec.to('radian'))
        dec_offset = (science.dec - ft.dec)
        return [ra_offset.deg * 3600 * 1000, dec_offset.deg * 3600 * 1000]  # in mas

    def getSiderealTimeConstraints(self, LSTINTERVAL):
        # by default, above 40 degree. Will generate a WAIVERABLE ERROR if not.
        # we could warn before ?
        intervals = []
        if LSTINTERVAL:
            for lst in LSTINTERVAL:
                lsts = lst.split('/')
                # p2 seems happy with endlst < startlst
                # a = SkyCoord(lstStartSex+' +0:0:0',unit=(u.hourangle,u.deg))
                # b = SkyCoord(lstEndSex+' +0:0:0',unit=(u.hourangle,u.deg))
                # if b.ra.deg < a.ra.deg:
                # api.saveSiderealTimeConstraints(obId,[ {'from': lstStartSex, 'to': '00:00'},{'from': '00:00','to': lstEndSex}], stcVersion)
                # else:
                lstStartSex = lsts[0]
                lstEndSex = lsts[1]
                intervals.append({'from': lstStartSex, 'to': lstEndSex})
        return intervals

    def saveSiderealTimeConstraints(self, api, obId, LSTINTERVAL):
        # wait for next Aspro release to only send constraints set by user
        return
        intervals = self.getSiderealTimeConstraints(LSTINTERVAL)
        if intervals:
            sidTCs, stcVersion = api.getSiderealTimeConstraints(obId)
            api.saveSiderealTimeConstraints(obId, intervals, stcVersion)

    def getHelp(self):
        s = self.getName()
        s_name = s
        if s_name == "GRAVITY":
            from a2p2.vlti.gravity import Gravity
            s += "\n\n GravityRangeTable: \n"
            s += Gravity.formatRangeTable(self)
            s += "\n\nGravityDitTable:\n"
            s += Gravity.formatDitTable(self)
        if s_name == "PIONIER":
            from a2p2.vlti.pionier import Pionier
            s += "\n\n PionierRangeTable: \n"
            s += Pionier.formatRangeTable(self)
            s += "\n\nPionierDitTable:\n"
            s += Pionier.formatDitTable(self)
        if s_name == "MATISSE_LM":  # "MATISSE_LM" "MATISSE_N"
            from a2p2.vlti.matisse import Matisse
            s += "\n\n MatisseRangeTable: \n"
            s += Matisse.formatRangeTable(self)
            s += "\n\nMatisseDitTable:\n"
            s += Matisse.formatDitTable(self)

        return s

    def showP2Response(self, response, ob, obId):
        if response['observable']:
            msg = 'OB ' + \
                  str(obId) + ' submitted successfully on P2\n' + \
                  ob['name'] + ' is OK.'
        else:
            msg = 'OB ' + str(obId) + ' submitted successfully on P2\n' + ob[
                'name'] + ' has WARNING.\n see LOG for details.'
        self.ui.addToLog('\n')
        #self.ui.ShowInfoMessage(msg)
        self.ui.addToLog(msg)
        self.ui.addToLog('\n'.join(response['messages']) + '\n\n')


# TemplateSignatureFile
# use new style class to get __getattr__ advantage


class TSF(object):

    def __init__(self, instrument, tpl):
        self.tpl = tpl
        self.instrument = instrument
        supportedTpl = instrument.getRangeTable().keys()

        # DO not init with default values for every keywords so we only transfert changed values
        # this also reduce the risk to transmit some  incompatible keywords accross various IP versions
        # a TODO will come to test accross dicts get from P2 and not in our json config
        # self.tsfParams = self.instrument.getRangeDefaults(tpl)
        self.tsfParams = {}

        self.__initialised = True
        # after initialisation, setting attributes is the same as setting an item

    def set(self, key, value, checkRange=True):
        if checkRange:
            if not self.instrument.isInRange(self.tpl, key, value):
                raise ValueError(
                    "Parameter value (%s) is out of range for keyword %s in template %s " % (str(value), key, self.tpl))
        # TODO check that key is valid when checkRange is False
        self.tsfParams[key] = value

    def get(self, key):
        # TODO offer to get default value
        return self.tsfParams[key]

    def getDict(self):
        return self.tsfParams

    def getP2Name(self):
        return self.tpl[0:-4]

    def __getattr__(self, name):  # called for non instance attributes (i.e. keywords)
        rname = name.replace('_', '.')
        if rname in self.tsfParams:
            return self.tsfParams[rname]
        else:
            raise AttributeError(
                "unknown keyword '%s' in template '%s'" % (rname, self.tpl))

    def __setattr__(self, name, value):
        if name in self.__dict__:  # any normal attributes are handled normal
            return object.__setattr__(self, name, value)
        if not '_TSF__initialised' in self.__dict__:  # this test allows attributes to be set in the __init__ method
            return object.__setattr__(self, name, value)

        # continue with keyword try
        rname = name.replace('_', '.')
        self.set(rname, value)

    def __str__(self):
        buffer = "TSF values (%s) : \n" % (self.tpl)
        for e in self.tsfParams:
            buffer += "    %30s : %s\n" % (e, str(self.tsfParams[e]))
        return buffer


class FixedDict(object):

    def __init__(self, keys):
        self.myKeys = keys
        self.myValues = {}

        # Note: we could enhance code for checking + default value support such as TSF
        # Note: keys may be synchronized with p2

        self.__initialised = True
        # after initialisation, setting attributes is the same as setting an
        # item

    def getDict(self):
        return self.myValues

    def __getattr__(self, name):  # called for non instance attributes (i.e. keywords)
        rname = name.replace('_', '.')
        if rname in self.myValues:
            return self.myValues[rname]
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.__dict__:  # any normal attributes are handled normally
            # print("set1 %s to %s"%(name, str(value)))
            return object.__setattr__(self, name, value)
        # this test allows attributes to be set in the __init__ method
        if not '_FixedDict__initialised' in self.__dict__:
            # print("set2 %s to %s"%(name, str(value)))
            return object.__setattr__(self, name, value)

        # continue with keyword try
        # print("set3 %s to %s"%(name, str(value)))
        rname = name.replace('_', '.')
        if rname in self.myKeys:
            self.myValues[name] = value
        else:
            raise ValueError(
                "keyword %s is not part of supported ones %s " % (name, self.myKeys))

    def __str__(self):
        buffer = "%s values:\n" % (type(self).__name__)
        for e in self.myValues:
            buffer += "    %30s : %s\n" % (e, str(self.myValues[e]))
        return buffer


class OBTarget(FixedDict):

    def __init__(self):
        FixedDict.__init__(
            self, ('name', 'ra', 'dec', 'properMotionRa', 'properMotionDec'))


class OBConstraints(TSF):

    def __init__(self, instrument):
        TSF.__init__(self, instrument, "instrumentConstraints.tsf")
        # WORKARROUND missing param in p2 json but valid and used in our code
        instrument.getRangeTable()[self.tpl]["name"]={}
