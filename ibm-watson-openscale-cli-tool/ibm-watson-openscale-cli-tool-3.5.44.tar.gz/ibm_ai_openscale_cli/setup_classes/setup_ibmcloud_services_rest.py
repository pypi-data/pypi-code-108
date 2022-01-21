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
# from ibm_ai_openscale_cli.setup_classes.cloud_foundry import CloudFoundry
from ibm_ai_openscale_cli.setup_classes.resource_controller import ResourceController
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services import SetupIBMCloudServices
from ibm_ai_openscale_cli.setup_classes.token_manager import TokenManager
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)
WML_V4_RESOURCE_ID_STAGING = '608df6d0-739d-4634-bb05-64c5f8e6d2dd'
WML_V4_RESOURCE_ID = '51c53b72-918f-4869-b834-2d99eb28422a'
WML_PLAN_LITE = '3f6acf43-ede8-413a-ac69-f8af3bb0cbfe'
WML_PLAN_STANDARD = '0f2a3c2c-456b-40f3-9b19-726d2740b11c'
WML_PLAN_PROFESSIONAL = 'b52ce7cf-a5c3-4da8-b368-a4ed3c61918c'
WML_PLAN_V2_STANDARD = 'a3d2f92f-06f9-48d0-b2e6-a7ba2b4e0577'
WML_PLAN_V2_PROFESSIONAL = 'd18d88b9-be7a-46ec-be1e-aff14904f1e9'
WOS_PLAN_LITE = "967ba182-c6e0-4adc-92ef-661a822cc1d7"
WOS_PLAN_STANDARD = "ba0d185f-b0e3-421f-aea4-15b305136e52"
WOS_PLAN_STANDARD_V2 = "6786f153-64a7-4e47-940a-eff204d0d39b"


class SetupIBMCloudServicesRest(SetupIBMCloudServices):

    def __init__(self, args):
        super().__init__(args)

        self.resourceController = None
        self.cloudFoundry = None
        if self._args.is_icp:
            return
        self._target = 'eu-de' if self._args.env == 'frprod' else 'us-south'
        iam_access_token = None
        if self._args.iam_token:
            iam_access_token = self._args.iam_token
        else:
            iam_access_token = TokenManager(
                apikey=self._args.apikey,
                url=self._args.env_dict['iam_url']
            ).get_token()
        self.resourceController = ResourceController(
            access_token=iam_access_token,
            url=self._args.env_dict['resource_controller_url'],
            resourceGroupUrl=self._args.env_dict['resource_group_url']
        )
        # uaa_access_token = TokenManager(
        #     apikey=self._args.apikey,
        #     url=self._args.env_dict['uaa_url'],
        #     iam_token=False
        # ).get_token()
        # self.cloudFoundry = CloudFoundry(access_token=uaa_access_token)

    def _get_credentials(self, service_display_name, params, is_rc_based, credentials_file=None):
        '''
        Returns the credentials from the specified credentials json file. If not
        then returns the credentials an instance of the specified Service.
        If there is no instance available, a new one is provisioned.
        If there are no existing credentials, new one is created and returned.
        '''
        credentials = None

        if credentials_file is not None:
            credentials = self.read_credentials_from_file(credentials_file)
        elif is_rc_based:
            params['resource_group_name'] = self._args.resource_group
            credentials = self.resourceController.get_or_create_instance(**params)
        # elif not is_rc_based:
        #     credentials = self.cloudFoundry.get_or_create_instance(
        #         service_name=params['service_name'],
        #         service_resource_name=params['resource_name'],
        #         service_plan_guid=params['service_plan_guid'],
        #         organization_name=self._args.organization,
        #         space_name=self._args.space
        #     )
        if ('name' in credentials):
            logger.log_info('{0} instance: {1}'.format(service_display_name, credentials['name']))
        return credentials

    def setup_aios(self):
        aiopenscale_params = {
            'resource_name': 'wos-expresspath' + "-" + self._target,
            'resource_id': '2ad019f3-0fd6-4c25-966d-f3952481a870',
            'resource_plan_id': WOS_PLAN_LITE
        }
        if self._args.openscale_plan == "standard":
            aiopenscale_params["resource_plan_id"] = WOS_PLAN_STANDARD
        elif self._args.openscale_plan == "standard-v2":
            aiopenscale_params["resource_plan_id"] = WOS_PLAN_STANDARD_V2
        aiopenscale_params['create_credentials'] = False
        # aiopenscale_params['credentials_role'] = 'Administrator'
        aiopenscale_params['target'] = self._target
        aios_instance = self._get_credentials('Watson OpenScale', aiopenscale_params, True)
        return self._aios_credentials(aios_instance['id'], aios_instance['crn'])

    def setup_wml(self):  # v4 only
        service_name = "IBM Watson Machine Learning"
        logger.log_info('Setting up {} instance'.format(service_name))

        if self._args.env == 'ys1dev':
            return self._setup_wml_v4_dev(service_name)

        wml_params = {
            'resource_name': 'wos-expresspath-wml' + "-" + self._target,
            'resource_id': WML_V4_RESOURCE_ID,
            'create_credentials': False,
            'target': self._target,
            'resource_plan_id': WML_PLAN_LITE
        }
        if self._args.wml_plan == 'standard':
            wml_params['resource_plan_id'] = WML_PLAN_V2_STANDARD
        elif self._args.wml_plan == 'professional':
            wml_params['resource_plan_id'] = WML_PLAN_V2_PROFESSIONAL

        provisioned_instance = self._get_credentials(service_name, wml_params, True, self._args.wml)
        if self._args.wml:
            credentials = provisioned_instance
        else:
            credentials = {
                'url': self._args.env_dict['wml_v4_url'],
                "instance_crn": provisioned_instance['crn'],
                "instance_name": provisioned_instance['name']
            }
            if self._args.apikey:
                credentials['apikey'] = self._args.apikey
            if self._args.iam_token:
                credentials['token'] = self._args.iam_token
        return credentials

    def _setup_wml_v4_dev(self, service_name):
        wml_params = {
            'resource_name': 'wos-expresspath-wml' + "-" + self._target,
            'resource_id': WML_V4_RESOURCE_ID_STAGING,
            'create_credentials': False,
            'target': self._target
        }
        if self._args.wml_plan.lower() == 'v2-standard':
            wml_params['resource_plan_id'] = '8ae8b1cd-7d64-41e7-bd20-48dc5b982728'
        elif self._args.wml_plan.lower() == 'v2-professional':
            wml_params['resource_plan_id'] = '1458e1bc-a34a-4acf-bdc0-76e82b25920b'
        elif self._args.wml_plan.lower() == "lite":
            wml_params["resource_plan_id"] = "1642f4af-8cba-4698-b8db-af55ae6b9aa2"
        provisioned_instance = self._get_credentials(service_name, wml_params, True, self._args.wml)
        if self._args.wml:
            credentials = provisioned_instance
        else:
            credentials = {
                'url': self._args.env_dict['wml_v4_url'],
                "instance_crn": provisioned_instance['crn'],
                "instance_name": provisioned_instance['name']
            }
            if self._args.apikey:
                credentials["apikey"] = self._args.apikey
            if self._args.iam_token:
                credentials["token"] = self._args.iam_token
        return credentials

    def setup_cos(self):
        service_name = 'IBM Cloud Object Storage'
        logger.log_info('Setting up {} instance'.format(service_name))
        if self._args.env == 'ys1dev':
            return self._setup_cos_staging(service_name)
        return self._setup_cos_prod(service_name)

    def _setup_cos_prod(self, service_name):
        cos_params = {
            'resource_name': 'wos-expresspath-cos-global',
            'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c',
            'resource_plan_id': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
            'create_credentials': True,
            'target': 'global'
        }
        credentials = self._get_credentials(service_name, cos_params, True, self._args.cos)['credentials']
        return credentials

    def _setup_cos_staging(self, service_name):
        cos_params = {
            'resource_name': 'wos-expresspath-cos-global',
            'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c',
            'resource_plan_id': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
            'create_credentials': True,
            'target': 'global'
        }
        credentials = self._get_credentials(service_name, cos_params, True, self._args.cos)['credentials']
        return credentials
