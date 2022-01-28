from ._base_policy import initialization_policy

local_environment = dict()
local_environment['root'] = '.analysis'
local_environment['exploratory_data_analysis'] = 'exploratory_data_analysis'
__analysis_bs__ = initialization_policy(local_environment)

from .ANALYSISInterfaces import DataProcessor
from .ANALYSISInterfaces import DataTransformer
from .ANALYSISInterfaces import Evaluation
from .ANALYSISInterfaces import EDA
from .ANALYSISInterfaces import Probability

from .ANALYSISInterfaces import time_splitor
