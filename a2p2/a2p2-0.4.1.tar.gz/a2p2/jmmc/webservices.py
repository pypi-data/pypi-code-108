#!/usr/bin/env python

__all__ = []

import logging
import json

from .utils import JmmcAPI
from . import PRODLABEL

logger = logging.getLogger(__name__)

class CallIper():
    """ Call IPER using its 'API' through simple methods.

    from a2p2.jmmc import CallIper
    calliper = CallIper()
    diskresult   = caliper.runDiskFit(pathname)
    ud = diskresult["diameter"]

    """
    def __init__(self, prod=False, apiUrl=None):
        self.prod = prod
        self.serviceName = "callIper"

        # Manage prod & preprod or user provided access points
        if apiUrl:
            self.apiUrl = apiUrl  # trust given url as callIperAPI if value is provided
        elif self.prod:
            self.apiUrl = ""  # no api in production yet
            raise Warning("sorry, no api for production yet")
        else:
            self.apiUrl = "http://apps.jmmc.fr/~mellag/LITproWebService/run.php"

        self.api = JmmcAPI(self.apiUrl)

        logger.info("Create calliper client to access '%s' (%s API at %s)" %
                    (self.serviceName, PRODLABEL[self.prod], self.api.rootURL))

    # API will evolve in the future with parameter to select fitter, model and data to fit...
    def runDiskFit(self, oifitsFilename, jsonOutput=True):
        """ Ask CallIper to fit given data for a simple disk """
        files = {'userfile': (oifitsFilename, open(oifitsFilename, 'rb'))}
        data = {'method': 'runJsonFit'}
        res=self.api._post("", data=data, files=files)
        if jsonOutput:
            return json.loads(res)
        return res
