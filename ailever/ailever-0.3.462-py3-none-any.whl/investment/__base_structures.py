from abc import *

class abstractstatic(staticmethod):
    __slots__ = ()
    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True


class BaseManagement(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass

    @abstractmethod
    def _local_filesystem_user_interfaces(self):
        pass

    @abstractmethod
    def _remote_filesystem_user_interfaces(self):
        pass

    @abstractmethod
    def _local_search(self):
        pass

    @abstractmethod
    def _remote_search(self):
        pass

    @abstractmethod
    def loading_connection(self):
        pass

    @abstractmethod
    def storing_connection(self):
        pass



class BaseTriggerBlock(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def ui_buffer(self):
        pass

    @abstractmethod
    def train(self):
        pass
    
    @abstractmethod
    def loaded_from(self):
        pass

    @abstractmethod
    def store_in(self):
        pass

    @abstractmethod
    def predict(self):
        pass
 
    @abstractmethod
    def ModelTransferCore(self):
        pass



class BaseTriggerBridge(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractstatic
    def _dynamic_import():
        pass
    
    @abstractmethod
    def into_trigger_bridge(self):
        pass

    @abstractmethod
    def into_trigger_block(self):
        pass

    # feature_store
    @abstractmethod
    def load_from_local_feature_store(self):
        pass
    # feature_store
    @abstractmethod
    def save_in_local_feature_store(self):
        pass
    # feature_store
    @abstractmethod
    def load_from_remote_feature_store(self):
        pass
    # feature_store
    @abstractmethod
    def save_in_remote_feature_store(self):
        pass

    # source_repository
    @abstractmethod
    def load_from_local_source_repository(self):
        pass
    # source_repository
    @abstractmethod
    def load_from_remote_source_repository(self):
        pass
    # source_repository
    @abstractmethod
    def save_in_local_source_repository(self):
        pass
    # source_repository
    @abstractmethod
    def save_in_remote_source_repository(self):
        pass
    
    # model_registry
    @abstractmethod
    def load_from_local_model_registry(self):
        pass
    # model_registry
    @abstractmethod
    def load_from_remote_model_registry(self):
        pass
    # model_registry
    @abstractmethod
    def save_in_local_model_registry(self):
        pass
    # model_registry
    @abstractmethod
    def save_in_remote_model_registry(self):
        pass
    
    # model_registry/forecasting_model_registry
    @abstractmethod
    def load_from_local_forecasting_model_registry(self):
        pass
    # model_registry/forecasting_model_registry
    @abstractmethod
    def load_from_remote_forecasting_model_registry(self):
        pass
    # model_registry/forecasting_model_registry
    @abstractmethod
    def save_in_local_forecasting_model_registry(self):
        pass
    # model_registry/forecasting_model_registry
    @abstractmethod
    def save_in_remote_forecasting_model_registry(self):
        pass

    # model_registry/strategy_model_registry
    @abstractmethod
    def load_from_local_strategy_model_registry(self):
        pass
    # model_registry/strategy_model_registry
    @abstractmethod
    def load_from_remote_strategy_model_registry(self):
        pass
    # model_registry/strategy_model_registry
    @abstractmethod
    def save_in_local_strategy_model_registry(self):
        pass
    # model_registry/strategy_model_registry
    @abstractmethod
    def save_in_remote_strategy_model_registry(self):
        pass

    # analysis_report_repository
    @abstractmethod
    def load_from_local_analysis_report_repository(self):
        pass
    # analysis_report_repository
    @abstractmethod
    def load_from_remote_analysis_report_repository(self):
        pass
    # analysis_report_repository
    @abstractmethod
    def save_in_local_analysis_report_repository(self):
        pass
    # analysis_report_repository
    @abstractmethod
    def save_in_remote_analysis_report_repository(self):
        pass
    
    # analysis_report_repository/fundamental_analysis_result
    @abstractmethod
    def load_from_local_fundamental_analysis_result(self):
        pass
    # analysis_report_repository/fundamental_analysis_result
    @abstractmethod
    def load_from_remote_fundamental_analysis_result(self):
        pass
    # analysis_report_repository/fundamental_analysis_result
    @abstractmethod
    def save_in_local_fundamental_analysis_result(self):
        pass
    # analysis_report_repository/fundamental_analysis_result
    @abstractmethod
    def save_in_remote_fundamental_analysis_result(self):
        pass

    # analysis_report_repository/technical_analysis_result
    @abstractmethod
    def load_from_local_technical_analysis_result(self):
        pass
    # analysis_report_repository/technical_analysis_result
    @abstractmethod
    def load_from_remote_technical_analysis_result(self):
        pass
    # analysis_report_repository/technical_analysis_result
    @abstractmethod
    def save_in_local_technical_analysis_result(self):
        pass
    # analysis_report_repository/technical_analysis_result
    @abstractmethod
    def save_in_remote_technical_analysis_result(self):
        pass

    # analysis_report_repository/model_prediction_result
    @abstractmethod
    def load_from_local_model_prediction_result(self):
        pass
    # analysis_report_repository/model_prediction_result
    @abstractmethod
    def load_from_remote_model_prediction_result(self):
        pass
    # analysis_report_repository/model_prediction_result
    @abstractmethod
    def save_in_local_model_prediction_result(self):
        pass
    # analysis_report_repository/model_prediction_result
    @abstractmethod
    def save_in_remote_model_prediction_result(self):
        pass

    # analysis_report_repository/sector_analysis_result
    @abstractmethod
    def load_from_local_sector_analysis_result(self):
        pass
    # analysis_report_repository/sector_analysis_result
    @abstractmethod
    def load_from_remote_sector_analysis_result(self):
        pass
    # analysis_report_repository/sector_analysis_result
    @abstractmethod
    def save_in_local_sector_analysis_result(self):
        pass
    # analysis_report_repository/sector_analysis_result
    @abstractmethod
    def save_in_remote_sector_analysis_result(self):
        pass

    # investment_outcome_repository
    @abstractmethod
    def load_from_local_investment_outcome_repository(self):
        pass
    # investment_outcome_repository
    @abstractmethod
    def load_from_remote_investment_outcome_repository(self):
        pass
    # investment_outcome_repository
    @abstractmethod
    def save_in_local_investment_outcome_repository(self):
        pass
    # investment_outcome_repository
    @abstractmethod
    def save_in_remote_investment_outcome_repository(self):
        pass

    # investment_outcome_repository/optimized_portfolio_registry
    @abstractmethod
    def load_from_local_optimized_portfolio_registry(self):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    @abstractmethod
    def load_from_remote_optimized_portfolio_registry(self):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    @abstractmethod
    def save_in_local_optimized_portfolio_registry(self):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    @abstractmethod
    def save_in_remote_optimized_portfolio_registry(self):
        pass

    # investment_outcome_repository/backtesting_repository
    @abstractmethod
    def load_from_local_backtesting_repository(self):
        pass
    # investment_outcome_repository/backtesting_repository
    @abstractmethod
    def load_from_remote_backtesting_repository(self):
        pass
    # investment_outcome_repository/backtesting_repository
    @abstractmethod
    def save_in_local_backtesting_repository(self):
        pass
    # investment_outcome_repository/backtesting_repository
    @abstractmethod
    def save_in_remote_backtesting_repository(self):
        pass

    # metadata store
    @abstractmethod
    def load_from_local_metadata_store(self):
        pass
    # metadata store
    @abstractmethod
    def load_from_remote_metadata_store(self):
        pass
    # metadata store
    @abstractmethod
    def save_in_local_metadata_store(self):
        pass
    # metadata store
    @abstractmethod
    def save_in_remote_metadata_store(self):
        pass

    # metadata_store/monitoring_source
    @abstractmethod
    def load_from_local_monitoring_source(self):
        pass
    # metadata_store/monitoring_source
    @abstractmethod
    def load_from_remote_monitoring_source(self):
        pass
    # metadata_store/monitoring_source
    @abstractmethod
    def save_in_local_monitoring_source(self):
        pass
    # metadata_store/monitoring_source
    @abstractmethod
    def save_in_remote_monitoring_source(self):
        pass

    
