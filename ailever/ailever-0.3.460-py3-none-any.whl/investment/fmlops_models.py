from ailever.investment import __fmlops_bs__ as fmlops_bs
from .fmlops_management import *
from .trigger_blocks import TorchTriggerBlock, TensorflowTriggerBlock, SklearnTriggerBlock, StatsmodelsTriggerBlock

import re
from pprint import pprint

"""

* FMLOps Policy
- [FMLOPS] .fmlops
  |-- [FS] feature_store [Semi-Automation]
      |--  [FS1d] 1d
      |--  [FS1H] 1H
      |--  [FS1M] 1M
      |--  [FS1t] 1t
  |-- [SR] source_repository [Semi-Automation]
  |-- [MR] model_registry [Automation]
      |-- [FMR] forecasting_model_registry [Automation]
      |-- [SMR] strategy_model_registry [Heuristic Semi-Automation]
  |-- [ARR] analysis_report_repository [Heuristic Semi-Automation]
      |-- [FAR] fundamental_analysis_result
      |-- [TAR] technical_analysis_result
      |-- [MPR] model_prediction_result
      |-- [SAR] sector_analysis_result
  |-- [IOR] investment_outcome_repository [Automation]
      |-- [SR1] screening_registry
      |-- [OPR] optimized_portfolio_registry
      |-- [BR] backtesting_repository
  |-- [MS] metadata_store [Automation]
      |-- [MS1] monitoring_source [Automation]
      |-- [DM] data_management
      |-- [MM] model_management
      |-- [MS2] model_specification


* Forecaster
- train_trigger loading process : [FS], [SR], [FMR]
- train_trigger storing process : [FMR], [MS3]
- prediction_trigger loading process : [FMR]
- prediction_trigger storing process : [MPR]
- analysis_trigger loading process : [FS]
- analysis_trigger storing process : [FAR], [TAR], [SAR]
- evaluation_trigger loading process : -
- evaluation_trigger storing process : -

* Strategist
- portfolio_trigger loading process : [FS], [FAR], [TAR], [MPR], [SAR]
- portfolio_trigger storing process : [OPR]
- backtesting_trigger loading process : [FS], [OPR]
- backtesting_trigger storing process : [BR]


"""




class Forecaster:
    def __init__(self, local_environment:dict=None, remote_environment:dict=None):
        self._fs_manager = FS_Manager() # feature_store
        self._sr_manager = SR_Manager() # source_repository
        self._mr_manager = MR_Manager() # model_registry
        self._fmr_manager = FMR_Manager() # forecasting_model_registry
        self._far_manager = FAR_Manager() # fundamental_analysis_result
        self._tar_manager = TAR_Manager() # technical_analysis_result
        self._mpr_manager = MPR_Manager() # model_prediction_result
        self._sar_manager = SAR_Manager() # sectore_analysis_result
        
        self.trigger_block = dict()
        self.trigger_block['torch'] = TorchTriggerBlock(local_environment=local_environment, remote_environment=remote_environment)
        self.trigger_block['tensorflow'] = None
        self.trigger_block['xgboost'] = None
        self.trigger_block['sklearn'] = None
        self.trigger_block['statsmodels'] = None
 
    def integrated_trigger(self, baskets:list, integrated_specifications:dict):
        train_trigger(integrated_specifications['train'])
        prediction_trigger(integrated_specifications['prediction'])
        analysis_trigger(integrated_specifications['analysis'])
        evaluation_trigger(integrated_specifications['evaluation'])

    def train_trigger(self, baskets:list, train_specifications:dict):
        trigger = 'train'
        for security in baskets:
            # initializing train_specification
            train_specifications[security]['ticker'] = security
            train_specification = train_specifications[security]
            train_specification['__loading_process_regulation__'] = list()
            train_specification['__storing_process_regulation__'] = list()
            framework = train_specification['framework']
            train_specification = self.trigger_block[framework].ui_buffer(train_specification, usage=trigger)
            
            # loading
            train_specification = self._fs_manager.loading_connection(train_specification, usage=trigger)
            train_specification = self._sr_manager.loading_connection(train_specification, usage=trigger)
            train_specification = self._fmr_manager.loading_connection(train_specification, usage=trigger)

            # trigger core : training
            self.trigger_block[framework].loaded_from(train_specification, usage=trigger)
            self.trigger_block[framework].train(train_specification)
            
            # storing
            train_specification = self._fmr_manager.storing_connection(train_specification, usage=trigger)
            self.trigger_block[framework].store_in(train_specification, usage=trigger)
    
    def prediction_trigger(self, baskets:list, prediction_specifications:dict):
        trigger = 'prediction'
        for security in baskets:
            # initializing prediction_specification
            prediction_specifications[security]['ticker'] = security
            prediction_specification = prediction_specifications[security]
            prediction_specification['__loading_process_regulation__'] = list()
            prediction_specification['__storing_process_regulation__'] = list()
            framework = prediction_specification['framework']
            prediction_specification = self.trigger_block[framework].ui_buffer(prediction_specification, usage=trigger)
            
            # loading
            prediction_specification = self._sr_manager.loading_connection(prediction_specification, usage=trigger)
            prediction_specification = self._fmr_manager.loading_connection(prediction_specification, usage=trigger)

            # trigger core : prediction
            self.trigger_block[framework].loaded_from(prediction_specification, usage=trigger)
            self.trigger_block[framework].predict(prediction_specification)
            
            # storing
            prediction_specification = self._mpr_manager.storing_connection(prediction_specification, usage=trigger)
            self.trigger_block[framework].store_in(prediction_specification, usage=trigger)

    def analysis_trigger(self, baskets:list, analysis_specifications:dict):
        pass

    def evaluation_trigger(self, baskets:list, evaluation_specifications:dict):
        pass
 
    def available_models(self, baskets:list):
        for security in baskets:
            local_model_saving_informations = self._fmr_manager.local_finder(entity='ticker', target=security, framework=None) # list of dicts
            available_local_models = list(filter(lambda x: x[entity] == security, local_model_saving_informations))
            remote_model_saving_informations = self._fmr_manager.remote_finder(entity='ticker', target=security, framework=None) # list of dicts
            available_remote_models = list(filter(lambda x: x[entity] == security, remote_model_saving_informations))
            pprint(f'[AILEVER] Available {security} models in local system (L): ', available_local_models)
            pprint(f'[AILEVER] Available {security} models in remote system (R): ', available_remote_models)
            
    def forecasting_model_registry(self, command:str, framework:str=None):
        if command == 'listdir':
            return self._listdir(framework, fmlops_symbol='fmr')
        elif command == 'listfiles':
            return self._listfiles(framework, fmlops_symbol='fmr')
        elif command == 'remove':
            return self._remove(framework, fmlops_symbol='fmr')
        elif command == 'clearall':
            return self._clearall(framework, fmlops_symbol='fmr')
        elif command == 'copyall':
            return self._copyall(framework, fmlops_symbol='fmr')

    def model_prediction_result(self, command:str, framework:str=None):
        if command == 'listdir':
            return self._listdir(framework, fmlops_symbol='mpr')
        elif command == 'listfiles':
            return self._listfiles(framework, fmlops_symbol='mpr')
        elif command == 'remove':
            return self._remove(framework, fmlops_symbol='mpr')
        elif command == 'clearall':
            return self._clearall(framework, fmlops_symbol='mpr')
        elif command == 'copyall':
            return self._copyall(framework, fmlops_symbol='mpr')

    def _listdir(self, framework:str=None, fmlops_symbol=None):
        return getattr(self, f'_{fmlops_symbol}_manager').listdir(framework=framework)
    
    def _listfiles(self, framework:str=None, fmlops_symbol=None):
        return getattr(self, f'_{fmlops_symbol}_manager').listfiles(framework=framework)

    def _remove(self, framework:str=None, fmlops_symbol=None):
        pprint(getattr(self, f'_{fmlops_symbol}_manager').listfiles(framework=framework))
        if fmlops_sysbol == 'fmr':
            id = int(input('ID : '))
            answer = input(f"Type 'Yes' if you really want to delete the model{id} in forecasting model registry.")
            if answer == 'Yes':
                model_saving_infomation = self._fmr_manager.local_finder(entity='id', target=id, framework=framework)
                self._fmr_manager.remove(name=model_saving_infomation['model_saving_name'], framework=framework)
        else:
            answer = input(f"Which file do you like to remove? : ")
            getattr(self, f'_{fmlops_symbol}_manager').remove(name=answer, framework=framework)
    
    def _clearall(self, framework=None, fmlops_symbol=None):
        answer = input(f"Type 'YES' if you really want to delete all models in forecasting model registry.")
        if answer == 'YES':
            getattr(self, f'_{fmlops_symbol}_manager').clearall(framework=framework)
    
    def _copyall(self, framework=None, fmlops_symbol=None):
        getattr(self, f'_{fmlops_symbol}_manager').copyall(framework=framework)


    def report(self, baskets:list):
        modelcore = self.trigger_block.ModelTransferCore()
        return modelcore

    def upload(self):
        pass

    def max_profit(self):
        pass

    def summary(self):
        pass



class Strategist:
    def __init__(self):
        self._ior_manager = IOR_Manager() # investment_outcome_repository
        self._opr_manager = OPR_Manager() # optimized_portfolio_registry

    def integrated_trigger(self):
        self.portfolio_trigger()
        self.backtesting_trigger()
    
    def portfolio_trigger(self):
        pass

    def backtesting_trigger(self):
        pass

    def strategy_model_registry(self, command:str, framework:str=None):
        pass

    def _smr_listdir(self, framework:str=None):
        pass

    def _smr_listfiles(self, framework:str=None):
        pass

    def _smr_remove(self, framework:str=None):
        pass

    def _smr_clearall(self, framework=None):
        pass

    def analysis_report_repository(self, command:str, framework:str=None):
        pass

    def _arr_listdir(self, framework:str=None):
        pass

    def _arr_listfiles(self, framework:str=None):
        pass

    def _arr_remove(self, framework:str=None):
        pass
    
    def _arr_clearall(self, framework=None):
        pass
