from __future__ import annotations
from .checks import Calculation
from badook_tests.dsl.enums import ComparisonPoint
from typing import Optional
import unittest
import logging
import sys
import json
import functools
import shortuuid


class DatasetSummary(object):

    name = ""
    display_name = ""

    def __init__(self, ctx):
        self._ctx = ctx
        self.summaries = {}
        self.joined_datasets = {}
        self.user_features = {}

    def set_dataset(self, dataset):
        self.dataset = dataset

    def add_summary(self, summary: Summary) -> DatasetSummary:
        self.summaries[summary.name] = summary
        return self

    def set_name(self, name: str) -> DatasetSummary:
        # this is the summary folder's name in storage which needs to be unique
        self.name = f'{name[0:24]}-{shortuuid.uuid()}'

        # this is the summary name itself for display
        self.display_name = name
        return self

    def get_summary(self, name: str) -> Summary:
        return self.summaries[name]

    def collect(self):
        self._ctx.collect(self, 'summaries')

    def set_project_id(self, id):
        self.project_id = id

    def set_run_id(self, id):
        self.run_id = id

    def set_batch(self, batch_value):
        self.batch_value = batch_value

    def join_on(self, name, key: list = None, key_l: list = None, key_r: list = None) -> DatasetSummary:
        keys = []
        # if both datasets share the same key name
        if key:
            for key_item in key:
                keys.append([key_item, key_item])

        # if each dataset has different name for the key
        elif key_l and key_r and len(key_l) == len(key_r):
            for index, ket_l_item in enumerate(key_l, start=0):
                keys.append([ket_l_item, key_r[index]])

        else:
            raise ValueError("Invalid keys")

        self.joined_datasets[name] = {'keys': keys}

        """
        Dict structure:
        for joinOn 1:
            key_temp =  [[<key1A>, <key1B>],[<key2A>, <key2B>]]
            joined_datasets['name1'] = {'keys': key_temp }

        for joinOn 2:
            key_temp =  [[<keyCA>, <keyCA>]]
            joined_datasets['name2'] = {'keys': key_temp }

        The above process creates the following dict:
        joined_dataset = {
            name1:  {
                'keys':[[<key1A>, <key1B>],[<key2A>, <key2B>]],
                'batch_value: <name> -> optional (will be added in test_cases.py)
            },
            name2:  {
                'keys':[[<keyCA>, <keyCA>]],
                'batch_value: <name> -> optional (will be added in test_cases.py)
            }
        }
        """
        return self

    def with_user_feature(self, name, features, expression, feature_type) -> DatasetSummary:
        dict_temp = {'expression': expression,
                     'feature': features, 'type':  feature_type}
        self.user_features[name] = dict_temp
        return self

    def get_user_feature(self, features, name: str) -> DatasetSummary:
        if name in self.user_features:
            return self.user_features[name]
        else:
            raise ValueError(f"user_feature {name} was not set")


class SummaryData(object):

    def __init__(self, dataset, summary_name, name, run_id, join_on, time_window, summary_type, model_params):
        self.name = name
        self.summary_name = summary_name
        self.run_id = run_id
        self.join_on = join_on
        self.time_window = time_window
        self.dataset = dataset
        self.type = summary_type
        self.model_params = model_params


class Summary(object):

    _ctx = None

    def __init__(self, feature: str, name: str):
        self.name = name
        self.feature = feature
        self.user_calculations = {}
        self.feature_set = {}
        self.groups = None
        self.time_window = None
        self.type = ''
        self.model_params = {
            'isFit': False,
            'isPredict': False
        }

    def group_by(self, *args) -> Summary:
        self.groups = list(args)
        return self

    def set_time_window(self, time_key: str, time_format: str,  units: str, number_of_units):
        # ToDo: Change the format option to spark options in the docstring. Change the units options to the runner
        # options in the docstring.
        """
        Time format option: {'date', timestamp'}
        Units options: {years, months, weeks, days, hours, minutes, seconds}
        """
        self.time_window = {
            'time_key': time_key,
            'number_of_units': number_of_units,
            'units': units,
            'time_format': time_format
        }
        return self

    def add_udc(self, name: str, calculation, input_columns=None) -> Summary:
        self.user_calculations[name] = {
            'func': calculation,
            'input_columns': input_columns
        }

    def get_udc(self, name: str) -> Calculation:
        if name in self.user_calculations:
            return self.__dict__[name]
        else:
            raise ValueError(f"udc {name} was not set")

    def on(self, dataset_summary: DatasetSummary) -> Summary:
        dataset_summary.add_summary(self)
        self._ctx = dataset_summary._ctx
        self.dataset = dataset_summary.dataset
        self.parent = dataset_summary.name

        return self

    def get_historical_run(self, offset=None, run_id=None):

        if offset:
            run_id = int(self.run_id) - offset

        summary_folder_name = self.parent
        display_name = self._ctx.dataset_summaries[summary_folder_name]['display_name']

        data = {
            'projectId': self._ctx.project_name,
            'runId': run_id,
            'datasetDisplayName': display_name
        }

        # get offset run's summary data from service managment
        response = self._ctx.api_client.send_json_post_request(
            data, "runhistory/run/summary")
        if response['error']:
            message = f'Failed getting summary from run {run_id}: ' + \
                response['error']['message']
            raise Exception(message)

        return SummaryData(self.dataset, self.name, response['data']['name'], int(run_id), self.groups,
                           self.time_window, self.type, self.model_params)

    def set_run_id(self, id):
        self.run_id = id
        self.data = SummaryData(self.dataset, self.name, self.parent, self.run_id, self.groups,
                                self.time_window, self.type, self.model_params)

        if len(self.user_calculations) > 0:
            # add user calculation as a methods
            for udc in self.user_calculations:
                self.__dict__[udc] = Calculation(self.data, udc, self._ctx)

    def fit(self):
        self.model_params['isFit'] = True
        return self

    def predict(self):
        self.model_params['isPredict'] = True
        return self

    def fit_predict(self):
        self.model_params['isFit'] = True
        self.model_params['isPredict'] = True
        return self


class DurationSummary(Summary):

    def __init__(self, feature: str, name: str, time_format=None):
        super().__init__(feature, name)
        self.type = 'DurationSummary'
        self.feature_format = time_format

    @property
    def min(self):
        return Calculation(self.data, 'min', self._ctx)

    @property
    def max(self):
        return Calculation(self.data, 'max', self._ctx)

    @property
    def duration(self):
        return Calculation(self.data, 'duration', self._ctx)


class CounterSummary(Summary):

    def __init__(self, feature: str, name: str):
        super().__init__(feature, name)
        self.type = 'CounterSummary'

    @property
    def count(self):
        return Calculation(self.data, 'count', self._ctx)

    @property
    def count_distinct(self):
        return Calculation(self.data, 'count_distinct', self._ctx)


class NumericSummary(CounterSummary):

    def __init__(self, feature: str, name: str):
        super().__init__(feature, name)
        self.type = 'NumericSummary'

    @property
    def min(self):
        return Calculation(self.data, 'min', self._ctx)

    @property
    def max(self):
        return Calculation(self.data, 'max', self._ctx)

    @property
    def std_dev(self):
        return Calculation(self.data, 'std_dev', self._ctx)

    @property
    def mean(self):
        return Calculation(self.data, 'mean', self._ctx)

    @property
    def median(self):
        return Calculation(self.data, 'median', self._ctx)

    @property
    def sum(self):
        return Calculation(self.data, 'sum', self._ctx)


class PointSummary(NumericSummary):

    def __init__(self, feature: str, name: str):
        super().__init__(feature, name)
        self.type = 'PointSummary'

    @property
    def count(self):
        return Calculation(self.data, 'count', self._ctx)

    @property
    def count_distinct(self):
        return Calculation(self.data, 'count_destinct', self._ctx)

    @property
    def group(self):
        return Calculation(self.data, 'group', self._ctx)

    @property
    def max(self):
        return Calculation(self.data, 'max', self._ctx)

    @property
    def poly_fit_params(self):
        return Calculation(self.data, 'min', self._ctx)

    @property
    def dimension(self):
        return Calculation(self.data, 'dimension', self._ctx)


class PolygonSummary(NumericSummary):

    def __init__(self, feature: str, name: str):
        super().__init__(feature, name)
        self.type = 'PolygonSummary'

    @property
    def count(self):
        return Calculation(self.data, 'count', self._ctx)

    @property
    def count_distinct(self):
        return Calculation(self.data, 'count_distinct', self._ctx)

    @property
    def mean_area(self):
        return Calculation(self.data, 'mean_area', self._ctx)

    @property
    def max_area(self):
        return Calculation(self.data, 'max_area', self._ctx)

    @property
    def min_area(self):
        return Calculation(self.data, 'min_area', self._ctx)

    @property
    def std_area(self):
        return Calculation(self.data, 'std_area', self._ctx)

    @property
    def union(self):
        return Calculation(self.data, 'union', self._ctx)


class BooleanSummary(CounterSummary):

    def __init__(self, feature: str, name: str):
        super().__init__(feature, name)
        self.type = 'BooleanSummary'

    @property
    def countTrue(self):
        return Calculation(self.data, 'countTrue', self._ctx)

    @property
    def countFalse(self):
        return Calculation(self.data, 'countFalse', self._ctx)


class CategoricalSummary(Summary):

    def __init__(self, feature: str, name: str):
        super().__init__(feature, name)
        self.type = 'CategoricalSummary'

    @property
    def count(self):
        return Calculation(self.data, 'count', self._ctx)

    @property
    def percentage(self):
        return Calculation(self.data, 'percentage', self._ctx)
