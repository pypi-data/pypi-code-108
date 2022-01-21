# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from __future__ import print_function


class Environments(object):

    def __init__(self, args):
        self._args = args

    def get_attributes(self):
        if self._args.env == 'frprod':
            return self._getFRProdEnv()
        if self._args.env == 'ypprod':
            return self._getYPProdEnv()
        if self._args.env == 'ypqa':
            return self._getYPQAEnv()
        if self._args.env == 'ypcr':
            return self._getYPCREnv()
        if self._args.env == 'ys1dev':
            return self._getYS1DevEnv()
        if self._args.env == 'icp':
            return self._getICPEnv()

    def _getFRProdEnv(self):
        attributes = {}
        attributes['name'] = 'FRPROD'
        attributes['api'] = 'https://api.eu-de.bluemix.net'
        attributes['aios_url'] = 'https://eu-de.aiopenscale.cloud.ibm.com'
        attributes['iam_url'] = 'https://iam.cloud.ibm.com/identity/token'
        attributes['uaa_url'] = 'https://login.eu-de.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['resource_group_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['cos_url'] = 'https://s3.us.cloud-object-storage.appdomain.cloud',
        attributes['wml_v4_url'] = 'https://eu-de.ml.cloud.ibm.com'
        return attributes

    def _getYPProdEnv(self):
        attributes = {}
        attributes['name'] = 'YPPROD'
        attributes['api'] = 'https://api.ng.bluemix.net'
        attributes['aios_url'] = 'https://api.aiopenscale.cloud.ibm.com'
        attributes['iam_url'] = 'https://iam.cloud.ibm.com/identity/token'
        attributes['uaa_url'] = 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['resource_group_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['cos_url'] = 'https://s3.us.cloud-object-storage.appdomain.cloud',
        attributes['wml_v4_url'] = 'https://us-south.ml.cloud.ibm.com'
        return attributes

    def _getYPQAEnv(self):
        attributes = {}
        attributes['name'] = 'YPQA'
        attributes['api'] = 'https://api.ng.bluemix.net'
        attributes['aios_url'] = 'https://api.aiopenscale.test.cloud.ibm.com'
        attributes['iam_url'] = 'https://iam.cloud.ibm.com/identity/token'
        attributes['uaa_url'] = 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['resource_group_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['cos_url'] = 'https://s3.us.cloud-object-storage.appdomain.cloud'
        attributes['wml_v4_url'] = 'https://us-south.ml.cloud.ibm.com'
        return attributes

    def _getYPCREnv(self):
        attributes = {}
        attributes['name'] = 'YPCR'
        attributes['api'] = 'https://api.ng.bluemix.net'
        attributes['aios_url'] = 'https://aios-yp-cr.us-south.containers.appdomain.cloud'
        attributes['iam_url'] = 'https://iam.cloud.ibm.com/identity/token'
        attributes['uaa_url'] = 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['resource_group_url'] = 'https://resource-controller.cloud.ibm.com'
        attributes['cos_url'] = 'https://s3.us.cloud-object-storage.appdomain.cloud',
        attributes['wml_v4_url'] = 'https://us-south.ml.cloud.ibm.com'
        return attributes

    def _getYS1DevEnv(self):
        attributes = {}
        attributes['name'] = 'YS1DEV'
        attributes['api'] = 'https://api.stage1.ng.bluemix.net'
        attributes['aios_url'] = 'https://aiopenscale-dev.us-south.containers.appdomain.cloud'
        attributes['iam_url'] = 'https://iam.test.cloud.ibm.com/identity/token'
        attributes['uaa_url'] = 'https://login.stage1.ng.bluemix.net/UAALoginServerWAR/oauth/token'
        attributes['resource_controller_url'] = 'https://resource-controller.test.cloud.ibm.com'
        attributes['resource_group_url'] = 'https://resource-controller.test.cloud.ibm.com'
        attributes['cos_url'] = 'https://s3.us-west.cloud-object-storage.test.appdomain.cloud',
        attributes['wml_v4_url'] = 'https://wml-fvt.ml.test.cloud.ibm.com'
        return attributes

    def _getICPEnv(self):
        attributes = {}
        attributes['name'] = 'ICP'
        attributes['api'] = None
        attributes['aios_url'] = self._args.url
        attributes['iam_url'] = None
        attributes['uaa_url'] = None
        attributes['resource_controller_url'] = None
        attributes['resource_group_url'] = None
        return attributes
