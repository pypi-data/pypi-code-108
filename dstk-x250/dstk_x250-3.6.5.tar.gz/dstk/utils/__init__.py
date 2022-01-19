#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ._chunk import Chunker, chunker
from ._date import date_inf, date_sup, convert_date_dataframe
from ._timeout import timeout
from ._check import check_dataframe, shape_list
from ._set_deep_params import set_params_deep
from ._statistique import weighted_avg_and_std
from ._transpose import (list_of_dict_2_dict_of_list,
                         dict_of_list_2_list_of_dict)
from ._rolling import RollingWindow

__all__ = (
    'Chunker',
    'chunker',
    'date_inf',
    'date_sup',
    'convert_date_dataframe',
    'timeout',
    'check_dataframe',
    'shape_list',
    'set_params_deep',
    'weighted_avg_and_std',
    'list_of_dict_2_dict_of_list',
    'dict_of_list_2_list_of_dict',
    'RollingWindow'
)
