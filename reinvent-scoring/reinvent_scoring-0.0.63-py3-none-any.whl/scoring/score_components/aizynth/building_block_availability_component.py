import json
import os
from typing import List

import numpy as np
from reinvent_chemistry.library_design.aizynth.aizynth_client import AiZynthClient

from reinvent_scoring.scoring.component_parameters import ComponentParameters
from reinvent_scoring.scoring.enums.environmental_variables_enum import EnvironmentalVariablesEnum
from reinvent_scoring.scoring.score_components.base_score_component import BaseScoreComponent
from reinvent_scoring.scoring.score_summary import ComponentSummary


class MockedLogger:
    def log_message(self, message: str):
        print(message)

class BuildingBlockAvailabilityComponent(BaseScoreComponent):
    def __init__(self, parameters: ComponentParameters):
        super().__init__(parameters)
        self._environment_keys = EnvironmentalVariablesEnum()
        self._aizynth_cient = self._set_up_client()

    def calculate_score(self, molecules: List, step=-1) -> ComponentSummary:
        valid_smiles = self._chemistry.mols_to_smiles(molecules)
        score = self._score_smiles(valid_smiles)
        score_summary = ComponentSummary(total_score=score, parameters=self.parameters, raw_score=score)

        return score_summary

    def _score_smiles(self, smiles: List[str]) -> np.array:
        list_of_pathways = self._aizynth_cient.batch_synthesis_prediction(smiles)
        results = self._aizynth_cient.batch_stock_availability_score(list_of_pathways)
        return np.array(results)

    def _set_up_client(self):
        logger = MockedLogger()
        prediction_url = self._get_enviornment_variable(self._environment_keys.AIZYNTH_PREDICTION_URL)
        availability_url = self._get_enviornment_variable(self._environment_keys.AIZYNTH_BUILDING_BLOCKS_URL)
        api_token = self._get_enviornment_variable(self._environment_keys.AIZYNTH_TOKEN)
        aizynth_cient = AiZynthClient(prediction_url, availability_url, api_token, logger)
        return aizynth_cient

    def _get_enviornment_variable(self, variable: str) -> str:
        try:
            return os.environ[variable]
        except KeyError:
            return self._retrieve_aizynth_key_from_config(variable)

    def _retrieve_aizynth_key_from_config(self, variable: str) -> str:
        try:
            project_root = os.path.dirname(__file__)
            with open(os.path.join(project_root, '../../../configs/config.json'), 'r') as f:
                config = json.load(f)
            environmental_variables = config[self._environment_keys.ENVIRONMENTAL_VARIABLES]
            return environmental_variables[variable]
        except KeyError as ex:
            raise KeyError(f"Key {variable} not found in reinvent_scoring/configs/config.json")