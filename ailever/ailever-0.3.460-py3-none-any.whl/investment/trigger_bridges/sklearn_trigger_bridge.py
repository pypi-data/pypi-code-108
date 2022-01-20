from ailever.investment import __fmlops_bs__ as fmlops_bs
from ..__base_structures import BaseTriggerBridge

import os
from importlib import import_module


class SklearnTriggerBridge(BaseTriggerBridge):
    def __init__(self):
        # Loading System
        self.__core_instances = dict()

    @staticmethod
    def _dynamic_import():
        pass
    
    def into_trigger_bridge(self):
        pass

    def into_trigger_block(self):
        pass

    # feature_store
    def load_from_local_feature_store(self):
        pass
    # feature_store
    def save_in_local_feature_store(self):
        pass
    # feature_store
    def load_from_remote_feature_store(self):
        pass
    # feature_store
    def save_in_remote_feature_store(self):
        pass

    # source_repository
    def load_from_local_source_repository(self):
        pass
    # source_repository
    def load_from_remote_source_repository(self):
        pass
    # source_repository
    def save_in_local_source_repository(self):
        pass
    # source_repository
    def save_in_remote_source_repository(self):
        pass
    
    # model_registry
    def load_from_local_model_registry(self):
        pass
    # model_registry
    def load_from_remote_model_registry(self):
        pass
    # model_registry
    def save_in_local_model_registry(self):
        pass
    # model_registry
    def save_in_remote_model_registry(self):
        pass
    
    # model_registry/forecasting_model_registry
    def load_from_local_forecasting_model_registry(self):
        pass
    # model_registry/forecasting_model_registry
    def load_from_remote_forecasting_model_registry(self):
        pass
    # model_registry/forecasting_model_registry
    def save_in_local_forecasting_model_registry(self):
        pass
    # model_registry/forecasting_model_registry
    def save_in_remote_forecasting_model_registry(self):
        pass

    # model_registry/strategy_model_registry
    def load_from_local_strategy_model_registry(self):
        pass
    # model_registry/strategy_model_registry
    def load_from_remote_strategy_model_registry(self):
        pass
    # model_registry/strategy_model_registry
    def save_in_local_strategy_model_registry(self):
        pass
    # model_registry/strategy_model_registry
    def save_in_remote_strategy_model_registry(self):
        pass

    # analysis_report_repository
    def load_from_local_analysis_report_repository(self):
        pass
    # analysis_report_repository
    def load_from_remote_analysis_report_repository(self):
        pass
    # analysis_report_repository
    def save_in_local_analysis_report_repository(self):
        pass
    # analysis_report_repository
    def save_in_remote_analysis_report_repository(self):
        pass
    
    # analysis_report_repository/fundamental_analysis_result
    def load_from_local_fundamental_analysis_result(self):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def load_from_remote_fundamental_analysis_result(self):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def save_in_local_fundamental_analysis_result(self):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def save_in_remote_fundamental_analysis_result(self):
        pass

    # analysis_report_repository/technical_analysis_result
    def load_from_local_technical_analysis_result(self):
        pass
    # analysis_report_repository/technical_analysis_result
    def load_from_remote_technical_analysis_result(self):
        pass
    # analysis_report_repository/technical_analysis_result
    def save_in_local_technical_analysis_result(self):
        pass
    # analysis_report_repository/technical_analysis_result
    def save_in_remote_technical_analysis_result(self):
        pass

    # analysis_report_repository/model_prediction_result
    def load_from_local_model_prediction_result(self):
        pass
    # analysis_report_repository/model_prediction_result
    def load_from_remote_model_prediction_result(self):
        pass
    # analysis_report_repository/model_prediction_result
    def save_in_local_model_prediction_result(self):
        pass
    # analysis_report_repository/model_prediction_result
    def save_in_remote_model_prediction_result(self):
        pass

    # analysis_report_repository/sector_analysis_result
    def load_from_local_sector_analysis_result(self):
        pass
    # analysis_report_repository/sector_analysis_result
    def load_from_remote_sector_analysis_result(self):
        pass
    # analysis_report_repository/sector_analysis_result
    def save_in_local_sector_analysis_result(self):
        pass
    # analysis_report_repository/sector_analysis_result
    def save_in_remote_sector_analysis_result(self):
        pass

    # investment_outcome_repository
    def load_from_local_investment_outcome_repository(self):
        pass
    # investment_outcome_repository
    def load_from_remote_investment_outcome_repository(self):
        pass
    # investment_outcome_repository
    def save_in_local_investment_outcome_repository(self):
        pass
    # investment_outcome_repository
    def save_in_remote_investment_outcome_repository(self):
        pass

    # investment_outcome_repository/optimized_portfolio_registry
    def load_from_local_optimized_portfolio_registry(self):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def load_from_remote_optimized_portfolio_registry(self):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def save_in_local_optimized_portfolio_registry(self):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def save_in_remote_optimized_portfolio_registry(self):
        pass

    # investment_outcome_repository/backtesting_repository
    def load_from_local_backtesting_repository(self):
        pass
    # investment_outcome_repository/backtesting_repository
    def load_from_remote_backtesting_repository(self):
        pass
    # investment_outcome_repository/backtesting_repository
    def save_in_local_backtesting_repository(self):
        pass
    # investment_outcome_repository/backtesting_repository
    def save_in_remote_backtesting_repository(self):
        pass

    # metadata store
    def load_from_local_metadata_store(self):
        pass
    # metadata store
    def load_from_remote_metadata_store(self):
        pass
    # metadata store
    def save_in_local_metadata_store(self):
        pass
    # metadata store
    def save_in_remote_metadata_store(self):
        pass

    # metadata_store/monitoring_source
    def load_from_local_monitoring_source(self):
        pass
    # metadata_store/monitoring_source
    def load_from_remote_monitoring_source(self):
        pass
    # metadata_store/monitoring_source
    def save_in_local_monitoring_source(self):
        pass
    # metadata_store/monitoring_source
    def save_in_remote_monitoring_source(self):
        pass

    
