from ailever.investment import __fmlops_bs__ as fmlops_bs
from ..__base_structures import BaseTriggerBridge

import os
from importlib import import_module
import torch



class TorchTriggerBridge(BaseTriggerBridge):
    def __init__(self):
        # Loading System
        self.__core_instances = dict()  # loading objects

    @staticmethod
    def _dynamic_import(architecture:str, module:str):
        return getattr(import_module(f'{architecture}'), module)

    def into_trigger_bridge(self, specification:dict, usage:str='train'):
        if usage == 'train':
            architecture = specification['architecture']
            InvestmentDataLoader = self._dynamic_import(architecture, 'InvestmentDataLoader')
            Model = self._dynamic_import(architecture, 'Model')
            Criterion = self._dynamic_import(architecture, 'Criterion')
            Optimizer = self._dynamic_import(architecture, 'Optimizer')
            retrainable_conditions = self._dynamic_import(architecture, 'retrainable_conditions')
            if specification['device'] == 'cpu':
                model = Model(specification)
                criterion = Criterion(specification)
            elif specification['device'] == 'cuda':
                model = Model(specification).cuda()
                criterion = Criterion(specification).cuda()
            optimizer = Optimizer(model, specification)
            train_dataloader, test_dataloader = InvestmentDataLoader(specification)
            return train_dataloader, test_dataloader, model, criterion, optimizer

        elif usage == 'prediction':
            architecture = specification['architecture']
            Scaler = self._dynamic_import(architecture, 'Scaler')
            InvestmentDataset = self._dynamic_import(architecture, 'InvestmentDataset')
            Model = self._dynamic_import(architecture, 'Model')
            retrainable_conditions = self._dynamic_import(architecture, 'retrainable_conditions')
            
            scaler = Scaler(specification)
            model = Model(specification).to('cpu')
            investment_dataset = InvestmentDataset(specification).type(mode='test')
            return scaler, investment_dataset, model

    def into_trigger_block(self, specification:dict, usage:str='train'):
        if usage == 'train':
            return self.__core_instances.pop('train_dataloader'),\
                   self.__core_instances.pop('test_dataloader'),\
                   self.__core_instances.pop('model'),\
                   self.__core_instances.pop('criterion'),\
                   self.__core_instances.pop('optimizer'),\
                   self.__core_instances.pop('cumulative_epochs') if 'cumulative_epochs' in self.__core_instances.keys() else None
        elif usage == 'prediction':
            return self.__core_instances.pop('scaler'),\
                   self.__core_instances.pop('investment_dataset'),\
                   self.__core_instances.pop('model'),\
                   self.__core_instances.pop('train_mse'),\
                   self.__core_instances.pop('validation_mse')



    def load_from_ailever_feature_store(self, specification:dict, usage:str='train'):
        pass
    def load_from_local_feature_store(self, specification:dict, usage:str='train'):
        pass
    def load_from_remote_feature_store(self, specification:dict, usage:str='train'):
        pass
    def save_in_ailever_feature_store(self, specification:dict, usage:str='train'):
        pass
    def save_in_local_feature_store(self, specification:dict, usage:str='train'):
        pass
    def save_in_remote_feature_store(self, specification:dict, usage:str='train'):
        pass





    def load_from_ailever_source_repository(self, specification:dict, usage:str='train'):
        if usage == 'train':
            train_dataloader, test_dataloader, model, criterion, optimizer = self.into_trigger_bridge(specification, usage)
            self.__core_instances['train_dataloader'] = train_dataloader
            self.__core_instances['test_dataloader'] = test_dataloader
            self.__core_instances['model'] = model
            self.__core_instances['criterion'] = criterion
            self.__core_instances['optimizer'] = optimizer
        elif usage == 'prediction':
            scaler, investment_dataset, model = self.into_trigger_bridge(specification, usage)
            self.__core_instances['investment_dataset'] = investment_dataset
            self.__core_instances['model'] = model
            self.__core_instances['scaler'] = scaler
    def load_from_local_source_repository(self, specification:dict, usage:str='train'):
        # return : dataloader, model, criterion, optimizer
        return None
    def load_from_remote_source_repository(self, specification:dict, usage:str='train'):
        return None
    def save_in_ailever_source_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_local_source_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_remote_source_repository(self, specification:dict, usage:str='train'):
        pass



    def load_from_ailever_model_registry(self, specification:dict, usage:str='train'):
        # return : model, optimizer
        return None
    def load_from_local_model_registry(self, specification:dict, usage:str='train'):
        pass
    def load_from_remote_model_registry(self, specification:dict, usage:str='train'):
        return None
    def save_in_ailever_model_registry(self, specification:dict, usage:str='train'):
        pass
    def save_in_local_model_registry(self, specification:dict, usage:str='train'):
        pass
    def save_in_remote_model_registry(self, specification:dict, usage:str='train'):
        pass



    # model_registry/forecasting_model_registry
    def load_from_ailever_forecasting_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/forecasting_model_registry
    def load_from_local_forecasting_model_registry(self, specification:dict, usage:str='train'):
        if usage == 'train':
            source = specification['__loading_name_from_FMR__']
            if source:
                checkpoint = torch.load(os.path.join(specification['__loading_path_from_FMR__'], source))
                self.__core_instances['model'].load_state_dict(checkpoint['model_state_dict'])
                self.__core_instances['optimizer'].load_state_dict(checkpoint['optimizer_state_dict'])
                self.__core_instances['cumulative_epochs'] = checkpoint['cumulative_epochs']
        elif usage == 'prediction':
            source = specification['__loading_name_from_FMR__']
            if source:
                checkpoint = torch.load(os.path.join(specification['__loading_path_from_FMR__'], source))
                self.__core_instances['model'].load_state_dict(checkpoint['model_state_dict'])
                self.__core_instances['train_mse'] = checkpoint['training_loss']
                self.__core_instances['validation_mse'] = checkpoint['validation_loss']
    # model_registry/forecasting_model_registry
    def load_from_remote_forecasting_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/forecasting_model_registry
    def save_in_ailever_forecasting_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/forecasting_model_registry
    def save_in_local_forecasting_model_registry(self, specification:dict, usage:str='train'):
        saving_path = os.path.join(specification['__storing_path_in_FMR__'], specification['__storing_name_in_FMR__']+'.pt')
        print(f"* Model's informations is saved({saving_path}).")
        torch.save({
            'model_state_dict': self.forecasting_model_registry['model'].to('cpu').state_dict(),
            'optimizer_state_dict': self.forecasting_model_registry['optimizer'].state_dict(),
            'epochs' : self.forecasting_model_registry['epochs'],
            'cumulative_epochs' : self.forecasting_model_registry['cumulative_epochs'],
            'training_loss': self.forecasting_model_registry['train_mse'],
            'validation_loss': self.forecasting_model_registry['validation_mse']}, saving_path)
    # model_registry/forecasting_model_registry
    def save_in_remote_forecasting_model_registry(self, specification:dict, usage:str='train'):
        pass



    # model_registry/strategy_model_registry
    def load_from_ailever_strategy_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/strategy_model_registry
    def load_from_local_strategy_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/strategy_model_registry
    def load_from_remote_strategy_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/strategy_model_registry
    def save_in_ailever_strategy_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/strategy_model_registry
    def save_in_local_strategy_model_registry(self, specification:dict, usage:str='train'):
        pass
    # model_registry/strategy_model_registry
    def save_in_remote_strategy_model_registry(self, specification:dict, usage:str='train'):
        pass




    def load_from_local_analysis_report_repository(self, specification:dict, usage:str='train'):
        pass
    def load_from_remote_analysis_report_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_ailever_analysis_report_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_local_analysis_report_repository(self, specification:dict, usage:str='prediction'):
        pass
    def load_from_ailever_analysis_report_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_remote_analysis_report_repository(self, specification:dict, usage:str='train'):
        pass




    # analysis_report_repository/fundamental_analysis_result
    def load_from_ailever_fundamental_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def load_from_local_fundamental_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def load_from_remote_fundamental_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def save_in_ailever_fundamental_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def save_in_local_fundamental_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/fundamental_analysis_result
    def save_in_remote_fundamental_analysis_result(self, specification:dict, usage:str='train'):
        pass




    # analysis_report_repository/technical_analysis_result
    def load_from_ailever_technical_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/technical_analysis_result
    def load_from_local_technical_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/technical_analysis_result
    def load_from_remote_technical_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/technical_analysis_result
    def save_in_ailever_technical_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/technical_analysis_result
    def save_in_local_technical_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/technical_analysis_result
    def save_in_remote_technical_analysis_result(self, specification:dict, usage:str='train'):
        pass




    # analysis_report_repository/model_prediction_result
    def load_from_ailever_model_prediction_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/model_prediction_result
    def load_from_local_model_prediction_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/model_prediction_result
    def load_from_remote_model_prediction_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/model_prediction_result
    def save_in_ailever_model_prediction_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/model_prediction_result
    def save_in_local_model_prediction_result(self, specification:dict, usage:str='train'):
        if usage == 'train':
            pass
        elif usage == 'prediction':
            saving_path = specification['__storing_path_in_MPR__']
            saving_name = specification['__storing_name_in_MPR__']
            prediction_table_file_name = os.path.join(saving_path, saving_name)
            self.model_prediction_result['prediction_table'].to_csv(prediction_table_file_name+'.csv')
            for column, fig in self.model_prediction_result['prediction_visualization'].items():
                prediction_image_file_name = os.path.join(saving_path, saving_name)
                fig.savefig(prediction_image_file_name + f'_{column}.png')
            print(f"* Model's prediction result is saved({saving_path}).")
    # analysis_report_repository/model_prediction_result
    def save_in_remote_model_prediction_result(self, specification:dict, usage:str='train'):
        pass




    # analysis_report_repository/sector_analysis_result
    def load_from_ailever_sector_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/sector_analysis_result
    def load_from_local_sector_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/sector_analysis_result
    def load_from_remote_sector_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/sector_analysis_result
    def save_in_ailever_sector_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/sector_analysis_result
    def save_in_local_sector_analysis_result(self, specification:dict, usage:str='train'):
        pass
    # analysis_report_repository/sector_analysis_result
    def save_in_remote_sector_analysis_result(self, specification:dict, usage:str='train'):
        pass




    def load_from_ailever_investment_outcome_repository(self, specification:dict, usage:str='train'):
        pass
    def load_from_local_investment_outcome_repository(self, specification:dict, usage:str='train'):
        pass
    def load_from_remote_investment_outcome_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_ailever_investment_outcome_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_local_investment_outcome_repository(self, specification:dict, usage:str='train'):
        pass
    def save_in_remote_investment_outcome_repository(self, specification:dict, usage:str='train'):
        pass



    # investment_outcome_repository/optimized_portfolio_registry
    def load_from_ailever_optimized_portfolio_registry(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def load_from_local_optimized_portfolio_registry(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def load_from_remote_optimized_portfolio_registry(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def save_in_ailever_optimized_portfolio_registry(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def save_in_local_optimized_portfolio_registry(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/optimized_portfolio_registry
    def save_in_remote_optimized_portfolio_registry(self, specification:dict, usage:str='train'):
        pass



    # investment_outcome_repository/backtesting_repository
    def load_from_ailever_backtesting_repository(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/backtesting_repository
    def load_from_local_backtesting_repository(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/backtesting_repository
    def load_from_remote_backtesting_repository(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/backtesting_repository
    def save_in_ailever_backtesting_repository(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/backtesting_repository
    def save_in_local_backtesting_repository(self, specification:dict, usage:str='train'):
        pass
    # investment_outcome_repository/backtesting_repository
    def save_in_remote_backtesting_repository(self, specification:dict, usage:str='train'):
        pass



    def load_from_ailever_metadata_store(self, specification:dict, usage:str='train'):
        # return : model_specification, outcome_reports
        return None
    def load_from_local_metadata_store(self, specification:dict, usage:str='train'):
        # return : model_specification, outcome_reports
        return None
    def load_from_remote_metadata_store(self, specification:dict, usage:str='train'):
        return None
    def save_in_ailever_metadata_store(self, specification:dict, usage:str='train'):
        pass
    def save_in_local_metadata_store(self, specification:dict, usage:str='train'):
        pass
    def save_in_remote_metadata_store(self, specification:dict, usage:str='train'):
        pass



    def load_from_ailever_monitoring_source(self, specification:dict, usage:str='train'):
        pass
    def load_from_local_monitoring_source(self, specification:dict, usage:str='train'):
        pass
    def load_from_remote_monitoring_source(self, specification:dict, usage:str='train'):
        pass
    def save_in_ailever_monitoring_source(self, specification:dict, usage:str='train'):
        pass
    def save_in_local_monitoring_source(self, specification:dict, usage:str='train'):
        pass
    def save_in_remote_monitoring_source(self, specification:dict, usage:str='train'):
        pass





