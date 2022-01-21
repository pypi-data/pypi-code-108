# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
import json
from ibm_ai_openscale_cli.utility_classes.utils import remove_port_from_url
from ibm_ai_openscale_cli.setup_classes.setup_services import SetupServices
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.api_environment import ApiEnvironment

logger = FastpathLogger(__name__)


class SetupIBMCloudPrivateServices(SetupServices):

    def __init__(self, args):
        super().__init__(args)

    def setup_aios(self):
        logger.log_info('Setting up {} instance'.format('Watson OpenScale'))
        aios_icp_credentials = {}
        if self._args.iam_token:
            aios_icp_credentials['iam_token'] = self._args.iam_token
        else:
            aios_icp_credentials['username'] = self._args.username
            aios_icp_credentials['password'] = self._args.password
        aios_icp_credentials['url'] = '{}'.format(self._args.url)
        aios_icp_credentials['hostname'] = ':'.join(self._args.url.split(':')[:2])
        try:
            aios_icp_credentials['port'] = self._args.url.split(':')[2]
        except Exception as e:
            pass
        aios_icp_credentials['data_mart_id'] = self._args.datamart_id
        return aios_icp_credentials

    def setup_wml(self):
        logger.log_info('Setting up {} instance'.format('Watson Machine Learning'))
        api_env = ApiEnvironment()
        wml_credentials = {}
        if self._args.wml:
            wml_credentials = self.read_credentials_from_file(self._args.wml)
        # elif self._args.wml_json:
        #     wml_credentials = json.loads(self._args.wml_json)
        else:
            if self._args.iam_token:
                wml_credentials['token'] = self._args.iam_token
            else:
                wml_credentials['username'] = self._args.username
                wml_credentials['password'] = self._args.password
            if self._args.v4:
                wml_credentials['instance_id'] = "openshift" if self._args.iam_integration else "wml_local"
                wml_credentials['version'] = "4.0" if self._args.iam_integration else "3.5"
                wml_credentials['url'] = ':'.join(self._args.url.split(':')[:2])
            else:
                wml_credentials['instance_id'] = 'icp'
                wml_credentials['url'] = ':'.join(self._args.url.split(':')[:2])
            if wml_credentials['url'] == api_env.icp_gateway_url:
                if self._args.v4:
                    wml_credentials['url'] = 'https://ibm-nginx-svc.{}'.format(api_env.aios_namespace)
                else:
                    wml_credentials['url'] = 'https://wmlproxyservice.{}'.format(api_env.icp4d_namespace)
        # if the cli is running locally, remove port as pypi wml client doesn't like it
        if not api_env.is_running_on_icp:
            wml_credentials['url'] = remove_port_from_url(wml_credentials['url'])
        # local or remote icp for v4
        if self._args.v4 and 'apikey' not in wml_credentials:
            if 'version' not in wml_credentials:
                wml_credentials['version'] = '3.5'
        return wml_credentials

