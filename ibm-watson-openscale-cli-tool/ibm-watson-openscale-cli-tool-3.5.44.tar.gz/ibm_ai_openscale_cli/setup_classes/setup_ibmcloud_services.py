# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from ibm_ai_openscale_cli.setup_classes.setup_services import SetupServices
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)

class SetupIBMCloudServices(SetupServices):

    def __init__(self, args):
        super().__init__(args)

    def _aios_credentials(self, data_mart_id, crn):
        aios_credentials = {}
        if self._args.apikey:
            aios_credentials['apikey'] = self._args.apikey
        if self._args.iam_token:
            aios_credentials['iam_token'] = self._args.iam_token
        aios_credentials['url'] = self._args.env_dict['aios_url']
        aios_credentials['data_mart_id'] = data_mart_id
        aios_credentials['crn'] = crn
        aios_credentials['headers'] = { 'Origin': 'cli://fastpath' }
        # get_crn

        return aios_credentials
