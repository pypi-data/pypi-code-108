from ailever.investment import __fmlops_bs__ as fmlops_bs
from ..__base_structures import BaseTriggerBlock
from ..trigger_bridges import TorchTriggerBridge, TensorflowTriggerBridge, SklearnTriggerBridge, StatsmodelsTriggerBridge
from .._base_transfer import ModelTransferCore

import sys
import os


class SklearnTriggerBlock(SklearnTriggerBridge, BaseTriggerBlock):
    def __init__(self, training_info:dict, local_environment:dict=None, remote_environment:dict=None):
        super(SklearnTriggerBlock, self).__init__()
        # storing system
        self.feature_store = dict()
        self.source_repository = dict()
        self.model_registry = dict()
        self.forecasting_model_registry = dict()
        self.strategy_model_registry = dict()
        self.analysis_report_repository = dict()
        self.funcdamental_analysis_result = dict()
        self.technical_analysis_result = dict()
        self.model_prediction_result = dict()
        self.sector_analysis_result = dict()
        self.optimized_portfolio_registry = dict()
        sys.path.append(os.path.join(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'fmlops_forecasters'), 'sklearn'))

    def ui_buffer(self, specification:dict, usage='train'):
        return specification

    def train(self):
        pass

    def loaded_from(self, specification:dict, usage='train'):
        trigger_loading_process = specification['__loading_process_regulation__']
        self = loading_process_interchange(self, trigger_loading_process, specification, usage=usage)       

    def store_in(self, specification:dict, usage='train'):
        trigger_storing_process = specification['__storing_process_regulation__']
        self = storing_process_interchange(self, trigger_storing_process, specification, usage=usage)       

    def predict(self):
        pass

    def outcome_report(self):
        pass

    def ModelTransferCore(self):
        modelcore = ModelTransferCore()
        return modelcore


# loading path
def loading_process_interchange(self, trigger_loading_process:list, specification:dict, usage='train'):
    loading_path = dict()
    loading_path['FS'] = list()  # feature_store
    loading_path['SR'] = list()  # source_rpository
    loading_path['MR'] = list()  # model_rpository
    loading_path['FMR'] = list()  # forecasting_model_rpository
    loading_path['SMR'] = list()  # forecasting_model_rpository

    loading_path['FS'].extend([
        self.load_from_ailever_feature_store,
        self.load_from_local_feature_store,
        self.load_from_remote_feature_store,
    ])
    loading_path['SR'].extend([
        self.load_from_ailever_source_repository, 
        self.load_from_local_source_repository,  
        self.load_from_remote_source_repository,
    ])
    loading_path['MR'].extend([
        self.load_from_ailever_model_registry,
        self.load_from_local_model_registry,
        self.load_from_remote_model_registry,
    ])
    
    for fmlops, mode in trigger_loading_process:
        loading_path[fmlops][mode](specification, usage)
    return self

# storing_path
def storing_process_interchange(self, trigger_storing_process:list, specification:dict, usage:str='train'):
    storing_path = dict()
    storing_path['FS'] = list() # feature_store
    storing_path['MR'] = list() # model_registry
    storing_path['MS'] = list() # metadata_store

    storing_path['FS'].extend([
        self.save_in_ailever_feature_store,
        self.save_in_local_feature_store,
        self.save_in_remote_feature_store,
    ])
    storing_path['MR'].extend([
        self.save_in_ailever_model_registry,
        self.save_in_local_model_registry,
        self.save_in_remote_model_registry,
    ])
    storing_path['MS'].extend([
        self.save_in_ailever_metadata_store,
        self.save_in_local_metadata_store,
        self.save_in_remote_metadata_store,
    ])

    for fmlops, mode in trigger_storing_process:
        storing_path[fmlops][mode](specification, usage)
    return self

