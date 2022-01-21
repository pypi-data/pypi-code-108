# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8

from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.utility_classes.utils import get_immediate_subdirectories, get_path
from ibm_ai_openscale_cli.credentials import Credentials
from ibm_ai_openscale_cli.database_classes.cos import CloudObjectStorage
from ibm_ai_openscale_cli.enums import MLEngineType, Environment
from ibm_ai_openscale_cli.ml_engines.azure_machine_learning import AzureMachineLearningStudioEngine, AzureMachineLearningServiceEngine
from ibm_ai_openscale_cli.ml_engines.custom_machine_learning import CustomMachineLearningEngine
from ibm_ai_openscale_cli.ml_engines.sagemaker_machine_learning import SageMakerMachineLearningEngine
from ibm_ai_openscale_cli.ml_engines.spss_machine_learning import SPSSMachineLearningEngine
from ibm_ai_openscale_cli.ml_engines.watson_machine_learning import WatsonMachineLearningEngine
from ibm_ai_openscale_cli.models.model import Model
from ibm_ai_openscale_cli.openscale.openscale_client import OpenScaleClient
import os
import time

logger = FastpathLogger(__name__)


class Ops:

    def __init__(self, args):
        self._args = args
        self._credentials = Credentials(args)
        self._ml_engine = None
        self._ml_engine_mrm = None
        self._cos_instance = None
        self.timers = dict()
        self.set_environment()

    def get_modeldata_instance(self, modelname, model_instance_num):
        model = Model(modelname, self._args, model_instance_num)
        return model

    def get_models_list(self):
        cwd = os.path.dirname(__file__)
        all_models_dir = get_path(cwd, [cwd, 'models'])
        modelnames_list = get_immediate_subdirectories(all_models_dir)
        if self._args.ml_engine_type is not MLEngineType.WML:
            for modelname in get_immediate_subdirectories(all_models_dir):
                model_dir = get_path(all_models_dir, [all_models_dir, modelname])
                all_engine_dirs = get_immediate_subdirectories(model_dir)
                if not self._args.ml_engine_type.name.lower() in all_engine_dirs:
                    modelnames_list.remove(modelname)
        else:
            for modelname in get_immediate_subdirectories(all_models_dir):
                wml_dir = get_path(all_models_dir, [all_models_dir, modelname, 'wml'])
                version_dirs = get_immediate_subdirectories(wml_dir)
                if self._args.v4 and ('v4' not in version_dirs):
                    modelnames_list.remove(modelname)
                elif (not self._args.v4) and ('v3' not in version_dirs):
                    modelnames_list.remove(modelname)
        modelnames_list.sort(key=str.lower)
        return modelnames_list

    def get_cos_instance(self):
        cos_credentials = self._credentials.get_cos_credentials()
        self._cos_instance = CloudObjectStorage(cos_credentials, self._args.env_dict['iam_url'], self._args.env_dict['cos_url'])
        return cos_credentials, self._cos_instance

    def get_ml_engine_instance(self, openscale_client, is_mrm=False):
        logger.log_info('Using {}'.format(self._args.ml_engine_type.value))
        if is_mrm:
            if not self._ml_engine_mrm:
                start = time.time()
                ml_engine_credentials = self._credentials.get_ml_engine_credentials()
                elapsed = time.time() - start
                self.timer('get ml engine credentials', elapsed)
                cos_credentials = None
                if not self._args.is_icp and self._args.v4:
                    cos_credentials = self._credentials.get_cos_credentials()
                self._ml_engine_mrm = WatsonMachineLearningEngine(credentials=ml_engine_credentials, openscale_client=openscale_client, cos_credentials=cos_credentials, is_v4=self._args.v4, is_mrm=is_mrm, is_icp=self._args.is_icp)
            return self._ml_engine_mrm
        if not self._ml_engine:
            start = time.time()
            ml_engine_credentials = self._credentials.get_ml_engine_credentials()
            elapsed = time.time() - start
            self.timer('get ml engine credentials', elapsed)
            cos_credentials = None
            if not self._args.is_icp and self._args.v4:
                cos_credentials = self._credentials.get_cos_credentials()
            if self._args.ml_engine_type is MLEngineType.WML:
                self._ml_engine = WatsonMachineLearningEngine(ml_engine_credentials, openscale_client, cos_credentials, self._args.v4, is_mrm, self._args.is_icp)
            elif self._args.ml_engine_type is MLEngineType.AZUREMLSTUDIO:
                self._ml_engine = AzureMachineLearningStudioEngine()
            elif self._args.ml_engine_type is MLEngineType.AZUREMLSERVICE:
                self._ml_engine = AzureMachineLearningServiceEngine()
            elif self._args.ml_engine_type is MLEngineType.SPSS:
                self._ml_engine = SPSSMachineLearningEngine(ml_engine_credentials)
            elif self._args.ml_engine_type is MLEngineType.CUSTOM:
                self._ml_engine = CustomMachineLearningEngine(ml_engine_credentials)
            elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
                self._ml_engine = SageMakerMachineLearningEngine(ml_engine_credentials)
        return self._ml_engine

    def timer(self, tag, seconds, count=1):
        if tag not in list(self.timers):
            self.timers[tag] = { 'count': 0, 'seconds': 0 }
        self.timers[tag]['count'] += count
        self.timers[tag]['seconds'] += seconds
        logger.log_timer('{} in {:.3f} seconds'.format(tag, seconds))
    
    def set_environment(self) -> None:
        """
        Sets the enviornment version in the namespace arguments.
        """
        # Setting the environment
        
        # Calling the fairness heartbeat API
        fairness_heartbeat_response = OpenScaleClient.get_fairness_heartbeat(self._args.env_dict["aios_url"])
        # Getting the fairness version
        fairness_version = fairness_heartbeat_response.get("version")
        if fairness_version.startswith("1"):
            self._args.environment = Environment.PUBLIC_CLOUD.value
        elif fairness_version.startswith("3"):
            self._args.environment = Environment.CPD_3_X.value
        elif fairness_version.startswith("4.0.0"):
            self._args.environment = Environment.CPD_4_0_0.value
        elif fairness_version.startswith("4.0.1"):
            self._args.environment = Environment.CPD_4_0_1.value
        elif fairness_version.startswith("4.0.2"):
            self._args.environment = Environment.CPD_4_0_2_PLUS.value
        else:
            self._args.environment = Environment.CPD_4_0_2_PLUS.value

        return
