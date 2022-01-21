# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from enum import Enum, unique

@unique
class MLEngineType(Enum):
    WML = 'IBM Watson Machine Learning'
    SAGEMAKER = 'Amazon Sagemaker'
    CUSTOM = 'Custom Machine Learning Engine'
    SPSS = 'IBM SPSS C&DS'
    AZUREMLSTUDIO = 'Microsoft Azure Machine Learning Studio'
    AZUREMLSERVICE = 'Microsoft Azure Machine Learning Service'

@unique
class ResetType(Enum):
    METRICS = 'metrics'
    MONITORS = 'monitors'
    DATAMART = 'datamart'
    MODEL = 'model'
    ALL = 'all'

@unique
class Environment(Enum):
    PUBLIC_CLOUD = "public_cloud"
    CPD_3_X = "cpd_3.x"
    CPD_4_0_0 = "cpd_4.0.0"
    CPD_4_0_1 = "cpd_4.0.1"
    CPD_4_0_2_PLUS = "cpd_4.0.2+"
