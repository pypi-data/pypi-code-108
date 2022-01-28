from ._fmlops_policy import initialization_policy

local_environment = dict()
local_environment['fmlops'] = '.fmlops'
local_environment['feature_store'] = 'feature_store'
local_environment['source_repository'] = 'source_repository'
local_environment['model_registry'] = 'model_registry'
local_environment['analysis_report_repository'] = 'analysis_report_repository'
local_environment['investment_outcome_repository'] = 'investment_outcome_repository'
local_environment['metadata_store'] = 'metadata_store'

local_environment['daily_data_feature'] = '1d'
local_environment['hourly_data_feature'] = '1H'
local_environment['minutely_data_feature'] = '1M'
local_environment['tick_data_feature'] = '1t'
local_environment['forecasting_model_registry'] = 'forecasting_model_registry'
local_environment['strategy_model_registry'] = 'strategy_model_registry'
local_environment['fundamental_analysis_result'] = 'fundamental_analysis_result'
local_environment['technical_analysis_result'] = 'technical_analysis_result'
local_environment['model_prediction_result'] = 'model_prediction_result'
local_environment['sector_analysis_result'] = 'sector_analysis_result'
local_environment['screening_registry'] = 'screening_registry'
local_environment['optimized_portfolio_registry'] = 'optimized_portfolio_registry'
local_environment['backtesting_repository'] = 'backtesting_repository'
local_environment['monitoring_source'] = 'monitoring_source'
local_environment['data_management'] = 'data_management'
local_environment['model_management'] = 'model_management'
local_environment['model_specification'] = 'model_specification'
__fmlops_bs__ = initialization_policy(local_environment=local_environment)

from .INVESTMENTInterfaces import Management
from .INVESTMENTInterfaces import IMQuery
from .INVESTMENTInterfaces import market_information, market_monitoring
from .INVESTMENTInterfaces import PortfolioManagement
from .INVESTMENTInterfaces import Forecaster
from .INVESTMENTInterfaces import sectors
from .INVESTMENTInterfaces import Preprocessor
from .INVESTMENTInterfaces import Screener

from .INVESTMENTInterfaces import Loader, ILoader
from .INVESTMENTInterfaces import prllz_loader
from .INVESTMENTInterfaces import parallelize
from .INVESTMENTInterfaces import Asset


