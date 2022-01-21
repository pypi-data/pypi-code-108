# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from ibm_watson_openscale.supporting_classes.enums import ProblemType
from ibm_watson_openscale.utils.training_stats import TrainingStats
from ibm_ai_openscale_cli.models.model import Model
import json
import pandas as pd

class StatisticsGenerator:

    def __init__(self, args):
        model = Model(args.model, args, 0)
        self._training_data_csv_file = model.training_data_csv_file
        self._problem_type_str = model.configuration_data['asset_metadata']['problem_type']
        self._label_column = model.configuration_data['asset_metadata']['label_column']
        self._feature_columns = model.configuration_data['asset_metadata']['feature_columns']
        self._training_data_type = model.configuration_data['training_data_type']
        self._categorical_columns = model.configuration_data['asset_metadata']['categorical_columns']
        self._fairness_inputs = {
            "fairness_attributes": model.configuration_data['fairness_configuration']['features'],
            "favourable_class": model.configuration_data['fairness_configuration']['favourable_classes'],
            "unfavourable_class": model.configuration_data['fairness_configuration']['unfavourable_classes'],
            "min_records": model.configuration_data['fairness_configuration']['min_records']
        }

    def generate_statistics(self):
        data_df = pd.read_csv( self._training_data_csv_file, dtype=self._training_data_type )
        properties = {
            'problem_type': self._get_problem_type_object(self._problem_type_str),
            'label_column': self._label_column,
            'feature_columns': self._feature_columns,
            'categorical_columns': self._categorical_columns,
            'fairness_inputs': self._fairness_inputs
        }
        training_data_stats = TrainingStats(data_df, properties, explain=True, fairness=True, drop_na=True).get_training_statistics()
        return json.dumps(training_data_stats)

    def _get_problem_type_object(self, type_str):
        if type_str == 'BINARY_CLASSIFICATION':
            return ProblemType.BINARY_CLASSIFICATION
        elif type_str == 'MULTICLASS_CLASSIFICATION':
            return ProblemType.MULTICLASS_CLASSIFICATION
        elif type_str == 'REGRESSION':
            return ProblemType.REGRESSION
        return None

