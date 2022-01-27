from modelify.frameworks.sklearn import SklearnController
from modelify.frameworks.keras import KerasController
from modelify.frameworks.xgboost import XGBoostController
from modelify.frameworks.lightgbm import LightGBMController
from modelify.frameworks.h2o import H2OController
from modelify.frameworks.catboost import CatBoostController
import os
from modelify.utils.constants import MODELIFY_TOKEN_VALIDATION_URL
import requests
import json
from modelify.utils.credential import Credential



class Modelify:
    def __init__(self, api_key):
        self.credential = Credential()
        self._connect(api_key)
        self.sklearn = SklearnController()
        self.keras = KerasController()
        self.xgboost = XGBoostController()
        self.lightgbm = LightGBMController()
        self.h2o = H2OController()
        self.catboost = CatBoostController()


    def _connect(self,api_key):
        # send request MODELIFY_TOKEN_VALIDATION_URL with app id
        self.credential.api_key = api_key
        headers = {"api-token": f"{self.credential.api_key}", "Content-Type": "application/json"}
        req = requests.get(MODELIFY_TOKEN_VALIDATION_URL, headers =headers)
        if req.status_code == 200:
            print("Connection established. ")
        else:
            print("Token is not valid.")




