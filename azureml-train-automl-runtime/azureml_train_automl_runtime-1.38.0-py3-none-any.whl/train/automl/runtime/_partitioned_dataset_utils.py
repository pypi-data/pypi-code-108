# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import random
import pandas as pd
import copy
from typing import Dict, Any, List

import dask.dataframe as dd
import dask.delayed as ddelayed
from azureml.data import TabularDataset
from azureml.dataprep import Dataflow


class CustomTabularDataset:
    """
    A workaround until we can read a partition without listing folders
    """

    def __init__(
        self,
        tabular_dataset: TabularDataset,
        grain_keys_values: Dict[str, Any],
    ):
        self.tabular_dataset = tabular_dataset
        self.grain_keys_values = grain_keys_values

    def to_pandas_dataframe(self) -> pd.DataFrame:
        dataframe_to_return = self.tabular_dataset.to_pandas_dataframe()
        for k in self.grain_keys_values:
            dataframe_to_return[k] = self.grain_keys_values[k]
        return dataframe_to_return


def _get_dataset_for_grain(grain_keys_values: Dict[str, Any],
                           partitioned_dataset: TabularDataset) -> TabularDataset:

    # build the new path to replace the old path with
    old_path = partitioned_dataset._dataflow._steps[0].arguments['datastores'][0]['path']
    partition_format = ""
    for step in partitioned_dataset._dataflow._steps[1:]:
        if step.step_type == "Microsoft.DPrep.AddColumnsFromPartitionFormatBlock":
            partition_format = step.arguments['partitionFormat']
            break

    for k in grain_keys_values:
        partition_format = partition_format.replace("{" + k + "}", str(grain_keys_values[k]), 1)
    new_path = '/'.join([old_path.strip('/'), partition_format.strip('/')])

    # we have the new path. So use it to build a new dataset
    new_datasource_step = copy.deepcopy(partitioned_dataset._dataflow._steps[0])
    new_datasource = new_datasource_step.arguments['datastores'][0]
    new_datasource['path'] = new_path
    new_datasource_step.arguments['datastores'] = [new_datasource]

    new_steps = [new_datasource_step]
    for step in partitioned_dataset._dataflow._steps[1:]:
        if step.step_type != "Microsoft.DPrep.AddColumnsFromPartitionFormatBlock":
            new_steps = new_steps + [step]

    new_dataflow = Dataflow(partitioned_dataset._dataflow._engine_api, new_steps)
    new_dataset = TabularDataset._create(new_dataflow, partitioned_dataset._properties,
                                         telemetry_info=partitioned_dataset._telemetry_info)
    return CustomTabularDataset(new_dataset, grain_keys_values)


def _get_dataset_for_grain_with_filter(grain_keys_values: Dict[str, Any],
                                       partitioned_dataset: TabularDataset) -> TabularDataset:
    filter_condition = None
    for key, value in grain_keys_values.items():
        new_condition = partitioned_dataset[key] == value
        filter_condition = new_condition if filter_condition is None else filter_condition & new_condition
    return partitioned_dataset.filter(filter_condition)


def _to_partitioned_dask_dataframe(partitioned_dataset: TabularDataset,
                                   all_grain_key_values: List[Dict[str, Any]]) -> dd:
    datasets_for_all_grains = [_get_dataset_for_grain(kv, partitioned_dataset)
                               for kv in all_grain_key_values]
    delayed_functions = [ddelayed(dataset_for_grain.to_pandas_dataframe)()
                         for dataset_for_grain in datasets_for_all_grains]
    ddf = dd.from_delayed(delayed_functions, verify_meta=False)
    return ddf


def _to_dask_dataframe_of_random_grains(partitioned_dataset: TabularDataset,
                                        all_grain_key_values: List[Dict[str, Any]],
                                        grain_count: int) -> dd:
    random_grain_key_values = all_grain_key_values
    if grain_count < len(all_grain_key_values):
        random_grain_key_values = random.sample(all_grain_key_values, grain_count)

    datasets_for_all_grains = [_get_dataset_for_grain(kv, partitioned_dataset)
                               for kv in random_grain_key_values]
    delayed_functions = [ddelayed(dataset_for_grain.to_pandas_dataframe)()
                         for dataset_for_grain in datasets_for_all_grains]
    ddf = dd.from_delayed(delayed_functions, verify_meta=False)
    return ddf
