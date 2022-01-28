from ._base_policy import initialization_policy

local_environment = dict()
local_environment['root'] = '.forecast'
local_environment['feature_store'] = 'feature_store'
local_environment['model_registry'] = 'model_registry'
local_environment['source_repository'] = 'source_repository'
local_environment['metadata_store'] = 'metadata_store'
__forecast_bs__ = initialization_policy(local_environment)

from .FORECASTInterfaces import FeatureSelection, regressor
from .FORECASTInterfaces import TSA, RSDA
from .FORECASTInterfaces import LightMLOps
from .FORECASTInterfaces import StockProphet
from ._stattools import scaler

