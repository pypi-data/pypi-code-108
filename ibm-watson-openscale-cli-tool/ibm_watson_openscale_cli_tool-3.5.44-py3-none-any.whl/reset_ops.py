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
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.openscale.openscale_client import OpenScaleClient
from ibm_ai_openscale_cli.enums import ResetType, MLEngineType
from ibm_ai_openscale_cli.ops import Ops

logger = FastpathLogger(__name__)

class ResetOps(Ops):

    def __init__(self, args):
        super().__init__(args)
        openscale_credentials = self._credentials.get_openscale_credentials()
        database_credentials = self._credentials.get_database_credentials()
        ml_engine_credentials = self._credentials.get_ml_engine_credentials()
        self._openscale_client = OpenScaleClient(self._args, openscale_credentials, database_credentials, ml_engine_credentials)

    def _reset_one_model(self, modelname, ml_engine):
        logger.log_info_h1('Model: {}, Engine: {}'.format(modelname, self._args.ml_engine_type.value))
        for model_instance_num in range(self._args.model_first_instance, self._args.model_first_instance + self._args.model_instances):
            modeldata = self.get_modeldata_instance(modelname, model_instance_num)
            ml_engine.set_model(modeldata)
            ml_engine.model_cleanup()

    def _reset_model(self):
        ml_engine = self.get_ml_engine_instance(self._openscale_client)
        for modelname in self.get_models_list():
            self._reset_one_model(modelname, ml_engine)
        if self._args.mrm:
            ml_engine = self.get_ml_engine_instance(self._openscale_client, self._args.mrm)
            for modelname in ['GermanCreditRiskModelPreProd', 'GermanCreditRiskModelChallenger']:
                self._reset_one_model(modelname, ml_engine)

    def _reset_openscale(self, reset_type):
        if reset_type == ResetType.ALL:
            self._openscale_client.reset(ResetType.DATAMART)
        else:
            self._openscale_client.reset(reset_type)

    def execute(self):
        if self._args.reset_type is not ResetType.MODEL:
            self._reset_openscale(self._args.reset_type)

        if (self._args.reset_type is ResetType.MODEL or self._args.reset_type is ResetType.ALL) and self._args.ml_engine_type is MLEngineType.WML:
            self._reset_model()
